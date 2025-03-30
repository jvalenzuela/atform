"""Cache file management.

The cache file stores content between script runs. Operation consists of two
phases:

1. Cache file is loaded making data from the previous run available when
   generating output.

2. Data resulting from this run is collected and written to the cache file
   when output generation is complete.
"""

import pickle

from . import state
from . import version


# Cache file name.
FILENAME = "atform.cache"


# This alias of the open() builtin supports unit tests, allowing this
# attribute to be patched without affecting open() for other modules,
# e.g., establishing IPC for concurrent builds.
OPEN = open


def load():
    """Reads the cache file."""
    try:
        with OPEN(FILENAME, "rb") as f:
            data = pickle.load(f)

        # Only accept cache data from matching module versions.
        if data["version"] != version.VERSION:
            raise KeyError

    # The very broad set of exceptions is due to the fact that
    # unpickling can result in pretty much any exception.
    # Defaults to an empty data set if the cache file could not be loaded,
    # e.g., no cache file exists or is otherwise invalid.
    except Exception:  # pylint: disable=broad-exception-caught
        return {}

    return data


def save(data):
    """Writes the data from this run to the cache file."""
    data["version"] = version.VERSION
    data["tests"] = {t.id: t for t in state.tests}

    try:
        f = OPEN(FILENAME, "wb")
    except OSError as e:
        print(f"Error writing cache file: {e}")
    else:
        with f:
            pickle.dump(data, f)
