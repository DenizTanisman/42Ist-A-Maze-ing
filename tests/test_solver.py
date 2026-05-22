"""Unit tests for MazeSolver — covers A3.4 (edge cases) and A3.5."""

import pytest

from mazegen.core.grid import Grid
from mazegen.core.directions import DX, DY
from mazegen.exceptions import NoPathError
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver


# --- helpers ----------------------------------------------------------------

def open_corridor(grid: Grid, cells: list[tuple[int, int]]) -> None:
    """Open the walls between each consecutive pair of cells in `cells`."""
    for i in range(len(cells) - 1):
        x0, y0 = cells[i]
        x1, y1 = cells[i + 1]
        grid.remove_wall_between(grid.get(x0, y0), grid.get(x1, y1))


def walk_path_is_open(
    grid: Grid, entry: tuple[int, int], path_string: str,
) -> bool:
    """Return True iff every step in `path_string` follows an open wall."""
    x, y = entry
    for direction in path_string:
        cell = grid.get(x, y)
        if cell.has_wall(direction):
            return False
        x += DX[direction]
        y += DY[direction]
    return True


# --- hand-crafted mazes -----------------------------------------------------

def test_straight_corridor() -> None:
    """A 5x1 corridor with all internal walls open solves to 'EEEE'."""
    grid = Grid(5, 1)
    open_corridor(grid, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])
    solver = MazeSolver(grid)
    assert solver.solve((0, 0), (4, 0)) == "EEEE"


def test_l_shape_path() -> None:
    """An L-shape corridor (down then right) solves to 'SSEE'."""
    grid = Grid(3, 3)
    open_corridor(grid, [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)])
    solver = MazeSolver(grid)
    assert solver.solve((0, 0), (2, 2)) == "SSEE"


# --- edge cases (A3.4) ------------------------------------------------------

def test_entry_equals_exit_returns_empty_string() -> None:
    """Solving from a cell to itself returns '' with a single path cell."""
    grid = Grid(5, 5)
    solver = MazeSolver(grid)
    assert solver.solve((2, 2), (2, 2)) == ""
    assert len(solver.path_cells) == 1
    assert (solver.path_cells[0].x, solver.path_cells[0].y) == (2, 2)


def test_1x1_maze() -> None:
    """A 1x1 maze has only one cell; the only valid solve is entry==exit."""
    grid = Grid(1, 1)
    solver = MazeSolver(grid)
    assert solver.solve((0, 0), (0, 0)) == ""


def test_no_path_raises() -> None:
    """A fully walled grid raises NoPathError when entry != exit."""
    grid = Grid(3, 3)  # all walls closed, no passages
    solver = MazeSolver(grid)
    with pytest.raises(NoPathError):
        solver.solve((0, 0), (2, 2))


# --- correctness on generated mazes -----------------------------------------

def test_path_walks_open_passages() -> None:
    """Every step in the returned path must follow an open wall."""
    gen = MazeGenerator(8, 6, seed=7)
    gen.generate()
    grid = gen.get_grid()
    solver = MazeSolver(grid)
    path = solver.solve((0, 0), (7, 5))
    assert walk_path_is_open(grid, (0, 0), path)


def test_path_starts_and_ends_correctly() -> None:
    """The first path cell is entry, the last is exit."""
    gen = MazeGenerator(8, 6, seed=7)
    gen.generate()
    solver = MazeSolver(gen.get_grid())
    solver.solve((0, 0), (7, 5))
    cells = solver.path_cells
    assert (cells[0].x, cells[0].y) == (0, 0)
    assert (cells[-1].x, cells[-1].y) == (7, 5)


def test_path_cells_count_matches_string_length() -> None:
    """N steps in the string = N+1 cells on the path."""
    gen = MazeGenerator(10, 10, seed=3)
    gen.generate()
    solver = MazeSolver(gen.get_grid())
    path = solver.solve((0, 0), (9, 9))
    assert len(solver.path_cells) == len(path) + 1


def test_reproducible_solve() -> None:
    """Solving the same maze twice gives the same path."""
    gen = MazeGenerator(10, 10, seed=42)
    gen.generate()
    solver = MazeSolver(gen.get_grid())
    p1 = solver.solve((0, 0), (9, 9))
    p2 = solver.solve((0, 0), (9, 9))
    assert p1 == p2


def test_path_string_only_direction_chars() -> None:
    """The returned path string contains only N/E/S/W characters."""
    gen = MazeGenerator(8, 6, seed=1)
    gen.generate()
    solver = MazeSolver(gen.get_grid())
    path = solver.solve((0, 0), (7, 5))
    for char in path:
        assert char in "NESW"


# --- get_path_cells (A3.6) --------------------------------------------------

def test_get_path_cells_returns_path_cells_attribute() -> None:
    """get_path_cells returns the same list as self.path_cells after solve."""
    grid = Grid(3, 1)
    open_corridor(grid, [(0, 0), (1, 0), (2, 0)])
    solver = MazeSolver(grid)
    solver.solve((0, 0), (2, 0))
    cells = solver.get_path_cells()
    assert cells == solver.path_cells
    assert len(cells) == 3


def test_get_path_cells_before_solve_is_empty() -> None:
    """Calling get_path_cells before solve returns an empty list."""
    grid = Grid(3, 3)
    solver = MazeSolver(grid)
    assert solver.get_path_cells() == []
