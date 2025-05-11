"""
Implements a frame allowing the user to add to the build queue by selecting
from a list of all tests.
"""

import tkinter as tk

from . import buildlist
from . import common
from .. import state
from . import testlist
from . import tkwidget


class SelectList(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Top-level widget housing the selection list."""

    def __init__(self, parent):
        super().__init__(parent)
        self._add_listing()
        self._add_buttons()

    def _add_listing(self):
        """Creates the test listing widget."""
        self.testlist = testlist.TestList(self)

        # Populate the list with all defined tests.
        for tid in state.tests:
            self.testlist.add_test(tid)

    def _add_buttons(self):
        """Creates additional buttons."""
        add = tkwidget.Button(
            self,
            text="Add Selected Tests To Build",
            command=self._on_add,
        )
        add.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

    def _on_add(self):
        """Event handler for the Add button."""
        buildlist.add(self.testlist.selected_tests)
        self.testlist.unselect_all()
