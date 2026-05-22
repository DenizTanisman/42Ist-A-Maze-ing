"""Grid — rectangular maze grid that owns all cells and wall transitions."""

from mazegen.core.cell import Cell
from mazegen.core.directions import OPPOSITE


class Grid:
    """A rectangular maze grid of width x height cells.

    Internal representation is a list of rows (list of lists of Cell):
    self.cells[y][x] gives the cell at column x, row y.

    External API always uses (x, y) order — consistent with CONTRACT.md.
    The [y][x] internal layout is hidden inside this class.
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a grid with all cells fully walled (every wall closed).

        Args:
            width: Number of columns -> x
            height: Number of rows -> y
        """
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] | None = None
        self.exit: tuple[int, int] | None = None

        # Build row by row. Outer list = rows, inner list = columns.
        self.cells: list[list[Cell]] = []
        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                row.append(Cell(x, y))
            self.cells.append(row)

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is a valid cell coordinate."""
        return (0 <= x < self.width) and (0 <= y < self.height)

    def get(self, x: int, y: int) -> Cell:
        """Return the cell at (x, y).

        Args:
            x: Column index (0 <= x < width).
            y: Row index (0 <= y < height).

        Returns:
            The Cell at that position.

        Raises:
            IndexError: If (x, y) is out of bounds.
        """
        if not self.in_bounds(x, y):
            raise IndexError(
                f"Cell ({x}, {y}) is out of bounds "
                f"for grid of size {self.width}x{self.height}"
            )
        # Internal layout is [y][x], external API is (x, y).
        # This is the ONLY place that conversion happens.
        return self.cells[y][x]

    def neighbors(self, x: int, y: int) -> dict[str, Cell]:
        """Return the in-bounds neighbours of cell (x, y), keyed by direction.

        Args:
            x: Column index of the source cell.
            y: Row index of the source cell.

        Returns:
            A dict mapping direction ("N", "E", "S", "W") to the neighbouring
            Cell on that side. Directions that fall outside the grid are
            omitted from the dict (no None values).
        """
        neigh: dict[str, Cell] = {}

        if self.in_bounds(x, y - 1):
            neigh["N"] = self.get(x, y - 1)
        if self.in_bounds(x + 1, y):
            neigh["E"] = self.get(x + 1, y)
        if self.in_bounds(x, y + 1):
            neigh["S"] = self.get(x, y + 1)
        if self.in_bounds(x - 1, y):
            neigh["W"] = self.get(x - 1, y)

        return neigh

    def remove_wall_between(self, a: Cell, b: Cell) -> None:
        """Open the wall between two adjacent cells, on both sides.

        This is the SINGLE place in the package that flips wall state on a
        Cell — it guarantees the wall is opened consistently on both a and b
        (the wall consistency invariant from CONTRACT.md).

        Args:
            a: One of the two cells.
            b: The other cell. Must be a 4-neighbour of a.

        Raises:
            ValueError: If a and b are not 4-neighbours
                (Manhattan distance != 1).
        """
        dx = b.x - a.x
        dy = b.y - a.y

        if abs(dx) + abs(dy) != 1:
            raise ValueError(
                f"Cells ({a.x}, {a.y}) and ({b.x}, {b.y}) are not adjacent"
            )
        if (a.unbreakable or b.unbreakable):
            raise ValueError(
                f"Cannot remove wall: cell ({a.x}, {a.y}) or "
                f"({b.x}, {b.y}) is unbreakable"
            )

        if dx == 0 and dy == -1:
            direction = "N"
        elif dx == 1 and dy == 0:
            direction = "E"
        elif dx == 0 and dy == 1:
            direction = "S"
        elif dx == -1 and dy == 0:
            direction = "W"

        a.open_wall(direction)
        b.open_wall(OPPOSITE[direction])

    def can_break_between(self, a: Cell, b: Cell) -> bool:
        """Return True if the wall between a and b can be opened.

        False if cells are not 4-neighbours, or either is unbreakable.
        Use this as a guard before calling remove_wall_between.
        """
        dx = b.x - a.x
        dy = b.y - a.y
        if abs(dx) + abs(dy) != 1:
            return False
        if (a.unbreakable or b.unbreakable):
            return False
        return True

    def to_hex_lines(self) -> list[str]:
        """Return the maze as one hex string per row, top to bottom."""
        lines: list[str] = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                new_hex = self.get(x, y).to_hex()
                row += new_hex
            lines.append(row)
        return lines
