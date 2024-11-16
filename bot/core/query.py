
import asyncio
import random
import sys
from urllib.parse import quote, unquote

import aiohttp
import cloudscraper
import requests
from aiocfscrape import CloudflareScraper
from aiofile import AIOFile
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from bot.core.agents import generate_random_user_agent, fetch_version
from bot.config import settings
from datetime import datetime, timedelta
from tzlocal import get_localzone
import time as time_module

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from random import randint
import os
from PIL import Image
import io
import traceback
from bot.core.image_checker import get_cords_and_color, template_to_join, inform, reachable
import urllib3
import json

from ..utils.ps import check_base_url
from bot.utils import launcher as lc

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_GAME_ENDPOINT = "https://notpx.app/api/v1"
class Tapper:
    def __init__(self, query: str, multi_thread):
        self.query = query
        try:
            fetch_data = unquote(self.query).split("user=")[1].split("&chat_instance=")[0]
        except:
            try:
                fetch_data = unquote(self.query).split("user=")[1].split("&auth_date=")[0]
            except:
                logger.warning(f"Invaild query: {query}")
                sys.exit()
        try:
            json_data = json.loads(fetch_data)
        except:
            fetch_data = unquote(fetch_data)
        json_data = json.loads(fetch_data)
        self.session_name = json_data['username']
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.auth_token = ""
        self.last_claim = None
        self.last_checkin = None
        self.balace = 0
        self.maxtime = 0
        self.fromstart = 0
        self.balance = 0
        self.color_list = ["#FFD635", "#7EED56", "#00CCC0", "#51E9F4", "#94B3FF", "#000000", "#898D90", "#E46E6E",
                           "#E4ABFF", "#FF99AA", "#FFB470", "#FFFFFF", "#BE0039", "#FF9600", "#00CC78", "#009EAA",
                           "#3690EA", "#6A5CFF", "#B44AC0", "#FF3881", "#9C6926", "#6D001A", "#BF4300", "#00A368",
                           "#00756F", "#2450A4", "#493AC1", "#811E9F", "#A00357", "#6D482F"]
        self.multi_thread = multi_thread
        self.my_ref = "f6624523270"
        self.clb_ref = "f7385650582"
        self.socket = None
        self.default_template = {
            'x': 244,
            'y': 244,
            'image_size': 510,
            'image': None
        }
        self.template_id = None
        self.can_run = True
        self.cache = os.path.join(os.getcwd(), "cache")

        self.max_lvl = {
            "energyLimit": 7,
            "paintReward": 7,
            "reChargeSpeed": 11
        }
        self.is_max_lvl = {
            "energyLimit": False,
            "paintReward": False,
            "reChargeSpeed": False
        }
        self.user_upgrades = None
        self.template_to_join = 0
        self.completed_task = None

    def paintv2(self, session, x, y, color, chance_left):
        pxId = y * 1000 + x + 1
        payload = {
            "pixelId": pxId,
            "newColor": color
        }

        for attempt in range(3):  # Retry logic
            try:
                res = session.post(f"{API_GAME_ENDPOINT}/repaint/start", headers=headers, json=payload)
                res.raise_for_status()
                logger.success(
                    f"{self.session_name} | Painted {pxId} successfully new color: {color} | Balance: {res.json().get('balance')} | Repaint left: {chance_left}"
                )
                return True
            except requests.HTTPError as e:
                logger.warning(f"{self.session_name} | Attempt {attempt+1}: Failed to repaint: {res.status_code} | Response: {res.text}")
                if res.status_code == 500 and attempt < 2:  # Retry for server errors
                    asyncio.sleep(5)
            except Exception as e:
                logger.error(f"{self.session_name} | Unexpected error: {e}")
                break
        return False
