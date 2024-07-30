# Unit tests for the version module


import testgen
import unittest
from unittest.mock import patch


class RequireVersion(unittest.TestCase):
    """Tests for the require_version() function."""

    def test_major_type(self):
        """Confirm exception if major is not an integer."""
        with self.assertRaises(TypeError):
            testgen.require_version('1')

    def test_major_invalid_value(self):
        """Confirm exception if major is less than 1."""
        with self.assertRaises(ValueError):
            testgen.require_version(0)

    def test_minor_type(self):
        """Confirm exception if minor is not an integer."""
        with self.assertRaises(TypeError):
            testgen.require_version(1, '0')

    def test_minor_invalid_value(self):
        """Confirm exception if minor is less than 0."""
        with self.assertRaises(ValueError):
            testgen.require_version(1, -1)

    @patch.object(testgen.version, 'VERSION', new='1.0')
    def test_major_less(self):
        """Confirm exception if installed major is less than required."""
        with self.assertRaises(SystemExit):
            testgen.require_version(2)

    @patch.object(testgen.version, 'VERSION', new='1.0')
    def test_major_equal(self):
        """Confirm no exception if installed major equals required."""
        testgen.require_version(1)

    @patch.object(testgen.version, 'VERSION', new='2.0')
    def test_major_greater(self):
        """Confirm exception if installed major is greater than required."""
        with self.assertRaises(SystemExit):
            testgen.require_version(1)

    @patch.object(testgen.version, 'VERSION', new='1.0')
    def test_minor_less(self):
        """Confirm exception if installed minor is less than required."""
        with self.assertRaises(SystemExit):
            testgen.require_version(1, 1)

    @patch.object(testgen.version, 'VERSION', new='1.0')
    def test_minor_equal(self):
        """Confirm no exception if installed minor equals required."""
        testgen.require_version(1, 0)

    @patch.object(testgen.version, 'VERSION', new='1.1')
    def test_minor_greater(self):
        """Confirm no exception if installed minor is greater than required."""
        testgen.require_version(1, 0)
