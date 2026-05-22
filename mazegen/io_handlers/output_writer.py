"""Write the maze, entry/exit, and solved path to a text file."""

from typing import List, Tuple

from mazegen.exceptions import OutputWriteError


def write_output(
    filename: str,
    hex_lines: List[str],
    entry: Tuple[int, int],
    exit_pt: Tuple[int, int],
    path: str,
) -> None:
    """Write the maze hex grid plus solution metadata to a UTF-8 text file.

    File layout (LF line endings):
        - One hex line per maze row.
        - A blank line.
        - entry as "x,y".
        - exit as "x,y".
        - The solved path as a direction string.

    Args:
        filename: Target file path. Overwrites if it already exists.
        hex_lines: One hex string per row of the maze.
        entry: Entry coordinate (x, y).
        exit_pt: Exit coordinate (x, y).
        path: Direction string from entry to exit (letters in "NESW").

    Raises:
        OutputWriteError: If the file cannot be opened or written.
    """
    try:
        with open(filename, 'w', encoding='utf-8', newline='\n') as f:
            i = 0
            while i < len(hex_lines):
                f.write(hex_lines[i] + '\n')
                i += 1
            f.write('\n')

            f.write(str(entry[0]) + "," + str(entry[1]) + "\n")
            f.write(str(exit_pt[0]) + "," + str(exit_pt[1]) + "\n")
            f.write(path + "\n")
    except IOError as e:
        raise OutputWriteError("An error occurs when writing to file:", str(e))
