import asyncio
from contextlib import suppress

from bot.utils.launcher import main


async def main():
    await main()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
