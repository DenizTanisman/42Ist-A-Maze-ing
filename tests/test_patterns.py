"""Unit tests for PatternPlacer — covers A4.6."""

import pytest

from mazegen.core.grid import Grid
from mazegen.patterns import (
    MIN_GRID_HEIGHT,
    MIN_GRID_WIDTH,
    PATTERN_HEIGHT,
    PATTERN_OFFSETS,
    PATTERN_WIDTH,
    PatternPlacer,
)


# --- threshold behaviour ----------------------------------------------------

def test_place_42_returns_true_on_minimum_grid() -> None:
    """A grid exactly at the threshold accepts the pattern."""
    grid = Grid(MIN_GRID_WIDTH, MIN_GRID_HEIGHT)
    placer = PatternPlacer(grid)
    assert placer.place_42()


def test_place_42_returns_false_on_narrow_grid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Narrower than MIN_GRID_WIDTH is skipped; warning printed to stderr."""
    grid = Grid(MIN_GRID_WIDTH - 1, MIN_GRID_HEIGHT)
    placer = PatternPlacer(grid)
    assert not placer.place_42()
    captured = capsys.readouterr()
    assert "too small" in captured.err.lower()


def test_place_42_returns_false_on_short_grid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Shorter than MIN_GRID_HEIGHT is skipped; warning printed to stderr."""
    grid = Grid(MIN_GRID_WIDTH, MIN_GRID_HEIGHT - 1)
    placer = PatternPlacer(grid)
    assert not placer.place_42()
    captured = capsys.readouterr()
    assert "too small" in captured.err.lower()


# --- placement correctness --------------------------------------------------

def test_place_42_marks_exactly_18_cells() -> None:
    """The "42" pattern occupies exactly 18 cells (7 for '4', 11 for '2')."""
    grid = Grid(13, 11)
    placer = PatternPlacer(grid)
    placer.place_42()

    assert len(placer.placed_cells) == 18
    assert len(PATTERN_OFFSETS) == 18

    count = 0
    for y in range(grid.height):
        for x in range(grid.width):
            if grid.get(x, y).unbreakable:
                count += 1
    assert count == 18


def test_place_42_centers_pattern() -> None:
    """The pattern's top-left cell lands at (W-7)//2, (H-5)//2."""
    grid = Grid(15, 13)
    placer = PatternPlacer(grid)
    placer.place_42()

    expected_start_x = (15 - PATTERN_WIDTH) // 2
    expected_start_y = (13 - PATTERN_HEIGHT) // 2
    assert (expected_start_x, expected_start_y) in placer.placed_cells


def test_place_42_sets_both_flags() -> None:
    """Every placed cell has unbreakable=True AND is_42_pattern=True."""
    grid = Grid(15, 15)
    placer = PatternPlacer(grid)
    placer.place_42()
    for x, y in placer.placed_cells:
        cell = grid.get(x, y)
        assert cell.unbreakable
        assert cell.is_42_pattern


def test_place_42_pattern_cells_stay_fully_walled() -> None:
    """Placed cells remain hex F (all four walls closed)."""
    grid = Grid(15, 15)
    placer = PatternPlacer(grid)
    placer.place_42()
    for x, y in placer.placed_cells:
        assert grid.get(x, y).to_hex() == "F"


def test_small_grid_no_cells_marked(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When skipped, no cell is marked unbreakable or is_42_pattern."""
    grid = Grid(5, 5)
    placer = PatternPlacer(grid)
    placer.place_42()
    capsys.readouterr()  # discard the warning

    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get(x, y)
            assert not cell.unbreakable
            assert not cell.is_42_pattern
    assert placer.placed_cells == []
