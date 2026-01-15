"""Miscellaneous metadata output functions."""

from . import addtest
from . import id as id_


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
    ids = sorted(addtest.tests.keys())
    return [(id_.to_string(tid), addtest.tests[tid].title) for tid in ids]
