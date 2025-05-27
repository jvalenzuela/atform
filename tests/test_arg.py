"""Unit tests for command line argument parsing."""

import functools
from itertools import chain, permutations
import sys
import unittest
from unittest.mock import patch

from tests import utils
import atform
from atform import arg


class InvalidId(unittest.TestCase):
    """Tests for invalid IDs."""

    def setUp(self):
        utils.reset()

    @patch("sys.argv", utils.mock_argv("foo"))
    def test_non_integer(self):
        """Confirm error if the entire ID string is not an integer."""
        with self.assertRaises(SystemExit):
            arg.parse()

    @patch("sys.argv", utils.mock_argv("1.spam"))
    def test_field_non_integer(self):
        """Confirm error if a single field is not an integer."""
        atform.set_id_depth(2)
        with self.assertRaises(SystemExit):
            arg.parse()

    def test_empty_field(self):
        """Confirm error for an empty field."""
        atform.set_id_depth(3)
        for s in [".2.3", "1..3", "1.2."]:
            with self.subTest(s=s):
                with self.assertRaises(SystemExit):
                    with patch("sys.argv", utils.mock_argv(s)):
                        arg.parse()

    @patch("sys.argv", utils.mock_argv("0.1"))
    def test_out_of_range(self):
        """Confirm error for a field value less than one."""
        atform.set_id_depth(2)
        with self.assertRaises(SystemExit):
            arg.parse()

    @patch("sys.argv", utils.mock_argv("1.2.3"))
    def test_too_long(self):
        """Confirm error for too many fields."""
        atform.set_id_depth(2)
        with self.assertRaises(SystemExit):
            arg.parse()


class ValidId(unittest.TestCase):
    """Tests for valid IDs."""

    def setUp(self):
        utils.reset()
        atform.set_id_depth(2)

    @patch("sys.argv", utils.mock_argv("042.0099"))
    def test_leading_zero(self):
        """Confirm values with leading zeros are correctly parsed."""
        ids = arg.parse().id
        self.assertEqual(ids[0], (42, 99))

    @patch("sys.argv", utils.mock_argv("42 88.99"))
    def test_fields(self):
        """Confirm IDs with fields up to the configured ID depth are correctly parsed."""
        ids = arg.parse().id
        self.assertEqual(ids, [(42,), (88, 99)])


class InvalidRange(unittest.TestCase):
    """Tests for invalid ranges."""

    def setUp(self):
        utils.reset()

    def test_order(self):
        """Confirm error if the end ID is not greater than the start ID."""
        atform.set_id_depth(2)
        cases = [
            "1-1",
            "2-1",
            "1.1-1.1",
            "1.3-1.2",
            "2.1-1.1",
            "1.1-1",
            "2.1-1",
            "2-1.1",
        ]
        for s in cases:
            with self.subTest(s=s):
                with self.assertRaises(SystemExit):
                    with patch("sys.argv", utils.mock_argv(s)):
                        arg.parse()

    def test_missing_id(self):
        """Confirm error for missing start or end IDs."""
        cases = [
            "-1",
            "1-",
        ]
        for s in cases:
            with self.subTest(s=s):
                with self.assertRaises(SystemExit):
                    with patch("sys.argv", utils.mock_argv(s)):
                        arg.parse()

    @patch("sys.argv", utils.mock_argv("1-2-3"))
    def test_extra_id(self):
        """Confirm error for more than two IDs."""
        with self.assertRaises(SystemExit):
            arg.parse()


class ValidRange(unittest.TestCase):
    """Tests for valid ranges."""

    def setUp(self):
        utils.reset()
        atform.set_id_depth(2)

    def test_hyphen_spacing(self):
        """Confirm ranges with various spacing around the hyphen are correctly parsed."""
        cases = [
            "1.2-3.4",  # No space
            "1.2 -3.4",  # Space before hyphen
            "1.2- 3.4",  # Space after hyphen
            "1.2 - 3.4",  # Space before and after hyphen
        ]
        for s in cases:
            with self.subTest(s=s):
                with patch("sys.argv", utils.mock_argv(s)):
                    ids = arg.parse().id
                self.assertEqual(ids, [((1, 2), (3, 4))])

    def test_different_widths(self):
        """Confirm ranges with different starting and ending widths are parsed correctly."""
        cases = {
            "1-2.1": ((1,), (2, 1)),
            "1.1-2": ((1, 1), (2,)),
        }
        for s in cases:
            with self.subTest(s=s):
                with patch("sys.argv", utils.mock_argv(s)):
                    ids = arg.parse().id
                self.assertEqual(ids, [cases[s]])


