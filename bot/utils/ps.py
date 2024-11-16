import requests
import re
import time
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

# Regular expression patterns for parsing
ls_pattern = re.compile(r'\b[a-zA-Z_]+\s*=\s*["\'](https?://[^"\']+)["\']')
e_get_pattern = re.compile(r'[a-zA-Z_]\.get\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')
e_put_pattern = re.compile(r'[a-zA-Z_]\.put\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')


def clean_url(url):
    """
    Cleans and normalizes the given URL.
    """
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    url = re.sub(r'//+', '/', url)
    return url


def fetch_remote_version(url, max_retries=3, retry_delay=2):
    """
    Fetches the remote version for advanced anti-detection.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: Failed to fetch remote version: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    logger.error("Failed to fetch remote version after multiple attempts.")
    return None


def get_main_js_format(base_url):
    """
    Fetches and identifies potential JS files from the given base URL.
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', response.text)
        return sorted(set(matches), key=len, reverse=True) if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None


def get_base_api(url):
    """
    Extracts and validates APIs from the JS content of the given URL.
    """
    try:
        logger.info("Checking for changes in API...")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        match = ls_pattern.findall(content)
        e_get_urls = e_get_pattern.findall(content)
        e_put_urls = e_put_pattern.findall(content)

        if not e_get_urls and not e_put_urls:
            return None

        urls = [url[0] if url[0] else url[1] for url in e_get_urls]
        urls_put = [url[0] if url[0] else url[1] for url in e_put_urls]
        clean_urls = [clean_url(url) for url in urls] + [clean_url(url) for url in urls_put]

        for api in apis:
            if api not in clean_urls:
                logger.warning(f"<yellow>API {api} changed!</yellow>")
                return None

        return match if match else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def check_base_url():
    """
    Verifies the base URL for any changes in JS files or APIs.
    """
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)

    if not main_js_formats:
        logger.warning("No JS formats found.")
        return False

    if settings.ADVANCED_ANTI_DETECTION:
        logger.info("Advanced anti-detection enabled. Checking JS file version...")
        remote_version_url = "https://raw.githubusercontent.com/Enukio/Nothing/refs/heads/main/px"
        remote_version = fetch_remote_version(remote_version_url)

        if not remote_version:
            logger.error("Could not verify JS file version due to failed remote fetch.")
            return False

        for js_file in main_js_formats:
            if remote_version in js_file:
                logger.success(f"No change in JS file: {remote_version}")
                return True

        logger.warning("Mismatch in JS file versions detected.")
        return False

    logger.info("Advanced anti-detection disabled. Checking API...")
    for js_format in main_js_formats:
        full_url = f"https://app.notpx.app{js_format}"
        result = get_base_api(full_url)
        if result and baseUrl in result:
            logger.success("<green>No change in API!</green>")
            return True

    logger.warning("Base URL or API verification failed.")
    return False
