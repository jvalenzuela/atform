"""Unit tests for the SelectList panel."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


class AddButton(unittest.TestCase):
    """Tests for the add to build button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        atform.add_test("baz")
        self.sl = atform.gui.selectlist.SelectList(None)

    def test_initialize(self):
        """Confirm all tests are initially added to the list."""
        self.assertEqual({(1,), (2,), (3,)}, self.sl.testlist.all_tests)

    @patch("atform.gui.buildlist.add")
    def test_add_to_build(self, mock_add):
        """Confirm selected tests are added to the build list."""
        self.sl.testlist.tree.selection_set((1,), (2,))
        utils.click_button(self.sl, "add")
        mock_add.assert_called_once_with({(1,), (2,)})

    @patch("atform.gui.buildlist.add")
    def test_clear_selection(self, _mock_add):
        """Confirm all items are unselected after being added."""
        self.sl.testlist.tree.selection_set((1,), (2,))
        utils.click_button(self.sl, "add")
        self.assertEqual(set(), self.sl.testlist.selected_tests)
