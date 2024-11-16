
from pyrogram import Client, errors

from bot.config import settings
from bot.utils import logger


async def register_sessions() -> None:
    API_ID = settings.API_ID
    API_HASH = settings.API_HASH

    if not API_ID or not API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    while True:
        session_name = input("\nEnter the session name (or type 'exit' to quit): ").strip()

        if session_name.lower() == 'exit':
            print("Exiting session registration.")
            return

        if not session_name:
            print("Session name cannot be empty. Please try again.")
            continue

        session = Client(
            name=session_name,
            api_id=API_ID,
            api_hash=API_HASH,
            workdir="sessions/"
        )

        try:
            async with session:
                user_data = await session.get_me()
                logger.success(f'Session added successfully @{user_data.username} | '
                               f'{user_data.first_name} {user_data.last_name}')
                break
        except errors.AccessTokenInvalid:
            logger.error("Invalid API ID or HASH. Please check your .env configuration.")
            break
        except errors.RPCError as rpc_error:
            logger.error(f"An RPC error occurred: {rpc_error}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
