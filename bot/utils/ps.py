import requests
import re
import os
from bot.utils import logger

# Base API URL
base_api_url = "https://notpx.app/api/v1/"
base_page_url = "https://app.notpx.app/"
js_save_path = "local_index.js"  # Path to save the updated JS file

# Patterns for detecting JavaScript and API references
js_file_pattern = re.compile(r'src="(/.*?/index.*?\.js)"')
api_pattern = re.compile(r'["\'](/api/v1/.*?)["\']')

# Expected API endpoints
expected_apis = [
    "/users/me",
    "/users/stats",
    "/image/template/my",
    "/mining/status",
    "/image/template/subscribe/",
    "/mining/claim",
    "/mining/boost/check/",
    "/mining/task/check/"
]


def fetch_page_content(url):
    """Fetch the HTML content of a webpage."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.warning(f"Error fetching page content from {url}: {e}")
        return None


def fetch_js_files(page_content):
    """Extract JavaScript file paths from the page content."""
    matches = js_file_pattern.findall(page_content)
    return sorted(set(matches), key=len, reverse=True) if matches else None


def fetch_and_save_js(js_url, save_path):
    """Download and save the JavaScript file locally."""
    try:
        response = requests.get(js_url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        logger.success(f"Updated JS file saved to {save_path}")
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch the JS file from {js_url}: {e}")


def verify_apis_in_js(js_url):
    """Check if the required APIs are present in the JavaScript file."""
    try:
        response = requests.get(js_url)
        response.raise_for_status()
        content = response.text
        detected_apis = api_pattern.findall(content)
        missing_apis = [api for api in expected_apis if api not in detected_apis]
        if missing_apis:
            logger.warning(f"Missing APIs: {missing_apis}")
            return False
        return True
    except requests.RequestException as e:
        logger.warning(f"Error fetching JS file for API verification: {e}")
        return False


def auto_update_js():
    """Main function to check and auto-update the JavaScript file."""
    logger.info("Checking for JavaScript updates...")
    page_content = fetch_page_content(base_page_url)
    if not page_content:
        logger.warning("Failed to fetch the base page content.")
        return

    js_files = fetch_js_files(page_content)
    if not js_files:
        logger.warning("No JavaScript files found on the base page.")
        return

    for js_file in js_files:
        js_url = f"{base_page_url.rstrip('/')}{js_file}"
        logger.info(f"Checking JavaScript file: {js_url}")

        if verify_apis_in_js(js_url):
            logger.success("No changes detected in API structure. File is up-to-date.")
        else:
            logger.warning("Changes detected. Fetching updated JavaScript file...")
            fetch_and_save_js(js_url, js_save_path)
            break  # Stop after handling the first update


if __name__ == "__main__":
    auto_update_js()
