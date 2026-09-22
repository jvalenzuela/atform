"""Approval signature API."""

import collections

from . import error
from . import misc
from . import state


# Storage object for each defined signature.
Signature = collections.namedtuple(
    "Signature",
    ["title", "initials"],
)


# Signature entries in the order they were defined.
#
# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
signatures: list[Signature] = []


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_signature(title, initials=True):
    """Adds an approval signature line.

    The signature entry contains title, name, signature, optional initials,
    and date fields that will appear at the conclusion of every test.
    Signatures will be presented in the order they are defined.

    .. seealso:: :ref:`setup`

    Args:
        title (str): A short description of the person signing; may not
            be blank.
        initials (bool, optional): If True the signature entry will include
            a field for initials, otherwise the initials field will be omitted.
    """
    if not isinstance(initials, bool):
        raise error.UserScriptError(
            f"Invalid initials data type: {type(initials).__name__}",
            "The initials option may only be True or False.",
        )
    sig = Signature(misc.nonempty_string("signature title", title), initials)
    signatures.append(sig)


@error.exit_on_script_error
@misc.setup_only
def set_signature_name_plain():
    """Globally disables interactive text entry for the signature name.

    The name field will instead be rendered as a blank area. May only be
    called once in the setup area.
    """
    if state.sig_name_plain:
        raise error.UserScriptError(
            "Duplicate function call.",
            """
            This function can only be called once to disable interactive
            forms for the signature name field; remove one of the calls to
            this function.
            """,
        )
    state.sig_name_plain = True
