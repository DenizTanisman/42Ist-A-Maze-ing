"""Unit tests for MazeGenerator — covers A2.4 (reproducibility) and A2.7."""

import random
from collections import deque

import pytest

from mazegen.core.directions import NORTH, EAST, SOUTH, WEST
from mazegen.core.grid import Grid
from mazegen.exceptions import InvalidParameterError, MazeGenerationError
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver


# --- helpers ----------------------------------------------------------------

def count_reachable(grid: Grid, start: tuple[int, int] = (0, 0)) -> int:
    """BFS from start; return count of cells reachable via open walls."""
    visited = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        cell = grid.get(x, y)
        for direction, neighbour in grid.neighbors(x, y).items():
            # An open wall on `direction` means a passage to that neighbour.
            if not cell.has_wall(direction):
                ncoord = (neighbour.x, neighbour.y)
                if ncoord not in visited:
                    visited.add(ncoord)
                    queue.append(ncoord)
    return len(visited)


def count_removed_walls(grid: Grid) -> int:
    """Count open wall segments; each shared wall is counted once."""
    removed = 0
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get(x, y)
            for direction in (NORTH, EAST, SOUTH, WEST):
                if not cell.has_wall(direction):
                    removed += 1
    return removed // 2  # each wall is shared by two cells


# --- lifecycle / state ------------------------------------------------------

def test_generated_flag_lifecycle() -> None:
    """generated is False before generate() and True afterwards."""
    gen = MazeGenerator(5, 5, seed=1)
    assert not gen.generated
    gen.generate()
    assert gen.generated


# --- A2.4: seed reproducibility ---------------------------------------------

def test_same_seed_produces_same_maze() -> None:
    """Two generators with the same seed and size produce identical mazes."""
    a = MazeGenerator(10, 8, seed=42)
    b = MazeGenerator(10, 8, seed=42)
    a.generate()
    b.generate()
    assert a.to_hex_lines() == b.to_hex_lines()


def test_different_seeds_produce_different_mazes() -> None:
    """Different seeds produce different mazes (10x10 — collision ~0)."""
    a = MazeGenerator(10, 10, seed=42)
    b = MazeGenerator(10, 10, seed=99)
    a.generate()
    b.generate()
    assert a.to_hex_lines() != b.to_hex_lines()


def test_uses_local_rng_not_global() -> None:
    """Polluting the global random state must not affect a seeded maze."""
    random.seed(123)
    first = MazeGenerator(8, 8, seed=42)
    first.generate()

    random.seed(999)   # change the global state
    random.random()    # advance it further
    second = MazeGenerator(8, 8, seed=42)
    second.generate()

    assert first.to_hex_lines() == second.to_hex_lines()


# --- A2.7: perfect maze properties ------------------------------------------

def test_all_cells_connected() -> None:
    """Every cell is reachable from (0, 0) — the maze is connected."""
    gen = MazeGenerator(5, 5, seed=7)
    gen.generate()
    grid = gen.get_grid()
    assert count_reachable(grid) == grid.width * grid.height


def test_spanning_tree_property() -> None:
    """A perfect maze removes exactly width*height - 1 walls (no cycles)."""
    gen = MazeGenerator(9, 6, seed=7)
    gen.generate()
    grid = gen.get_grid()
    assert count_removed_walls(grid) == grid.width * grid.height - 1


# --- A2.3: edge cases -------------------------------------------------------

def test_1x1_maze() -> None:
    """A 1x1 maze has no walls to remove and a single reachable cell."""
    gen = MazeGenerator(1, 1, seed=1)
    gen.generate()
    grid = gen.get_grid()
    assert count_removed_walls(grid) == 0
    assert count_reachable(grid) == 1
    assert gen.to_hex_lines() == ["F"]


def test_2x2_maze() -> None:
    """A 2x2 perfect maze is connected and removes exactly 3 walls."""
    gen = MazeGenerator(2, 2, seed=1)
    gen.generate()
    grid = gen.get_grid()
    assert count_reachable(grid) == 4
    assert count_removed_walls(grid) == 3


def test_1x5_thin_maze() -> None:
    """A 1x5 vertical strip generates a valid 4-edge spanning tree."""
    gen = MazeGenerator(1, 5, seed=1, add_42=False)
    gen.generate()
    grid = gen.get_grid()
    assert count_reachable(grid) == 5
    assert count_removed_walls(grid) == 4


