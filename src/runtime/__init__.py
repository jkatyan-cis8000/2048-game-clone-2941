"""Runtime module for the 2048 game lifecycle."""

from src.providers import RandomProvider
from src.service import GameService
from src.ui import GameUI


def run_game() -> None:
    """Run the 2048 game."""
    random_provider = RandomProvider()
    game_service = GameService(random_provider)
    ui = GameUI(game_service)
    ui.start()


if __name__ == "__main__":
    run_game()
