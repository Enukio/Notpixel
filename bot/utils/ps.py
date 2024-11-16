import os
import re
import requests
from bot.utils import logger

BASE_URL = "https://app.notpx.app/"
ASSETS_URL = "https://app.notpx.app/assets/"
LOCAL_JS_PATH = "./index-jwT_7CAk.js"  # Path to save the JS file locally
TARGET_JS_PATTERN = r'index-[^"]+\.js'  # Pattern to match index files like `index-jwT_7CAk.js`


def fetch_index_js_files():
    """Fetches JavaScript files from the assets directory."""
    try:
        logger.info(f"Fetching JavaScript files from: {BASE_URL}")
        response = requests.get(BASE_URL)
        response.raise_for_status()
        content = response.text

        # Regex to find `index-*.js` in assets
        matches = re.findall(r'src="(/assets/' + TARGET_JS_PATTERN + r')"', content)
        if matches:
            js_files = [f"{BASE_URL.rstrip('/')}{match}" for match in matches]
            logger.success(f"Found JS files: {js_files}")
            return js_files
        else:
            logger.warning("No matching index JS files found.")
            return None

    except requests.RequestException as e:
        logger.error(f"Error while fetching JavaScript files: {e}")
        return None


def download_js_file(file_url, save_path):
    """Downloads the specific JavaScript file if available."""
    try:
        logger.info(f"Attempting to download: {file_url}")
        response = requests.get(file_url)
        response.raise_for_status()

        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        logger.success(f"File downloaded and saved to {save_path}")
        return True

    except requests.RequestException as e:
        logger.error(f"Error downloading the file: {e}")
        return False


def auto_update_js_file():
    """Auto-updates JavaScript files matching the target pattern."""
    logger.info("Starting auto-update for index JS files...")
    js_files = fetch_index_js_files()

    if not js_files:
        logger.warning("No index JS files available for update.")
        return

    for file_url in js_files:
        if TARGET_JS_PATTERN in file_url:
            success = download_js_file(file_url, LOCAL_JS_PATH)
            if success:
                logger.success(f"Auto-update completed for: {file_url}")
                break
        else:
            logger.info(f"Skipping file: {file_url}")


if __name__ == "__main__":
    auto_update_js_file()
