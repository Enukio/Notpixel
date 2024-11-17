import asyncio
import json
import random
from itertools import cycle
from urllib.parse import unquote

import aiohttp
import requests
from aiocfscrape import CloudflareScraper
from aiofile import AIOFile
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw.functions.messages import RequestAppWebView
from bot.core.agents import generate_random_user_agent, fetch_version
from bot.config import settings
from datetime import datetime, timedelta
from tzlocal import get_localzone
import time as time_module

from bot.core.image_checker import get_cords_and_color, template_to_join, inform, reachable
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from random import randint
import urllib3
import base64
import os
from PIL import Image
import io
import traceback
from bot.utils.ps import check_base_url
import sys
import cloudscraper
from bot.utils import launcher as lc


def generate_websocket_key():
    random_bytes = os.urandom(16)
    websocket_key = base64.b64encode(random_bytes).decode('utf-8')
    return websocket_key


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_GAME_ENDPOINT = "https://notpx.app/api/v1"


class Tapper:
    def __init__(self, tg_client: Client, multi_thread: bool):
        self.tg_client = tg_client
        self.session_name = tg_client.name
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
        self.query_anti = None

    async def get_tg_web_data(self, proxy: str | None) -> str:
        try:
            if settings.REF_LINK == "":
                ref_param = "f6624523270"
            else:
                ref_param = settings.REF_LINK.split("=")[1]
        except Exception as e:
            logger.error(f"{self.session_name} | Ref link invalid, please check again! Error: {e}")
            sys.exit()

        actual = random.choices([self.my_ref, self.clb_ref, ref_param], weights=[20, 10, 70])

        try:
            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=await self.tg_client.resolve_peer('notpixel'),
                app=InputBotAppShortName(bot_id=await self.tg_client.resolve_peer('notpixel'), short_name="app"),
                platform='android',
                write_allowed=True,
                start_param=actual[0]
            ))

            auth_url = web_view.url
            tg_web_data = unquote(auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            tg_web_data_decoded = unquote(unquote(tg_web_data))

            try:
                tg_web_data_json = tg_web_data_decoded.split('user=')[1].split('&chat_instance')[0]
                user_data = json.loads(tg_web_data_json)
                self.user_id = user_data['id']
            except (IndexError, json.JSONDecodeError) as e:
                logger.error(f"Error processing tg_web_data_json: {tg_web_data_json} | Error: {e}")
                raise

            return tg_web_data
        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {e}")
            await asyncio.sleep(3)
            raise
