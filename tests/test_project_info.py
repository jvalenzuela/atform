# Unit tests for the set_project_info() function.


from tests import utils
import string
import atform
import unittest


class ParameterBase(object):
    """Base class for testing values for a single parameter."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(atform.error.UserScriptError):
            self.do(42)

    def test_empty(self):
        """Confirm exception for an empty parameter."""
        with self.assertRaises(atform.error.UserScriptError):
            self.do("")

    def test_blank(self):
        """Confirm exception for a parameter containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            self.do(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed the value."""
        self.do(string.whitespace + "foo" + string.whitespace)
        self.assertEqual("foo", atform.state.project_info[self.parameter])

    def do(self, value):
        """Calls set_project_info() with a given parameter value."""
        atform.set_project_info(**{self.parameter: value})


class Project(ParameterBase, unittest.TestCase):
    """Unit tests for setting the project name."""

    parameter = "project"


class System(ParameterBase, unittest.TestCase):
    """Unit tests for setting the system name."""

    parameter = "system"
