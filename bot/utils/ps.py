from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import requests

def download_index_file_with_selenium(base_url, download_path="downloads"):
    """
    Uses Selenium to download a dynamically loaded JavaScript index file.

    :param base_url: The base URL to scrape and download from.
    :param download_path: The directory to save the downloaded file.
    """
    try:
        print(f"Opening browser to {base_url}...")

        # Setup Selenium WebDriver
        service = Service("path/to/chromedriver")  # Update with your ChromeDriver path
        driver = webdriver.Chrome(service=service)
        driver.get(base_url)

        # Wait for the page to load and find JS files
        driver.implicitly_wait(10)
        js_files = driver.find_elements(By.XPATH, "//script[contains(@src, 'index-')]")
        
        if not js_files:
            print("No matching index files found on the page.")
            return

        # Get the first match (update if you want to handle multiple files)
        js_url = js_files[0].get_attribute("src")
        print(f"Found file: {js_url}")

        # Download the file using requests
        os.makedirs(download_path, exist_ok=True)
        file_name = os.path.basename(js_url)
        file_response = requests.get(js_url)
        file_response.raise_for_status()

        # Save the file locally
        file_path = os.path.join(download_path, file_name)
        with open(file_path, "wb") as file:
            file.write(file_response.content)

        print(f"File successfully downloaded to: {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    base_url = "https://app.notpx.app"
    download_index_file_with_selenium(base_url)
