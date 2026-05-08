"""UI module for the 2048 game."""

import os
import sys
import termios
import tty

from src.config import GRID_SIZE, WINNING_TILE
from src.service import GameService
from src.types import Direction, GameState


class GameUI:
    """Handles user interface for the 2048 game."""

    # ANSI color codes for tile values
    COLORS = {
        2: "\033[97m",    # white
        4: "\033[92m",    # green
        8: "\033[93m",    # yellow
        16: "\033[91m",   # red
        32: "\033[95m",   # magenta
        64: "\033[94m",   # blue
        128: "\033[96m",  # cyan
        256: "\033[37m",  # light gray
        512: "\033[36m",  # cyan
        1024: "\033[35m", # purple
        2048: "\033[31m", # bright red
    }
    RESET = "\033[0m"
    BG_RESET = "\033[49m"

    def __init__(self, game_service: GameService):
        self.game_service = game_service
        self._game_state: GameState | None = None

    def start(self) -> None:
        """Start the game loop."""
        self._game_state = self.game_service.create_initial_state()
        self._clear_screen()
        self._draw_game()

        # Set terminal to raw mode for key capture
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            self._game_loop()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _game_loop(self) -> None:
        """Main game loop."""
        while True:
            key = self._get_key()
            direction = self._parse_key(key)
            
            if direction is None:
                continue

            if self._game_state.game_over:
                self._handle_game_over()
                break

            if self._game_state.won:
                if self._handle_win():
                    # Continue playing
                    pass
                else:
                    break

            self._game_state = self.game_service.move(self._game_state, direction)
            self._clear_screen()
            self._draw_game()

    def _get_key(self) -> str:
        """Read a single keypress from stdin."""
        ch = sys.stdin.read(1)
        if ch == "\x1b":  # Escape sequence
            ch += sys.stdin.read(2)
        return ch

    def _parse_key(self, key: str) -> Direction | None:
        """Parse a keypress into a direction."""
        if key in ("up", "w", "\x1b[A"):
            return Direction.UP
        elif key in ("down", "s", "\x1b[B"):
            return Direction.DOWN
        elif key in ("left", "a", "\x1b[D"):
            return Direction.LEFT
        elif key in ("right", "d", "\x1b[C"):
            return Direction.RIGHT
        elif key in ("q", "\x1b"):
            return None
        return None

    def _clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system("clear" if os.name == "posix" else "cls")

    def _draw_game(self) -> None:
        """Draw the current game state."""
        if self._game_state is None:
            return

        state = self._game_state
        grid = state.grid

        print(f"Score: {state.score}  |  Highest Tile: {state.highest_tile}")
        print()

        # Draw header
        print("+" + "-" * (GRID_SIZE * 6) + "+")

        for row in grid:
            print("|", end="")
            for cell in row:
                if cell is None:
                    print("      |", end="")
                else:
                    color = self.COLORS.get(cell, "\033[37m")
                    print(f" {color}{cell:4}{self.RESET}  |", end="")
            print()
            print("+" + "-" * (GRID_SIZE * 6) + "+")

        print()
        if state.won and not state.game_over:
            print(f"Congratulations! You reached {WINNING_TILE}!")
            print("Press 'n' to continue playing or 'q' to quit.")
        elif state.game_over:
            print("Game Over! No more moves possible.")
            print("Press 'r' to restart or 'q' to quit.")

    def _handle_game_over(self) -> None:
        """Handle game over state."""
        self._draw_game()
        print("Game Over! No more moves possible.")
        print("Press 'r' to restart or 'q' to quit.")

        while True:
            key = self._get_key()
            if key == "r":
                self._game_state = self.game_service.create_initial_state()
                self._clear_screen()
                self._draw_game()
                return
            elif key == "q" or key == "\x1b":
                print("Thanks for playing!")
                return

    def _handle_win(self) -> bool:
        """Handle win state. Returns True if continuing, False if quitting."""
        print("Press 'c' to continue or 'q' to quit.")

        while True:
            key = self._get_key()
            if key == "c":
                return True
            elif key == "q" or key == "\x1b":
                print("Thanks for playing!")
                return False
