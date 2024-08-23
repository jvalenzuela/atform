# Unit tests for the error module.


import atform
import unittest


@atform.error.exit_on_script_error
class ExternalCallDummy(object):
    """Dummy class for testing the external_call decorator."""

    @atform.error.external_call
    def ext(self):
        raise atform.error.UserScriptError('foo')


def make_external_call_dummy():
    """Factory to create ExternalCallDummy instances.

    Provides a named location where instances are created, i.e.,
    the name of this function, which is used for verifying tracebacks.
    """
    return ExternalCallDummy()


class ExitOnScriptError(unittest.TestCase):
    """Unit tests for the exit_on_script_error decorator."""

    def test_convert_user_script_error(self):
        """Confirm a UserScriptError is converted to SystemExit."""
        @atform.error.exit_on_script_error
        def func():
            raise atform.error.UserScriptError('foo')

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
            return 'spam'

        self.assertEqual('spam', func())

    def test_traceback_file(self):
        """Confirm the traceback points to the call of the wrapped function."""
        @atform.error.exit_on_script_error
        def func():
            raise atform.error.UserScriptError('foo')

        with self.assertRaises(SystemExit) as e:
            func()
        self.assertEqual(__file__, e.exception.__context__.call_frame.filename)

    def test_object_instance_call_frame(self):
        """Confirm instances of a wrapped class contain a call frame where the instance was created."""
        @atform.error.exit_on_script_error
        class MyClass(object):
            pass

        obj = MyClass()

        this_test_method_name = self.id().split('.')[-1]
        self.assertEqual(this_test_method_name, obj._call_frame.name)

    def test_external_call_frame(self):
        """Confirm a UserScriptError raised in a method called after a wrapped class is instantiated contains a call frame pointing back to the original object creation point."""
        @atform.error.exit_on_script_error
        def func():
            make_external_call_dummy().ext()

        with self.assertRaises(SystemExit) as cm:
            func()

        self.assertEqual(
            'make_external_call_dummy',
            cm.exception.__context__.call_frame.name
        )


class ExternalCall(unittest.TestCase):
    """Tests for the external_call decorator."""

    def test_parameters(self):
        """Confirm positional and keyword arguments are passed to the wrapped method."""
        @atform.error.exit_on_script_error
        class TheClass(object):

            @atform.error.external_call
            def method(self, a, b='spam'):
                self.a = a
                self.b = b

        obj = TheClass()
        obj.method('foo', b='bar')

        self.assertEqual('foo', obj.a)
        self.assertEqual('bar', obj.b)

    def test_return_value(self):
        """Confirm return value of the wrapped method is preserved."""
        @atform.error.exit_on_script_error
        class TheClass(object):

            @atform.error.external_call
            def method(self):
                return 'foo'

        obj = TheClass()

        self.assertEqual('foo', obj.method())

    def test_call_frame(self):
        """Confirm the call frame where the parent object was created is attached to a UserScriptError."""
        with self.assertRaises(atform.error.UserScriptError) as cm:
            make_external_call_dummy().ext()

        self.assertEqual(
            'make_external_call_dummy',
            cm.exception.call_frame.name,
        )
