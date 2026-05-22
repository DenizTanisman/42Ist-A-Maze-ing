"""PatternPlacer — lock the "42" shape into the grid before maze generation."""

import sys

from mazegen.core.grid import Grid


PATTERN_WIDTH = 7
PATTERN_HEIGHT = 5
MIN_GRID_WIDTH = 13     # PATTERN_WIDTH + 3 margin each side
MIN_GRID_HEIGHT = 11    # PATTERN_HEIGHT + 3 margin each side

# Cells that form the "42" shape, relative to the bounding-box top-left.
PATTERN_OFFSETS: list[tuple[int, int]] = [
    # "4"
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
    # "2"
    (4, 0), (5, 0), (6, 0), (6, 1), (6, 2),
    (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4),
]


class PatternPlacer:
    """Mark the cells that form a "42" shape as unbreakable.

    Called before maze generation so Prim carves the maze around the
    pattern. Pattern is always centered with floor division (closer to
    top-left when the slack is odd).
    """
    def __init__(self, grid: Grid) -> None:
        """Initialize the placer with the grid to mark on.

        Args:
            grid: The grid to place the pattern into.
        """
        self.grid = grid
        self.placed_cells: list[tuple[int, int]] = []

    def place_42(self) -> bool:
        """Mark the 42 cells as unbreakable. Skip if grid is too small
        or if entry/exit overlaps the pattern area.

        Returns:
            True if the pattern was placed; False if the grid is too
            small or entry/exit collides with a pattern cell (a warning
            is printed to stderr in that case).
        """
        if (self.grid.width < MIN_GRID_WIDTH
                or self.grid.height < MIN_GRID_HEIGHT):
            print("warning: maze too small for 42 pattern", file=sys.stderr)
            return False
        start_x = (self.grid.width - PATTERN_WIDTH) // 2
        start_y = (self.grid.height - PATTERN_HEIGHT) // 2

        pattern_cells: set[tuple[int, int]] = set()
        for dx, dy in PATTERN_OFFSETS:
            pattern_cells.add((start_x + dx, start_y + dy))

        if self.grid.entry in pattern_cells or self.grid.exit in pattern_cells:
            print(
                "warning: entry/exit overlaps 42 pattern; skipping",
                file=sys.stderr,
            )
            return False

        for x, y in pattern_cells:
            cell = self.grid.get(x, y)
            cell.unbreakable = True
            cell.is_42_pattern = True
            self.placed_cells.append((x, y))
        return True
