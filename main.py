import asyncio
from contextlib import suppress

async def process():
    return "Process executed successfully!"

async def main():
    result = await process()
    print(result)

if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
