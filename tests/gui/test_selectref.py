"""Tests for the reference select panel."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


def get_treeview(parent):
    """Finds the treeview widget."""
    return utils.find_widget_by_class(parent, "Treeview")


@patch("atform.gui.buildlist.add")
class Add(unittest.TestCase):
    """Tests for the add button."""

    def setUp(self):
        utils.reset()
        atform.add_reference_category("r1", "r1")
        atform.add_reference_category("r2", "r2")
        atform.add_test("t1", references={"r1": ["i1"]})
        atform.add_test("t2", references={"r1": ["i1"]})
        atform.add_test("t3", references={"r2": ["i2"]})
        atform.add_test("t4", references={"r2": ["i2"]})

    def test_none_selected(self, mock_build):
        """Confirm nothing is added to the build if no items are selected."""
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        tree.selection_set()
        self.click_add(panel)
        mock_build.assert_called_once_with(set())

    def test_category_selected(self, mock_build):
        """Confirm tests for all items are added to the build when a category is selected."""
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        r1 = tree.get_children()[0]
        tree.selection_set(r1)
        self.click_add(panel)
        mock_build.assert_called_once_with({(1,), (2,)})

    def test_item_selected(self, mock_build):
        """Confirm tests for the selected child item are added to the build."""
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        r1 = tree.get_children()[0]
        i1 = tree.get_children(r1)
        tree.selection_set(i1)
        self.click_add(panel)
        mock_build.assert_called_once_with({(1,), (2,)})

    def click_add(self, panel):
        """Simulates clicking the add to build button."""
        utils.click_button(panel, "Add Selected References To Build")


class CategoryListing(unittest.TestCase):
    """Tests for parent reference category listings."""

    def setUp(self):
        utils.reset()

    def test_empty(self):
        """Confirm a category with no items is listed."""
        atform.add_reference_category("ref", "ref")
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        self.assertEqual(1, len(tree.get_children()))

    def test_order(self):
        """Confirm categories are listed in the order defined."""
        # Define categories not in alphabetic order.
        atform.add_reference_category("spam", "spam")
        atform.add_reference_category("foo", "foo")
        atform.add_reference_category("bar", "bar")
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        children = tree.get_children()
        self.assertEqual("spam", tree.item(children[0], "text"))
        self.assertEqual("foo", tree.item(children[1], "text"))
        self.assertEqual("bar", tree.item(children[2], "text"))


class ItemListing(unittest.TestCase):
    """Tests for child reference item listings."""

    def setUp(self):
        utils.reset()

    def test_category(self):
        """Confirm items are placed under the correct parent category."""
        atform.add_reference_category("r1", "r1")
        atform.add_reference_category("r2", "r2")
        atform.add_test(
            "title",
            references={
                "r1": ["i1"],
                "r2": ["i2"],
            },
        )
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        cats = tree.get_children()
        i1 = tree.get_children(cats[0])[0]
        self.assertEqual("i1", tree.item(i1, "text"))
        i2 = tree.get_children(cats[1])[0]
        self.assertEqual("i2", tree.item(i2, "text"))

    def test_order(self):
        """Confirm items are listed in sorted order."""
        atform.add_reference_category("ref", "ref")

        # Reference items are intentionally defined not in alphabetic order.
        atform.add_test("title", references={"ref": ["c", "a", "b"]})

        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        items = tree.get_children(ref)
        self.assertEqual("a", tree.item(items[0], "text"))
        self.assertEqual("b", tree.item(items[1], "text"))
        self.assertEqual("c", tree.item(items[2], "text"))

    def test_children(self):
        """Confirm items contain no children."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("title", references={"ref": ["item"]})
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        item = tree.get_children(ref)[0]
        self.assertEqual(0, len(tree.get_children(item)))


class TestQuantity(unittest.TestCase):
    """Tests for the test quantity column."""

    def setUp(self):
        utils.reset()

    def test_empty_category(self):
        """Confirm a category with no references lists zero tests."""
        atform.add_reference_category("ref", "ref")
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        self.assert_quantity(tree, ref, 0)

    def test_category_overlap_tests(self):
        """Confirm count for a category with multiple items referenced by the same test."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("t1", references={"ref": ["foo", "bar"]})
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        self.assert_quantity(tree, ref, 1)

    def test_category_separate_tests(self):
        """Confirm count for a category with multiple items referenced by different tests."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("t1", references={"ref": ["foo", "bar"]})
        atform.add_test("t2", references={"ref": ["spam", "eggs"]})
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        self.assert_quantity(tree, ref, 2)

    def test_item_single_test(self):
        """Confirm count for an item referenced by a single test."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("t1", references={"ref": ["i1"]})
        atform.add_test("t2", references={"ref": ["i2"]})
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        i1 = tree.get_children(ref)[0]
        self.assert_quantity(tree, i1, 1)

    def test_item_multiple_tests(self):
        """Confirm count for an item referenced by multiple tests."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("t1", references={"ref": ["i1"]})
        atform.add_test("t2", references={"ref": ["i1"]})
        panel = atform.gui.selectref.SelectRef(None)
        tree = get_treeview(panel)
        ref = tree.get_children()[0]
        i1 = tree.get_children(ref)[0]
        self.assert_quantity(tree, i1, 2)

    def assert_quantity(self, tree, item, expected):
        """Confirms an item has the expected test quantity."""
        self.assertEqual(str(expected), tree.item(item, "values")[0])
