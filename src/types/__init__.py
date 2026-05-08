"""Type definitions for the 2048 game."""

from dataclasses import dataclass
from enum import Enum
from typing import NewType, Tuple

GridPosition = NewType("GridPosition", Tuple[int, int])


class Direction(Enum):
    """Cardinal directions for tile movement."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class Tile:
    """Represents a tile on the grid."""

    value: int
    position: GridPosition
    merged_from: Tuple[int, int] | None = None


@dataclass(frozen=True)
class GridCell:
    """Represents a single cell in the grid."""

    row: int
    col: int
    tile_value: int | None = None


@dataclass
class GameState:
    """Complete game state."""

    grid: list[list[int | None]]
    score: int
    highest_tile: int
    won: bool = False
    game_over: bool = False
