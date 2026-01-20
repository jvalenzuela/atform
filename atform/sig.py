"""Approval sigature API."""

from . import error
from . import misc
from . import state


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_signature(title: str) -> None:
    """Adds an approval signature line.

    The signature entry contains title, name, signature, and date
    fields that will appear at the conclusion of every test. Signatures
    will be presented in the order they are defined.

    .. seealso:: :ref:`setup`

    Args:
        title (str): A short description of the person signing; may not
            be blank.
    """
    state.signatures.append(misc.nonempty_string("signature title", title))
