# Unit tests for the error module.


import atform
import unittest


class ExitOnScriptError(unittest.TestCase):
    """Unit tests for the exit_on_script_error decorator."""

    def test_convert_user_script_error(self):
        """Confirm a UserScriptError is converted to SystemExit."""

        @atform.error.exit_on_script_error
        def func():
            raise atform.error.UserScriptError("foo")

        with self.assertRaises(SystemExit):
            func()

    def test_non_user_script_error(self):
        """Confirm exceptions other than UserScriptError pass unaffected."""

        @atform.error.exit_on_script_error
        def func():
            raise KeyError

        with self.assertRaises(KeyError):
            func()

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
            raise atform.error.UserScriptError("foo")

        with self.assertRaises(SystemExit) as e:
            func()
        self.assertEqual(__file__, e.exception.__context__.call_frame.filename)
