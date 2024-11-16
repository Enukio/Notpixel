import re
from typing import Optional

import ua_generator
from ua_generator.options import Options
from ua_generator.data.version import VersionRange

def generate_random_user_agent(device_type: str = 'android', browser_type: str = 'chrome') -> Optional[str]:
    """
    Generates a random user agent string based on device and browser type.

    :param device_type: Type of device ('android', 'ios', etc.)
    :param browser_type: Type of browser ('chrome', 'firefox', etc.)
    :return: A random user agent string or None if generation fails.
    """
    try:
        # Define version range for Chrome (default example)
        chrome_version_range = VersionRange(min_version=117, max_version=130)
        options = Options(version_ranges={'chrome': chrome_version_range})

        # Generate user agent
        ua = ua_generator.generate(platform=device_type, browser=browser_type, options=options)
        return ua.text
    except Exception as e:
        print(f"Error generating user agent: {e}")
        return None

def fetch_version(ua: str) -> Optional[str]:
    """
    Extracts the major version number from a user agent string.

    :param ua: The user agent string.
    :return: The major version number as a string, or None if not found.
    """
    match = re.search(r"Chrome/(\d+)", ua)
    if match:
        return match.group(1)
    return None
