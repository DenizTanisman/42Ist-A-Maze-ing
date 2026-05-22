"""Direction constants and lookup tables.

Single source of truth for direction encoding across the package.
Bit layout (per project contract, LSB-first):
    bit 0 -> N, bit 1 -> E, bit 2 -> S, bit 3 -> W
"""


NORTH = "N"
EAST = "E"
SOUTH = "S"
WEST = "W"

# Bit value for each direction. cell.walls & BIT[d] -> wall closed?
BIT: dict[str, int] = {
    NORTH: 1,   # 0b0001
    EAST:  2,   # 0b0010
    SOUTH: 4,   # 0b0100
    WEST:  8,   # 0b1000
}

ALL_WALLS_CLOSED = 0xF   # 0b1111 = 15 = 0xF.

# Coordinate deltas for moving one cell in a given direction.
# Screen coordinates: (0,0) top-left, x grows right, y grows DOWN.
DX: dict[str, int] = {NORTH:  0, EAST:  1, SOUTH:  0, WEST: -1}
DY: dict[str, int] = {NORTH: -1, EAST:  0, SOUTH:  1, WEST:  0}

# Opposite direction lookup — used for consistency when removing walls.
OPPOSITE: dict[str, str] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST:  WEST,
    WEST:  EAST,
}

# Iteration order — fixed so generation is deterministic given a seed.
ALL_DIRECTIONS: tuple[str, ...] = (NORTH, EAST, SOUTH, WEST)

# Reverse lookup: a (dx, dy) coordinate step back to its direction letter.
# Used by the solver to convert a path of coordinates into a direction string.
STEP_TO_DIR: dict[tuple[int, int], str] = {
    (0, -1): NORTH,
    (1, 0): EAST,
    (0, 1): SOUTH,
    (-1, 0): WEST,
}
