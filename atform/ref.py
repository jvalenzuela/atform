"""External reference management.

This module implements handling for external references, i.e., setup for
content passed to the Test.__init__() references parameter.
"""

from . import error
from . import id as id_
from . import misc
from . import state


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_reference_category(title: str, label: str) -> None:
    """Creates a topic for listing external references.

    This function does not create any actual references; they must be
    added to each test individually with the ``references`` argument of
    :py:class:`atform.Test`. This function is only available in the setup
    area of the script before any tests or sections are created.

    .. seealso:: :ref:`ref`

    Args:
        title (str): The full name of the category that will be displayed
            on the test documents; must not be blank.
        label (str): A shorthand abbreviation to identify this category
            when adding references to individual tests. Must be unique across
            all reference categories, and may not be blank.
    """
    # Validate title.
    title_stripped = misc.nonempty_string("reference category title", title)

    # Validate label.
    label_stripped = misc.nonempty_string("reference category label", label)
    if label_stripped in state.ref_titles:
        raise error.UserScriptError(
            f"Duplicate reference label: {label_stripped}",
            f"Create a unique label for {title} references.",
        )

    state.ref_titles[label_stripped] = title_stripped


def get_xref() -> dict[str, dict[str, list[str]]]:
    """Builds a cross-reference of tests assigned to each reference.

    For use in the output section of a script, after all tests have
    been defined.

    .. seealso:: :ref:`xref`

    Returns:
        dict: A cross-reference between tests and references represented as a
        nested dictionary. The top-level dictionary is keyed by category labels
        defined with :py:func:`atform.add_reference_category`; second-level
        dictionaries are keyed by references in that category, i.e., items
        passed to the ``references`` argument of :py:class:`atform.Test`.
        Final values of the inner dictionary are lists of test identifiers,
        formatted as strings, assigned to that reference. As an example,
        the keys yielding a list of all tests assigned ``"SF42"`` in the
        ``"sf"`` category would be ``["sf"]["SF42"]``.
    """
    # Initialize all categories with empty dictionaries, i.e., no references.
    xref = {label: {} for label in state.ref_titles}

    # Iterate through all Test instances to populate second-level
    # reference dictionaries and test lists.
    for tid in sorted(state.tests.keys()):
        test_id = id_.to_string(tid)
        for ref in state.tests[tid].references:
            for item in ref.items:
                xref[ref.label].setdefault(item, []).append(test_id)

    return xref
