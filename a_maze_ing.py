import sys

from mazegen.io_handlers.config_parser import parse_config
from mazegen.visual.terminal import TerminalRenderer
from mazegen.visual.interaction import InteractionHandler
from mazegen.exceptions import AMazeError


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config_data = parse_config(config_path)

        renderer = TerminalRenderer()

        handler = InteractionHandler(None, renderer, config_data)
        handler.start()

    except AMazeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
