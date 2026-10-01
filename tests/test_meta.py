"""Unit tests for functions in the metadata output module."""

import unittest
from unittest.mock import patch

import atform
from atform.error import UserScriptError
from tests import utils


class ListTests(unittest.TestCase):
    """Tests for the list_tests() function."""

    def setUp(self):
        utils.reset()

    def test_content(self):
        """Confirm returned list contains correct test listing."""
        atform.section(1)
        atform.add_test("t1")
        atform.add_test("t2")
        self.assertEqual([("1.1", "t1"), ("1.2", "t2")], atform.list_tests())

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    def test_after_generate(self):
        """Confirm correct operation when called after generate()."""
        atform.section(1)
        atform.add_test("t1")
        atform.add_test("t2")
        atform.generate()
        self.assertEqual([("1.1", "t1"), ("1.2", "t2")], atform.list_tests())

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
                ("1.1", "t1"),
                ("1.2", "t2"),
                ("1.3", "t3"),
            ],
            tests,
        )

    def test_empty(self):
        """Confirm empty list is returned if no tests were defined."""
        self.assertEqual([], atform.list_tests())


class ListTestsWithSections(unittest.TestCase):
    """Tests for the sections option of list_tests()."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-bool value."""
        with self.assertRaises(UserScriptError):
            atform.list_tests(sections=0)

    def test_keyword_argument(self):
        """Confirm exception if not passed as a keyword argument."""
        with self.assertRaises(TypeError):
            # Pylint message disabled because this test is explicitly testing
            # for a non-keyword argument.
            atform.list_tests(True)  # pylint: disable=too-many-function-args

    def test_no_sections(self):
        """Confirm correct output if no sections are defined."""
        atform.add_test("t1")
        atform.add_test("t2")
        self.assert_result(
            [
                ("1", "t1"),
                ("2", "t2"),
            ]
        )

    def test_no_tests(self):
        """Confirm correct output if no tests are defined."""
        atform.section(1, title="foo")
        atform.section(2, title="bar")
        self.assert_result(
            [
                ("1", "foo"),
                ("1.1", "bar"),
            ]
        )

    def test_no_tests_or_sections(self):
        """Confirm correct output if no tests or sections are defined."""
        self.assert_result([])

    def test_implicit_section(self):
        """Confirm implicitly created parent sections are listed."""
        atform.section(2)  # Implicit 1.x parent section.
        atform.add_test("t1")
        self.assert_result(
            [
                ("1", None),
                ("1.1", None),
                ("1.1.1", "t1"),
            ]
        )

    def test_title(self):
        """Confirm title is returned for sections defined with a title."""
        atform.section(1, title="foo")
        self.assert_result([("1", "foo")])

    def test_no_title(self):
        """Confirm None is returned for sections without a title."""
        atform.section(1)
        self.assert_result([("1", None)])

    def test_order(self):
        """Confirm tests and sections are correctly ordered."""
        atform.section(1, title="foo")
        atform.add_test("bar")
        atform.section(2, title="spam")
        atform.add_test("eggs")
        self.assert_result(
            [
                ("1", "foo"),
                ("1.1", "bar"),
                ("1.2", "spam"),
                ("1.2.1", "eggs"),
            ]
        )

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    def assert_result(self, expected):
        """Verifies the return value of list_tests()."""
        atform.generate()
        self.assertEqual(expected, atform.list_tests(sections=True))
