import requests
import sys  # Import sys to allow exiting the script

class WordPressAPI:
    BASE_URL = "https://api.wordpress.org/{}/info/1.2/"

    def __init__(self, endpoint):
        self.url = self.BASE_URL.format(endpoint)

    def fetch(self, criteria, max_results, extra=None):
        params = {
            'action': 'query_plugins' if self.url.endswith('plugins/info/1.2/') else 'query_themes',
            'per_page': max_results,
            'browse': criteria
        }
        if extra:
            params['slug'] = extra if criteria == 'tag' else ''
            params['author'] = extra if criteria == 'author' else ''

        response = requests.get(self.url, params=params)

        try:
            # Attempt to parse JSON
            data = response.json()
            return data.get('plugins', []) if 'plugins' in response.json() else response.json().get('themes', [])

        except ValueError:  # Raised by response.json() if decoding fails
            print("Failed to decode JSON response.")
            print("Raw response content:")
            print(response.content)
            sys.exit(1)