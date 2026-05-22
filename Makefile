# A-Maze-ing Makefile
# Usage: make <target>
# Targets: install, run, debug, test, lint, lint-strict, clean, defense, help

PYTHON  := python3
PIP     := $(PYTHON) -m pip
ENTRY   := a_maze_ing.py
CONFIG  ?= config.txt

MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports \
              --disallow-untyped-defs --check-untyped-defs

.PHONY: help install run debug test lint lint-strict clean defense all

help:
	@echo "A-Maze-ing make targets:"
	@echo "  make install                       - pip install -e ."
	@echo "  make run                           - Run the program"
	@echo "  make debug                         - Run under pdb"
	@echo "  make test                          - pytest"
	@echo "  make lint                          - flake8 + mypy (subject flags)"
	@echo "  make lint-strict                   - flake8 + mypy --strict"
	@echo "  make defense                       - ./defense_tester.sh ."
	@echo "  make clean                         - Remove caches and build artefacts"

install:
	$(PIP) install -e ".[dev]"

run:
	$(PYTHON) $(ENTRY) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(ENTRY) $(CONFIG)

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

defense:
	./defense_tester.sh .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf build dist *.egg-info mazegen.egg-info

all: lint test
