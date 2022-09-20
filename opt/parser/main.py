import asyncio
from habr import Habr


async def async_main():
    habr = Habr()
    await asyncio.ensure_future(habr.async_start())


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())


if __name__ == "__main__":
    main()
