"""
snake.py
--------
The Snake entity: its body segments, movement, growth, and the
anti-reversal input guard.

The snake is modelled as a list of (x, y) grid coordinates where index 0
is the head. Movement is implemented by inserting a new head cell and
dropping the tail cell (unless the snake just ate food and must grow).
"""

import settings


class Snake:
    """Represents the player-controlled snake on the grid."""

    def __init__(self, start_x, start_y, start_length=3):
        # The snake starts facing right, laid out horizontally so the
        # head is the right-most cell and the tail trails to the left.
        self._direction = settings.DIRECTION_RIGHT

        # Body stored head-first: self._body[0] is the head.
        self._body = [
            (start_x - i, start_y) for i in range(start_length)
        ]

        # Pending growth counter. When > 0 the tail is NOT removed on
        # the next move, making the snake one cell longer.
        self._growth_pending = 0

    # --- Public API -----------------------------------------------------

    @property
    def head(self):
        """Return the (x, y) grid coordinate of the snake's head."""
        return self._body[0]

    @property
    def body(self):
        """Return the full list of body segments (head first)."""
        return self._body

    def change_direction(self, new_direction):
        """
        Attempt to change the snake's heading.

        ANTI-REVERSAL LOGIC:
        A snake cannot legally turn 180 degrees into itself. If the new
        direction is the exact opposite of the current one, the input is
        ignored. This prevents an instant self-collision when, for
        example, the snake is moving Right and the player presses 'A'
        (Left).

        The check compares the sum of the two direction vectors:
            current + new == (0, 0)  =>  they are opposites.
        """
        # Opposite directions cancel out to the zero vector.
        is_reversal = (
            self._direction[0] + new_direction[0] == 0
            and self._direction[1] + new_direction[1] == 0
        )

        if not is_reversal:
            self._direction = new_direction

    def move(self):
        """
        Advance the snake one cell in its current direction.

        COLLISION-READY MATH:
        The new head position is computed by adding the direction vector
        to the current head:
            new_head = (head_x + dx, head_y + dy)
        The caller (GameManager) is responsible for checking whether this
        new head collides with a wall or the body before committing.
        """
        dx, dy = self._direction
        head_x, head_y = self._body[0]
        new_head = (head_x + dx, head_y + dy)

        # Insert the new head at the front.
        self._body.insert(0, new_head)

        if self._growth_pending > 0:
            # Eating food: keep the tail so the snake grows by one.
            self._growth_pending -= 1
        else:
            # Normal move: drop the tail cell to keep length constant.
            self._body.pop()

    def grow(self):
        """Queue one segment of growth (called when food is eaten)."""
        self._growth_pending += 1

    def collides_with_self(self):
        """
        Return True if the head overlaps any other body segment.

        COLLISION MATH:
        The head is self._body[0]. We compare it against every segment
        from index 1 onward. Two cells collide when their (x, y) grid
        coordinates are identical. Because the head was already inserted
        by move(), a match means the snake ran into its own body.
        """
        head = self._body[0]
        return head in self._body[1:]

    def collides_with_point(self, point):
        """
        Return True if the head occupies the given (x, y) grid cell.
        Used to detect the snake eating food.
        """
        return self._body[0] == point
