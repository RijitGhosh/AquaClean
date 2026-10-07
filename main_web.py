"""
main_web.py
-----------
Entry point for the BROWSER / PHONE version of AquaClean (built with pygbag).
The desktop game still starts from main.py - this file is only used for the web build.

On a phone: hold your finger on the screen and the boat steers toward it.
"""

import asyncio
from game import Game


async def main():
    game = Game()
    await game.run_async()


asyncio.run(main())
