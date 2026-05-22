"""Read and validate a `key = value` config file into a typed dict."""

import os

from typing import Dict, Any

from mazegen.exceptions import (
    ConfigError,
    ConfigFileNotFoundError,
    InvalidParameterError,
)

MANDATORY_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
OPTIONAL_KEYS = {"SEED", "ALGORITHM"}
VALID_ALGORITHMS = {"prim"}


def parse_config(file_path: str) -> Dict[str, Any]:
    """Parse a `key = value` config file and return a validated, typed dict.

    Lines starting with `#` and blank lines are skipped. Keys are normalized
    to uppercase. ENTRY/EXIT are parsed as `x,y` integer tuples and bounds-
    checked against WIDTH/HEIGHT. SEED and ALGORITHM are optional; if missing
    they default to None and "prim". OUTPUT_FILE must be a relative path
    without `..` segments.

    Args:
        file_path: Path to the config file.

    Returns:
        Dict with keys: width, height, entry, exit, perfect, output_file,
        seed, algorithm.

    Raises:
        ConfigFileNotFoundError: If the file does not exist.
        ConfigError: On syntax errors or missing mandatory keys.
        InvalidParameterError: On out-of-range or malformed values.
    """
    if not os.path.exists(file_path):
        raise ConfigFileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    raw_config: Dict[str, str] = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if len(line) == 0 or line[0] == '#':
            i += 1
            continue

        eq_index = line.find('=')
        if eq_index == -1:
            raise ConfigError(
                "Line " + str(i + 1) + " has bad syntax: '=' missing."
            )

        key = line[0:eq_index].strip().upper()
        value = line[eq_index + 1:].strip()

        if len(key) == 0 or len(value) == 0:
            raise ConfigError(
                "Line " + str(i + 1) + ": Key or Value cannot be empty."
            )
        raw_config[key] = value
        i += 1

    for key in MANDATORY_KEYS:
        if key not in raw_config:
            raise ConfigError("Missing mandatory key: " + key)
    parsed_config: Dict[str, Any] = {}

    if not raw_config["WIDTH"].isdigit():
        raise InvalidParameterError("WIDTH must be a positive integer.")
    if not raw_config["HEIGHT"].isdigit():
        raise InvalidParameterError("HEIGHT must be a positive integer")

    width = int(raw_config["WIDTH"])
    height = int(raw_config["HEIGHT"])
    if width < 5 or width > 1000:
        raise InvalidParameterError("WIDTH out of range (5-1000).")
    if height < 5 or height > 1000:
        raise InvalidParameterError("HEIGHT out of range (5-1000).")

    parsed_config["width"] = width
    parsed_config["height"] = height
    entry_str = raw_config["ENTRY"]

    comma_index = entry_str.find(',')
    if comma_index == -1:
        raise InvalidParameterError("ENTRY must be in x,y format.")

    ex_str = entry_str[0:comma_index].strip()
    ey_str = entry_str[comma_index + 1:].strip()

    if not ex_str.isdigit() or not ey_str.isdigit():
        raise InvalidParameterError("ENTRY coordinates must be integers.")
    ex = int(ex_str)
    ey = int(ey_str)

    if ex < 0 or ex >= width or ey < 0 or ey >= height:
        raise InvalidParameterError("Coordinates must be in maze bounds.")
    parsed_config["entry"] = (ex, ey)
    exit_str = raw_config["EXIT"]
    comma_index = exit_str.find(',')
    if comma_index == -1:
        raise InvalidParameterError("EXIT must be in x, y format.")

    xx_str = exit_str[0:comma_index].strip()
    xy_str = exit_str[comma_index + 1:].strip()
    if not xx_str.isdigit() or not xy_str.isdigit():
        raise InvalidParameterError("EXIT coordinates must be integers.")
    xx = int(xx_str)
    xy = int(xy_str)
    if xx < 0 or xx >= width or xy < 0 or xy >= height:
        raise InvalidParameterError("EXIT is outside the maze bounds.")

    if ex == xx and ey == xy:
        raise InvalidParameterError("ENTRY and EXIT must be different.")
    parsed_config["exit"] = (xx, xy)
    perfect = raw_config["PERFECT"]
    if perfect == "True":
        parsed_config["perfect"] = True
    elif perfect == "False":
        parsed_config["perfect"] = False
    else:
        raise InvalidParameterError("PERFECT must be 'True' or 'False'.")

    out_file = raw_config["OUTPUT_FILE"]
    if ".." in out_file or (len(out_file) > 0 and out_file[0] == '/'):
        raise InvalidParameterError("OUPUT_FILE path is not allowed.")
    parsed_config["output_file"] = out_file
    if "SEED" in raw_config:
        if not raw_config["SEED"].isdigit():
            raise InvalidParameterError("SEED must be a positive integer.")
        parsed_config["seed"] = int(raw_config["SEED"])
    else:
        parsed_config["seed"] = None

    if "ALGORITHM" in raw_config:
        algorithm = raw_config["ALGORITHM"]
        if algorithm not in VALID_ALGORITHMS:
            raise InvalidParameterError("Unsupported ALGORITHM. Use 'prim'.")
        parsed_config["algorithm"] = algorithm
    else:
        parsed_config["algorithm"] = "prim"

    return parsed_config
