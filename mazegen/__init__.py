"""mazegen — perfect maze generator with Prim and BFS solver."""

from mazegen.core.cell import Cell
from mazegen.core.grid import Grid
from mazegen.exceptions import (
    AMazeError,
    ConfigError,
    ConfigFileNotFoundError,
    InvalidParameterError,
    MazeGenerationError,
    NoPathError,
    MazeTooSmallError,
    OutputWriteError,
)
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver

__all__ = [
    "Cell",
    "Grid",
    "MazeGenerator",
    "MazeSolver",
    "AMazeError",
    "ConfigError",
    "ConfigFileNotFoundError",
    "InvalidParameterError",
    "MazeGenerationError",
    "NoPathError",
    "MazeTooSmallError",
    "OutputWriteError",
]

__version__ = "1.0.0"
