"""
main.py
-------
Entry point for AquaClean. Run this file to start the game:

    python main.py

It creates a Game instance and starts the main loop, which opens
directly to the main menu.
"""

from game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
