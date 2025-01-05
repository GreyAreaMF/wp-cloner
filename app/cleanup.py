import os
import json
from packaging import version

MANIFEST_FILE = "downloads/manifest.json"
PLUGIN_DIR = "downloads/plugins"
THEME_DIR = "downloads/themes"

removed_items = []


def cleanup_downloads():
    global removed_items

    if not os.path.exists(MANIFEST_FILE):
        print("Manifest file not found. No cleanup needed.")
        exit_script()

    with open(MANIFEST_FILE, 'r') as f:
        manifest_data = json.load(f)

    print("\nStarting cleanup...")

    # Process plugins and themes
    for content_type in ['plugins', 'themes']:
        if content_type in manifest_data:
            for slug, versions in manifest_data[content_type].items():
                perform_cleanup(slug, versions, content_type, manifest_data)

    # Save updated manifest
    save_manifest(manifest_data)
    print_summary()
    exit_script()


def perform_cleanup(slug, versions, content_type, manifest_data):
    global removed_items
    duplicates = {}

    for ver, data in versions.items():
        key = (data.get('version file'), data.get('version type'), data.get('version regex'))
        if key not in duplicates:
            duplicates[key] = []
        duplicates[key].append(ver)

    # Remove older versions if duplicates exist
    for key, version_list in duplicates.items():
        if len(version_list) > 1:
            version_list.sort(key=version.parse)

            for old_version in version_list[:-1]:
                print(f"Removing {slug} (v{old_version}) due to duplicate metadata.")
                remove_version(slug, old_version, content_type)
                removed_items.append(f"{slug} (v{old_version})")
                del manifest_data[content_type][slug][old_version]

            if not manifest_data[content_type][slug]:
                del manifest_data[content_type][slug]


def remove_version(slug, ver, content_type):
    target_dir = os.path.join(f"downloads/{content_type}", slug, ver)
    if os.path.exists(target_dir):
        print(f"Deleting {target_dir}")
        os.system(f"rm -rf {target_dir}")
    else:
        print(f"{target_dir} not found. Skipping filesystem cleanup.")


def save_manifest(manifest_data):
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Manifest updated at {MANIFEST_FILE}")


def print_summary():
    if removed_items:
        print("\nCleanup Summary:")
        for item in removed_items:
            print(f" - {item}")
    else:
        print("\nNo duplicate versions found. No files were removed.")


def exit_script():
    print("\nCleanup process completed. Exiting...")
    os._exit(0)