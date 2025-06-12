"""Unit tests for the top-level Application widget."""

import unittest

import atform
from .. import utils


class Title(unittest.TestCase):
    """Window title tests."""

    def setUp(self):
        utils.reset()

    def test_no_project(self):
        """Confirm window title if no project name was provided."""
        self.app = atform.gui.app.Application("foo", 0)
        self.assertEqual("ATFORM", self.app.title())

    def test_project_name(self):
        """Confirm the window title contains the project name."""
        atform.set_project_info(project="Spam")
        self.app = atform.gui.app.Application("foo", 0)
        self.assertEqual("ATFORM - Spam", self.app.title())

    def tearDown(self):
        self.app.destroy()
