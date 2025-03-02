"""Cache file management.

The cache file stores certain parameters resulting from output generation that
can be used to accelerate future runs. Operation consists of two phases:

1. Cache file is loaded making data from the previous run available when
   generating output.

2. Data resulting from this run is collected and written to the cache file
   when output generation is complete, overwriting all previous data.
"""

import pickle

from . import version


# Cache file name.
FILENAME = "atform.cache"


# This alias of the open() builtin supports unit tests, allowing this
# attribute to be patched without affecting open() for other modules,
# e.g., establishing IPC for concurrent builds.
OPEN = open


def default_data():
    """Generates an empty cache data set."""
    return {
        "tests": {},  # Data specific to tests; keyed by test ID tuple.
    }


def load():
    """Reads the cache file.

    Defaults to an empty data set if the cache file could not be loaded, e.g.,
    no cache file exists or is otherwise invalid.
    """
    try:
        with OPEN(FILENAME, "rb") as f:
            data = pickle.load(f)

        # Only accept cache data from matching module versions.
        if data["version"] != version.VERSION:
            raise KeyError

    # The very broad set of exceptions is due to the fact that
    # unpickling can result in pretty much any exception.
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    else:
        global last_data  # pylint: disable=global-statement
        last_data = data


def save():
    """Writes the data from this run to the cache file."""
    # Include module version information.
    new_data["version"] = version.VERSION

    try:
        f = OPEN(FILENAME, "wb")
    except OSError as e:
        print(f"Error writing cache file: {e}")
    else:
        with f:
            pickle.dump(new_data, f)


def get_test_data(tid):
    """Retrieves cached data from the previous run for a given test."""
    try:
        data = last_data["tests"][tid]
    except KeyError:
        data = None
    return data


def set_test_data(tid, data):
    """Stores data to be cached for a given test."""
    new_data["tests"][tid] = data


# Data from a previous run loaded from the cache file by load().
last_data = default_data()


# Data resulting from this run, which will be written to the cache file.
new_data = default_data()
