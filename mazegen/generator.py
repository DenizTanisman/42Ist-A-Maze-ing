import random

from mazegen.core.grid import Grid
from mazegen.exceptions import InvalidParameterError, MazeGenerationError
from mazegen.patterns import PatternPlacer


class MazeGenerator:
    """Generate a perfect maze using a randomized Prim's algorithm."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        algorithm: str = "prim",
        add_42: bool = True,
    ) -> None:
        """Initialize the generator with maze dimensions and options.

        Args:
            width: Number of columns (x axis).
            height: Number of rows (y axis).
            seed: Optional RNG seed for reproducible mazes.
            algorithm: Generation algorithm ("prim" only).
            add_42: Whether to embed the "42" pattern after generation.
        """
        self.algorithm = algorithm
        self.add_42 = add_42
        self.grid = Grid(width, height)
        self.rng = random.Random(seed)
        self.generated = False

    def generate(self) -> None:
        """Generate the maze using the configured algorithm.

        If self.add_42 is True and the grid is large enough, a "42"
        pattern is locked in the centre first, so Prim carves around it.
        """
        if self.generated:
            raise MazeGenerationError(
                "generate() has already been called; "
                "create a new MazeGenerator instance for another maze"
            )
        if self.algorithm == "prim":
            if self.add_42:
                PatternPlacer(self.grid).place_42()
            self.generate_prim()
        else:
            raise InvalidParameterError(
                f"algorithm must be 'prim', got: {self.algorithm!r}"
            )
        self.generated = True

    def get_grid(self) -> Grid:
        """Return the generated grid."""
        if not self.generated:
            raise MazeGenerationError(
                "generate() must be called before get_grid()"
            )
        return self.grid

    def to_hex_lines(self) -> list[str]:
        """Return the generated maze as one hex string per row."""
        if not self.generated:
            raise MazeGenerationError(
                "generate() must be called before to_hex_lines()"
            )
        return self.grid.to_hex_lines()

    def neighbor_coords(self, coord: tuple[int, int]) -> list[tuple[int, int]]:
        """Return in-bounds, breakable neighbour coords of the given cell."""
        x, y = coord
        result: list[tuple[int, int]] = []
        for cell in self.grid.neighbors(x, y).values():
            if not cell.unbreakable:
                result.append((cell.x, cell.y))
        return result

    def generate_prim(self) -> None:
        """Carve a perfect maze in place using randomized Prim."""
        while True:
            x = self.rng.randrange(self.grid.width)
            y = self.rng.randrange(self.grid.height)
            if not self.grid.get(x, y).unbreakable:
                break
        start: tuple[int, int] = (x, y)
        in_maze: set[tuple[int, int]] = {start}
        frontier: set[tuple[int, int]] = set(self.neighbor_coords(start))
        while frontier:
            self.create_one_cell(in_maze, frontier)

    def create_one_cell(
        self,
        in_maze: set[tuple[int, int]],
        frontier: set[tuple[int, int]],
    ) -> None:
        """Pull one cell from the frontier, connect it, and grow it."""
        current: tuple[int, int] = self.rng.choice(list(frontier))
        bridges: list[tuple[int, int]] = []
        for cell in self.neighbor_coords(current):
            if cell in in_maze:
                bridges.append(cell)
        bridge = self.rng.choice(bridges)

        cur_x, cur_y = current
        cell_cur = self.grid.get(cur_x, cur_y)
        brid_x, brid_y = bridge
        cell_brid = self.grid.get(brid_x, brid_y)
        self.grid.remove_wall_between(cell_cur, cell_brid)
        in_maze.add(current)
        frontier.remove(current)
        for neigh in self.neighbor_coords(current):
            if neigh not in in_maze:
                frontier.add(neigh)
