import requests
import re
from bot.config import settings
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

ls_pattern = re.compile(r'\b[a-zA-Z]+\s*=\s*["\'](https?://[^"\']+)["\']')
e_get_pattern = re.compile(r'[a-zA-Z]\.get\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')
e_put_pattern = re.compile(r'[a-zA-Z]\.put\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')

def clean_url(url):
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    url = re.sub(r'//+', '/', url)
    return url

def fetch_latest_index():
    """Fetch the latest index file from the provided URL and log the changes."""
    index_url = "https://app.notpx.app/assets/index"
    try:
        response = requests.get(index_url)
        response.raise_for_status()
        content = response.text
        logger.info("Fetched the latest index file successfully.")
        return content
    except requests.RequestException as e:
        logger.warning(f"Error fetching the index file: {e}")
        return None

def update_apis(new_api_list):
    """Update the API list based on the detected changes."""
    global apis
    logger.info(f"Updating API list with: {new_api_list}")
    apis = new_api_list

def auto_fix_changes(base_url, detected_changes):
    """Auto-fix detected API changes by fetching updated information."""
    try:
        logger.warning("Detected API changes. Attempting auto-fix...")
        latest_index = fetch_latest_index()
        if latest_index:
            logger.success("Successfully fetched the latest index.")
            # Parse the new APIs from the index if necessary
            # For this example, we'll log and assume the user handles further parsing
            new_apis = re.findall(r'"(/[^"]+)"', latest_index)
            update_apis(new_apis)
            return True
        else:
            logger.error("Failed to auto-fix changes.")
            return False
    except Exception as e:
        logger.error(f"Error during auto-fix: {e}")
        return False

def get_main_js_format(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        return sorted(set(matches), key=len, reverse=True) if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None

def check_base_url():
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        for format in main_js_formats:
            full_url = f"https://app.notpx.app{format}"
            result = get_base_api(full_url)
            if result is None:
                logger.warning("API change detected.")
                auto_fix_changes(base_url, apis)
                return False
            elif baseUrl in result:
                logger.success("<green>No change in API!</green>")
                return True
        else:
            logger.warning("Could not verify 'baseURL' in the JS files.")
            return False
    else:
        logger.info("Could not find main.js formats.")
        return False
