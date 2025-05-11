"""Unit tests for the TestList widget."""

import tkinter as tk
import unittest
from unittest.mock import patch

import atform
from .. import utils


class Base(unittest.TestCase):
    """Base class for all test cases."""

    def setUp(self):
        utils.reset()
        self.btn_patch = patch("atform.gui.testlist.tkwidget.Button")
        self.mock_buttons = self.btn_patch.start()
        self.tl = atform.gui.testlist.TestList(None)

    def set_open(self, id_, open_):
        """Opens or closes a given section."""
        self.tl.tree.item(id_, open=open_)

    def assert_open(self, id_, open_):
        """Confirms a section is open or closed."""
        self.assertEqual(self.tl.tree.item(id_, option="open"), open_)

    def tearDown(self):
        self.btn_patch.stop()


class AddTest(Base):
    """Tests for the add_test() method."""

    def test_duplicate(self):
        """Confirm adding a test that is already listed does nothing."""
        atform.add_test("foo")
        self.tl.add_test((1,))
        self.tl.add_test((1,))
        self.assertEqual([(1,)], self.tl.tree.get_children())

    def test_add_sections(self):
        """Confirm enclosing sections are automatically added."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        self.tl.add_test((1, 1, 1))
        self.assertEqual([(1,)], self.tl.tree.get_children())
        self.assertEqual([(1, 1)], self.tl.tree.get_children((1,)))

    def test_visible(self):
        """Confirm parent sections of added tests start fully expanded."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        self.tl.add_test((1, 1, 1))
        self.assertEqual(tk.TRUE, self.tl.tree.item((1,), option="open"))
        self.assertEqual(tk.TRUE, self.tl.tree.item((1, 1), option="open"))


class RemoveTest(Base):
    """Tests for the remove_test() method."""

    def test_remove_one_test(self):
        """Confirm removing one test from a section containing several tests."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1, 1))
        self.tl.add_test((1, 2))
        self.tl.remove_test((1, 1))
        self.assertTrue(self.tl.tree.exists((1,)))
        self.assertFalse(self.tl.tree.exists((1, 1)))
        self.assertTrue(self.tl.tree.exists((1, 2)))

    def test_remove_section(self):
        """Confirm removing all tests from a section also removes empty parent sections."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1, 1))
        self.tl.add_test((1, 2))
        self.tl.remove_test((1, 1))
        self.tl.remove_test((1, 2))
        self.assertFalse(self.tl.tree.exists((1,)))
        self.assertFalse(self.tl.tree.exists((1, 1)))
        self.assertFalse(self.tl.tree.exists((1, 2)))

    def test_remove_nonexistent(self):
        """Confirm removing a test that is not listed has no effect."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1, 1))
        self.tl.add_test((1, 2))
        self.tl.remove_test((1, 3))
        self.assertTrue(self.tl.tree.exists((1,)))
        self.assertTrue(self.tl.tree.exists((1, 1)))
        self.assertTrue(self.tl.tree.exists((1, 2)))


class Clear(Base):
    """Tests for the clear() method."""

    def test_removal(self):
        """Confirm all items are removed."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        self.tl.add_test((1, 1))
        self.tl.add_test((2, 1))
        self.tl.clear()
        self.assertEqual([], self.tl.tree.get_children())


class DisplayId(Base):
    """Tests for the displayed test and section IDs."""

    def test_test(self):
        """Confirm test IDs are displayed correctly."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.assert_id((1,), "1")
        self.assert_id((2,), "2")

    def test_section(self):
        """Confirm section IDs are displayed correctly."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        self.tl.add_test((1, 1, 1))
        self.assert_id((1,), "1")
        self.assert_id((1, 1), "1.1")

    def assert_id(self, id_, text):
        """Confirms the ID text displayed for a given test."""
        actual = self.tl.tree.item(id_, option="text")
        self.assertEqual(text, actual)


