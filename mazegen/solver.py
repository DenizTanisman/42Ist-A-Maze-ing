"""MazeSolver — shortest-path search over a generated grid using BFS."""

from mazegen.core.grid import Grid
from mazegen.core.cell import Cell
from mazegen.core.directions import STEP_TO_DIR
from mazegen.exceptions import NoPathError
from collections import deque


class MazeSolver:
    """Solve a maze with breadth-first search, returning the shortest path."""
    def __init__(self, grid: Grid) -> None:
        """Initialize the solver with the grid to search.

        Args:
            grid: The maze grid to solve. Must already be generated.
        """
        self.grid = grid
        self.path_cells: list[Cell] = []

    def solve(self, entry: tuple[int, int], exit: tuple[int, int]) -> str:
        """Return the shortest path from entry to exit as a direction string.

        Args:
            entry: The (x, y) coordinate to start from.
            exit: The (x, y) coordinate to reach.

        Returns:
            A string of direction letters ("N", "E", "S", "W"), one per step.
        """
        visited: set[tuple[int, int]] = {entry}
        queue: deque[tuple[int, int]] = deque([entry])
        parent: dict[tuple[int, int], tuple[int, int]] = {}
        self.bfs(exit, visited, queue, parent)

        if exit not in parent and exit != entry:
            raise NoPathError(f"no path from {entry} to {exit}")

        return self.reconstruct_path(entry, exit, parent)

    def bfs(
        self,
        exit: tuple[int, int],
        visited: set[tuple[int, int]],
        queue: deque[tuple[int, int]],
        parent: dict[tuple[int, int], tuple[int, int]],
    ) -> None:
        """Run breadth-first search; stop early if exit is popped.

        Mutates `visited`, `queue`, and `parent` in place. After this call,
        `parent` describes the BFS search tree from the seeded entry.
        """
        while queue:
            current = queue.popleft()
            if current == exit:
                break
            cur_x, cur_y = current
            cell = self.grid.get(cur_x, cur_y)
            for direc, neigh_cell in self.grid.neighbors(cur_x, cur_y).items():
                if not cell.has_wall(direc):
                    neighbour = (neigh_cell.x, neigh_cell.y)
                    if neighbour not in visited:
                        visited.add(neighbour)
                        parent[neighbour] = current
                        queue.append(neighbour)

    def reconstruct_path(
        self,
        entry: tuple[int, int],
        exit: tuple[int, int],
        parent: dict[tuple[int, int], tuple[int, int]],
    ) -> str:
        """Walk parent from exit to entry.

        Fills self.path_cells and returns the direction string.
        """
        path: list[tuple[int, int]] = [exit]
        node = exit
        while node != entry:
            node = parent[node]
            path.append(node)
        path.reverse()

        self.path_cells = []
        for x, y in path:
            self.path_cells.append(self.grid.get(x, y))

        result: str = ""
        for i in range(len(path) - 1):
            x0, y0 = path[i]
            x1, y1 = path[i + 1]
            dx = x1 - x0
            dy = y1 - y0
            result += STEP_TO_DIR[(dx, dy)]
        return result

    def get_path_cells(self) -> list[Cell]:
        """Return the cells on the most recently solved path."""
        return self.path_cells
