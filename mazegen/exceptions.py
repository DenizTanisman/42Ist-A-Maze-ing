"""Custom exception hierarchy for the mazegen package."""


class AMazeError(Exception):
    """Base exception for all mazegen errors."""


class ConfigError(AMazeError):
    """Raised when configuration is missing or invalid."""


class MazeGenerationError(AMazeError):
    """Raised when maze generation fails or is used before generate()."""


class NoPathError(AMazeError):
    """Raised when no path exists between entry and exit."""


class MazeTooSmallError(AMazeError):
    """Raised when the maze is too small to embed the 42 pattern."""


class OutputWriteError(AMazeError):
    """Raised when the output file cannot be written."""


class ConfigFileNotFoundError(ConfigError):
    """Raised when the config file does not exist."""


class InvalidParameterError(ConfigError):
    """Raised when a parameter value is outside its valid range."""
