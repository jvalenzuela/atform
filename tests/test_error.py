# Unit tests for the error module.


import atform
from atform.error import UserScriptError
import sys
import traceback
import unittest


class ExitOnScriptError(unittest.TestCase):
    """Unit tests for the exit_on_script_error decorator."""

    def test_parameters(self):
        """Confirm positional and keyword arguments are passed to the wrapped function."""

        @atform.error.exit_on_script_error
        def func(a, b=0):
            self.assertEqual(1, a)
            self.assertEqual(2, b)

        func(1, b=2)

    def test_return_value(self):
        """Confirm return value of wrapped function is preserved."""

        @atform.error.exit_on_script_error
        def func():
            return "spam"

        self.assertEqual("spam", func())

    def test_traceback_file(self):
        """Confirm the traceback points to the call of the wrapped function."""

        @atform.error.exit_on_script_error
        def func():
            raise UserScriptError("foo")

        with self.assertRaises(UserScriptError) as cm:
            func()
        self.assertEqual(__file__, cm.exception.call_frame.filename)


class Excepthook(unittest.TestCase):
    """Tests for the installed exception handler."""

    def test_convert_user_script_error(self):
        """Confirm a UserScriptError is converted to SystemExit."""
        e = UserScriptError("foo")
        e.call_frame = traceback.extract_stack()[-1]
        with self.assertRaises(SystemExit):
            sys.excepthook(UserScriptError, e, None)

    def test_non_user_script_error(self):
        """Confirm exceptions other than UserScriptError pass unaffected."""
        with self.assertRaises(KeyError):
            sys.excepthook(KeyError, KeyError(), None)
