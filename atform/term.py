"""

"""

import dataclasses

from . import error
from . import format as format_
from . import label as label_
from . import misc
from . import state


@dataclasses.dataclass
class Term:
    """ """
    text: str

    # ID tuples of tests supporting this term.
    supporting_tests: set = dataclasses.field(init=False, default_factory=set)

    def __str__(self):
        return self.text


def gen_repl_text(text, typeface, font):
    """Computes the string that will replace the label."""
    if not isinstance(text, str):
        raise error.UserScriptError(
            f"Invalid text type: {type(text).__name__}",
            "Term text must be a string.",
        )

    if (typeface is not None) or (font is not None):
        # Supply default formatting parameters.
        if typeface is None:
            typeface = "normal"
        if font is None:
            font = "normal"

        format_.validate(typeface, font)
        return format_.format_text(text, typeface=typeface, font=font)

    # Use the original string if no formatting arguments were given.
    return text


def add_supporting_test(tid, term_labels):
    """Defines a test as supporting a given set of terms."""
    if not isinstance(term_labels, list):
        raise error.UserScriptError(
            f"Invalid terms type: {type(term_labels).__name__}",
            """
            The terms argument must be a list of labels assigned
            with the atform.add_term() function.
            """
        )
    for lbl in term_labels:
        try:
            supporting_tests = state.labels[lbl].supporting_tests

        except (AttributeError, KeyError):
            raise error.UserScriptError(
                f'Unknown term label: "{lbl}"',
                """
                Each item in the terms argument must be a label defined
                with the atform.add_term() function.
                """
            )

        if tid in supporting_tests:
            raise error.UserScriptError(
                f"Duplicate term label: {lbl}",
                """
                Each label in the terms argument may only be listed once.
                """
            )

        supporting_tests.add(tid)


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_term(text, label, *, typeface=None, font=None):
    """Defines a new term to be used within test content.

    The appearance of the term in the output documents may optionally be
    formatted with the ``typeface``, ``font``, or ``fmt_func`` arguments.

    .. seealso:: :ref:`term`

    Args:
        text (str): The term's literal text.
        label (str): An identifier to be used in content strings that will
            be replaced with the term's text. Must not be blank.
        typeface (str, optional): Equivalent to the
            :py:func:`atform.format_text` argument of the same name. May not
            be used in combination with the ``fmt_func`` argument.
        font (str, optional): Equivalent to the
            :py:func:`atform.format_text` argument of the same name. May not
            be used in combination with the ``fmt_func`` argument.
    """
    repl_text = gen_repl_text(text, typeface, font)
    trm = Term(repl_text)
    label_.add(label, trm)
