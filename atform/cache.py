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


# Current data, initially loaded from the cache file, and updated with
# content during the build process.
#
# Pylint invalid-name is disabled because this is not a constant.
data = None  # pylint: disable=invalid-name


def load():
    """Reads the cache file."""
    global data  # pylint: disable=global-statement
    try:
        with OPEN(FILENAME, "rb") as f:
            from_file = pickle.load(f)

        # Only accept cache data from matching module versions.
        if from_file["version"] != version.VERSION:
            raise KeyError

    # The very broad set of exceptions is due to the fact that
    # unpickling can result in pretty much any exception.
    # Defaults to an empty data set if the cache file could not be loaded,
    # e.g., no cache file exists or is otherwise invalid.
    except Exception:  # pylint: disable=broad-exception-caught
        from_file = {}

    data = from_file


def save():
    """Writes the data from this run to the cache file."""
    data["version"] = version.VERSION
    data["tests"] = state.tests

    try:
        f = OPEN(FILENAME, "wb")
    except OSError as e:
        print(f"Error writing cache file: {e}")
    else:
        with f:
            pickle.dump(data, f)
