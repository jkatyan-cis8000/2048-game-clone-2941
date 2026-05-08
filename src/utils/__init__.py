"""Pure utility functions for the 2048 game."""

from src.types import Direction


def parse_direction(key: str) -> Direction | None:
    """Parse a keyboard input into a direction."""
    key = key.lower()
    if key in ("up", "w", "\x1b[A"):
        return Direction.UP
    elif key in ("down", "s", "\x1b[B"):
        return Direction.DOWN
    elif key in ("left", "a", "\x1b[D"):
        return Direction.LEFT
    elif key in ("right", "d", "\x1b[C"):
        return Direction.RIGHT
    return None
