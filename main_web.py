# /// script
# dependencies = [
#   "pygame-ce",
# ]
# ///

import asyncio
import pygame
from game import Game


async def main():
    print("AquaClean web startup")
    print("Pygame module:", getattr(pygame, "__file__", "unknown"))
    print("Pygame init available:", hasattr(pygame, "init"))

    game = Game()
    await game.run_async()


asyncio.run(main())
