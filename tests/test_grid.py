import pytest

from mazegen.core.grid import Grid


def test_new_grid_all_walls_closed() -> None:
    grid = Grid(4, 4)

    for y in range(grid.height):
        for x in range(grid.width):
            # 3. O konumdaki hücreyi al
            cell = grid.get(x, y)
            # 4. Hex değerinin "F" olduğunu doğrula
            assert cell.to_hex() == "F"


def test_remove_wall_between_consistency() -> None:
    # 1. ARRANGE: grid oluştur, iki bitişik hücreyi al
    grid = Grid(2, 2)        # Boyut: en az 2x1 yeter ama 2x2 daha temiz
    a = grid.get(0, 0)       # sol hücre
    b = grid.get(1, 0)       # a'nın doğu komşusu

    # 2. (Bonus) Sanity check: başlangıçta iki duvar da kapalı
    assert a.has_wall("E")   # True olmalı
    assert b.has_wall("W")  # True olmalı

    # 3. ACT: duvarı kaldır
    grid.remove_wall_between(a, b)

    # 4. ASSERT: iki taraf da artık duvar yok
    assert not a.has_wall("E")   # False olmalı
    assert not b.has_wall("W")   # False olmalı


def test_remove_wall_between_non_adjacent_raises() -> None:
    """Non-adjacent cells must raise ValueError when their wall is removed."""
    grid = Grid(3, 3)
    a = grid.get(0, 0)
    b = grid.get(1, 1)  # diagonal — Manhattan distance == 2

    with pytest.raises(ValueError):
        grid.remove_wall_between(a, b)


def test_in_bounds_boundaries() -> None:
    """in_bounds is True for valid cells (incl. corners), False outside."""
    grid = Grid(4, 3)  # width=4, height=3

    # Corners — all valid
    assert grid.in_bounds(0, 0)       # top-left
    assert grid.in_bounds(3, 0)       # top-right
    assert grid.in_bounds(0, 2)       # bottom-left
    assert grid.in_bounds(3, 2)       # bottom-right

    # Out of bounds — all invalid
    assert not grid.in_bounds(-1, 0)     # x too small
    assert not grid.in_bounds(4, 0)      # x too large (width)
    assert not grid.in_bounds(0, -1)     # y too small
    assert not grid.in_bounds(0, 3)      # y too large (height)
    assert not grid.in_bounds(-1, -1)    # both negative
    assert not grid.in_bounds(4, 3)      # both too large


def test_neighbors_count_by_position() -> None:
    """A corner has 2 neighbours, an edge cell 3, an interior cell 4."""
    grid = Grid(3, 3)

    # Corner: top-left only has E and S neighbours
    assert len(grid.neighbors(0, 0)) == 2

    # Edge: top-middle has W, E, S but no N
    assert len(grid.neighbors(1, 0)) == 3

    # Interior: center has all four neighbours
    assert len(grid.neighbors(1, 1)) == 4


def test_to_hex_various_combinations() -> None:
    """to_hex returns the correct hex digit for various wall configs."""
    grid = Grid(2, 2)

    # 1) All walls closed (default) -> "F" (binary 1111)
    cell = grid.get(0, 0)
    assert cell.to_hex() == "F"

    # 2) All walls open -> "0" (binary 0000)
    cell = grid.get(1, 0)
    cell.open_wall("N")
    cell.open_wall("E")
    cell.open_wall("S")
    cell.open_wall("W")
    assert cell.to_hex() == "0"

    # 3) Only N and E closed -> "3" (binary 0011)
    cell = grid.get(0, 1)
    cell.open_wall("S")
    cell.open_wall("W")
    assert cell.to_hex() == "3"

    # 4) Only S and W closed -> "C" (binary 1100)
    cell = grid.get(1, 1)
    cell.open_wall("N")
    cell.open_wall("E")
    assert cell.to_hex() == "C"


# --- unbreakable mechanism (Day 2 redesign for 42 pattern) -----------------

def test_cell_unbreakable_default_false() -> None:
    """A fresh Cell is breakable by default."""
    grid = Grid(2, 2)
    assert not grid.get(0, 0).unbreakable


def test_can_break_between_breakable_neighbours() -> None:
    """Adjacent breakable cells return True."""
    grid = Grid(2, 1)
    a = grid.get(0, 0)
    b = grid.get(1, 0)
    assert grid.can_break_between(a, b)


def test_can_break_between_unbreakable_returns_false() -> None:
    """If either cell is unbreakable, can_break_between returns False."""
    grid = Grid(2, 1)
    a = grid.get(0, 0)
    b = grid.get(1, 0)
    a.unbreakable = True
    assert not grid.can_break_between(a, b)

    a.unbreakable = False
    b.unbreakable = True
    assert not grid.can_break_between(a, b)


def test_can_break_between_non_adjacent_returns_false() -> None:
    """Non-adjacent cells return False even if both are breakable."""
    grid = Grid(3, 3)
    a = grid.get(0, 0)
    b = grid.get(2, 2)
    assert not grid.can_break_between(a, b)


def test_remove_wall_between_unbreakable_raises() -> None:
    """remove_wall_between raises ValueError if either cell is unbreakable."""
    grid = Grid(2, 1)
    a = grid.get(0, 0)
    b = grid.get(1, 0)
    a.unbreakable = True
    with pytest.raises(ValueError):
        grid.remove_wall_between(a, b)
