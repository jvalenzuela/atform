"""Unit tests for the terms selection GUI panel."""

import tkinter as tk
import unittest
from unittest.mock import patch

import atform
from .. import utils


def make_panel():
    """Creates a term selection GUI panel."""
    # Pregenerate process is necessary to build term use database.
    for t in atform.addtest.tests.values():
        t.pregenerate()

    panel = atform.gui.selectterm.SelectTerm(None)
    get_tree(panel).selection_set()  # Ensure empty initial selection.
    return panel


def get_tree(panel):
    """Locates the treeview object within the GUI panel."""
    return utils.find_widget_by_class(panel, "Treeview")


def select(panel, term, child=None):
    """Selects an item in the treeview."""
    tree = get_tree(panel)
    for term_iid in tree.get_children():
        if tree.item(term_iid, "text") == term:
            # Select the parent term if no child is specified.
            if child is None:
                tree.selection_add(term_iid)
                break

            # Otherwise select the matching child item.
            for child_iid in tree.get_children(term_iid):
                if tree.item(child_iid, "text") == child:
                    tree.selection_add(child_iid)


def click_add(panel):
    """Simulates clicking the add to build button."""
    utils.click_button(panel, "Add Selected Terms To Build")


class TreeConfig(unittest.TestCase):
    """Tests ensuring correct treeview configuration."""

    def setUp(self):
        utils.reset()

    def test_multiple_select(self):
        """Confirm multiple items can be simultaneously selected."""
        panel = make_panel()
        tree = get_tree(panel)
        mode = str(tree.config("selectmode")[-1])
        self.assertEqual(tk.EXTENDED, mode)


class TermListing(unittest.TestCase):
    """Tests verifying the listing of defined terms."""

    def setUp(self):
        utils.reset()

    def test_empty(self):
        """Confirm empty listing when no terms are defined."""
        tree = get_tree(make_panel())
        self.assertEqual((), tree.get_children())

    def test_order(self):
        """Confirm terms are sorted according their raw text."""
        atform.add_term("spam", "a")
        atform.add_term("foo", "b")
        atform.add_term("eggs", "c")
        atform.add_term("bar", "d")
        tree = get_tree(make_panel())
        items = [tree.item(iid, "text") for iid in tree.get_children()]
        self.assertEqual(["bar", "eggs", "foo", "spam"], items)

    def test_subitems(self):
        """Confirm each term contains support and use child items."""
        atform.add_term("foo", "a")
        atform.add_term("bar", "b")
        tree = get_tree(make_panel())
        for term_iid in tree.get_children():
            child_iids = tree.get_children(term_iid)

            # Verify each child is a leaf node, i.e., no grandchildren.
            for child in child_iids:
                self.assertEqual((), tree.get_children(child))

            # Verify uniform child item order.
            child_text = [tree.item(iid, "text") for iid in child_iids]
            self.assertEqual(["Support", "Use"], child_text)


class TestQuantity(unittest.TestCase):
    """Tests verifying the number of tests displayed for each item."""

    def setUp(self):
        utils.reset()

    def test_unused(self):
        """Confirm quantities for a term without support or use."""
        atform.add_term("foo", "foo")
        self._assert_qty()

    def test_support_only(self):
        """Confirm quantities for a term with only supporting tests."""
        atform.add_term("term", "term")
        atform.add_test("t1", supports_terms=["term"])
        self._assert_qty(term=1, support=1)

    def test_use_only(self):
        """Confirm quantities for a term with only use tests."""
        atform.add_term("term", "term")
        atform.add_test("t1", objective="$term")
        self._assert_qty(term=1, use=1)

    def test_support_and_use(self):
        """Confirm quantities for a term with supporting and use tests."""
        atform.add_term("term", "term")
        atform.add_test("t1", objective="$term")
        atform.add_test("t2", supports_terms=["term"])
        self._assert_qty(term=2, support=1, use=1)

    def _assert_qty(self, term=0, support=0, use=0):
        """ """
        tree = get_tree(make_panel())
        qty = {}
        term_iid = tree.get_children()[0]
        qty["term"] = self._get_qty(tree, term_iid)
        for iid in tree.get_children(term_iid):
            text = tree.item(iid, "text").lower()
            qty[text] = self._get_qty(tree, iid)

        self.assertEqual({"term": term, "support": support, "use": use}, qty)

    def _get_qty(self, tree, iid):
        """Returns the test quantity for a given tree item."""
        return int(tree.item(iid, "values")[0])


@patch("atform.gui.buildlist.add")
class NoSelection(unittest.TestCase):
    """Verify operation when nothing is selected."""

    def setUp(self):
        utils.reset()

    def test_empty(self, mock_add):
        """Confirm operation when no terms are defined."""
        panel = make_panel()
        click_add(panel)
        mock_add.assert_called_once_with(set())

    def test_no_selection(self, mock_add):
        """Confirm operation when terms exist, but nothing is selected."""
        atform.add_term("foo", "bar")
        panel = make_panel()
        click_add(panel)
        mock_add.assert_called_once_with(set())


