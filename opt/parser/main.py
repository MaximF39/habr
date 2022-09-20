import asyncio
from habr import Habr


async def main():
    habr = Habr()

    await asyncio.ensure_future(habr.async_start())


if __name__ == "__main__":
    print("Start")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
