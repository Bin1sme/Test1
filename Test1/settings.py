"""
settings.py
------------
Central configuration module for the Snake game.

All tunable constants live here so gameplay tuning never requires
touching the game logic files. Keeping these values in one place is a
core part of the "no global variables scattered around" OOP design.
"""

# --- Window / Grid dimensions -------------------------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Each grid cell is a 20x20 pixel square.
CELL_SIZE = 20

# Number of cells across and down the play field.
GRID_COLUMNS = WINDOW_WIDTH // CELL_SIZE   # 40 columns
GRID_ROWS = WINDOW_HEIGHT // CELL_SIZE     # 30 rows

# --- Colors (RGB tuples) ------------------------------------------------
COLOR_BACKGROUND = (20, 20, 30)      # dark slate background
COLOR_GRID_LINE = (40, 40, 55)       # subtle grid lines
COLOR_SNAKE_HEAD = (80, 220, 120)    # bright green head
COLOR_SNAKE_BODY = (40, 160, 90)     # darker green body
COLOR_FOOD = (230, 80, 80)           # red food
COLOR_TEXT = (240, 240, 240)         # near-white text
COLOR_TEXT_DIM = (160, 160, 170)     # muted secondary text

# --- Gameplay tuning ----------------------------------------------------
BASE_SPEED_FPS = 10          # starting speed (ticks per second)
FOODS_PER_LEVEL = 5          # food eaten to trigger a speed increase
SPEED_INCREMENT = 2          # FPS added each level
MAX_SPEED_FPS = 30           # hard cap so the game stays playable

# --- Direction vectors --------------------------------------------------
# Directions are stored as (dx, dy) grid offsets. The snake moves one
# cell per tick in the direction it is currently facing.
DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)

# --- State identifiers --------------------------------------------------
# String keys used by the state machine in game_manager.py.
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
