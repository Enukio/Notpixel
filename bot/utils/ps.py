import os
import requests
import re
from bot.config import settings
from bot.utils import logger

# Base URLs and API
baseUrl = "https://notpx.app/api/v1/"
SPECIFIC_JS_URL = "https://app.notpx.app/assets/index-jwT_7CAk.js"
LOCAL_JS_PATH = "./index-jwT_7CAk.js"  # Path to save the JS file locally

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


def auto_update_js_file(js_url, local_path):
    """Fetches the specific JavaScript file and updates it if there's any change."""
    try:
        logger.info(f"Checking for updates in the JS file: {js_url}")
        response = requests.get(js_url)
        response.raise_for_status()  # Raise an error for bad responses

        # Check if the local file exists and compare its content
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as file:
                local_content = file.read()

            if response.text == local_content:
                logger.success("No changes detected in the JS file.")
                return True
            else:
                logger.warning("Changes detected in the JS file. Updating...")
        
        # Save the new version of the file
        with open(local_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        logger.success(f"JS file updated and saved to {local_path}")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to fetch the JS file: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during JS file update: {e}")
        return False


def get_main_js_format(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        if matches:
            # Return all matches, sorted by length (assuming longer is more specific)
            return sorted(set(matches), key=len, reverse=True)
        else:
            return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None


def get_base_api(url):
    try:
        logger.info("Checking for changes in API...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        match = ls_pattern.findall(content)
        e_get_urls = e_get_pattern.findall(content)
        e_put_urls = e_put_pattern.findall(content)

        if e_get_urls is None:
            return None

        urls = [url[0] if url[0] else url[1] for url in e_get_urls]
        urls_put = [url[0] if url[0] else url[1] for url in e_put_urls]
        clean_urls = [clean_url(url) for url in urls] + [clean_url(url) for url in urls_put]

        for url in apis:
            if url not in clean_urls:
                logger.warning(f"<yellow>API {url} changed!</yellow>")
                return None

        if match:
            return match
        else:
            logger.info("Could not find 'API' in the content.")
            return None

    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def check_base_url():
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        if settings.ADVANCED_ANTI_DETECTION:
            r = requests.get("https://raw.githubusercontent.com/Enukio/Nothing/refs/heads/main/px")
            js_ver = r.text.strip()
            for js in main_js_formats:
                if js_ver in js:
                    logger.success(f"<green>No change in JS file: {js_ver}</green>")
                    return True
            return False
        else:
            for format in main_js_formats:
                logger.info(f"Trying format: {format}")
                full_url = f"https://app.notpx.app{format}"
                result = get_base_api(full_url)
                if result is None:
                    return False

                if baseUrl in result:
                    logger.success("<green>No change in API!</green>")
                    return True
                return False
            else:
                logger.warning("Could not find 'baseURL' in any of the JS files.")
                return False
    else:
        logger.info("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])  # Print first 1000 characters of the page
            return False
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
            return False


def check_and_update_specific_js():
    logger.info("Starting specific JS file update check...")
    if auto_update_js_file(SPECIFIC_JS_URL, LOCAL_JS_PATH):
        logger.success("Specific JS file is up-to-date.")
    else:
        logger.error("Failed to update the specific JS file.")


# Integration
if __name__ == "__main__":
    check_and_update_specific_js()
    check_base_url()
