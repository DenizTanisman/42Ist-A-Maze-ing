"""Cell — a single maze cell with bit-encoded wall state."""

from mazegen.core.directions import ALL_WALLS_CLOSED, BIT


class Cell:
    """A single cell in the maze grid.

    Wall state is stored as a 4-bit integer (bits 0..3 -> N, E, S, W).
    A set bit means the wall is CLOSED. A cleared bit means it is OPEN.

    By team convention, open_wall / close_wall are only called from
    Grid.remove_wall_between so the wall consistency invariant lives
    in one place. Enforcement is discipline, not language — no
    underscore prefix.

    PatternPlacer sets `unbreakable=True` on its cells so
    Grid.remove_wall_between refuses to open their walls.
    """

    def __init__(self, x: int, y: int) -> None:
        """Create a cell with all four walls closed.

        Args:
            x: Column index (0 = leftmost).
            y: Row index (0 = topmost).
        """
        self.x: int = x
        self.y: int = y
        self.walls: int = ALL_WALLS_CLOSED   # 0b1111 — all four walls closed
        self.is_on_path: bool = False        # set by MazeSolver
        self.is_42_pattern: bool = False     # set by PatternPlacer
        self.unbreakable: bool = False       # locked by PatternPlacer

    def has_wall(self, direction: str) -> bool:
        """Return True if the wall on the given side is closed.

        Args:
            direction: One of "N", "E", "S", "W".

        Returns:
            True if that wall is closed, False if it is open.
        """
        return bool(self.walls & BIT[direction])

    def open_wall(self, direction: str) -> None:
        """Clear the bit for the given direction (open the wall).

        Convention: only Grid.remove_wall_between should call this,
        so the opposite wall of the neighbour cell is opened in sync.
        """
        # AND with the complement: every bit stays except the target,
        # which is forced to 0.
        self.walls &= ~BIT[direction]

    def close_wall(self, direction: str) -> None:
        """Set the bit for the given direction (close the wall).

        Used by PatternPlacer when isolating the "42" pattern cells.
        """
        self.walls |= BIT[direction]

    def to_hex(self) -> str:
        """Return the wall state as a single uppercase hex digit ("0".."F")."""
        # walls is always in 0..15, so :X produces exactly one character.
        return f"{self.walls:X}"

    def __repr__(self) -> str:
        return f"Cell(x={self.x}, y={self.y}, walls=0x{self.walls:X})"
