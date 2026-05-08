"""Game service for the 2048 game."""

from src.config import GRID_SIZE, INITIAL_TILES, NEW_TILE_VALUES, NEW_TILE_PROBABILITIES, WINNING_TILE
from src.providers import RandomProvider
from src.types import Direction, GameState, GridPosition


class GameService:
    """Handles game logic: moves, merging, win/loss detection."""

    def __init__(self, random_provider: RandomProvider | None = None):
        self._random = random_provider or RandomProvider()

    def create_initial_state(self) -> GameState:
        """Create a new game with initial tiles."""
        grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        score = 0
        highest_tile = 0

        for _ in range(INITIAL_TILES):
            grid, score, highest_tile = self._add_random_tile(grid, score, highest_tile)

        return GameState(
            grid=grid,
            score=score,
            highest_tile=highest_tile,
            won=False,
            game_over=False,
        )

    def _add_random_tile(self, grid: list[list[int | None]], score: int, highest_tile: int) -> tuple[list[list[int | None]], int, int]:
        """Add a random tile to an empty cell."""
        empty_cells = self._get_empty_cells(grid)
        if not empty_cells:
            return grid, score, highest_tile

        row, col = self._random.choice(empty_cells)
        value = self._random.choices(NEW_TILE_VALUES, NEW_TILE_PROBABILITIES)[0]

        new_grid = [row.copy() for row in grid]
        new_grid[row][col] = value

        return new_grid, score, max(highest_tile, value)

    def _get_empty_cells(self, grid: list[list[int | None]]) -> list[tuple[int, int]]:
        """Get all empty cell positions."""
        empty = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] is None:
                    empty.append((r, c))
        return empty

    def move(self, state: GameState, direction: Direction) -> GameState:
        """Execute a move in the given direction."""
        grid = [row.copy() for row in state.grid]
        score = state.score
        highest_tile = state.highest_tile

        # Process each row or column based on direction
        if direction in (Direction.LEFT, Direction.RIGHT):
            grid = self._process_rows(grid, direction)
        else:
            grid = self._process_columns(grid, direction)

        # Check if grid changed
        if grid == state.grid:
            # No change, check if game is over
            if not self._has_moves_available(grid):
                return GameState(
                    grid=grid,
                    score=score,
                    highest_tile=highest_tile,
                    won=state.won,
                    game_over=True,
                )
            return GameState(
                grid=grid,
                score=score,
                highest_tile=highest_tile,
                won=state.won,
                game_over=False,
            )

        # Add new tile and update state
        grid, score, highest_tile = self._add_random_tile(grid, score, highest_tile)

        # Check win condition
        won = state.won or highest_tile >= WINNING_TILE

        # Check if game is over
        game_over = not self._has_moves_available(grid)

        return GameState(
            grid=grid,
            score=score,
            highest_tile=highest_tile,
            won=won,
            game_over=game_over,
        )

    def _process_rows(self, grid: list[list[int | None]], direction: Direction) -> list[list[int | None]]:
        """Process all rows for left or right movement."""
        new_grid = []
        for row in grid:
            if direction == Direction.LEFT:
                processed, score_delta = self._slide_and_merge(row)
            else:
                processed, score_delta = self._slide_and_merge(row[::-1])
                processed = processed[::-1]
            new_grid.append(processed)
        return new_grid

    def _process_columns(self, grid: list[list[int | None]], direction: Direction) -> list[list[int | None]]:
        """Process all columns for up or down movement."""
        # Transpose to work with columns as rows
        transposed = [[grid[r][c] for r in range(GRID_SIZE)] for c in range(GRID_SIZE)]
        
        if direction == Direction.UP:
            processed = self._process_rows(transposed, Direction.LEFT)
        else:
            processed = self._process_rows(transposed, Direction.RIGHT)
            # Transpose back
            processed = [[processed[c][r] for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        
        return processed

    def _slide_and_merge(self, row: list[int | None]) -> tuple[list[int | None], int]:
        """Slide and merge tiles in a row."""
        # Remove Nones and slide left
        tiles = [t for t in row if t is not None]
        
        result = []
        score_delta = 0
        
        i = 0
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                merged_value = tiles[i] * 2
                result.append(merged_value)
                score_delta += merged_value
                i += 2
            else:
                result.append(tiles[i])
                i += 1
        
        # Pad with Nones to fill grid size
        while len(result) < GRID_SIZE:
            result.append(None)
        
        return result, score_delta

    def _has_moves_available(self, grid: list[list[int | None]]) -> bool:
        """Check if any moves are possible."""
        # Check for empty cells
        if any(cell is None for row in grid for cell in row):
            return True

        # Check for adjacent matching tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                current = grid[r][c]
                # Check right neighbor
                if c + 1 < GRID_SIZE and grid[r][c + 1] == current:
                    return True
                # Check bottom neighbor
                if r + 1 < GRID_SIZE and grid[r + 1][c] == current:
                    return True

        return False
