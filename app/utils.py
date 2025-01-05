import os
import zipfile

def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)

def extract_zip(zip_path, extract_to):
    ensure_directory_exists(extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)