class Misc(unittest.TestCase):
    """Miscellaneous ID parsing tests."""

    def setUp(self):
        utils.reset()
        atform.set_id_depth(2)

    @utils.no_args
    def test_none(self):
        """Verify empty result if no arguments are given."""
        ids = arg.parse().id
        self.assertEqual(ids, [])

    @patch("sys.argv", utils.mock_argv("1 2.1-3.1 4.1 5.1-6.1"))
    def test_multiple(self):
        """Verify a combination of IDs and ranges are parsed correctly."""
        ids = arg.parse().id
        self.assertEqual(
            ids,
            [
                (1,),
                ((2, 1), (3, 1)),
                (4, 1),
                ((5, 1), (6, 1)),
            ],
        )


class FilterId(unittest.TestCase):
    """Base class for verifying command line IDs filtering generated output."""

    def setUp(self):
        utils.reset()
        atform.set_id_depth(2)

    @utils.no_pdf_output
    @utils.disable_idlock
    @patch("atform.cache.load")
    def gen(self, args, expected, mock_load):
        """Verifies generated tests match the expected tests."""
        with patch("sys.argv", utils.mock_argv(args)):
            atform.cache.data = {}
            atform.generate()

        # Collect IDs from tests that have been built from the mock cache.
        built = set(atform.cache.data["page counts"])

        self.assertEqual(expected, built)

    @utils.no_args
    def test_none(self):
        """Confirm all tests are built if no IDs are provided."""
        for sec in range(3):
            atform.section(1)
            for test in range(3):
                atform.add_test(f"{test}")
        self.gen(
            "", {(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)}
        )

    def test_arg(self):
        """Confirm correct tests are built based on ID arguments."""
        ids = {
            # Single test IDs.
            "3.3": {(3, 3)},  # TID
            "3.2": set(),  # nonexistent TID
            # Single section IDs.
            "7": {(7, 1), (7, 3)},  # SID
            "2": set(),  # nonexistent SID
            # Ranges within the same section.
            "3.3-3.5": {(3, 3), (3, 4), (3, 5)},  # TID-TID
            "3.4-3.6": {(3, 4), (3, 5)},  # TID-nonexistent TID
            "3.2-3.4": {(3, 3), (3, 4)},  # nonexistent TID-TID
            "3.2-3.6": {(3, 3), (3, 4), (3, 5)},  # nonexistent TID-nonexistent TID
            "3-3.3": {(3, 1), (3, 3)},  # SID-TID
            "3-3.6": {(3, 1), (3, 3), (3, 4), (3, 5)},  # SID-nonexistent TID
            # Ranges spanning sections.
            "3.7-5.1": {(3, 7), (5, 1)},  # TID-TID
            "3.7-5.2": {(3, 7), (5, 1)},  # TID-nonexistent TID
            "3.6-5.1": {(3, 7), (5, 1)},  # nonexistent TID-TID
            "3.6-5.2": {(3, 7), (5, 1)},  # nonexistent TID-nonexistent TID
            "3.7-5": {(3, 7), (5, 1), (5, 3)},  # TID-SID
            "3.6-5": {(3, 7), (5, 1), (5, 3)},  # nonexistent TID-SID
            "3.7-6": {(3, 7), (5, 1), (5, 3)},  # TID-nonexistent SID
            "3.6-6": {(3, 7), (5, 1), (5, 3)},  # nonexistent TID-nonexistent SID
            "5-7.1": {(5, 1), (5, 3), (7, 1)},  # SID-TID
            "4-5.3": {(5, 1), (5, 3)},  # nonexistent SID-TID
            "5-7.2": {(5, 1), (5, 3), (7, 1)},  # SID-nonexistent TID
            "4-7.2": {(5, 1), (5, 3), (7, 1)},  # nonexistent SID-nonexistent TID
            "5-7": {(5, 1), (5, 3), (7, 1), (7, 3)},  # SID-SID
            "5-6": {(5, 1), (5, 3)},  # SID-nonexistent SID
            "4-5": {(5, 1), (5, 3)},  # nonexistent SID-SID
            "4-6": {(5, 1), (5, 3)},  # nonexistent SID-nonexistent SID
        }

        # Generate all combinations of above, up to two arguments.
        combos = chain.from_iterable(permutations(ids, r) for r in range(1, 3))

        for args in combos:
            utils.reset()
            atform.set_id_depth(2)

            atform.add_test("1.1")

            atform.section(1, id=3)
            atform.add_test("3.1")
            atform.skip_test()
            atform.add_test("3.3")
            atform.add_test("3.4")
            atform.add_test("3.5")
            atform.skip_test()
            atform.add_test("3.7")

            atform.section(1, id=5)
            atform.add_test("5.1")
            atform.skip_test()
            atform.add_test("5.3")

            atform.section(1, id=7)
            atform.add_test("7.1")
            atform.skip_test()
            atform.add_test("7.3")

            atform.section(1, id=10)
            atform.add_test("10.1")

            expected = set(chain.from_iterable(ids[i] for i in args))
            with self.subTest(args=args):
                self.gen(" ".join(args), expected)