@patch("atform.gui.buildlist.add")
class SelectTerm(unittest.TestCase):
    """Verify operation when selecting a parent term."""

    def setUp(self):
        utils.reset()
        atform.add_term("term", "term")

    def test_unused(self, mock_add):
        """Confirm operation for a term with no support or use."""
        atform.add_test("title")
        panel = make_panel()
        select(panel, "term")
        click_add(panel)
        mock_add.assert_called_once_with(set())

    def test_support(self, mock_add):
        """Confirm operation for a term with only support tests."""
        atform.add_test("t1")
        atform.add_test("t2", supports_terms=["term"])
        panel = make_panel()
        select(panel, "term")
        click_add(panel)
        mock_add.assert_called_once_with({(2,)})

    def test_use(self, mock_add):
        """Confirm operation for a term with only use tests."""
        atform.add_test("t1")
        atform.add_test("t2", objective="$term")
        panel = make_panel()
        select(panel, "term")
        click_add(panel)
        mock_add.assert_called_once_with({(2,)})

    def test_support_and_use(self, mock_add):
        """Confirm operation for a term with both support and use tests."""
        atform.add_test("t1")
        atform.add_test("t2", objective="$term")
        atform.add_test("t3", supports_terms=["term"])
        panel = make_panel()
        select(panel, "term")
        click_add(panel)
        mock_add.assert_called_once_with({(2,), (3,)})


@patch("atform.gui.buildlist.add")
class SelectSupport(unittest.TestCase):
    """Verify operation when selecting a term's support tests."""

    def setUp(self):
        utils.reset()
        atform.add_term("term", "term")

    def test_unused(self, mock_add):
        """Confirm operation for a term with no support or use."""
        atform.add_test("title")
        panel = make_panel()
        select(panel, "term", "Support")
        click_add(panel)
        mock_add.assert_called_once_with(set())

    def test_support(self, mock_add):
        """Confirm operation for a term with only support tests."""
        atform.add_test("t1")
        atform.add_test("t2", supports_terms=["term"])
        panel = make_panel()
        select(panel, "term", "Support")
        click_add(panel)
        mock_add.assert_called_once_with({(2,)})

    def test_use(self, mock_add):
        """Confirm operation for a term with only use tests."""
        atform.add_test("t1")
        atform.add_test("t2", objective="$term")
        panel = make_panel()
        select(panel, "term", "Support")
        click_add(panel)
        mock_add.assert_called_once_with(set())

    def test_support_and_use(self, mock_add):
        """Confirm operation for a term with both support and use tests."""
        atform.add_test("t1")
        atform.add_test("t2", objective="$term")
        atform.add_test("t3", supports_terms=["term"])
        panel = make_panel()
        select(panel, "term", "Support")
        click_add(panel)
        mock_add.assert_called_once_with({(3,)})


@patch("atform.gui.buildlist.add")
class SelectUse(unittest.TestCase):
    """Verify operation when selecting a term's use tests."""

    def setUp(self):
        utils.reset()
        atform.add_term("term", "term")

    def test_unused(self, mock_add):
        """Confirm operation for a term with no support or use."""
        atform.add_test("title")
        panel = make_panel()
        select(panel, "term", "Use")
        click_add(panel)
        mock_add.assert_called_once_with(set())

    def test_support(self, mock_add):
        """Confirm operation for a term with only support tests."""
        atform.add_test("t1")
        atform.add_test("t2", supports_terms=["term"])
        panel = make_panel()
        select(panel, "term", "Use")
        click_add(panel)
        mock_add.assert_called_once_with(set())

    def test_use(self, mock_add):
        """Confirm operation for a term with only use tests."""
        atform.add_test("t1")
        atform.add_test("t2", objective="$term")
        panel = make_panel()
        select(panel, "term", "Use")
        click_add(panel)
        mock_add.assert_called_once_with({(2,)})

    def test_support_and_use(self, mock_add):
        """Confirm operation for a term with both support and use tests."""
        atform.add_test("t1")
        atform.add_test("t2", objective="$term")
        atform.add_test("t3", supports_terms=["term"])
        panel = make_panel()
        select(panel, "term", "Use")
        click_add(panel)
        mock_add.assert_called_once_with({(2,)})


@patch("atform.gui.buildlist.add")
class MultipleSelect(unittest.TestCase):
    """Verify operation when multiple items are selected."""

    def setUp(self):
        utils.reset()
        atform.add_term("term1", "term1")
        atform.add_term("term2", "term2")

        atform.add_test("t1", supports_terms=["term1"])
        atform.add_test("t2", objective="$term1")

        atform.add_test("t3", supports_terms=["term2"])
        atform.add_test("t4", objective="$term2")

        # Test not associated with any term to serve as a false-positive.
        atform.add_test("No terms")

        self.panel = make_panel()

    def test_terms(self, mock_add):
        """Confirm operation when multiple terms are selected."""
        select(self.panel, "term1")
        select(self.panel, "term2")
        click_add(self.panel)
        mock_add.assert_called_once_with({(1,), (2,), (3,), (4,)})

    def test_children_same_term(self, mock_add):
        """Confirm operation when selecting support and use of the same term."""
        select(self.panel, "term1", "Support")
        select(self.panel, "term1", "Use")
        click_add(self.panel)
        mock_add.assert_called_once_with({(1,), (2,)})

    def test_children_different_term(self, mock_add):
        """Confirm operation when selecting support and use of different terms."""
        select(self.panel, "term1", "Support")
        select(self.panel, "term2", "Use")
        click_add(self.panel)
        mock_add.assert_called_once_with({(1,), (4,)})
