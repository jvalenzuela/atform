"""Unit tests for functions in the metadata output module."""

import unittest
from unittest.mock import patch

import atform
from tests import utils


class ListTests(unittest.TestCase):
    """Tests for the list_tests() function."""

    def setUp(self):
        utils.reset()

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    def test_after_generate(self):
        """Confirm correct operation when called after generate()."""
        atform.section(1)
        atform.add_test("t1")
        atform.add_test("t2")
        atform.generate()
        self.assertEqual(
            [
                ("1", None, "section"),
                ("1.1", "t1", "test"),
                ("1.2", "t2", "test"),
            ],
            atform.list_tests(),
        )

    @utils.no_pdf_output
    @utils.disable_idlock
    def test_cli_filters(self):
        """Confirm CLI option filters do not limit returned test list."""
        atform.section(1)
        atform.add_test("t1")
        atform.add_test("t2")
        with patch("sys.argv", utils.mock_argv("")):
            atform.generate()  # Call to update cache.

        utils.reset()
        atform.section(1)
        atform.add_test("t1", objective="foo")
        atform.add_test("t2")
        atform.add_test("t3")
        with patch("sys.argv", utils.mock_argv("2")):
            tests = atform.list_tests()
        self.assertEqual(
            [
                ("1", None, "section"),
                ("1.1", "t1", "test"),
                ("1.2", "t2", "test"),
                ("1.3", "t3", "test"),
            ],
            tests,
        )

    def test_member_names(self):
        """Confirm returned members are accessible by name."""
        atform.add_test("title")
        test = atform.list_tests()[0]
        self.assertEqual("1", test.id)
        self.assertEqual("title", test.title)
        self.assertEqual("test", test.type)

    def test_order(self):
        """Confirm tests and sections are correctly ordered."""
        atform.section(1, title="foo")
        atform.add_test("bar")
        atform.section(2, title="spam")
        atform.add_test("eggs")
        self.assertEqual(
            [
                ("1", "foo", "section"),
                ("1.1", "bar", "test"),
                ("1.2", "spam", "section"),
                ("1.2.1", "eggs", "test"),
            ],
            atform.list_tests(),
        )

    def test_no_section_title(self):
        """Confirm None is returned for sections without a title."""
        atform.section(1)
        self.assertEqual([("1", None, "section")], atform.list_tests())

    def test_section_title(self):
        """Confirm title is returned for sections with a title."""
        atform.section(1, title="foo")
        self.assertEqual([("1", "foo", "section")], atform.list_tests())

    def test_implicit_section(self):
        """Confirm implicitly created parent sections are listed."""
        atform.section(2)  # Implicit 1.x parent section.
        atform.add_test("t1")
        self.assertEqual(
            [
                ("1", None, "section"),
                ("1.1", None, "section"),
                ("1.1.1", "t1", "test"),
            ],
            atform.list_tests(),
        )

    def test_no_sections(self):
        """Confirm correct output if no sections are defined."""
        atform.add_test("t1")
        atform.add_test("t2")
        self.assertEqual(
            [
                ("1", "t1", "test"),
                ("2", "t2", "test"),
            ],
            atform.list_tests(),
        )

    def test_no_tests(self):
        """Confirm correct output if no tests are defined."""
        atform.section(1, title="foo")
        atform.section(2, title="bar")
        self.assertEqual(
            [
                ("1", "foo", "section"),
                ("1.1", "bar", "section"),
            ],
            atform.list_tests(),
        )

    def test_no_tests_or_sections(self):
        """Confirm result when no tests or sections are defined."""
        self.assertEqual([], atform.list_tests())
