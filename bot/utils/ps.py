import requests
import re
import os
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

def download_js_file(full_url, output_dir="./"):
    """Download and save a JavaScript file to the specified directory."""
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        file_name = os.path.basename(full_url)
        output_path = os.path.join(output_dir, file_name)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        logger.success(f"Downloaded: {file_name}")
        return True
    except requests.RequestException as e:
        logger.warning(f"Error downloading file {full_url}: {e}")
        return False

def get_main_js_format(base_url, output_dir="./"):
    """Get and download main JavaScript files."""
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        if matches:
            matches = sorted(set(matches), key=len, reverse=True)
            for match in matches:
                full_url = f"https://notpx.app{match}"
                download_js_file(full_url, output_dir)
            return matches
        else:
            logger.info("No matching JavaScript files found.")
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
            logger.info("Could not find 'api' in the content.")
            return None

    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None

def check_base_url(output_dir="./"):
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url, output_dir)

    if main_js_formats:
        for format in main_js_formats:
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
