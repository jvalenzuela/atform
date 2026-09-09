"""External reference management.

This module implements handling for external references, i.e., setup for
content passed to the add_test() references parameter.
"""

import collections

from . import error
from . import misc


# Stores a single category as defined by add_reference_category().
Category = collections.namedtuple(
    "Category",
    ["title", "persist"],
)


# Defined reference categories, keyed by label. Stored as an ordered
# dictionary because the order the categories are created defines
# the order they are listed in the output documents.
#
# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
categories: dict[str, Category] = collections.OrderedDict()


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_reference_category(title, label, *, persist=False):
    """Creates a topic for listing external references.

    This function does not create any actual references; they must be
    added to each test individually with the ``references`` argument of
    :py:func:`atform.add_test`. This function is only available in the setup
    area of the script before any tests or sections are created.

    .. seealso:: :ref:`ref`

    Args:
        title (str): The full name of the category that will be displayed
            on the test documents; must not be blank.
        label (str): A shorthand abbreviation to identify this category
            when adding references to individual tests. Must be unique across
            all reference categories, and may not be blank.
        persist (bool, optional): If False this category will only be
            shown on tests which provide one or more reference items.
            If True it will be listed on every test regardless of the number
            of items.
    """
    # Validate title.
    title_stripped = misc.nonempty_string("reference category title", title)

    # Validate label.
    label_stripped = misc.nonempty_string("reference category label", label)
    if label_stripped in categories:
        raise error.UserScriptError(
            f"Duplicate reference label: {label_stripped}",
            f"Create a unique label for {title} references.",
        )

    # Validate persist.
    if not isinstance(persist, bool):
        raise error.UserScriptError(
            f"Invalid persist type: {type(persist).__name__}",
            "persist may only be True or False.",
        )

    categories[label_stripped] = Category(title_stripped, persist)
