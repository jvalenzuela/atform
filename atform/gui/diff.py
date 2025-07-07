"""
This module implements comparing the current test content with content from
the cache to identify altered, new, and unmodified tests.
"""

from .. import cache
from .. import state


# Comparison result test ID sets; created by load().
CHANGED = None  # Modified tests.
NEW = None  # Newly created tests.
SAME = None  # Unmodified tests.


def load():
    """Compares content with the cache, generating the result sets."""
    global CHANGED  # pylint: disable=global-statement
    global NEW  # pylint: disable=global-statement
    global SAME  # pylint: disable=global-statement

    try:
        orig = cache.data["tests"]

    # No cache data containing previous test content; diff unavailable.
    except KeyError:
        return False

    CHANGED = changed_tests(orig)
    NEW = new_tests(orig)
    SAME = same_tests()

    return True


def changed_tests(orig):
    """Identifies tests modified since the cached version."""
    changed = set()

    for tid, current_test in state.tests.items():
        try:
            if current_test != orig[tid]:
                changed.add(tid)

        # Ignore tests not in the cache, i.e., newly created tests.
        except KeyError:
            pass

    return frozenset(changed)


def new_tests(orig):
    """Identifies tests added since the cached version."""
    new = set(state.tests.keys())
    new.difference_update(orig.keys())
    return frozenset(new)


def same_tests():
    """Identifies tests unchanged since the cached version."""
    ids = set(state.tests.keys())
    ids.difference_update(CHANGED)
    ids.difference_update(NEW)
    return frozenset(ids)
