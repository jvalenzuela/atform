"""Miscellaneous metadata output functions."""

import collections

from . import addtest
from . import error
from . import id as id_
from . import term


def format_term_xref(xref):
    """
    Converts a cross-reference of internal term data into a formatted
    dictionary to be returned by get_terms().
    """
    formatted = collections.OrderedDict()

    for lbl, ids in sorted(xref.items(), key=lambda i: term.terms[i[0]].raw):
        # Omit terms with no associated tests.
        if not ids:
            continue

        # Keys are converted from label to the original raw term text.
        key = term.terms[lbl].raw

        # Values are converted from a set of test IDs to a sorted list
        # of full names(ID + title).
        tests = [addtest.tests[tid].full_name for tid in sorted(ids)]

        formatted[key] = tests

    return formatted


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


@error.exit_on_script_error
def get_terms(which="both"):
    """Builds a cross-reference of terms to tests.

    The function must only be called after :py:func:`atform.generate`,
    and be subject to the same ``if __name__ == "__main__":`` condition.

    .. seealso:: :ref:`term`

    Args:
        which (str, optional): Filters the returned terms based on how they
            are referenced. ``"support"`` selects only terms supported
            by tests as defined by the ``supports_terms`` argument of
            :py:func:`atform.add_test`; ``"use"`` selects terms appearing
            in test content. The default value, ``"both"``, exports the
            combination of ``"support"`` and ``"use"``.

    Returns:
        dict: A cross-reference keyed by literal term text as defined
        by the ``text`` argument of :py:func:`atform.add_term`.
        Values are lists of tests in numerical order, each represented
        as a string containing the test's ID and title. The returned
        dictionary is ordered such that iterating over its keys will yield
        terms in alphabetical order.
    """
    refs = {
        "support": term.supporting_tests,
        "use": term.used_terms,
    }
    refs["both"] = {
        lbl: term.supporting_tests[lbl].union(term.used_terms[lbl])
        for lbl in term.terms
    }

    try:
        terms = refs[which]
    except (KeyError, TypeError) as e:
        raise error.UserScriptError(
            f"Invalid which value: {which}",
            remedy="""
            Allowable values for the which parameter are "support", "use",
            or "both".
            """,
        ) from e

    return format_term_xref(terms)
