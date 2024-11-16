import json
import requests
import time
from bot.utils import logger

# Configurable endpoint
ENDPOINT = "https://62.60.156.241"

def retry_on_failure(func):
    """
    Decorator to retry a function on failure up to a certain number of times.
    """
    def wrapper(*args, times_to_fall=20, **kwargs):
        attempt = 0
        while attempt < times_to_fall:
            try:
                return func(*args, **kwargs)
            except requests.RequestException as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{times_to_fall} failed: {e}")
                time.sleep(30)
        logger.error(f"All {times_to_fall} attempts failed for {func.__name__}.")
        raise RuntimeError(f"Failed to complete {func.__name__} after {times_to_fall} attempts.")
    return wrapper

@retry_on_failure
def reachable():
    response = requests.get(f"{ENDPOINT}/is_reacheble/", verify=False)
    response.raise_for_status()
    data = response.json()
    logger.success(f"Connected to server. Your UUID: {data.get('uuid')}")
    return data

@retry_on_failure
def inform(user_id, balance=0):
    response = requests.put(
        f"{ENDPOINT}/info/", 
        json={"user_id": user_id, "balance": balance}, 
        verify=False
    )
    response.raise_for_status()
    return response.json()

@retry_on_failure
def get_cords_and_color(user_id, template):
    response = requests.get(
        f"{ENDPOINT}/get_pixel/?user_id={user_id}&template={template}", 
        verify=False
    )
    response.raise_for_status()
    return response.json()

@retry_on_failure
def template_to_join(cur_template=0):
    response = requests.get(
        f"{ENDPOINT}/get_uncolored/?template={cur_template}", 
        verify=False
    )
    response.raise_for_status()
    resp = response.json()
    return resp.get('template')
