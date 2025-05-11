"""Unit tests for the BuildList panel."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


def click_build(mock_buttons):
    """Simulates clicking the build button."""
    utils.click_button(mock_buttons, "Build PDFs")


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


@patch("atform.gui.buildlist.tkwidget.Button")
class RemoveButton(unittest.TestCase):
    """Tests for the remove selected button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")

    def test_remove_some(self, mock_buttons):
        """Confirm removal when some tests are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set((1,))
        self.click(mock_buttons)
        self.assert_remaining_tests({(2,)})

    def test_remove_all(self, mock_buttons):
        """Confirm removal when all tests are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set((1,), (2,))
        self.click(mock_buttons)
        self.assert_remaining_tests(set())

    def test_remove_none(self, mock_buttons):
        """Confirm no change when no tests are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set()
        self.click(mock_buttons)
        self.assert_remaining_tests({(1,), (2,)})

    def click(self, mock_buttons):
        """Simulates clicking the remove button."""
        utils.click_button(mock_buttons, "Remove Selected")

    def assert_remaining_tests(self, expected):
        """Confirms the test list contains the expected set of tests."""
        actual = atform.gui.buildlist.BuildList.instance.testlist.all_tests
        self.assertEqual(expected, actual)


@patch("atform.gui.buildlist.tkwidget.Button")
@patch("atform.gui.build.build")
class BuildButton(unittest.TestCase):
    """Tests for the build button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")

    def test_none_selected(self, mock_build, mock_buttons):
        """Confirm all tests are built when none are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set()
        click_build(mock_buttons)
        mock_build.assert_called_once_with({(1,), (2,)}, None, None)

    def test_some_selected(self, mock_build, mock_buttons):
        """Confirm all tests are built when some are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set((1,))
        click_build(mock_buttons)
        mock_build.assert_called_once_with({(1,), (2,)}, None, None)

    def test_empty(self, mock_build, mock_buttons):
        """Confirm nothing is built if the list is empty."""
        atform.gui.buildlist.BuildList(None, None, None)
        click_build(mock_buttons)
        mock_build.assert_not_called()

    def test_clear_after(self, _mock_build, mock_buttons):
        """Confirm listing is cleared after building."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        click_build(mock_buttons)
        self.assertEqual(
            set(), atform.gui.buildlist.BuildList.instance.testlist.all_tests
        )


@patch("atform.gui.buildlist.tkwidget.Button")
@patch("atform.gui.build.build")
class BuildParameters(unittest.TestCase):
    """Tests for parameters passed to the builder."""

    def setUp(self):
        utils.reset()

    def test_path(self, mock_build, mock_buttons):
        """Confirm the path parameter is passed to build."""
        atform.add_test("title")
        atform.gui.buildlist.BuildList(None, "foo", None)
        atform.gui.buildlist.add({(1,)})
        click_build(mock_buttons)
        self.assertEqual("foo", mock_build.call_args[0][1])

    def test_folder_depth(self, mock_build, mock_buttons):
        """Confirm the folder depth parameter is passed to build."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.gui.buildlist.BuildList(None, None, 2)
        atform.gui.buildlist.add({(1, 1, 1)})
        click_build(mock_buttons)
        self.assertEqual(2, mock_build.call_args[0][2])
