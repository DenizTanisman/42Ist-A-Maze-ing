*This project has been created as part of the 42 curriculum by <itanisma>, <mualemda>.*

# A-Maze-ing

Random maze generator with a guaranteed shortest-path solver and a terminal
visualisation. Perfect mazes are produced by a randomized **Prim's algorithm**;
the shortest path between entry and exit is found with **breadth-first search
(BFS)**.

---

## Description

A-Maze-ing takes a plain-text configuration file, generates a maze of the
requested size, embeds a decorative **"42"** pattern in the centre when the
grid is large enough, and writes the result to a hex-encoded output file.
The same maze is rendered to the terminal with an interactive menu (regenerate,
show/hide the shortest path, cycle wall colours, quit).

The maze generator itself lives in a standalone, pip-installable package
(`mazegen`) so it can be reused in other projects without dragging the CLI
or the renderer along.

---

## Instructions

### Requirements

- Python **3.10+**
- `make`
- A POSIX shell (macOS or Linux)

### Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install the project in editable mode (plus dev tools)
make install
pip install pytest flake8 mypy
```

### Run

```bash
make run CONFIG=config.txt
```

This launches the interactive menu:

```
--- A-Maze-ing Menu ---
1. Re-generate a new maze
2. Show/Hide shortest path
3. Change maze wall colors (Cycle)
4. Quit
```

### Other Make targets

| Target | What it does |
|---|---|
| `make install` | `pip install -e .` |
| `make run CONFIG=path` | Run the program with the given config |
| `make debug CONFIG=path` | Run under `pdb` (Python debugger) |
| `make test` | Run the `pytest` suite |
| `make lint` | `flake8 .` + `mypy .` with the subject-mandated flags |
| `make lint-strict` | `flake8 .` + `mypy . --strict` |
| `make clean` | Remove caches and build artefacts |
| `make defense` | Run the local defense tester script |
| `make help` | List targets |

---

## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and ignored.

### Mandatory keys

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width in cells (5–1000) | `WIDTH=20` |
| `HEIGHT` | Maze height in cells (5–1000) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename (no `..` or absolute paths) | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True` for a perfect maze (single solution) | `PERFECT=True` |

### Optional keys

| Key | Description | Default |
|---|---|---|
| `SEED` | Positive integer for reproducible mazes | random |
| `ALGORITHM` | `prim` (only supported value) | `prim` |

### Example (`config.txt`)

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze_output.txt
PERFECT=True
ALGORITHM=prim
```

A working `config.txt` is shipped at the repository root.

---

## Output file format

Each cell is written as one **hexadecimal digit** encoding which of its 4 walls
are closed:

| Bit | Direction | Value |
|---|---|---|
| 0 (LSB) | North | 1 |
| 1 | East  | 2 |
| 2 | South | 4 |
| 3 | West  | 8 |

A set bit means the wall is **closed**. `F` (binary `1111`) is a fully walled
cell; `3` (binary `0011`) is open to south and west.

Cells are stored row by row, one row per line. After an empty line, three more
lines follow: entry coordinates, exit coordinates, and the shortest path string
made of `N`/`E`/`S`/`W` letters. All lines end with `\n`.

---

## Algorithm

### Generation — Randomized Prim's Algorithm

Starting from a single random cell, we maintain a frontier of walls touching the
already-carved region. At each step we pop a random frontier wall: if it
separates a carved cell from an uncarved cell, we open it and add the new
cell's walls to the frontier. We stop when every cell is reachable.

### Why Prim?

- **Perfect by construction.** Prim produces a spanning tree of the grid graph,
  which is exactly the definition of a perfect maze (one and only one path
  between any two cells).
- **Branchy aesthetic.** Compared to the recursive backtracker (which produces
  long winding corridors), Prim's randomized variant yields short, frequently
  branching corridors — visually more "maze-like".
- **Plays nicely with locked cells.** The "42" pattern is placed by marking
  18 central cells as `unbreakable` *before* generation. Prim simply skips
  walls adjacent to locked cells, so the pattern is carved around naturally
  without any post-processing.
- **Reproducible.** A single `random.Random(seed)` instance drives every
  random choice, so `(width, height, seed)` uniquely determines the output.

### Solver — Breadth-First Search (BFS)

BFS from the entry expands cells layer by layer; the first time it reaches the
exit, the parent pointers describe a **provably shortest** path in unweighted
terms (every step has cost 1). The path is then walked from exit back to entry
and converted into a `N`/`E`/`S`/`W` direction string.

---

## Reusable module — `mazegen`

The generator lives in its own package, shipped as
`mazegen-1.0.0-py3-none-any.whl` (and `.tar.gz`) at the repository root. It is
self-contained and has no runtime dependencies beyond the Python standard
library.

### Install from the wheel

```bash
pip install ./mazegen-1.0.0-py3-none-any.whl
```

### Quick start

```python
from mazegen import MazeGenerator, MazeSolver

# Generate a 20x20 maze with the "42" pattern embedded
gen = MazeGenerator(20, 20, seed=42, add_42=True)
gen.generate()

# Get the maze as a list of hex strings (one per row)
for line in gen.to_hex_lines():
    print(line)

