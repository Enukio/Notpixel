import requests
import re
from bot.config import settings
from bot.utils import logger

BASE_URL = "https://notpx.app/api/v1/"

API_ENDPOINTS = [
    "/users/me",
    "/users/stats",
    "/image/template/my",
    "/mining/status",
    "/image/template/subscribe/",
    "/mining/claim",
    "/mining/boost/check/",
    "/mining/task/check/"
]

LS_PATTERN = re.compile(r'\b[a-zA-Z]+\s*=\s*["\'](https?://[^"\']+)["\']')
E_GET_PATTERN = re.compile(r'[a-zA-Z]\.get\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')
E_PUT_PATTERN = re.compile(r'[a-zA-Z]\.put\(\s*["\']([^"\']+)["\']|\(\s*`([^`]+)`\s*\)')


def clean_url(url):
    """Clean and normalize a URL by removing query parameters and redundant slashes."""
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    return re.sub(r'//+', '/', url)


def get_main_js_formats(base_url):
    """Fetch main.js formats by scanning the HTML content of the base URL."""
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', response.text)
        return sorted(set(matches), key=len, reverse=True) if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None


def get_base_api(js_url):
    """Extract API URLs from the JavaScript content."""
    try:
        logger.info("Checking for changes in API...")
        response = requests.get(js_url, timeout=10)
        response.raise_for_status()
        content = response.text

        # Extract GET and PUT URLs
        e_get_urls = [url[0] or url[1] for url in E_GET_PATTERN.findall(content)]
        e_put_urls = [url[0] or url[1] for url in E_PUT_PATTERN.findall(content)]
        clean_urls = [clean_url(url) for url in e_get_urls + e_put_urls]

        # Check for changes in known API endpoints
        for endpoint in API_ENDPOINTS:
            if endpoint not in clean_urls:
                logger.warning(f"<yellow>API {endpoint} changed!</yellow>")
                return None

        # Match base URL patterns
        matches = LS_PATTERN.findall(content)
        return matches if matches else None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def check_base_url():
    """Verify if the base URL and its APIs remain unchanged."""
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_formats(base_url)

    if not main_js_formats:
        logger.info("No main.js format found. Dumping page content for inspection...")
        try:
            response = requests.get(base_url, timeout=10)
            logger.debug(response.text[:1000])  # Print the first 1000 characters for debugging
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
        return False

    for js_path in main_js_formats:
        full_url = f"https://app.notpx.app{js_path}"
        logger.info(f"Trying format: {js_path}")

        if settings.ADVANCED_ANTI_DETECTION:
            try:
                r = requests.get("https://raw.githubusercontent.com/Enukio/Nothing/refs/heads/main/px", timeout=10)
                js_version = r.text.strip()
                if js_version in js_path:
                    logger.success(f"<green>No change in JS file: {js_version}</green>")
                    return True
            except requests.RequestException as e:
                logger.warning(f"Error fetching JS version: {e}")
        else:
            result = get_base_api(full_url)
            if result is None:
                return False
            if BASE_URL in result:
                logger.success("<green>No change in API!</green>")
                return True

    logger.warning("Base URL or APIs have changed!")
    return False
