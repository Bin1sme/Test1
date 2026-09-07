"""
main.py
-------
Entry point for the Snake game.

This module is intentionally thin: it initialises Pygame, creates the
window, and hands control to the GameManager. All game logic lives in
the other modules (settings, snake, food, game_manager).
"""

import pygame

import settings
from game_manager import GameManager


def main():
    """Initialise Pygame and start the game loop."""
    pygame.init()

    # Create the game window.
    screen = pygame.display.set_mode(
        (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
    )
    pygame.display.set_caption("Snake")

    # Hand control to the GameManager, which owns the state machine and
    # the main loop. main() blocks here until the game exits.
    manager = GameManager(screen)
    manager.run()


if __name__ == "__main__":
    main()
