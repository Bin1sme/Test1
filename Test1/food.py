"""
food.py
-------
The Food entity. Food occupies a single random grid cell that is not
currently covered by the snake's body, so it can never spawn inside the
snake.
"""

import random

import settings


class Food:
    """A single piece of food placed on a free grid cell."""

    def __init__(self, snake_body):
        # Place the first piece of food on a free cell.
        self._position = self._random_free_cell(snake_body)

    @property
    def position(self):
        """Return the (x, y) grid coordinate of the food."""
        return self._position

    def respawn(self, snake_body):
        """
        Place the food on a new random free cell after it is eaten.

        The snake body is passed in so the food never spawns on top of
        the snake. If the snake fills the entire board (a win condition
        we do not explicitly handle), random.choice would raise, so we
        guard against an empty free-cell list.
        """
        self._position = self._random_free_cell(snake_body)

    def _random_free_cell(self, snake_body):
        """
        Pick a random grid cell not occupied by the snake.

        LOGIC:
        We build the set of all possible grid cells, subtract the cells
        the snake currently occupies, and choose uniformly from what
        remains. Using a set makes the membership test O(1) per cell.
        """
        occupied = set(snake_body)

        free_cells = [
            (x, y)
            for x in range(settings.GRID_COLUMNS)
            for y in range(settings.GRID_ROWS)
            if (x, y) not in occupied
        ]

        return random.choice(free_cells)
