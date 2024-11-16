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

START_TEXT = """
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
"""

async def initialize_file(file_path: str, default_content: str):
    """Initialize a file with default content if it doesn't exist."""
    if not os.path.exists(file_path):
        async with AIOFile(file_path, "w") as file:
            await file.write(default_content)
        logger.info(f"{file_path} created successfully")


def get_session_names() -> list[str]:
    """Fetch all available session names."""
    return [
        os.path.splitext(os.path.basename(file))[0]
        for file in sorted(glob.glob("sessions/*.session"))
    ]


def get_proxies() -> list[Proxy]:
    """Retrieve proxies from a file if configured."""
    if settings.USE_PROXY_FROM_FILE:
        with open("bot/config/proxies.txt", encoding="utf-8-sig") as file:
            return [Proxy.from_str(row.strip()).as_url for row in file]
    return []


async def get_tg_clients() -> list[Client]:
    """Initialize Telegram clients for each session."""
    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("No session files found.")
    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH are missing in the configuration.")

    return [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins={"root": "bot/plugins"},
        )
        for session_name in session_names
    ]


def fetch_username(query: str) -> str:
    """Extract username from a query."""
    try:
        fetch_data = unquote(query).split("user=")[1].split("&")[0]
        return json.loads(fetch_data)["username"]
    except Exception as e:
        logger.warning(f"Invalid query: {query} | Error: {e}")
        sys.exit()


async def get_user_agent(session_name: str) -> str:
    """Retrieve or generate a user agent for a session."""
    async with AIOFile("user_agents.json", "r") as file:
        user_agents = json.loads(await file.read())

    if session_name not in user_agents:
        logger.info(f"Generating user agent for {session_name}...")
        user_agents[session_name] = generate_random_user_agent(
            device_type="android", browser_type="chrome"
        )
        async with AIOFile("user_agents.json", "w") as file:
            await file.write(json.dumps(user_agents, indent=4))
    return user_agents[session_name]


def get_unused_proxy(used_proxies: list[Proxy]) -> Proxy:
    """Find an unused proxy."""
    proxies = get_proxies()
    return next((proxy for proxy in proxies if proxy not in used_proxies), None)


async def get_proxy(session_name: str) -> Proxy:
    """Retrieve or assign a proxy to a session."""
    if settings.USE_PROXY_FROM_FILE:
        async with AIOFile("proxy.json", "r") as file:
            proxies = json.loads(await file.read())

        if session_name not in proxies:
            logger.info(f"Assigning new proxy for {session_name}...")
            proxies[session_name] = get_unused_proxy(list(proxies.values()))
            async with AIOFile("proxy.json", "w") as file:
                await file.write(json.dumps(proxies, indent=4))
        return proxies[session_name]
    return None


async def run_tasks_query(query_ids: list[str]):
    """Run tasks for processing queries."""
    tasks = [
        asyncio.create_task(
            run_query_tapper(
                query=query,
                proxy=await get_proxy(fetch_username(query)),
                ua=await get_user_agent(fetch_username(query)),
            )
        )
        for query in query_ids
    ]
    await asyncio.gather(*tasks)


async def run_tasks(tg_clients: list[Client]):
    """Run tasks for Telegram clients."""
    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=client,
                proxy=await get_proxy(client.name),
                ua=await get_user_agent(client.name),
            )
        )
        for client in tg_clients
    ]
    await asyncio.gather(*tasks)


async def process():
    print("Process function executed.")
    """Main entry point for the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")
    parser.add_argument("-m", "--multithread", type=str, help="Enable multi-threading")
    args = parser.parse_args()

    await initialize_file("user_agents.json", "{}")
    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

    action = args.action or int(input(START_TEXT + "> "))

    if action == 2:
        await register_sessions()
    elif action in [1, 3]:
        ans = args.multithread or input("Enable multi-threading? (y/n) > ").lower()
        tg_clients = await get_tg_clients()
        if action == 1:
            await (run_tasks(tg_clients) if ans == "y" else run_tapper1(tg_clients))
        elif action == 3:
            with open("data.txt") as file:
                query_ids = [line.strip() for line in file.readlines()]
            await (run_tasks_query(query_ids) if ans == "y" else run_query_tapper1(query_ids))


if __name__ == "__main__":
    asyncio.run(main())

print("Launcher module is loaded.")
