"""Unit tests for the top-level Application widget."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


@patch("atform.cache.data", new={"vcs": None})
class Title(unittest.TestCase):
    """Window title tests."""

    def setUp(self):
        utils.reset()

    def test_no_project(self):
        """Confirm window title if no project name was provided."""
        app = atform.gui.app.Application("foo", 0)
        self.assertEqual("ATFORM", app.title())

    def test_project_name(self):
        """Confirm the window title contains the project name."""
        atform.set_project_info(project="Spam")
        app = atform.gui.app.Application("foo", 0)
        self.assertEqual("ATFORM - Spam", app.title())


@patch("sys.argv", new=utils.mock_argv("--gui"))
@patch("atform.gui.app.Application.mainloop")
@patch("atform.gui.buildlist.BuildList")
class BuildListParameters(unittest.TestCase):
    """Tests for parameters passed to the build list."""

    @utils.disable_idlock
    def test_path(self, mock_build, *_mocks):
        """Confirm the path parameter is passed to build."""
        atform.generate(path="foo")
        self.assertEqual("foo", mock_build.call_args[0][1])

    @utils.disable_idlock
    def test_folder_depth(self, mock_build, *_mocks):
        """Confirm the folder depth parameter is passed to build."""
        atform.set_id_depth(3)
        atform.generate(folder_depth=2)
        self.assertEqual(2, mock_build.call_args[0][2])
