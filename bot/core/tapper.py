import asyncio
import json
import random
from itertools import cycle
from urllib.parse import unquote
import os
import base64
from datetime import datetime, timedelta
from tzlocal import get_localzone
import aiohttp
import requests
from aiofile import AIOFile
from aiohttp_proxy import ProxyConnector
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw.functions.messages import RequestAppWebView
from PIL import Image
import io
import traceback

from aiocfscrape import CloudflareScraper
from better_proxy import Proxy
from bot.core.agents import generate_random_user_agent, fetch_version
from bot.config import settings
from bot.core.image_checker import get_cords_and_color, template_to_join, inform, reachable
from bot.utils import logger
from bot.exceptions import InvalidSession
from bot.utils.ps import check_base_url
from .headers import headers

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_GAME_ENDPOINT = "https://notpx.app/api/v1"


class Tapper:
    """Main class for managing and automating the painting bot."""
    
    def __init__(self, tg_client: Client, multi_thread: bool):
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.balance = 0
        self.multi_thread = multi_thread
        self.can_run = True
        self.default_template = {
            'x': 244,
            'y': 244,
            'image_size': 510,
            'image': None
        }
        self.cache = os.path.join(os.getcwd(), "cache")
        self.color_list = [
            "#FFD635", "#7EED56", "#00CCC0", "#51E9F4", "#94B3FF", "#000000",
            "#898D90", "#E46E6E", "#E4ABFF", "#FF99AA", "#FFB470", "#FFFFFF",
            "#BE0039", "#FF9600", "#00CC78", "#009EAA", "#3690EA", "#6A5CFF",
            "#B44AC0", "#FF3881", "#9C6926", "#6D001A", "#BF4300", "#00A368",
            "#00756F", "#2450A4", "#493AC1", "#811E9F", "#A00357", "#6D482F"
        ]

    def generate_websocket_key(self):
        """Generates a unique websocket key."""
        random_bytes = os.urandom(16)
        return base64.b64encode(random_bytes).decode('utf-8')

    async def get_tg_web_data(self, proxy: str | None) -> str:
        """Fetch Telegram WebView data."""
        try:
            if settings.REF_LINK == "":
                ref_param = "default_ref_id"
            else:
                ref_param = settings.REF_LINK.split("=")[1]
            
            proxy_dict = Proxy.from_str(proxy).to_dict() if proxy else None
            self.tg_client.proxy = proxy_dict

            # Ensure client connection
            if not self.tg_client.is_connected:
                await self.tg_client.connect()

            # Resolve bot peer and get WebView data
            peer = await self.tg_client.resolve_peer('notpixel')
            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotAppShortName(bot_id=peer, short_name="app"),
                platform='android',
                write_allowed=True,
                start_param=ref_param
            ))

            tg_web_data = unquote(unquote(web_view.url.split('tgWebAppData=')[1].split('&')[0]))
            return tg_web_data

        except Exception as error:
            logger.error(f"{self.session_name} | Error fetching WebView data: {error}")
            return ""

    # Add more methods, keeping the improvements consistent.
