"""
This module implements comparing the current test content with content from
the cache to identify altered, new, and unmodified tests.
"""

import collections
from typing import Iterable, Optional

from ..addtest import TestContent
from .. import cache
from ..id import IdType
from .. import state


CompareResult = collections.namedtuple(
    "CompareResult",
    [
        "changed",  # Modified tests.
        "new",  # Newly created tests.
        "same",  # Unmodified tests.
    ],
)


def load() -> bool:
    """Compares content with the cache, generating the result sets."""
    try:
        orig = cache.data["tests"]

    # No cache data containing previous test content; diff unavailable.
    except KeyError:
        return None

    changed = changed_tests(orig)
    new = new_tests(orig)
    same = same_tests(changed, new)

    return CompareResult(changed=changed, new=new, same=same)


def changed_tests(orig: dict[IdType, TestContent]) -> frozenset[IdType]:
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


def new_tests(orig: dict[IdType, TestContent]) -> frozenset[IdType]:
    """Identifies tests added since the cached version."""
    new = set(state.tests.keys())
    new.difference_update(orig.keys())
    return frozenset(new)


def same_tests(changed: Iterable[IdType], new: Iterable[IdType]) -> frozenset[IdType]:
    """Identifies tests unchanged since the cached version."""
    ids = set(state.tests.keys())
    ids.difference_update(changed)
    ids.difference_update(new)
    return frozenset(ids)
