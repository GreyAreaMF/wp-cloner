import os
import csv
import requests
from urllib.parse import urlparse, urlencode

OUTPUT_DIR = "output"
DOWNLOAD_DIR = "downloads"
API_URL = "https://api.wordpress.org/{}/info/1.2/"


def download_from_website_csv(domain):
    csv_file = os.path.join(OUTPUT_DIR, f"{domain}.csv")

    if not os.path.exists(csv_file):
        print(f"No CSV found for {domain}. Run a site scan first.")
        return

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row['slug']
            content_type = row['type']  # plugin or theme
            version = row['version']

            if version == "unknown":
                print(f"{slug} has unknown version. Fetching latest version...")
                version = get_latest_version(slug, content_type)

            if not version:
                print(f"Skipping {slug}. Unable to determine version.")
                continue

            download_path = os.path.join(DOWNLOAD_DIR, content_type, slug, version)

            if os.path.exists(download_path):
                print(f"{slug} (v{version}) already downloaded.")
                continue

            print(f"Downloading {slug} (v{version})...")
            download_plugin_or_theme(slug, version, content_type, download_type)


def get_latest_version(slug, content_type):
    api_action = 'plugin_information' if content_type == 'plugin' else 'theme_information'
    params = {
        'action': api_action,
        'request[slug]': slug
    }

    try:
        response = requests.get(API_URL.format(content_type), params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('version')
    except (requests.RequestException, ValueError):
        print(f"Failed to fetch latest version for {slug}.")
        return None


def download_plugins_or_themes(download_type, browse=None, tag=None, author=None):
    # Prompt the user for the number of items to download
    default_dl_size = 10
    max_items = input(f"How many {download_type} would you like to download? (default {default_dl_size}): ").strip()
    max_items = int(max_items) if max_items.isdigit() else default_dl_size

    if download_type == "plugins":
        params = {
            'action': f'query_{download_type}',
            'request[browse]': browse,
            'request[tag]': tag,
            'request[author]': author,
            'request[per_page]': max_items,
        }
    else:
        params = {
            'action': f'query_{download_type}',
            'per_page': max_items,
            'fields': {
                'downloadlink': True,
            }
        }
        if browse:
            params['browse'] = browse
        if tag:
            params['tag'] = tag
        if author:
            params['author'] = author
        

    try:
        response = requests.get(API_URL.format(download_type), params=params)
        response.raise_for_status()
        data = response.json()

        items = data.get(download_type, [])
        for item in items:
            slug = item['slug']
            version = item['version']
            download_link = item['download_link']

            download_path = os.path.join(DOWNLOAD_DIR, download_type, slug)
            if os.path.exists(os.path.join(download_path, version)):
                print(f"{slug} (v{version}) already downloaded.")
                continue

            print(f"Downloading {slug} (v{version})...")
            download_and_extract(download_link, download_path, slug, version)
            
    except requests.RequestException as e:
        print(f"Failed to fetch {download_type}: {e}")
        query_string = urlencode(params, doseq=True)
        print(f"{API_URL.format(download_type)}?{query_string}")
    except ValueError as e:
        print("Failed to parse response from API.")
        print(response.content)
    except Exception as e:
        query_string = urlencode(params, doseq=True)
        print(f"{API_URL.format(download_type)}?{query_string}")
        raise


def download_plugin_or_theme(slug, version, content_type):
    api_action = 'plugin_information' if content_type == 'plugin' else 'theme_information'

    params = {
        'action': api_action,
        'request[slug]': slug
    }

    try:
        response = requests.get(API_URL.format(content_type), params=params)
        response.raise_for_status()
        data = response.json()

        if 'download_link' in data and (data['version'] == version or version == "latest"):
            download_link = data['download_link']
            save_path = os.path.join(DOWNLOAD_DIR, content_type, slug)
            os.makedirs(save_path, exist_ok=True)
            download_and_extract(download_link, save_path, slug, version)
        else:
            print(f"Version mismatch or download link not found for {slug}.")
    except ValueError as e:
        print(f"Failed to parse API response for {slug}. Error: {e}")
        print(response.content)


def download_and_extract(url, save_path, slug, version):
    zip_file = os.path.join(save_path, "download.zip")

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            os.makedirs(save_path, exist_ok=True)
            with open(zip_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded to {zip_file}. Extracting...")

        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(save_path)
        os.remove(zip_file)

        # Move the extracted plugin to the version directory.
        os.rename(os.path.join(save_path, slug), os.path.join(save_path, version))
        print("Extraction complete.")
    except Exception as e:
        print(f"Error during download or extraction: {e}")
