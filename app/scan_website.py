import os
import csv
import json
import requests
from urllib.parse import urlparse
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

MANIFEST_FILE = "downloads/manifest.json"
OUTPUT_DIR = "output"
FILE_CHECK_LIMIT = 10  # Default limit for file checks per plugin/theme

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def scan_website():
    url = input("Enter the website URL to scan: ").strip()
    if not url.startswith('http'):
        url = 'http://' + url

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split('.')[-2]  # Extract top-level domain
    output_file = os.path.join(OUTPUT_DIR, f"{domain}.csv")

    if not os.path.exists(MANIFEST_FILE):
        print("Manifest file not found. Please build the manifest first.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"Failed to fetch website: {e}")
        return

    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)

    results = []

    # Scan plugins and themes using the manifest
    for content_type in ['plugins', 'themes']:
        if content_type in manifest:
            for slug, versions in manifest[content_type].items():
                print(f"Looking for {slug}...")
                found, version = check_for_match(slug, versions, html, url)
                if found:
                    print(f"Found {slug} (v{version})")
                    results.append({
                        "slug": slug,
                        "type": content_type[:-1],
                        "version": version or "unknown"
                    })

    # Additional HTML parsing to detect unknown plugins/themes
    found_slugs = {entry["slug"] for entry in results}

    # Regex to extract href/src attributes from tags, handling single and double quotes
    tag_regex = r'(?:href|src)=["\'](https?://.*?/wp-content/(plugins|themes)/([^/]+)/)'

    for match in re.findall(tag_regex, html):
        link = match[0]
        slug = match[2]
        check_link(link, url, found_slugs, results, slug, match[1])

    # Write results to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["slug", "type", "version"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Scan complete. Results saved to {output_file}")
    os._exit(0)


def check_link(link, url, found_slugs, results, slug, content_type):
    if slug not in found_slugs:
        print(f"Found {slug} (vunknown)")
        results.append({"slug": slug, "type": content_type, "version": "unknown"})
        found_slugs.add(slug)


def check_for_match(slug, versions, html, base_url):
    for version, details in versions.items():
        version_file = details.get('version file', '')
        version_regex = details.get('version regex', '')
        files = details.get('files', [])[:FILE_CHECK_LIMIT]

        if version_file and version_file in html:
            match = re.search(version_regex, html)
            return True, match.group(0) if match else version

        for file in files:
            file_url = f"{base_url}/{file}"
            try:
                response = requests.head(file_url, verify=False)
                if response.status_code == 200:
                    return True, version
            except requests.RequestException:
                continue

    return False, None