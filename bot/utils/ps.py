import requests
import re
import os
from bot.utils import logger

baseUrl = "https://notpx.app/api/v1/"

apis = [
    "/users/me",
    "/users/stats",
    "/image/template/my",
    "/mining/status",
    "/image/template/subscribe/",
    "/mining/claim",
    "/mining/boost/check/",
    "/mining/task/check/"
]

# Regular expressions for patterns
ls_pattern = re.compile(r'\b[a-zA-Z]+\s*=\s*["\'](https?://[^"\']+)["\']')
e_get_pattern = re.compile(r'[a-zA-Z]\.get\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')
e_put_pattern = re.compile(r'[a-zA-Z]\.put\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')


def clean_url(url):
    """Clean the URL by removing dynamic segments."""
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    url = re.sub(r'//+', '/', url)
    return url


def get_main_js_format(base_url):
    """Fetch the base URL and look for JavaScript files matching 'index.*.js'."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        return sorted(set(matches), key=len, reverse=True) if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None


def fetch_and_save_js(file_url, save_path):
    """Fetch the latest JavaScript file and save it locally."""
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        logger.success(f"Updated JS file saved to {save_path}")
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch the updated JS file: {e}")


def get_base_api(url):
    """Check for changes in the API structure."""
    try:
        logger.info("Checking for changes in the API...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        e_get_urls = e_get_pattern.findall(content)
        e_put_urls = e_put_pattern.findall(content)

        urls = [url[0] if url[0] else url[1] for url in e_get_urls]
        urls_put = [url[0] if url[0] else url[1] for url in e_put_urls]
        clean_urls = [clean_url(url) for url in urls] + [clean_url(url) for url in urls_put]

        for api in apis:
            if api not in clean_urls:
                logger.warning(f"<yellow>API {api} changed!</yellow>")
                return None

        match = ls_pattern.findall(content)
        return match if match else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def check_and_auto_update():
    """Check the base URL for updates and auto-fetch the latest file if needed."""
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)
    save_path = "local_index.js"

    if main_js_formats:
        for js_file in main_js_formats:
            full_url = f"https://app.notpx.app{js_file}"
            result = get_base_api(full_url)

            if result is None:
                logger.warning("Mismatch detected. Fetching the updated file...")
                fetch_and_save_js(full_url, save_path)
                return False

            if baseUrl in result:
                logger.success("<green>No changes detected in the API!</green>")
                return True
        logger.warning("Could not find 'baseUrl' in any of the JS files.")
        return False
    else:
        logger.info("No JS file formats found. Manual inspection required.")
        return False