# Solve from top-left to bottom-right
solver = MazeSolver(gen.get_grid())
path = solver.solve((0, 0), (19, 19))
print(path)            # e.g. "EESSESE..."
print(len(path))       # shortest-path length in steps
```

### Public API

| Symbol | Purpose |
|---|---|
| `MazeGenerator(width, height, seed=None, algorithm="prim", add_42=True)` | Build a maze |
| `MazeGenerator.generate()` | Run the chosen algorithm (call once) |
| `MazeGenerator.get_grid()` | Return the generated `Grid` |
| `MazeGenerator.to_hex_lines()` | Return the maze as a list of hex strings |
| `MazeSolver(grid)` | BFS solver |
| `MazeSolver.solve(entry, exit)` | Return the shortest-path direction string |
| `MazeSolver.get_path_cells()` | Return the list of cells on the last solved path |
| `Grid`, `Cell` | Underlying data structures |
| `AMazeError` (+ subclasses) | All package errors derive from this — single `except` clause is enough at top level |

### Reproducibility

```python
a = MazeGenerator(10, 10, seed=7); a.generate()
b = MazeGenerator(10, 10, seed=7); b.generate()
assert a.to_hex_lines() == b.to_hex_lines()
```

### Rebuilding the wheel from source

```bash
pip install build
python -m build
# wheel and sdist appear in dist/
```

---

## Team and project management

### Roles

| Member | Role | Scope |
|---|---|---|
| **<itanisma>** | Algorithm Engineer | `mazegen` package — `Cell`, `Grid`, generator, solver, patterns, packaging |
| **<mualemda>** | Systems & Interaction Engineer | Config parser, output writer, terminal renderer, interaction handler, CLI entry point |

### Planning

We allocated **9 days** with a clear split between independent work and a
shared integration day:

- **Days 1–5** — Parallel tracks. Algorithm engineer built the data model,
  generator, solver, and 42 pattern; interaction engineer built the config
  parser, output writer, renderer, and menu loop against mock generators.
- **Day 6 — Integration.** Mocks were removed and the real `mazegen` package
  was wired into the CLI. This day surfaced the real layout issue (initial
  `io_handlers/` and `visual/` were not inside the `mazegen` package) and we
  refactored them under `mazegen/io_handlers/` and `mazegen/visual/` so the
  whole runtime imports cleanly from one package root.
- **Days 7–8** — Buffer, lint pass, README, defense rehearsal.
- **Day 9** — Evaluation.

### What evolved

- The `Re-generate` menu option originally called `generator.generate()` again
  on the same instance — which the generator (correctly) rejects after the
  first call. We moved generator construction into the `InteractionHandler`
  so each "regenerate" gets a fresh instance instead.
- The output renderer originally read `grid.entry` and `grid.exit` even though
  the `Grid` class never set them. We now set those attributes on the grid in
  `InteractionHandler.make_generator()` from the parsed config.
- Solver wiring was a no-op at first (`generator = None` in main). Once the
  package import paths were corrected, the menu's *Show/Hide path* option
  was wired through `MazeSolver` and started painting the shortest path on
  the rendered grid.

### What worked well

- **Mock-first development** let the two tracks ship in parallel; integration
  day was structural, not algorithmic.
- **A single exception hierarchy (`AMazeError`)** kept the CLI's error
  handling to one `except` clause and produced consistent user messages.
- **Reproducible seeds** made test failures deterministic — every generator
  test pins a seed and asserts on the exact maze.

### What could improve

- The first integration day was Day 6 — too late. Earlier mini-integrations
  would have caught the package layout issue before any production code was
  written against the wrong import path.
- The renderer mutates cells (`cell.is_on_path = True`) instead of receiving
  the path as a side channel. This couples solver output to grid state and
  makes it awkward to render two paths side-by-side.

### Tools used

- **Python 3.10+**, `venv` for isolation
- **pytest** — 51 unit tests covering grid, generator, solver, and pattern
  placement edge cases
- **flake8** + **mypy** — lint + static typing, enforced via `make lint`
- **setuptools / build** — wheel + sdist packaging from `pyproject.toml`
- **Make** — task automation; subject-mandated targets
- **Git + GitHub Pull Requests** — every feature on its own branch, merged
  via PR after a peer read

---

## Resources

### Algorithm references

- *Maze generation algorithm — Wikipedia.* <https://en.wikipedia.org/wiki/Maze_generation_algorithm>
- *Prim's algorithm — Wikipedia.* <https://en.wikipedia.org/wiki/Prim%27s_algorithm>
- *Breadth-first search — Wikipedia.* <https://en.wikipedia.org/wiki/Breadth-first_search>
- Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf) — chapters on
  Prim's randomized variant and on rendering grid-based mazes in ASCII.
- *Spanning tree — Wikipedia.* <https://en.wikipedia.org/wiki/Spanning_tree>
  (explains why a perfect maze is exactly a spanning tree of the grid graph).

### Packaging references

- *Packaging Python Projects — Python Packaging User Guide.*
  <https://packaging.python.org/en/latest/tutorials/packaging-projects/>
- `pyproject.toml` reference — PEP 621.

### AI usage

Per the subject's transparency requirement, AI assistance was used as follows:

- **Test scaffolding.** Initial `pytest` harness and edge-case lists were
  drafted with AI assistance, then the team wrote the actual assertions and
  reviewed every test by hand.
- **Boilerplate refactor.** When `io_handlers/` and `visual/` were moved
  under `mazegen/`, the mechanical PEP8 cleanup (trailing whitespace,
  inline-comment style, line length) was done with AI help — no algorithmic
  code changed.
- **README structure.** This README's outline was sketched with AI assistance
  against the subject's Chapter VII requirements; section contents were
  written and verified by the team.
- **Pair-programming style code review.** AI was used to spot-check small
  changes (typing, naming, missing exception cases). All accepted suggestions
  were re-read and tested locally before commit.

Core algorithmic code (Prim generator, BFS solver, 42-pattern placement) was
written by the algorithm engineer; AI was not used to author those.