class Title(Base):
    """Tests for the section and test title column."""

    def test_test_title(self):
        """Confirm test titles are displayed."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.assert_title((1,), "foo")
        self.assert_title((2,), "bar")

    def test_section_title(self):
        """Confirm section titles are displayed."""
        atform.set_id_depth(2)
        atform.section(1, title="foo")
        atform.add_test("a test")
        self.tl.add_test((1, 1))
        self.assert_title((1,), "foo")

    def test_section_no_title(self):
        """Confirm a section with no title is blank."""
        atform.set_id_depth(2)
        atform.add_test("a test")
        self.tl.add_test((1, 1))
        self.assert_title((1,), "")

    def assert_title(self, id_, title):
        """Confirms the title column contains the expected string."""
        values = self.tl.tree.item(id_, option="values")
        self.assertEqual(title, values[0])


class Heirarchy(Base):
    """Tests for the tree structure created as tests are added."""

    def test_flat(self):
        """Confirm correct ordering when no sections are present."""
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")

        # These are intentionally added out of order.
        self.tl.add_test((3,))
        self.tl.add_test((2,))
        self.tl.add_test((1,))

        self.assertEqual([(1,), (2,), (3,)], self.tl.tree.get_children())
        self.assert_no_test_children()

    def test_sections(self):
        """Confirm correct structure when sections are present."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.add_test("bar")
        atform.section(1)
        atform.add_test("spam")
        atform.add_test("eggs")

        # These are intentionally added out of order.
        self.tl.add_test((2, 2))
        self.tl.add_test((2, 1))
        self.tl.add_test((1, 2))
        self.tl.add_test((1, 1))

        self.assertEqual([(1,), (2,)], self.tl.tree.get_children())
        self.assertEqual([(1, 1), (1, 2)], self.tl.tree.get_children((1,)))
        self.assertEqual([(2, 1), (2, 2)], self.tl.tree.get_children((2,)))
        self.assert_no_test_children()

    def assert_no_test_children(self):
        """Confirms all tests are leaf nodes."""
        for id_ in self.tl.all_tests:
            self.assertEqual([], self.tl.tree.get_children(id_))


class AllTests(Base):
    """Tests for the all_tests property."""

    def test_empty(self):
        """Confirm an empty set is returned if the list has no content."""
        self.assertEqual(set(), self.tl.all_tests)

    def test_no_section(self):
        """Confirm test IDs when no sections are defined."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.assertEqual({(1,), (2,)}, self.tl.all_tests)

    def test_section(self):
        """Confirm test IDs when sections are defined."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        self.tl.add_test((1, 1))
        self.tl.add_test((2, 1))
        self.assertEqual({(1, 1), (2, 1)}, self.tl.all_tests)


