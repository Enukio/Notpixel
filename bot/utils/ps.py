import requests
import re
import time
from urllib.parse import urlparse, urlunparse

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
    Normalizes and cleans a given URL by:
    - Removing query strings and fragments.
    - Replacing redundant slashes.
    - Stripping any placeholder interpolations.
    """
    parsed_url = urlparse(url)
    cleaned_url = urlunparse(parsed_url._replace(query="", fragment=""))
    cleaned_url = re.sub(r'\$\{.*?\}', '', cleaned_url)
    cleaned_url = re.sub(r'//+', '/', cleaned_url)
    return cleaned_url


def safe_request(url, method="GET", max_retries=3, retry_delay=2, **kwargs):
    """
    Safe wrapper for requests to handle errors and retry on HTTP 500 responses.
    
    Parameters:
        - url (str): The URL to fetch.
        - method (str): HTTP method (default: GET).
        - max_retries (int): Number of retry attempts for server errors (500).
        - retry_delay (int): Delay between retries in seconds.
        - kwargs: Additional arguments for the request.
    """
    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, **kwargs)
            else:
                raise ValueError("Unsupported method.")
            
            if response.status_code == 500:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Server error 500 at {url}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Server error 500 persists after {max_retries} attempts at {url}")
                    return None
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts.")
                return None


def get_main_js_format(base_url):
    """
    Fetches and identifies potential JS files from a given base URL.
    """
    try:
        response = safe_request(base_url)
        if not response:
            return []
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', response.text)
        return sorted(set(matches), key=lambda x: len(x), reverse=True)
    except Exception as e:
        logger.warning(f"Unexpected error: {e}")
        return []


def get_base_api(url):
    """
    Extracts and validates APIs from the JS content of a given URL.
    """
    try:
        logger.info("Checking for changes in API...")
        response = safe_request(url)
        if not response:
            return None

        content = response.text
        match = ls_pattern.findall(content)
        e_get_urls = e_get_pattern.findall(content)
        e_put_urls = e_put_pattern.findall(content)

        if not e_get_urls and not e_put_urls:
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
    """
    Verifies the base URL for any changes in JS files or APIs.
    """
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)

    if not main_js_formats:
        logger.info("No JS formats found. Dumping page content...")
        response = safe_request(base_url)
        if response:
            logger.debug(response.text[:1000].encode("utf-8", errors="replace").decode("utf-8"))
        return False

    for format in main_js_formats:
        logger.info(f"Trying format: {format}")
        full_url = f"{base_url.rstrip('/')}{format}"
        result = get_base_api(full_url)
        if result and baseUrl in result:
            logger.success("<green>No change in API!</green>")
            return True

    logger.warning("Base URL or API verification failed.")
    return False
