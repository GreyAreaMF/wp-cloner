import os
from ..downloader import download_plugins_or_themes, download_from_website_csv


OUTPUT_DIR = "output"


def select_themes_or_plugins():
    while True:
        options = {
            "1": "Plugins",
            "2": "Themes",
            "3": "Back to Main Menu",
        }
        
        print("\nSelect Download Type:")
        for key, value in options.items():
            print(f"{key}. {value}")

        choice = input("\nSelect and option: ")
    
        if choice == "1":
            download_menu("plugins")
        elif choice == "2":
            download_menu("themes")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
            download_themes_or_plugins()

def download_menu(download_type):
    while True:
        print("\nDownload Themes or Plugins")
        print("1. Active Installs")
        print("2. Newest")
        print("3. Author")
        print("4. Recently Updated")
        print("5. Tag")
        print("6. From Website CSV")
        print("7. Back to Download Type Selection")

        choice = input("Select an option: ")

        if choice == '1':
            download_plugins_or_themes(download_type, browse="popular")
        elif choice == '2':
            download_plugins_or_themes(download_type, browse="new")
        elif choice == '4':
            download_plugins_or_themes(download_type, browse="updated")
        elif choice == '3':
            author = input("Enter the author name: ").strip()
            if author:
                download_plugins_or_themes(download_type, author=author)
            else:
                print("Author name cannot be empty.")
        elif choice == '5':
            tag = input("Enter the tag: ").strip()
            if tag:
                download_plugins_or_themes(download_type, tag=tag)
            else:
                print("Tag cannot be empty.")
        elif choice == '6':
            list_and_download_from_csv()
        elif choice == '7':
            break
        else:
            print("This option is not yet implemented.")
    
def list_and_download_from_csv():
    if not os.path.exists(OUTPUT_DIR):
        print("Output directory not found.")
        return

    csv_files = [
        f[:-4] for f in os.listdir(OUTPUT_DIR)
        if f.endswith('.csv')
    ]

    if not csv_files:
        print("No CSV files found in the output directory.")
        return

    print("\nSelect a CSV file to download plugins/themes from:")
    for i, file in enumerate(csv_files, start=1):
        print(f"{i}. {file}")

    try:
        selection = int(input("\nEnter the number of the CSV: ")) - 1
        if selection < 0 or selection >= len(csv_files):
            print("Invalid selection.")
            return

        selected_domain = csv_files[selection]
        download_from_website_csv(selected_domain)
    except ValueError:
        print("Invalid input. Please enter a number.")
