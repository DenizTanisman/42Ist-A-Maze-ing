"""
InteractionHandler:
Driver that wires config, generator, solver, and renderer for the CLI.
"""

from typing import Any

from mazegen.generator import MazeGenerator
from mazegen.io_handlers.output_writer import write_output
from mazegen.solver import MazeSolver


class InteractionHandler:
    """Run the interactive A-Maze-ing menu loop.

    Holds the parsed config and a TerminalRenderer, and lazily creates a
    MazeGenerator on each (re)generation. Each menu cycle generates a maze,
    solves it, writes the hex output, and renders it; subsequent choices
    toggle the path overlay, cycle wall colors, or quit.
    """

    def __init__(
        self,
        generator: Any,
        renderer: Any,
        config: dict[str, Any],
    ) -> None:
        """Store the renderer and parsed config; generator is built lazily.

        Args:
            generator: Unused at construction; reassigned in make_generator().
            renderer: A TerminalRenderer used to print every maze state.
            config: Dict returned by parse_config().
        """
        self.generator = generator
        self.renderer = renderer
        self.config = config

    def make_generator(self) -> MazeGenerator:
        """Build a fresh MazeGenerator and attach entry/exit."""
        gen = MazeGenerator(
            width=self.config["width"],
            height=self.config["height"],
            seed=self.config["seed"],
            algorithm=self.config["algorithm"],
        )
        gen.grid.entry = self.config["entry"]
        gen.grid.exit = self.config["exit"]
        return gen

    def generate_and_render(self) -> None:
        """Generate, solve, write the output file, then render to stdout.

        Each call replaces self.generator with a new instance — MazeGenerator
        cannot be called twice on the same object.
        """
        self.generator = self.make_generator()
        self.generator.generate()
        grid = self.generator.get_grid()
        solver = MazeSolver(grid)
        path = solver.solve(self.config["entry"], self.config["exit"])
        for cell in solver.get_path_cells():
            cell.is_on_path = True
        write_output(
            self.config["output_file"],
            self.generator.to_hex_lines(),
            self.config["entry"],
            self.config["exit"],
            path,
        )
        self.renderer.render(grid)

    def start(self) -> None:
        """Run menu loop: regenerate, toggle path, cycle colors, quit."""
        print("Generating maze...\n")
        self.generate_and_render()

        while True:
            print("\n--- A-Maze-ing Menu ---")
            print("1. Re-generate a new maze")
            print("2. Show/Hide shortest path")
            print("3. Change maze wall colors (Cycle)")
            print("4. Quit")

            choice = input("\nChoice? (1-4): ").strip()

            if choice == "1":
                print("Generating new maze...\n")
                self.generate_and_render()

            elif choice == "2":
                self.renderer.toggle_path()
                self.renderer.render(self.generator.get_grid())

            elif choice == "3":
                print("Rotating colors...\n")
                self.renderer.cycle_colors()
                self.renderer.render(self.generator.get_grid())

            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid choice, please try again.")
