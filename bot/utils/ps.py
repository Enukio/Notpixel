import requests
import re
from bot.config import settings
from bot.utils import logger
from requests.exceptions import HTTPError, Timeout, RequestException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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

@retry(
    retry=retry_if_exception_type(RequestException),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)

def clean_url(url):
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    url = re.sub(r'//+', '/', url)
    return url

def get_main_js_format(base_url):
    try:
        response = fetch_url_with_retries(base_url)
        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        if matches:
            logger.info(f"JS file matches found: {matches}")
            return sorted(set(matches), key=len, reverse=True)
        else:
            logger.warning("No JS matches found.")
            return None
    except HTTPError as http_err:
        logger.error(f"HTTP error for {base_url}: {http_err}")
    except Timeout as timeout_err:
        logger.error(f"Timeout for {base_url}: {timeout_err}")
    except RequestException as req_err:
        logger.error(f"Request exception for {base_url}: {req_err}")
    return None

def get_base_api(url):
    try:
        logger.info(f"Checking API at URL: {url}")
        response = fetch_url_with_retries(url)
        content = response.text
        e_get_urls = e_get_pattern.findall(content)
        e_put_urls = e_put_pattern.findall(content)

        urls = [url[0] if url[0] else url[1] for url in e_get_urls]
        urls_put = [url[0] if url[0] else url[1] for url in e_put_urls]
        clean_urls = [clean_url(url) for url in urls] + [clean_url(url) for url in urls_put]

        for api in apis:
            if api not in clean_urls:
                logger.warning(f"<yellow>API {api} has changed.</yellow>")
                return None
        return True
    except HTTPError as http_err:
        logger.error(f"HTTP error for {url}: {http_err}")
    except Timeout as timeout_err:
        logger.error(f"Timeout for {url}: {timeout_err}")
    except RequestException as req_err:
        logger.error(f"Request exception for {url}: {req_err}")
    return None

def check_base_url():
    base_url = "https://app.notpx.app/"
    logger.info(f"Starting base URL check: {base_url}")
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        if settings.ADVANCED_ANTI_DETECTION:
            try:
                response = fetch_url_with_retries("https://raw.githubusercontent.com/Enukio/Nothing/refs/heads/main/px")
                js_ver = response.text.strip()
                for js in main_js_formats:
                    if js_ver in js:
                        logger.success(f"<green>No changes in JS file: {js_ver}</green>")
                        return True
            except RequestException as req_err:
                logger.error(f"Error fetching remote JS version: {req_err}")
            return False
        else:
            for format in main_js_formats:
                full_url = f"{base_url}{format}"
                result = get_base_api(full_url)
                if result:
                    logger.success("<green>No changes in API detected.</green>")
                    return True
                else:
                    logger.warning(f"Failed to validate API for URL: {full_url}")
            logger.warning("No valid base URL or API changes found.")
            return False
    else:
        logger.warning("No main JS formats found. Attempting to dump page content.")
        try:
            response = fetch_url_with_retries(base_url)
            logger.debug(f"Page content snippet: {response.text[:500]}")
        except RequestException as req_err:
            logger.error(f"Error fetching base URL content: {req_err}")
        return False
