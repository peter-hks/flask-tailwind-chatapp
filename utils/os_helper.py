"""os_helper.py"""

import pathlib


def get_most_recent_file(directory: str, pattern: str = "*") -> str:
    """Get the most recent file in a directory.

    Args:
        - `directory (str)`: The directory to search.\n
        - `pattern (str)`: The pattern to search for. Defaults to `*`.\n
    Returns:
        - `str`: The most recent file in the directory.
    """
    list_of_paths = pathlib.Path(directory).glob(pattern)
    latest_path = max(list_of_paths, key=lambda p: p.stat().st_ctime)
    return str(latest_path.absolute())
