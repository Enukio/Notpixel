import os
import re
import requests
import logging
import time
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Custom logging formatter with colors
class ColorFormatter(logging.Formatter):
    def format(self, record):
        # Define color styles for log levels
        level_color = {
            'INFO': Fore.CYAN,          # INFO: Cyan
            'WARNING': Fore.MAGENTA,    # WARNING: Magenta
            'ERROR': Fore.YELLOW,       # ERROR: Yellow
            'CRITICAL': Fore.RED + Style.BRIGHT  # CRITICAL: Bright Red
        }.get(record.levelname, Fore.WHITE)  # Default to white

        # Add color to the log level and "[Not pixel]"
        record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        record.notpixel = f"{Fore.RED}[Not pixel]{Style.RESET_ALL}"  # [Not pixel] in red
        record.msg = f"{Style.BRIGHT}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

# Configure logger
formatter = ColorFormatter('%(notpixel)s - %(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger('[Not pixel]')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def save_filename_to_cgi(filenames, output_file):
    """
    Save the list of JavaScript filenames to a px file.

    :param filenames: List of JavaScript filenames to save.
    :param output_file: Path to the px file where filenames will be saved.
    """
    try:
        with open(output_file, 'w') as f:
            for filename in filenames:
                f.write(filename + '\n')  # Write each filename on a new line
        logger.info(f"Saved {len(filenames)} filenames to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save filenames to {output_file}: {e}")

def get_main_js_format(base_url, output_file="./px"):
    """
    Scrape the base page to find JavaScript files matching the pattern and save filenames.

    :param base_url: The URL of the webpage to scrape.
    :param output_file: The file to save the list of JavaScript filenames (as file).
    :return: A list of filenames or None if no matches are found.
    """
    try:
        logger.info(f"Fetching base URL: {base_url}")
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        content = response.text

        # Use regex to find JavaScript file paths
        matches = re.findall(r'src="(/.*?/index.*?\.js)"', content)
        if matches:
            logger.info(f"Found {len(matches)} JavaScript files matching the pattern.")
            matches = sorted(set(matches), key=len, reverse=True)  # Remove duplicates and sort
            filenames = []

            for match in matches:
                # Extract the filename with .js extension
                filename = os.path.basename(match)
                filenames.append(filename)

            # Save the filenames to the px file
            save_filename_to_cgi(filenames, output_file)
            return filenames
        else:
            logger.warning("No matching JavaScript files found.")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching the base URL: {e}")
        return None

# Main block for execution
if __name__ == "__main__":
    # Simulate a progress bar for script initialization
    print(Fore.GREEN + "Starting the script..." + Style.RESET_ALL)
    for _ in tqdm(range(100), desc="Loading", ascii=True, ncols=75):
        time.sleep(0.03)  # Simulate some delay

    # Actual script functionality
    BASE_URL = "https://app.notpx.app"  # Replace with your target URL
    OUTPUT_FILE = "./px"  # Output file for filenames
    
    try:
        logger = logging.getLogger('[Not pixel]')
        filenames = get_main_js_format(BASE_URL, OUTPUT_FILE)
        if filenames:
            logger.info(f"Found and saved {len(filenames)} filenames.")
        else:
            logger.info("No filenames were saved.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
