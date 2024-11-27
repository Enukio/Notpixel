import os
import sys
import re
from loguru import logger
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Constants
BASE_URL = "https://app.notpx.app"  # Replace with the actual URL
OUTPUT_FILE = "./px"  # File to save filenames

# Configure logger
logger.remove()
logger.add(
    sink=sys.stdout,
    format="<r>[Not Pixel]</r> | <white>{time:YYYY-MM-DD HH:mm:ss}</white> | "
           "<level>{level}</level> | <cyan>{line}</cyan> | {message}",
    colorize=True
)
logger = logger.opt(colors=True)

# Function to save filenames to a file
def storage(filenames, output_file):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for filename in filenames:
                f.write(filename + '\n')
        logger.info(f"Saved {len(filenames)} filenames to <green>{output_file}</green>")
    except Exception as e:
        logger.error(f"Failed to save filenames to {output_file}: {e}")

# Function to fetch JavaScript filenames from a base URL
def get_main_js_format(base_url, output_file="./px"):
    if not base_url.startswith(("http://", "https://")):
        logger.error(f"Invalid URL format: {base_url}")
        return None

    try:
        logger.info(f"Fetching base URL: <green>{base_url}</green>")
        
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = session.get(base_url, timeout=10)
        response.raise_for_status()

        if not response.headers.get('Content-Type', '').lower().startswith('text/html'):
            logger.error("Unexpected content type. Expected HTML.")
            return None

        content = response.text
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        if matches:
            logger.info(f"Found {len(matches)} JavaScript files.")
            matches = sorted(set(matches), key=len, reverse=True)

            filenames = [os.path.basename(match) for match in matches]
            storage(filenames, output_file)
            return filenames
        else:
            logger.warning("No matching JavaScript files found.")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching the base URL: {e}")
        return None

# Main execution
if __name__ == "__main__":
    filenames = get_main_js_format(BASE_URL, OUTPUT_FILE)

    if not filenames:
        logger.info("No filenames were saved.")
    else:
        logger.info(f"Filenames processed: <green>{filenames}</green>")

    # Return to main.py
    print("\n🔄 Returning to Menu in 2 seconds...\n")
    if os.path.exists("main.py"):
        os.system(f'"{sys.executable}" main.py')
    else:
        logger.error("main.py not found. Exiting.")
