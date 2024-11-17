import requests
import re
import os
from bot.config import settings
from bot.utils import logger

# Constants
BASE_URL = "https://notpx.app/api/v1/"
APIS = [
    "/users/me",
    "/users/stats",
    "/image/template/my",
    "/mining/status",
    "/image/template/subscribe/",
    "/mining/claim",
    "/mining/boost/check/",
    "/mining/task/check/"
]

# Regex patterns
LS_PATTERN = re.compile(r'\b[a-zA-Z]+\s*=\s*["\'](https?://[^"\']+)["\']')
E_GET_PATTERN = re.compile(r'[a-zA-Z]\.get\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')
E_PUT_PATTERN = re.compile(r'[a-zA-Z]\.put\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')

# Utility Functions
def clean_url(url):
    """Cleans a URL by removing query parameters and template expressions."""
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    url = re.sub(r'//+', '/', url)
    return url

def get_main_js_format(base_url):
    """Fetches main.js file formats from the base URL."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        return sorted(set(matches), key=len, reverse=True) if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None

def get_base_api(url):
    """Checks for API changes in the provided JavaScript file URL."""
    try:
        logger.info("Checking for changes in API...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        matches = LS_PATTERN.findall(content)
        e_get_urls = E_GET_PATTERN.findall(content)
        e_put_urls = E_PUT_PATTERN.findall(content)

        urls = [url[0] if url[0] else url[1] for url in e_get_urls]
        urls_put = [url[0] if url[0] else url[1] for url in e_put_urls]
        clean_urls = [clean_url(url) for url in urls + urls_put]

        for api in APIS:
            if api not in clean_urls:
                logger.warning(f"API {api} has changed!")
                return None

        return matches if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None

def find_px_file(project_root):
    """
    Searches for the 'px' file starting from the given project root.

    Args:
        project_root (str): The root directory to start the search.

    Returns:
        str: The full path to the 'px' file if found, else None.
    """
    logger.info(f"Searching for 'px' file starting from: {project_root}")
    for root, _, files in os.walk(project_root):
        if "px" in files:
            px_path = os.path.join(root, "px")
            logger.info(f"Found 'px' file at: {px_path}")
            return px_path
    logger.error(f"The file 'px' was not found in the project directory: {project_root}")
    return None

def check_base_url():
    """Checks if the base URL's JavaScript files or APIs have changed."""
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)

    if not main_js_formats:
        logger.info("No main.js formats found. Attempting to inspect base URL content.")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])  # Print a snippet of the page for debugging
        except requests.RequestException as e:
            logger.warning(f"Error fetching base URL content: {e}")
        return False

    if settings.ADVANCED_ANTI_DETECTION:
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            px_path = find_px_file(project_root)
            if not px_path:
                return False

            with open(px_path, "r") as file:
                js_ver = file.read().strip()
                logger.info(f"Read version from 'px': {js_ver}")

            if any(js_ver in js for js in main_js_formats):
                logger.success(f"<green>No changes detected in js file: {js_ver}</green>")
                return True

            logger.warning("Version in 'px' does not match any detected JS files.")
        except FileNotFoundError:
            logger.error("The 'px' file was not found.")
        except Exception as e:
            logger.error(f"Unexpected error reading 'px': {e}")
        return False
    else:
        for js_format in main_js_formats:
            full_url = f"https://app.notpx.app{js_format}"
            if get_base_api(full_url):
                logger.success("<green>No changes detected in API!</green>")
                return True
        logger.warning("No matching baseURL detected in JavaScript files.")
        return False

if __name__ == "__main__":
    # Example Usage: Find `px` in the "Notpixel" directory
    notpixel_root = "/path/to/Notpixel"  # Update with your Notpixel directory
    px_file_path = find_px_file(notpixel_root)

    if px_file_path:
        print(f"'px' file found at: {px_file_path}")
    else:
        print("File 'px' not found.")
