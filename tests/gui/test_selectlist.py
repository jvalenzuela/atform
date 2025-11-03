"""Unit tests for the SelectList panel."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


class Initialize(unittest.TestCase):
    """List initialization tests."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")

    def test_initialize(self):
        """Confirm all tests are initially added to the list."""
        sl = atform.gui.selectlist.SelectList(None)
        self.assertEqual({(1,), (2,), (3,)}, sl.testlist.all_tests)


@patch("atform.gui.buildlist.add")
class AddButton(unittest.TestCase):
    """Tests for the add to build button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")

    def test_add_selected(self, mock_add):
        """Confirm selected tests are added to the build list."""
        sl = atform.gui.selectlist.SelectList(None)
        sl.testlist.tree.ttv_selection_set((1,), (2,))
        self.click(sl)
        mock_add.assert_called_once_with({(1,), (2,)})

    def test_empty(self, mock_add):
        """Confirm nothing is added when nothing is selected."""
        sl = atform.gui.selectlist.SelectList(None)
        sl.testlist.tree.ttv_selection_set()
        self.click(sl)
        mock_add.assert_called_once_with(set())

    def test_clear_selection(self, _mock_add):
        """Confirm all items are unselected after being added."""
        sl = atform.gui.selectlist.SelectList(None)
        sl.testlist.tree.ttv_selection_set((1,), (2,))
        self.click(sl)
        self.assertEqual(set(), sl.testlist.selected_tests)

    def click(self, parent):
        """Simulates clicking the add button."""
        utils.click_button(parent, "Add Selected Tests To Build")
