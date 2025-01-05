import os
import re

# Default patterns for detecting versions in files
DEFAULT_PATTERNS = [
    r"== Changelog ==.*?= ([0-9]+\.[0-9]+\.[0-9]+) =",  # Changelog in readme.txt
    r"##\s+([0-9]+\.[0-9]+(\.[0-9]+)?)\s+-\s+[0-9]{4}-[0-9]{2}-[0-9]{2}",  # CHANGELOG.md format
    r"## ([0-9]+\.[0-9]+(\.[0-9]+)?) / [0-9]{4}-[0-9]{2}-[0-9]{2}",  # Alt changelog format (7.0.3 / 2023-10-16)
    r"Stable tag:\s+([0-9]+\.[0-9]+(\.[0-9]+)?)",  # Readme stable tag
]

# Default files to check for versioning information
DEFAULT_VERSION_FILES = ["readme.txt", "changelog.txt", "CHANGELOG.md"]


def detect_version(plugin_path):
    """
    Detects the version of a plugin or theme by scanning version files (e.g., readme.txt, CHANGELOG.md).
    Returns the regex that matched, the file it was found in, or None if no match is found.
    """
    for file in DEFAULT_VERSION_FILES:
        file_path = os.path.join('./', plugin_path, file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in DEFAULT_PATTERNS:
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        return pattern, file

    return None, None
