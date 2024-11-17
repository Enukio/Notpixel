import json
import os
import glob
import asyncio
import argparse
import sys
from urllib.parse import unquote

from aiofile import AIOFile
from pyrogram import Client
from better_proxy import Proxy

from bot.config import settings
from bot.core.agents import generate_random_user_agent
from bot.utils import logger
from bot.core.tapper import run_tapper, run_tapper1
from bot.core.query import run_query_tapper, run_query_tapper1
from bot.core.registrator import register_sessions


start_text = """
███████╗███╗░░██╗██╗░░░██╗██╗░░██╗██╗░█████╗░
██╔════╝████╗░██║██║░░░██║██║░██╔╝██║██╔══██╗
█████╗░░██╔██╗██║██║░░░██║█████═╝░██║██║░░██║
██╔══╝░░██║╚████║██║░░░██║██╔═██╗░██║██║░░██║
███████╗██║░╚███║╚██████╔╝██║░╚██╗██║╚█████╔╝
╚══════╝╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚═╝░╚════╝░  

Select an action:
    1. Start Drawing (Session)
    2. Create Session
    3. Start Drawing (Query)
    4. Update Index
"""

global tg_clients

def run_idx_script():
    """
    Menjalankan script idx.py yang berada dua tingkat di atas direktori ini.
    """
    idx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../idx.py")
    if os.path.exists(idx_path):
        os.system(f"python {idx_path}")
    else:
        logger.error("File idx.py tidak ditemukan di direktori dua tingkat di atas.")

def get_session_names() -> list[str]:
    session_names = sorted(glob.glob("sessions/*.session"))
    session_names = [
        os.path.splitext(os.path.basename(file))[0] for file in session_names
    ]
    return session_names

def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file="bot/config/proxies.txt", encoding="utf-8-sig") as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []
    return proxies

async def get_tg_clients() -> list[Client]:
    global tg_clients

    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]
    return tg_clients

async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")
    parser.add_argument("-m", "--multithread", type=str, help="Enable multi-threading")

    action = parser.parse_args().action
    ans = parser.parse_args().multithread
    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

    if not os.path.exists("user_agents.json"):
        with open("user_agents.json", 'w') as file:
            file.write("{}")
        logger.info("User agents file created successfully")

    if not action:
        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2", "3", "4"]:
                logger.warning("Action must be 1, 2, 3, or 4")
            else:
                action = int(action)
                break

    if action == 2:
        await register_sessions()
    elif action == 1:
        if ans is None:
            while True:
                ans = input("> Do you want to run the bot with multi-thread? (y/n) ")
                if ans not in ["y", "n"]:
                    logger.warning("Answer must be y or n")
                else:
                    break

        if ans == "y":
            tg_clients = await get_tg_clients()
            await run_tasks(tg_clients=tg_clients)
        else:
            tg_clients = await get_tg_clients()
            await run_tapper1(tg_clients=tg_clients)
    elif action == 3:
        if ans is None:
            while True:
                ans = input("> Do you want to run the bot with multi-thread? (y/n) ")
                if ans not in ["y", "n"]:
                    logger.warning("Answer must be y or n")
                else:
                    break
        if ans == "y":
            with open("data.txt", "r") as f:
                query_ids = [line.strip() for line in f.readlines()]
            await run_tasks_query(query_ids)
        else:
            with open("data.txt", "r") as f:
                query_ids = [line.strip() for line in f.readlines()]
            await run_query_tapper1(query_ids)
    elif action == 4:
        run_idx_script()

async def run_tasks_query(query_ids: list[str]):
    tasks = [
        asyncio.create_task(
            run_query_tapper(
                query=query, 
                proxy=await get_proxy(fetch_username(query)),
                ua=await get_user_agent(fetch_username(query))
            )
        )
        for query in query_ids
    ]
    await asyncio.gather(*tasks)

async def run_tasks(tg_clients: list[Client]):
    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=tg_client,
                proxy=await get_proxy(tg_client.name),
                ua=await get_user_agent(tg_client.name)
            )
        )
        for tg_client in tg_clients
    ]
    await asyncio.gather(*tasks)
