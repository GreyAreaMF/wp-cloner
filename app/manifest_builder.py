import os
import json
from .detect_version import detect_version  # Use the refactored detect_version.py

MANIFEST_FILE = "downloads/manifest.json"
PLUGIN_DIR = "downloads/plugins"
THEME_DIR = "downloads/themes"

# List of paths to ignore during manifest generations
IGNORE_PATHS = ["vendor_prefixed", "vendor", "modules", "jetpack_vendor"]

no_match_plugins = []


def build_manifests():
    if os.path.exists(MANIFEST_FILE):
        choice = input(
            "Manifest file already exists. Would you like to (1) Update or (2) Replace it? [1/2]: "
        ).strip()
        if choice == '2':
            os.remove(MANIFEST_FILE)
            print("Manifest file replaced.")
        else:
            print("Manifest will be updated.")
    manifest_data = load_manifest()

    print("\nBuilding manifest files...")

    # Process plugins
    generate_manifest(PLUGIN_DIR, "plugins", manifest_data)

    # Process themes
    generate_manifest(THEME_DIR, "themes", manifest_data)

    save_manifest(manifest_data)

    if no_match_plugins:
        print("\nPlugins with no version match found:")
        for item in no_match_plugins:
            print(f" - {item['slug']} (v{item['version']})")
    else:
        print("\nAll plugins matched successfully.")

    print("Manifest generation completed. Exiting...")
    os._exit(0)


def generate_manifest(base_dir, content_type, manifest_data):
    if not os.path.exists(base_dir):
        print(f"{base_dir} not found. Skipping...")
        return

    for slug in os.listdir(base_dir):
        slug_path = os.path.join(base_dir, slug)
        if os.path.isdir(slug_path):
            for version in os.listdir(slug_path):
                version_path = os.path.join(slug_path, version)
                if os.path.isdir(version_path):
                    version_regex, version_file = detect_version(version_path)  # Refactored detect_version
                    if not version_regex and not version_file:
                        no_match_plugins.append({'slug': slug, 'version': version})
                    update_manifest(manifest_data, content_type, slug, version, slug_path, version_file, version_regex)


def update_manifest(manifest_data, content_type, slug, version, slug_path, version_file, version_regex):        
    manifest_entry = manifest_data.setdefault(content_type, {}).setdefault(slug, {}).setdefault(version, {
        'slug': slug,
        'version file': version_file,
        'version regex': version_regex,
        'files': []
    })

    # Add files, removing the version number from paths
    for root, _, files in os.walk(slug_path):
        if any(ignored in root.split(os.sep) for ignored in IGNORE_PATHS):
            continue
        for file in files:
            if not file.endswith('.php'):
                full_path = os.path.join(root, file)

                # Remove the irrelevant part of the path
                parts = full_path.split(os.sep)
                normalized_path = os.path.join('wp_content', content_type, slug, *parts[4:])
                
                manifest_entry['files'].append(normalized_path)


def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_manifest(manifest_data):
    with open(MANIFEST_FILE, 'w') as f:
        json_data = json.dumps(manifest_data, indent=4, ensure_ascii=False)
        f.write(json_data)

    print(f"Manifest updated at {MANIFEST_FILE}")
