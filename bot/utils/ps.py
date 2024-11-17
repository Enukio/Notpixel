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

# Function to clean URLs
def clean_url(url):
    url = url.split('?')[0]
    url = re.sub(r'\$\{.*?\}', '', url)
    url = re.sub(r'//+', '/', url)
    return url

# Function to fetch main.js formats
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

# Function to analyze base API changes
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

# Function to find the px file using os.walk
def find_px_file(project_root):
    logger.info(f"Searching for 'px' file starting from: {project_root}")
    for root, _, files in os.walk(project_root):
        if "px" in files:
            px_path = os.path.join(root, "px")
            logger.info(f"Found 'px' file at: {px_path}")
            return px_path
    logger.error(f"The file 'px' was not found in the project directory: {project_root}")
    return None

# Function to check if the base URL has changed
def check_base_url():
    base_url = "https://app.notpx.app/"
    main_js_formats = get_main_js_format(base_url)

    if main_js_formats:
        if settings.ADVANCED_ANTI_DETECTION:
            try:
                # Locate the project root directory dynamically
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Adjust if needed
                px_path = find_px_file(project_root)  # Search for the px file

                if not px_path:
                    return False

                # Attempt to open and read the file
                with open(px_path, "r") as file:
                    js_ver = file.read().strip()
                    logger.info(f"Successfully read version from 'px': {js_ver}")
                
                # Check if the version matches any of the main.js formats
                for js in main_js_formats:
                    if js_ver in js:
                        logger.success(f"<green>No change in js file: {js_ver}</green>")
                        return True
                logger.warning("The version in 'px' does not match any detected JS files.")
                return False
            
            except FileNotFoundError:
                logger.error(f"The file 'px' was not found in the directory: {project_root}")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred while reading 'px': {e}")
                return False

        else:
            # Process formats when ADVANCED_ANTI_DETECTION is disabled
            for format in main_js_formats:
                logger.info(f"Trying format: {format}")
                full_url = f"https://app.notpx.app{format}"
                result = get_base_api(full_url)
                if result is None:
                    logger.warning("API check failed. Possible changes detected.")
                    return False

                if baseUrl in result:
                    logger.success("<green>No change in API!</green>")
                    return True
            logger.warning("Could not find 'baseURL' in any of the JS files.")
            return False
    else:
        logger.info("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])  # Print the first 1000 characters of the page
            return False
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
            return False
