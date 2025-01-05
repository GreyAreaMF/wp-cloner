from .download import select_themes_or_plugins
from ..scan_website import scan_website
from ..manifest_builder import build_manifests
from ..cleanup import cleanup_downloads

def show():
    print("Welcome to WordPress Cloner!")

    while True:
        print("\nMain Menu")
        print("1. Download Themes or Plugins")
        print("2. Find a Website's Installed Themes and Plugins")
        print("3. Build Manifest File")
        print("4. Cleanup Downloads")
        print("5. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            select_themes_or_plugins()
        elif choice == '2':
            scan_website()
        elif choice == '3':
            build_manifests()
        elif choice == '4':
            cleanup_downloads()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid selection. Please try again.")

