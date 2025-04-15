# Unit tests for the version module


import atform
import unittest
from unittest.mock import patch


class RequireVersion(unittest.TestCase):
    """Tests for the require_version() function."""

    def test_major_type(self):
        """Confirm exception if major is not an integer."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version("1")

    def test_major_invalid_value(self):
        """Confirm exception if major is less than 1."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version(0)

    def test_minor_type(self):
        """Confirm exception if minor is not an integer."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version(1, "0")

    def test_minor_invalid_value(self):
        """Confirm exception if minor is less than 0."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version(1, -1)

    @patch.object(atform.version, "VERSION", new="1.0")
    def test_major_less(self):
        """Confirm exception if installed major is less than required."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version(2)

    @patch.object(atform.version, "VERSION", new="1.0")
    def test_major_equal(self):
        """Confirm no exception if installed major equals required."""
        atform.require_version(1)

    @patch.object(atform.version, "VERSION", new="2.0")
    def test_major_greater(self):
        """Confirm exception if installed major is greater than required."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version(1)

    @patch.object(atform.version, "VERSION", new="1.0")
    def test_minor_less(self):
        """Confirm exception if installed minor is less than required."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.require_version(1, 1)

    @patch.object(atform.version, "VERSION", new="1.0")
    def test_minor_equal(self):
        """Confirm no exception if installed minor equals required."""
        atform.require_version(1, 0)

    @patch.object(atform.version, "VERSION", new="1.1")
    def test_minor_greater(self):
        """Confirm no exception if installed minor is greater than required."""
        atform.require_version(1, 0)
