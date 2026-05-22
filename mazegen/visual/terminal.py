"""TerminalRenderer — draw a maze grid to the terminal with ANSI colors."""

from typing import Any

RESET = "\033[0m"
ENTRY_COLOR = "\033[38;5;82m"
EXIT_COLOR = "\033[38;5;196m"
PATH_COLOR = "\033[38;5;39m"
PATTERN_COLOR = "\033[38;5;201m"

WALL_PALETTE = [
    "\033[38;5;244m",  # gray (default)
    "\033[38;5;220m",  # yellow
    "\033[38;5;46m",   # green
    "\033[38;5;208m",  # orange
    "\033[38;5;177m",  # purple
]


class TerminalRenderer:
    """Render a Grid to stdout using ANSI color codes and block characters.

    Each cell is drawn as a 1x1 block; walls between cells and corner posts
    fill the gaps, so the printed maze is 2*width+1 columns wide and
    2*height+1 rows tall. Entry, exit, the "42" pattern, and the solved path
    each get a distinct color. The wall color can be cycled and the solved
    path can be hidden via toggle_path().
    """

    def __init__(self) -> None:
        """Initialize with path visible and the default (gray) wall palette."""
        self.show_path = True
        self.wall_char = "█"
        self.palette_index = 0
        self.wall_color = WALL_PALETTE[0]

    def cycle_colors(self) -> None:
        """Advance the wall color to the next WALL_PALETTE entry."""
        self.palette_index = (self.palette_index + 1) % len(WALL_PALETTE)
        self.wall_color = WALL_PALETTE[self.palette_index]

    def render(self, grid: Any) -> None:
        """Print the maze to stdout, row by row, with walls and path overlays.

        The grid is drawn as alternating cell rows and wall rows. Each cell
        is two characters wide because terminal characters are taller than
        they are wide; without this doubling the maze looks vertically
        stretched. Corner posts between cells are drawn as walls only when
        at least one of the four touching walls is closed.
        """
        try:
            top_border = ""
            for i in range(grid.width * 2 + 1):
                top_border += self.wall_char
            print(self.wall_color + top_border + RESET)

            for y in range(grid.height):
                line_output = self.wall_color + self.wall_char + RESET

                for x in range(grid.width):
                    cell = grid.get(x, y)
                    char_to_draw = " "
                    color_to_apply = RESET

                    if (x, y) == grid.entry:
                        char_to_draw = "S"
                        color_to_apply = ENTRY_COLOR
                    elif (x, y) == grid.exit:
                        char_to_draw = "E"
                        color_to_apply = EXIT_COLOR
                    elif cell.is_42_pattern:
                        char_to_draw = self.wall_char
                        color_to_apply = PATTERN_COLOR
                    elif self.show_path and cell.is_on_path:
                        char_to_draw = self.wall_char
                        color_to_apply = PATH_COLOR

                    line_output += color_to_apply + char_to_draw + RESET

                    if cell.has_wall("E"):
                        line_output += self.wall_color + self.wall_char + RESET
                    elif (
                        self.show_path
                        and cell.is_on_path
                        and x + 1 < grid.width
                        and grid.get(x + 1, y).is_on_path
                    ):
                        line_output += PATH_COLOR + self.wall_char + RESET
                    else:
                        line_output += " "

                print(line_output)

                if y < grid.height - 1:
                    bottom_line = self.wall_color + self.wall_char + RESET
                    for x in range(grid.width):
                        cell = grid.get(x, y)
                        below_cell = grid.get(x, y + 1)
                        if cell.has_wall("S"):
                            bottom_line += (
                                self.wall_color + self.wall_char + RESET
                            )
                        elif (
                            self.show_path
                            and cell.is_on_path
                            and below_cell.is_on_path
                        ):
                            bottom_line += PATH_COLOR + self.wall_char + RESET
                        else:
                            bottom_line += " "
                        if x == grid.width - 1:
                            is_corner_wall = True
                        else:
                            right_cell = grid.get(x + 1, y)
                            is_corner_wall = (
                                cell.has_wall("S")
                                or right_cell.has_wall("S")
                                or cell.has_wall("E")
                                or below_cell.has_wall("E")
                            )
                        if is_corner_wall:
                            bottom_line += (
                                self.wall_color + self.wall_char + RESET
                            )
                        else:
                            bottom_line += " "
                    print(bottom_line)

            print(self.wall_color + top_border + RESET)

        except Exception as e:
            print("Rendering error: " + str(e))

    def toggle_path(self) -> None:
        """Flip whether the path overlay is shown on next render()."""
        self.show_path = not self.show_path