class SelectedTests(Base):
    """Tests for the selected_tests property."""

    def test_empty(self):
        """Confirm an empty set is returned if the list has no tests."""
        self.assertEqual(set(), self.tl.selected_tests)

    def test_none_selected(self):
        """Confirm an empty set is returned if no tests are selected."""
        atform.add_test("foo")
        self.tl.add_test((1,))
        self.assertEqual(set(), self.tl.selected_tests)

    def test_single_selected(self):
        """Confirm correct IDs when a single test is selected."""
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.tl.add_test((3,))
        self.tl.tree.selection_set((2,))
        self.assertEqual({(2,)}, self.tl.selected_tests)

    def test_multiple_selected(self):
        """Confirm correct IDs when multiple tests are selected."""
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.tl.add_test((3,))
        self.tl.tree.selection_set((1,), (2,))
        self.assertEqual({(1,), (2,)}, self.tl.selected_tests)

    def test_section(self):
        """Confirm child tests are returned when a section is selected."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")
        atform.section(1)
        atform.add_test("spam")
        atform.add_test("eggs")
        self.tl.add_test((1, 1, 1))
        self.tl.add_test((1, 1, 2))
        self.tl.add_test((1, 1, 3))
        self.tl.add_test((2, 1, 1))
        self.tl.add_test((2, 1, 2))
        self.tl.tree.selection_set((2,))
        self.assertEqual({(2, 1, 1), (2, 1, 2)}, self.tl.selected_tests)


class ExpandAll(Base):
    """Tests for the expand all button."""

    def setUp(self):
        super().setUp()
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        self.tl.add_test((1, 1, 1))
        self.tl.add_test((2, 1, 1))

    def test_all_closed(self):
        """Confirm all sections are opened if all are initially closed."""
        self.set_open((1,), tk.FALSE)
        self.set_open((1, 1), tk.FALSE)
        self.set_open((2,), tk.FALSE)
        self.set_open((2, 1), tk.FALSE)
        self.click()
        self.assert_all_open()

    def test_some_open(self):
        """Confirm all sections are opened if some are initially open."""
        self.set_open((1,), tk.TRUE)
        self.set_open((1, 1), tk.TRUE)
        self.set_open((2,), tk.FALSE)
        self.set_open((2, 1), tk.FALSE)
        self.click()
        self.assert_all_open()

    def test_all_open(self):
        """Confirm all sections remain open if all are initially open."""
        self.set_open((1,), tk.TRUE)
        self.set_open((1, 1), tk.TRUE)
        self.set_open((2,), tk.TRUE)
        self.set_open((2, 1), tk.TRUE)
        self.click()
        self.assert_all_open()

    def assert_all_open(self):
        """Confirms all sections are open."""
        self.assert_open((1,), tk.TRUE)
        self.assert_open((1, 1), tk.TRUE)
        self.assert_open((2,), tk.TRUE)
        self.assert_open((2, 1), tk.TRUE)

    def click(self):
        """Simulates clicking the expand all button."""
        utils.click_button(self.mock_buttons, "Expand All")


class CollapseAll(Base):
    """Tests for the collapse all button."""

    def setUp(self):
        super().setUp()
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        self.tl.add_test((1, 1, 1))
        self.tl.add_test((2, 1, 1))

    def test_all_closed(self):
        """Confirm all sections remain closed if all are initially closed."""
        self.set_open((1,), tk.FALSE)
        self.set_open((1, 1), tk.FALSE)
        self.set_open((2,), tk.FALSE)
        self.set_open((2, 1), tk.FALSE)
        self.click()
        self.assert_all_closed()

    def test_some_open(self):
        """Confirm all sections are closed if some are initially open."""
        self.set_open((1,), tk.TRUE)
        self.set_open((1, 1), tk.TRUE)
        self.set_open((2,), tk.FALSE)
        self.set_open((2, 1), tk.FALSE)
        self.click()
        self.assert_all_closed()

    def test_all_open(self):
        """Confirm all sections are closed if all are initially open."""
        self.set_open((1,), tk.TRUE)
        self.set_open((1, 1), tk.TRUE)
        self.set_open((2,), tk.TRUE)
        self.set_open((2, 1), tk.TRUE)
        self.click()
        self.assert_all_closed()

    def assert_all_closed(self):
        """Confirms all sections are closed."""
        self.assert_open((1,), tk.FALSE)
        self.assert_open((1, 1), tk.FALSE)
        self.assert_open((2,), tk.FALSE)
        self.assert_open((2, 1), tk.FALSE)

    def click(self):
        """Simulates clicking the collapse all button."""
        utils.click_button(self.mock_buttons, "Collapse All")


class SelectAll(Base):
    """Tests for the select all button."""

    def setUp(self):
        super().setUp()
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        self.tl.add_test((1, 1, 1))
        self.tl.add_test((2, 1, 1))

    def test_initial_none(self):
        """Confirm all items are selected when none are initially selected."""
        self.tl.tree.selection_set()
        self.click()
        self.assert_all_selected()

    def test_initial_some(self):
        """Confirm all items are selected when some are initially selected."""
        self.tl.tree.selection_set((1, 1, 1))
        self.click()
        self.assert_all_selected()

    def test_initial_all(self):
        """Confirm all items remain selected if all are initially selected."""
        self.tl.tree.selection_set(
            (1,),
            (1, 1),
            (1, 1, 1),
            (2,),
            (2, 1),
            (2, 1, 1),
        )
        self.click()
        self.assert_all_selected()

    def assert_all_selected(self):
        """Confirms all items are selected."""
        self.assertEqual(
            (
                (1,),
                (1, 1),
                (1, 1, 1),
                (2,),
                (2, 1),
                (2, 1, 1),
            ),
            self.tl.tree.selection(),
        )

    def click(self):
        """Simulates clicking the select all button."""
        utils.click_button(self.mock_buttons, "Select All")


class UnselectAll(Base):
    """Tests for the unselect all button."""

    def setUp(self):
        super().setUp()
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.section(1)
        atform.add_test("bar")
        self.tl.add_test((1, 1, 1))
        self.tl.add_test((2, 1, 1))

    def test_initial_none(self):
        """Confirm all items remain unselected when none are initially selected."""
        self.tl.tree.selection_set()
        self.click()
        self.assert_none_selected()

    def test_initial_some(self):
        """Confirm all items are unselected if some are initially selected."""
        self.tl.tree.selection_set((1, 1, 1))
        self.click()
        self.assert_none_selected()

    def test_initial_all(self):
        """Confirm all items are unselected if all are initially selected."""
        self.tl.tree.selection_set(
            (1,),
            (1, 1),
            (1, 1, 1),
            (2,),
            (2, 1),
            (2, 1, 1),
        )
        self.click()
        self.assert_none_selected()

    def assert_none_selected(self):
        """Confirms no items are selected."""
        self.assertEqual((), self.tl.tree.selection())

    def click(self):
        """Simulates clicking the unselect all button."""
        utils.click_button(self.mock_buttons, "Unselect All")


class InvertSelection(Base):
    """Tests for the invert selection button."""

    def setUp(self):
        super().setUp()
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.add_test("bar")
        atform.section(1)
        atform.add_test("spam")
        atform.add_test("eggs")
        self.tl.add_test((1, 1, 1))
        self.tl.add_test((1, 1, 2))
        self.tl.add_test((2, 1, 1))
        self.tl.add_test((2, 1, 2))

    def test_initial_none(self):
        """Confirm all tests are selected if nothing is initially selected."""
        self.tl.tree.selection_set()
        self.click()
        self.assertEqual(
            (
                (1, 1, 1),
                (1, 1, 2),
                (2, 1, 1),
                (2, 1, 2),
            ),
            self.tl.tree.selection(),
        )

    def test_initial_all(self):
        """Confirm all items are unselected if everything is initially selected."""
        self.tl.tree.selection_set(
            (1,),
            (1, 1),
            (1, 1, 1),
            (1, 1, 2),
            (2,),
            (2, 1),
            (2, 1, 1),
            (2, 1, 2),
        )
        self.click()
        self.assertEqual((), self.tl.tree.selection())

    def test_single(self):
        """Confirm inversion if a single test is initially selcted."""
        self.tl.tree.selection_set((1, 1, 2))
        self.click()
        self.assertEqual(
            (
                (1, 1, 1),
                (2, 1, 1),
                (2, 1, 2),
            ),
            self.tl.tree.selection(),
        )

    def test_multiple(self):
        """Confirm inversion if multiple tests are initially selected."""
        self.tl.tree.selection_set((1, 1, 2), (2, 1, 2))
        self.click()
        self.assertEqual(
            (
                (1, 1, 1),
                (2, 1, 1),
            ),
            self.tl.tree.selection(),
        )

    def test_section(self):
        """Confirm inversion if a section is initally selected."""
        self.tl.tree.selection_set((1,))
        self.click()
        self.assertEqual(
            (
                (2, 1, 1),
                (2, 1, 2),
            ),
            self.tl.tree.selection(),
        )

    def click(self):
        """Simulates clicking the invert selection button."""
        utils.click_button(self.mock_buttons, "Invert Selection")


class TotalCount(Base):
    """Tests for the total counter."""

    def test_empty(self):
        """Confirm zero count when initially created."""
        self.assert_count(0)

    def test_after_add(self):
        """Confirm correct count after adding items."""
        for i in range(3):
            atform.add_test(f"t{i}")

        for i in range(3):
            with self.subTest(i=i):
                self.assert_count(i)
                self.tl.add_test((i + 1,))
                self.assert_count(i + 1)

    def test_after_remove(self):
        """Confirm correct count after removing items."""
        for i in range(3):
            atform.add_test(f"t{i}")
            self.tl.add_test((i + 1,))

        for i in range(3, 0, -1):
            with self.subTest(i=i):
                self.assert_count(i)
                self.tl.remove_test((i,))
                self.assert_count(i - 1)

    def test_after_clear(self):
        """Confirm correct count after clearing the list."""
        for i in range(3):
            atform.add_test(f"t{i}")
            self.tl.add_test((i + 1,))

        self.tl.clear()
        self.assert_count(0)

    def assert_count(self, expected):
        """Confirms an expected count value."""
        self.assertEqual(expected, self.tl.controls.counts.total.get())


class SelectedCount(Base):
    """Tests for the selected counter."""

    def test_empty(self):
        """Confirm correct count if the list is empty."""
        self.assert_count(0)

    def test_none_selected(self):
        """Confirm correct count if nothing is selected."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.tl.tree.selection_set()
        self.assert_count(0)

    def test_single(self):
        """Confirm correct count if a single test is selected."""
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("spam")
        atform.add_test("eggs")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.tl.add_test((3,))
        self.tl.add_test((4,))
        self.tl.tree.selection_set((1,))
        self.assert_count(1)

    def test_multiple(self):
        """Confirm correct count if multiple tests are selected."""
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("spam")
        atform.add_test("eggs")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.tl.add_test((3,))
        self.tl.add_test((4,))
        self.tl.tree.selection_set((1,), (2,), (3,))
        self.assert_count(3)

    def test_section(self):
        """Confirm correct count if a section is selected."""
        atform.set_id_depth(2)
        atform.add_test("foo")
        atform.add_test("bar")
        atform.section(1)
        atform.add_test("spam")
        atform.add_test("eggs")
        self.tl.add_test((1, 1))
        self.tl.add_test((1, 2))
        self.tl.add_test((2, 1))
        self.tl.add_test((2, 2))
        self.tl.tree.selection_set((1,))
        self.assert_count(2)

    def test_remove(self):
        """Confirm correct count if a selected entry is removed."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.tl.add_test((1,))
        self.tl.add_test((2,))
        self.tl.tree.selection_set((1,), (2,))
        self.tl.remove_test((2,))
        self.assert_count(1)

    def assert_count(self, expected):
        """Confirms an expected count value."""
        # A selection event is required to trigger the count update.
        self.tl.tree.event_generate("<<TreeviewSelect>>")

        self.assertEqual(expected, self.tl.controls.counts.sel.get())
