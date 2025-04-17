"""User script error handling.

Nothing in this module is exported to the public API because script errors
are not intended to be caught with try/except blocks, but rather simply
exit with a message describing the problem. Furthermore, this implementation is
intended to generate a simplified message, as opposed to the normal
stack trace which is unnecessary and possibly confusing for users new
to programming or Python.
"""

import collections
import functools
import textwrap
import traceback
import sys


# Container holding information pointing to the location of the most recent API
# function call. Intended as a pickle-able container for specific
# traceback.FrameSummary attributes because FrameSummary objects themselves cannot be
# pickled.
CallFrame = collections.namedtuple("CallFrame", ["filename", "lineno"])


# Call frame of the current API being called.
# Pylint invalid-name is disabled because this is not a constant.
api_call_frame = None  # pylint: disable=invalid-name


def set_call_frame(frame):
    """Updates the current call frame."""
    global api_call_frame  # pylint: disable=global-statement
    api_call_frame = CallFrame(frame.filename, frame.lineno)


def exit_on_script_error(api):
    """Decorator to exit upon catching a ScriptError.

    This must only be applied to public API functions to ensure all context
    is added to the original exception. When stacked with other decorators
    it must be outermost, i.e., listed first.
    """

    @functools.wraps(api)
    def wrapper(*args, **kwargs):
        # Capture the location where this API was called from the
        # user script. The normal exception traceback is not used
        # because it is difficult to determine which frame represents
        # the departure from the user script, whereas it is always
        # in the same location in a traceback relative to this wrapper
        # function.
        set_call_frame(traceback.extract_stack(limit=2)[0])

        try:
            result = api(*args, **kwargs)

        except UserScriptError as e:
            # Use the frame from this call if the exception does not
            # provide one.
            if not e.call_frame:
                e.call_frame = api_call_frame
                e.api = api

            raise

        return result

    return wrapper


class UserScriptError(Exception):
    """Raised when a problem was encountered in a user script.

    Implements storing key:value fields to help describe the context of
    the error, which can be added as the exception propagates up.
    """

    # String separating keys and values in the formatted presentation string.
    FIELD_SEP = ": "

    # These fields may contain lengthy strings, and are therefore line wrapped
    # in the string output.
    MULTILINE_FIELDS = set(
        [
            "Description",
            "Remedy",
        ]
    )

    def __init__(
        self,
        desc,
        remedy=None,
    ):
        self.fields = collections.OrderedDict()
        if remedy:
            self.fields["Remedy"] = remedy
        self.fields["Description"] = desc
        self.call_frame = None
        self.api = None

    def add_field(self, key, value):
        """Appends an item describing the context of the error."""
        self.fields[key] = value

    def __str__(self):
        """Formats all fields into a simple key: value table."""
        if self.api:
            self.fields["In Call To"] = f"atform.{self.api.__name__}"

        self.fields["Line Number"] = self.call_frame.lineno
        self.fields["File"] = self.call_frame.filename

        # Compute the indentation required to right-align all field names.
        indent = max(len(s) for s in self.fields.keys())

        lines = []

        # Fields are added from most specific to most general as the
        # exception propagates up from its origin, so they are listed here
        # in reverse order to render top to bottom in increasing specificity.
        for field in reversed(self.fields):
            value = str(self.fields[field])

            # Wrap multiline fields.
            if field in self.MULTILINE_FIELDS:
                collapsed = " ".join(value.split())  # Collapse whitespace.
                line = textwrap.fill(
                    self.FIELD_SEP.join((field, collapsed)),
                    # Indent first line so the field name is right-aligned
                    # with other field names.
                    initial_indent=" " * (indent - len(field)),
                    # Remaining lines are indented to align with other
                    # field values.
                    subsequent_indent=" " * (indent + len(self.FIELD_SEP)),
                )

            # Single line field.
            else:
                line = self.FIELD_SEP.join((field.rjust(indent), value))

            lines.append(line)

        # Add API docstring.
        if self.api:
            lines.append("")
            lines.append(f"atform.{self.api.__name__} help: {self.api.__doc__}")

        return "\n".join(lines)


def handle_user_script_error(exc_type, exc_value, _traceback):
    """Handler for UserScriptError exceptions."""
    # Handle only UserScriptErrors; all other exceptions are passed unaltered.
    if exc_type is not UserScriptError:
        raise exc_value

    sys.exit(f"The following error was encountered:\n\n{exc_value}")


sys.excepthook = handle_user_script_error
