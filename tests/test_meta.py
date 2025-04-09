"""Unit tests for functions in the metadata output module."""

import sys
import unittest
from unittest.mock import patch

import atform
from tests import utils


class ListTests(unittest.TestCase):
    """Tests for the list_tests() function."""

    def setUp(self):
        utils.reset()

    def test_content(self):
        """Confirm returned list contains correct test listing."""
        atform.set_id_depth(2)
        atform.add_test("t1")
        atform.add_test("t2")
        self.assertEqual([("1.1", "t1"), ("1.2", "t2")], atform.list_tests())

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    def test_after_generate(self):
        """Confirm correct operation when called after generate()."""
        atform.set_id_depth(2)
        atform.add_test("t1")
        atform.add_test("t2")
        atform.generate()
        self.assertEqual([("1.1", "t1"), ("1.2", "t2")], atform.list_tests())

    @utils.no_pdf_output
    @utils.disable_idlock
    def test_cli_filters(self):
        """Confirm CLI option filters do not limit returned test list."""
        atform.set_id_depth(2)
        atform.add_test("t1")
        atform.add_test("t2")
        with patch("sys.argv", utils.mock_argv("")):
            atform.generate()  # Call to update cache.

        utils.reset()
        atform.set_id_depth(2)
        atform.add_test("t1", objective="foo")
        atform.add_test("t2")
        atform.add_test("t3")
        with patch("sys.argv", utils.mock_argv("--diff 2")):
            tests = atform.list_tests()
        self.assertEqual(
            [
                ("1.1", "t1"),
                ("1.2", "t2"),
                ("1.3", "t3"),
            ],
            tests,
        )

    def test_empty(self):
        """Confirm empty list is returned if no tests were defined."""
        self.assertEqual([], atform.list_tests())
