"""
game_manager.py
---------------
The GameManager owns the game state machine and the core game loop
logic. It coordinates the Snake, the Food, scoring, speed progression,
and collision detection.

STATE MACHINE OVERVIEW
----------------------
The game has three states: MENU, PLAYING, and GAME_OVER.

    MENU  --(SPACE)-->  PLAYING
    PLAYING --(death)--> GAME_OVER
    GAME_OVER --(SPACE)--> PLAYING   (restart)
    GAME_OVER --(ESC)-->  quit

Each state has its own handle_event() and update()/draw() behaviour.
Transitions are triggered by user input (SPACE / ESC) or by a collision
that ends the round.
"""

import pygame

import settings
from food import Food
from snake import Snake


class GameManager:
    """Coordinates the state machine, entities, and rendering."""

    def __init__(self, screen):
        self._screen = screen
        self._clock = pygame.time.Clock()

        # --- State machine fields ---
        self._state = settings.STATE_MENU

        # --- Round-scoped entities (rebuilt on each new game) ---
        self._snake = None
        self._food = None
        self._score = 0
        self._foods_eaten = 0      # counter for the current level
        self._current_speed = settings.BASE_SPEED_FPS

        # Fonts are created once and reused.
        self._font_title = pygame.font.SysFont("consolas", 64, bold=True)
        self._font_prompt = pygame.font.SysFont("consolas", 28)
        self._font_hud = pygame.font.SysFont("consolas", 24)

    # ------------------------------------------------------------------
    # Public entry points called from main.py
    # ------------------------------------------------------------------

    def run(self):
        """
        Main game loop. Runs forever until the window is closed or the
        player quits from the Game Over screen.
        """
        running = True
        while running:
            # Fixed-timestep tick: the snake advances at most once per
            # clock tick, which is what makes the game feel "turn based"
            # and controllable.
            self._clock.tick(self._current_speed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._handle_event(event)

            self._update()
            self._draw()

            pygame.display.flip()

        pygame.quit()

    # ------------------------------------------------------------------
    # Event handling (state machine input routing)
    # ------------------------------------------------------------------

    def _handle_event(self, event):
        """
        Route an input event to the handler for the current state.

        STATE TRANSITION LOGIC:
        Each state only reacts to the keys that are meaningful to it.
        SPACE is overloaded: it starts a game from the menu and restarts
        from the game-over screen. ESC quits from the game-over screen.
        """
        if self._state == settings.STATE_MENU:
            self._handle_menu_event(event)
        elif self._state == settings.STATE_PLAYING:
            self._handle_playing_event(event)
        elif self._state == settings.STATE_GAME_OVER:
            self._handle_game_over_event(event)

    def _handle_menu_event(self, event):
        """In the menu, SPACE starts a new game."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._start_new_game()

    def _handle_playing_event(self, event):
        """In play, WASD steers the snake (anti-reversal handled inside)."""
        if event.type != pygame.KEYDOWN:
            return

        # Map WASD keys to direction vectors.
        key_to_direction = {
            pygame.K_w: settings.DIRECTION_UP,
            pygame.K_s: settings.DIRECTION_DOWN,
            pygame.K_a: settings.DIRECTION_LEFT,
            pygame.K_d: settings.DIRECTION_RIGHT,
        }

        if event.key in key_to_direction:
            # The Snake.change_direction() method applies the
            # anti-reversal guard, so a 180-degree turn is ignored.
            self._snake.change_direction(key_to_direction[event.key])

    def _handle_game_over_event(self, event):
        """In game over, SPACE restarts and ESC quits."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self._start_new_game()
        elif event.key == pygame.K_ESCAPE:
            # Signal the main loop to stop by quitting pygame.
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ------------------------------------------------------------------
    # Game setup / progression
    # ------------------------------------------------------------------

    def _start_new_game(self):
        """
        Reset all round-scoped state and transition to PLAYING.

        STATE TRANSITION:
        Called from MENU (SPACE) and GAME_OVER (SPACE). It rebuilds the
        snake and food, zeroes the score, and restores base speed.
        """
        # Start the snake near the centre of the board.
        start_x = settings.GRID_COLUMNS // 2
        start_y = settings.GRID_ROWS // 2

        self._snake = Snake(start_x, start_y, start_length=3)
        self._food = Food(self._snake.body)

        self._score = 0
        self._foods_eaten = 0
        self._current_speed = settings.BASE_SPEED_FPS

        self._state = settings.STATE_PLAYING

    def _increase_speed(self):
        """
        Raise the game speed after enough food is eaten.

        PROGRESSION LOGIC:
        Every FOODS_PER_LEVEL pieces of food, add SPEED_INCREMENT FPS,
        capped at MAX_SPEED_FPS so the game never becomes unplayable.
        """
        if self._foods_eaten % settings.FOODS_PER_LEVEL == 0:
            self._current_speed = min(
                self._current_speed + settings.SPEED_INCREMENT,
                settings.MAX_SPEED_FPS,
            )

    # ------------------------------------------------------------------
    # Update logic (only meaningful in the PLAYING state)
    # ------------------------------------------------------------------

    def _update(self):
        """Advance the simulation one tick for the current state."""
        if self._state == settings.STATE_PLAYING:
            self._update_playing()

    def _update_playing(self):
        """
        Advance the snake and evaluate collisions.

        COLLISION DETECTION MATH:
        1. Wall collision: the new head is computed inside Snake.move().
           After moving, if the head's x or y falls outside the grid
           bounds [0, GRID_COLUMNS) x [0, GRID_ROWS), the snake has hit
           a screen boundary -> game over.
        2. Self collision: Snake.collides_with_self() checks whether the
           head now overlaps any other body segment.
        3. Food collision: if the head occupies the food cell, the snake
           grows and the food respawns on a free cell.
        """
        self._snake.move()

        # --- Wall collision check ---
        head_x, head_y = self._snake.head
        hit_wall = (
            head_x < 0
            or head_x >= settings.GRID_COLUMNS
            or head_y < 0
            or head_y >= settings.GRID_ROWS
        )

        # --- Self collision check ---
        hit_self = self._snake.collides_with_self()

        if hit_wall or hit_self:
            # STATE TRANSITION: PLAYING -> GAME_OVER
            self._state = settings.STATE_GAME_OVER
            return

        # --- Food collision check ---
        if self._snake.collides_with_point(self._food.position):
            self._snake.grow()
            self._score += 1
            self._foods_eaten += 1
            self._increase_speed()
            self._food.respawn(self._snake.body)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _draw(self):
        """Render the current state to the screen."""
        if self._state == settings.STATE_MENU:
            self._draw_menu()
        elif self._state == settings.STATE_PLAYING:
            self._draw_playing()
        elif self._state == settings.STATE_GAME_OVER:
            self._draw_game_over()

    def _draw_menu(self):
        """Draw the main menu title and start prompt."""
        self._screen.fill(settings.COLOR_BACKGROUND)

        title = self._font_title.render("SNAKE", True, settings.COLOR_SNAKE_HEAD)
        prompt = self._font_prompt.render(
            "Press SPACE to Start", True, settings.COLOR_TEXT
        )

        self._center_text(title, offset_y=-60)
        self._center_text(prompt, offset_y=40)

    def _draw_playing(self):
        """Draw the board, snake, food, and HUD score."""
        self._screen.fill(settings.COLOR_BACKGROUND)
        self._draw_grid()

        # Draw food.
        fx, fy = self._food.position
        self._draw_cell(fx, fy, settings.COLOR_FOOD)

        # Draw the snake body (tail first so the head renders on top).
        for index, (x, y) in enumerate(self._snake.body):
            color = (
                settings.COLOR_SNAKE_HEAD if index == 0 else settings.COLOR_SNAKE_BODY
            )
            self._draw_cell(x, y, color)

        # HUD: current score.
        score_text = self._font_hud.render(
            f"Score: {self._score}", True, settings.COLOR_TEXT
        )
        self._screen.blit(score_text, (10, 10))

    def _draw_game_over(self):
        """Draw the final score and restart/quit prompt."""
        self._screen.fill(settings.COLOR_BACKGROUND)

        title = self._font_title.render("GAME OVER", True, settings.COLOR_FOOD)
        score = self._font_prompt.render(
            f"Final Score: {self._score}", True, settings.COLOR_TEXT
        )
        prompt = self._font_prompt.render(
            "Press SPACE to Restart or ESC to Quit",
            True,
            settings.COLOR_TEXT_DIM,
        )

        self._center_text(title, offset_y=-80)
        self._center_text(score, offset_y=0)
        self._center_text(prompt, offset_y=60)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_grid(self):
        """Draw faint grid lines so the 20px cells are visible."""
        for x in range(0, settings.WINDOW_WIDTH, settings.CELL_SIZE):
            pygame.draw.line(
                self._screen,
                settings.COLOR_GRID_LINE,
                (x, 0),
                (x, settings.WINDOW_HEIGHT),
            )
        for y in range(0, settings.WINDOW_HEIGHT, settings.CELL_SIZE):
            pygame.draw.line(
                self._screen,
                settings.COLOR_GRID_LINE,
                (0, y),
                (settings.WINDOW_WIDTH, y),
            )

    def _draw_cell(self, grid_x, grid_y, color):
        """
        Draw a filled square for one grid cell.

        PIXEL CONVERSION MATH:
        A grid cell (gx, gy) maps to a pixel rectangle by multiplying by
        CELL_SIZE. A 1px inset creates a small gap between cells so the
        snake body reads as distinct segments.
        """
        inset = 1
        rect = pygame.Rect(
            grid_x * settings.CELL_SIZE + inset,
            grid_y * settings.CELL_SIZE + inset,
            settings.CELL_SIZE - inset * 2,
            settings.CELL_SIZE - inset * 2,
        )
        pygame.draw.rect(self._screen, color, rect)

    def _center_text(self, surface, offset_y=0):
        """
        Blit a text surface horizontally centred, with a vertical offset
        from the middle of the window.
        """
        text_rect = surface.get_rect()
        text_rect.centerx = settings.WINDOW_WIDTH // 2
        text_rect.centery = settings.WINDOW_HEIGHT // 2 + offset_y
        self._screen.blit(surface, text_rect)
