"""Tests for the section() function."""

import unittest

import atform
from atform.error import UserScriptError
from tests import utils


class Level(unittest.TestCase):
    """Tests for the level parameter."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm an exception is raised for a non-integer."""
        with self.assertRaises(UserScriptError):
            atform.section("0")

    def test_leq_zero(self):
        """Confirm an exception is raised for zero or negative values."""
        for level in [-1, 0]:
            utils.reset()
            with self.subTest(level=level), self.assertRaises(UserScriptError):
                atform.section(level)


class Subsection(unittest.TestCase):
    """Tests for creating a subsection below the current level."""

    def setUp(self):
        utils.reset()

    def test_initial(self):
        """Verify creating the first top-level section."""
        atform.section(1)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((1, 1), test.id)

    def test_child_empty_parent(self):
        """Verify creating a subsection directly below a section containing no tests."""
        atform.section(1)
        atform.section(2)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((1, 1, 1), test.id)

    def test_child_populated_parent(self):
        """Verify creating a subsection directly below a section containing other tests."""
        atform.section(1)
        atform.add_test("foo")
        atform.section(2)
        atform.add_test("bar")
        test = utils.get_test_content()
        self.assertEqual((1, 2, 1), test.id)

    def test_grandchild_empty_parent(self):
        """Verify creating a subsubsection below a parent containing no tests."""
        atform.section(1)
        atform.section(3)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((1, 1, 1, 1), test.id)

    def test_grandchild_populated_parent(self):
        """Verify creating a subsubsection below a parent containing other tests."""
        atform.section(1)
        atform.add_test("foo")
        atform.section(3)
        atform.add_test("bar")
        test = utils.get_test_content()
        self.assertEqual((1, 2, 1, 1), test.id)


class Advance(unittest.TestCase):
    """Tests for creating new sections by incrementing a given level."""

    def setUp(self):
        utils.reset()

    def test_same_empty(self):
        """Verify advancing the current level with no tests in the current section.."""
        atform.section(1)
        atform.section(1)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((2, 1), test.id)

    def test_same_populated(self):
        """Verify advancing the current level with tests in the current section."""
        atform.section(1)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        test = utils.get_test_content()
        self.assertEqual((2, 1), test.id)

    def test_parent_empty(self):
        """Verify advancing a parent section with no tests in the current section."""
        atform.section(2)
        atform.section(1)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((2, 1), test.id)

    def test_parent_populated(self):
        """Verify advancing a parent section with tests in the current section."""
        atform.section(2)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        test = utils.get_test_content()
        self.assertEqual((2, 1), test.id)

    def test_grandparent_empty(self):
        """Verify advancing a grandparent section with no tests in the current section."""
        atform.section(3)
        atform.section(1)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((2, 1), test.id)

    def test_grandparent_populated(self):
        """Verify advancing a grandparent section with tests in the current section."""
        atform.section(3)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        test = utils.get_test_content()
        self.assertEqual((2, 1), test.id)


