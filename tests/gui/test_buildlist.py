"""Unit tests for the BuildList panel."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


class Add(unittest.TestCase):
    """Tests for the add() function."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        self.buildlist = atform.gui.buildlist.BuildList(None, None, None)

    def test_add(self):
        """Confirm tests are added to the test list."""
        atform.gui.buildlist.add({(1,), (2,)})
        self.assertEqual({(1,), (2,)}, self.buildlist.testlist.all_tests)


class RemoveButton(unittest.TestCase):
    """Tests for the remove selected button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        self.buildlist = atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})

    def test_remove_some(self):
        """Confirm removal when some tests are selected."""
        self.buildlist.testlist.tree.selection_set((1,))
        utils.click_button(self.buildlist, "remove")
        self.assertEqual({(2,)}, self.buildlist.testlist.all_tests)

    def test_remove_none(self):
        """Confirm no change when no tests are selected."""
        self.buildlist.testlist.tree.selection_set()
        utils.click_button(self.buildlist, "remove")
        self.assertEqual({(1,), (2,)}, self.buildlist.testlist.all_tests)


class BuildButton(unittest.TestCase):
    """Tests for the build button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        self.buildlist = atform.gui.buildlist.BuildList(None, None, None)

    @patch("atform.gui.build.build")
    def test_none_selected(self, mock_build):
        """Confirm all tests are built when none are selected."""
        atform.gui.buildlist.add({(1,), (2,)})
        self.buildlist.testlist.tree.selection_set()
        utils.click_button(self.buildlist, "build")
        mock_build.assert_called_once_with({(1,), (2,)}, None, None)

    @patch("atform.gui.build.build")
    def test_some_selected(self, mock_build):
        """Confirm all tests are built when some are selected."""
        atform.gui.buildlist.add({(1,), (2,)})
        self.buildlist.testlist.tree.selection_set((1,))
        utils.click_button(self.buildlist, "build")
        mock_build.assert_called_once_with({(1,), (2,)}, None, None)

    @patch("atform.gui.build.build")
    def test_empty(self, mock_build):
        """Confirm nothing is built if the list is empty."""
        utils.click_button(self.buildlist, "build")
        mock_build.assert_not_called()

    @patch("atform.gui.build.build")
    def test_clear_after(self, _mock_build):
        """Confirm listing is cleared after building."""
        atform.gui.buildlist.add({(1,), (2,)})
        utils.click_button(self.buildlist, "build")
        self.assertEqual(set(), self.buildlist.testlist.all_tests)


@patch("sys.argv", new=utils.mock_argv("--gui"))
@patch("atform.gui.app.Application.mainloop")
class GenerateParameters(unittest.TestCase):
    """Tests for generate() parameters passed to the builder."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    @patch("atform.gui.build.build")
    def test_path(self, _mock_mainloop, mock_build):
        """Confirm the path parameter is passed to build."""
        atform.add_test("foo")
        atform.generate(path="foo")
        atform.gui.buildlist.add({(1,)})
        utils.click_button(atform.gui.buildlist.BuildList.instance, "build")
        self.assertEqual("foo", mock_build.call_args[0][1])

    @utils.disable_idlock
    @patch("atform.gui.build.build")
    def test_folder_depth(self, _mock_mainloop, mock_build):
        """Confirm the folder depth parameter is passed to build."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.generate(folder_depth=2)
        atform.gui.buildlist.add({(1, 1, 1)})
        utils.click_button(atform.gui.buildlist.BuildList.instance, "build")
        self.assertEqual(2, mock_build.call_args[0][2])