def test_5x1_thin_maze() -> None:
    """A 5x1 horizontal strip generates a valid 4-edge spanning tree."""
    gen = MazeGenerator(5, 1, seed=1, add_42=False)
    gen.generate()
    grid = gen.get_grid()
    assert count_reachable(grid) == 5
    assert count_removed_walls(grid) == 4


# --- error handling ---------------------------------------------------------

def test_invalid_algorithm_raises() -> None:
    """generate() with an unsupported algorithm raises."""
    gen = MazeGenerator(5, 5, seed=1, algorithm="wilson")
    with pytest.raises(InvalidParameterError):
        gen.generate()


def test_get_grid_before_generate_raises() -> None:
    """get_grid() before generate() raises MazeGenerationError."""
    gen = MazeGenerator(5, 5, seed=1)
    with pytest.raises(MazeGenerationError):
        gen.get_grid()


def test_to_hex_lines_before_generate_raises() -> None:
    """to_hex_lines() before generate() raises MazeGenerationError."""
    gen = MazeGenerator(5, 5, seed=1)
    with pytest.raises(MazeGenerationError):
        gen.to_hex_lines()


def test_generate_called_twice_raises() -> None:
    """A second generate() on the same instance raises MazeGenerationError."""
    gen = MazeGenerator(5, 5, seed=1, add_42=False)
    gen.generate()
    with pytest.raises(MazeGenerationError):
        gen.generate()


# --- output format ----------------------------------------------------------

def test_to_hex_lines_format() -> None:
    """to_hex_lines() returns one hex string per row, each width chars long."""
    gen = MazeGenerator(6, 4, seed=3)
    gen.generate()
    lines = gen.to_hex_lines()

    assert isinstance(lines, list)
    assert len(lines) == 4
    for row in lines:
        assert len(row) == 6
        for char in row:
            assert char in "0123456789ABCDEF"


# --- A4: pattern integration (pattern-first generation) ---------------------

def test_generate_add_42_false_no_pattern_marks() -> None:
    """With add_42=False, no cell is marked as pattern or unbreakable."""
    gen = MazeGenerator(15, 15, seed=1, add_42=False)
    gen.generate()
    grid = gen.get_grid()
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get(x, y)
            assert not cell.unbreakable
            assert not cell.is_42_pattern


def test_generate_with_pattern_marks_18_cells() -> None:
    """add_42=True on a large grid marks exactly 18 cells as pattern."""
    gen = MazeGenerator(15, 15, seed=1, add_42=True)
    gen.generate()
    grid = gen.get_grid()
    count = 0
    for y in range(grid.height):
        for x in range(grid.width):
            if grid.get(x, y).is_42_pattern:
                count += 1
    assert count == 18


def test_generate_pattern_cells_stay_fully_walled() -> None:
    """Prim does not open walls on pattern cells (stay hex F)."""
    gen = MazeGenerator(15, 15, seed=1, add_42=True)
    gen.generate()
    grid = gen.get_grid()
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get(x, y)
            if cell.is_42_pattern:
                assert cell.to_hex() == "F"


def test_generate_with_pattern_path_avoids_pattern() -> None:
    """The entry-to-exit path does not touch any pattern cell."""
    gen = MazeGenerator(15, 15, seed=1, add_42=True)
    gen.generate()
    grid = gen.get_grid()
    solver = MazeSolver(grid)
    solver.solve((0, 0), (14, 14))

    pattern_set: set[tuple[int, int]] = set()
    for y in range(grid.height):
        for x in range(grid.width):
            if grid.get(x, y).is_42_pattern:
                pattern_set.add((x, y))

    path_set: set[tuple[int, int]] = set()
    for cell in solver.path_cells:
        path_set.add((cell.x, cell.y))

    assert path_set.isdisjoint(pattern_set)


def test_generate_small_grid_with_add_42_still_works(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """add_42=True on a small grid produces a valid maze with no pattern."""
    gen = MazeGenerator(5, 5, seed=1, add_42=True)
    gen.generate()
    capsys.readouterr()  # discard the "too small" warning
    grid = gen.get_grid()
    for y in range(grid.height):
        for x in range(grid.width):
            assert not grid.get(x, y).is_42_pattern
