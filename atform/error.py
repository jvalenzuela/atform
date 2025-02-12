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


# Setting to true will revert to normal Python exception handling,
# generating a complete traceback.
DEBUG = False


# Call frame of the current API being called.
# Pylint invalid-name is disabled because this is not a constant.
api_call_frame = None # pylint: disable=invalid-name


def exit_on_script_error(api):
    """Decorator to exit upon catching a ScriptError.

    This must only be applied to public API objects to ensure all context
    is added to the original exception. When stacked with other decorators
    it must be outermost, i.e., listed first.
    """
    @functools.wraps(api)
    def wrapper(*args, **kwargs):
        global api_call_frame # pylint: disable=global-statement

        # Capture the location where this API was called from the
        # user script. The normal exception traceback is not used
        # because it is difficult to determine which frame represents
        # the departure from the user script, whereas it is always
        # in the same location in a traceback relative to this wrapper
        # function.
        api_call_frame = traceback.extract_stack(limit=2)[0]

        try:
            result = api(*args, **kwargs)

        except UserScriptError as e:
            try:
                e.call_frame

            # Use the frame from this call if the exception does not
            # provide one.
            except AttributeError:
                e.call_frame = api_call_frame
                e.api = api

            if DEBUG:
                raise

            # Translate the original exception to SystemExit, which doesn't
            # print the stack trace.
            raise SystemExit(e) from e

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
    MULTILINE_FIELDS = set([
        "Description",
        "Remedy",
    ])

    def __init__(self, desc, remedy=None,):
        self.fields = collections.OrderedDict()
        if remedy:
            self.fields["Remedy"] = remedy
        self.fields["Description"] = desc

    def add_field(self, key, value):
        """Appends an item describing the context of the error."""
        self.fields[key] = value

    def __str__(self):
        """Formats all fields into a simple key: value table."""

        has_api = hasattr(self, "api")

        if has_api:
            self.fields["In Call To"] = f"atform.{self.api.__name__}"

        self.fields["Line Number"] = self.call_frame.lineno
        self.fields["File"] = self.call_frame.filename

        # Compute the indentation required to right-align all field names.
        indent = max(len(s) for s in self.fields.keys())

        lines = ["The following error was encountered:"]
        lines.append("")

        # Fields are added from most specific to most general as the
        # exception propagates up from its origin, so they are listed here
        # in reverse order to render top to bottom in increasing specificity.
        for field in reversed(self.fields):
            value = str(self.fields[field])

            # Wrap multiline fields.
            if field in self.MULTILINE_FIELDS:
                collapsed = " ".join(value.split()) # Collapse whitespace.
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
        if has_api:
            lines.append("")
            lines.append(
                f"atform.{self.api.__name__} help: {self.api.__doc__}"
            )

        return "\n".join(lines)
