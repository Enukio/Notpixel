import os
import sys
import platform
import re
import requests
import logging
from colorama import init, Fore, Style
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Initialize colorama
init(autoreset=True)

# Custom logging formatter with colors
class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, name="Not Pixel"):
        super().__init__(fmt, datefmt)
        self.name = name  # Set custom name

    def format(self, record):
        # Define color styles for log levels
        level_color = {
            'INFO': Fore.CYAN,                   # INFO: Cyan
            'WARNING': Fore.MAGENTA,             # WARNING: Magenta
            'ERROR': Fore.YELLOW,                # ERROR: Yellow
            'CRITICAL': Fore.RED + Style.BRIGHT  # CRITICAL: Bright Red
        }.get(record.levelname, Fore.WHITE)      # Default to white

        # Add color to the log level
        record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        record.botname = f"{Fore.RED}[{self.name}]{Style.RESET_ALL}"
        record.msg = f"{Style.BRIGHT}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

# Configure logger
name = "Not Pixel"
formatter = ColorFormatter('%(botname)s | %(asctime)s | %(levelname)s | %(message)s', '%Y-%m-%d %H:%M:%S', name)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(name)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Function to save filenames to a file
def storage(filenames, output_file):

    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for filename in filenames:
                f.write(filename + '\n')
        logger.info(f"Saved {len(filenames)} filenames to {Fore.GREEN}{output_file}{Style.RESET_ALL}.")
    except Exception as e:
        logger.error(f"Failed to save filenames to {Fore.RED}{output_file}{Style.RESET_ALL}: {Fore.YELLOW}{e}{Style.RESET_ALL}")

# Function to fetch JavaScript filenames from a base URL
def get_main_js_format(base_url, output_file="./px"):

    try:
        logger.info(f"Fetching base URL: {Fore.GREEN}{base_url}{Style.RESET_ALL}")
        
        # Setup session with retry logic
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        response = session.get(base_url, timeout=10)
        response.raise_for_status()

        if not response.headers.get('Content-Type', '').lower().startswith('text/html'):
            logger.error("Unexpected content type. Expected HTML.")
            return None

        content = response.text
        # Use regex to find JavaScript file paths
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        if matches:
            logger.info(f"Found {len(matches)} JavaScript files.")
            matches = sorted(set(matches), key=len, reverse=True)
            duplicates_removed = len(matches) - len(set(matches))
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate filenames.")

            filenames = [os.path.basename(match) for match in matches]

            # Save the filenames to the output file
            storage(filenames, output_file)
            return filenames
        else:
            logger.warning("No matching JavaScript files found.")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching the base URL: {e}")
        return None

# Main block for execution
BASE_URL = "https://app.notpx.app"  # Replace with the actual URL to test
OUTPUT_FILE = "./px"  # Save all filenames to this px file

filenames = get_main_js_format(BASE_URL, OUTPUT_FILE)

if not filenames:
    logger.info(f"{Fore.YELLOW}No filenames were saved.{Style.RESET_ALL}")
else:
    logger.info(f"Filenames processed: {Fore.GREEN}{filenames}{Style.RESET_ALL}")

# Retrieve the Python version
python_version = platform.python_version()
logger.info(f"Using Python interpreter: Python {python_version}")

# Return to main.py using the same interpreter
logger.info("Returning to Menu...")
os.system(f'"{sys.executable}" main.py')
