"""Unit tests for the GUI diff tab."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


@patch("atform.gui.diff.load", return_value=True)
@patch("atform.cache.data", new={"vcs": None})
@patch("atform.gui.buildlist.add")
@patch("atform.gui.tkwidget.Button")
class AddButtons(unittest.TestCase):
    """Tests for the add to build buttons."""

    @patch("atform.gui.diff.CHANGED", new="pass")
    @patch("atform.gui.diff.NEW", new="fail")
    @patch("atform.gui.diff.SAME", new="fail")
    def test_changed(self, mock_button, mock_build, *_mocks):
        """Confirm the changed button adds only changed tests to the build list."""
        atform.gui.diffwidget.Diff(None)
        utils.click_button(mock_button, "Add Changed Tests To Build")
        mock_build.assert_called_once_with("pass")

    @patch("atform.gui.diff.CHANGED", new="fail")
    @patch("atform.gui.diff.NEW", new="pass")
    @patch("atform.gui.diff.SAME", new="fail")
    def test_new(self, mock_button, mock_build, *_mocks):
        """Confirm the new button adds only new tests to the build list."""
        atform.gui.diffwidget.Diff(None)
        utils.click_button(mock_button, "Add New Tests To Build")
        mock_build.assert_called_once_with("pass")

    @patch("atform.gui.diff.CHANGED", new="fail")
    @patch("atform.gui.diff.NEW", new="fail")
    @patch("atform.gui.diff.SAME", new="pass")
    def test_unmodified(self, mock_button, mock_build, *_mocks):
        """Confirm the unmodified button adds only unmodified tests to the build list."""
        atform.gui.diffwidget.Diff(None)
        utils.click_button(mock_button, "Add Unmodified Tests To Build")
        mock_build.assert_called_once_with("pass")
