import asyncio

from db import DB
from habr import Habr


async def async_main():
    habr = Habr(_db=DB)
    await habr.async_start()
    await asyncio.sleep(1e4)


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
