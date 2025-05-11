"""Miscellaneous metadata output functions."""

from . import id as id_
from . import state


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


def list_tests():
    """Lists all defined tests.

    Intended to be called in the Output section, after all calls to
    :py:func:`atform.add_test`, and before or after :py:func:`atform.generate`.
    The returned list is unaffected by command line options limiting
    generated PDF files.

    Returns:
        list[tuple]: A list of ``(id, title)`` tuples in ascending order.
    """
    ids = sorted(state.tests.keys())
    return [(id_.to_string(tid), state.tests[tid].title) for tid in ids]