class Resume(unittest.TestCase):
    """Tests for resuming an existing section."""

    def setUp(self):
        utils.reset()

    def test_empty_parent_empty_child(self):
        """Resume the direct parent with no tests in either the parent or child."""
        atform.section(2)
        atform.section(1, resume=True)
        atform.add_test("parent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 2), test.id)

    def test_empty_parent_populated_child(self):
        """Resume the direct parent with tests only in the child."""
        atform.section(2)
        atform.add_test("child")
        atform.section(1, resume=True)
        atform.add_test("parent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 2), test.id)

    def test_populated_parent_empty_child(self):
        """Resume the direct parent with tests only in the parent."""
        atform.section(1)
        atform.add_test("parent")
        atform.section(2)
        atform.section(1, resume=True)
        atform.add_test("parent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 3), test.id)

    def test_populated_parent_populated_child(self):
        """Resume the direct parent with tests in both the parent and child."""
        atform.section(1)
        atform.add_test("parent")
        atform.section(2)
        atform.add_test("child")
        atform.section(1, resume=True)
        atform.add_test("parent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 3), test.id)

    def test_empty_grandparent_empty_child(self):
        """Resume a section above the direct parent with no tests in the grandparent or child."""
        atform.section(3)
        atform.section(1, resume=True)
        atform.add_test("grandparent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 2), test.id)

    def test_empty_grandparent_populated_child(self):
        """Resume a section above the direct parent with tests only in the child."""
        atform.section(3)
        atform.add_test("child")
        atform.section(1, resume=True)
        atform.add_test("grandparent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 2), test.id)

    def test_populated_grandparent_empty_child(self):
        """Resume a section above the direct parent with tests only in the grandparent."""
        atform.section(1)
        atform.add_test("grandparent")
        atform.section(3)
        atform.section(1, resume=True)
        atform.add_test("grandparent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 3), test.id)

    def test_populated_grandparent_populated_child(self):
        """Resume a section above the direct parent with tests in both the grandparent and child."""
        atform.section(1)
        atform.add_test("grandparent")
        atform.section(3)
        atform.add_test("child")
        atform.section(1, resume=True)
        atform.add_test("grandparent resume")
        test = utils.get_test_content()
        self.assertEqual((1, 3), test.id)


class ResumeError(unittest.TestCase):
    """Tests for invalid uses of the resume parameter."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-boolean values."""
        for resume in [0, "foo"]:
            utils.reset()
            with self.subTest(resume=resume), self.assertRaises(UserScriptError):
                atform.section(1, resume=resume)

    def test_id(self):
        """Confirm exception when used with id parameter."""
        with self.assertRaises(UserScriptError):
            atform.section(1, id=42, resume=True)

    def test_title(self):
        """Confirm exception when used with the title parameter."""
        with self.assertRaises(UserScriptError):
            atform.section(1, title="foo", resume=True)

    def test_same_section(self):
        """Confirm exception when resuming the current section."""
        for level in [1, 2]:
            utils.reset()
            atform.section(level)
            with self.subTest(level=level), self.assertRaises(UserScriptError):
                atform.section(level, resume=True)

    def test_new_subsection(self):
        """Confirm exception when resuming a newly-created subsection."""
        for level in [2, 3]:
            utils.reset()
            atform.section(1)
            with self.subTest(level=level), self.assertRaises(UserScriptError):
                atform.section(level, resume=True)


class Id(unittest.TestCase):
    """Tests for specifying a specific section ID."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception if id is not an integer."""
        with self.assertRaises(UserScriptError):
            atform.section(1, id="42")

    def test_backwards_same(self):
        """Confirm exception when targeting a previous section at the same level."""
        for id_ in [1, 2, 3, 4]:
            utils.reset()
            atform.section(1)
            atform.section(1)
            atform.section(1)
            with self.subTest(id=id_), self.assertRaises(UserScriptError):
                atform.section(1, id=id_)

    def test_backwards_parent(self):
        """Confirm exception when targeting a previous section in a parent level."""
        for id_ in [1, 2, 3, 4]:
            utils.reset()
            atform.section(1)
            atform.section(1)
            atform.section(1)
            atform.section(2)
            with self.subTest(id=id_), self.assertRaises(UserScriptError):
                atform.section(1, id=id_)

    def test_forward_same(self):
        """Verify advancing to a new section at the same level."""
        atform.section(1)
        atform.section(1, id=42)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((42, 1), test.id)

    def test_forward_parent(self):
        """Verify advancing to a new section in a parent level."""
        atform.section(2)
        atform.section(1, id=42)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((42, 1), test.id)

    def test_forward_grandparent(self):
        """Verify advancing to a new section in a level above the immediate parent."""
        atform.section(3)
        atform.section(1, id=42)
        atform.add_test("foo")
        test = utils.get_test_content()
        self.assertEqual((42, 1), test.id)


class Title(unittest.TestCase):
    """Tests for defining a section title."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm an exception is raised if title is not a string."""
        with self.assertRaises(UserScriptError):
            atform.section(1, title=42)

    def test_no_title(self):
        """Confirm no title is saved if title is omitted."""
        atform.section(1)
        self.assertEqual({}, atform.id.section_titles)

    def test_invalid(self):
        """Confirm exception for a title that is not a valid folder name.

        The list of invalid characters varies widely among operating
        systems, so this test uses a single character universally
        rejected.
        """
        with self.assertRaises(UserScriptError):
            atform.section(1, title="/")

    def test_store(self):
        """Confirm the title is saved."""
        atform.section(1, title="spam")
        atform.section(2, title="eggs")
        atform.section(1, title="foo")
        self.assertEqual(
            {
                (1,): "spam",
                (1, 1): "eggs",
                (2,): "foo",
            },
            atform.id.section_titles,
        )
