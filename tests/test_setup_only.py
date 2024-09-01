# Unit tests for the setup_only() decorator.


from tests import utils
import atform
import unittest


@atform.misc.setup_only
def func(a, b=0):
    """Dummy function to test the decorator."""
    return a, b


class SetupOnly(unittest.TestCase):

    def setUp(self):
        utils.reset()

    def test_call_before(self):
        """Confirm a decorated function succeeds when called before section() or Test()."""
        func(0)

    def test_call_after_section(self):
        """Confirm exception when calling a decorated function after section()."""
        atform.set_id_depth(2)
        atform.section(1)
        with self.assertRaises(atform.error.UserScriptError):
            func(0)

    def test_call_after_test(self):
        """Confirm exception when calling a decorated function after Test()."""
        atform.Test("title")
        with self.assertRaises(atform.error.UserScriptError):
            func(0)

    def test_params(self):
        """Confirm positional and keyword parameters are passed to the decorated function."""
        self.assertEqual((42, "foo"), func(42, b="foo"))
