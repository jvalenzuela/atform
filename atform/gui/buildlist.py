"""Top-level frame containing the list of tests that will be built."""

import tkinter as tk

from . import build
from . import common
from . import testlist
from . import tkwidget


def add(ids):
    """Adds tests to the build list."""
    for id_ in ids:
        BuildList.instance.add_test(id_)


class BuildList(tkwidget.LabelFrame):  # pylint: disable=too-many-ancestors
    """Top-level frame containing all components."""

    def __init__(self, parent, path, folder_depth):
        super().__init__(parent, text="Build")
        self.path = path
        self.folder_depth = folder_depth
        self.testlist = testlist.TestList(self)
        self._add_buttons()

        # Store this instance so the build list is accessible at module level.
        BuildList.instance = self

    def _add_buttons(self):
        """Creates the buttons."""
        btn = tkwidget.Button(
            self,
            text="Remove Selected",
            command=self._on_remove,
        )
        btn.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

        btn = tkwidget.Button(
            self,
            text="Build PDFs",
            command=self._on_build,
        )
        btn.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

    def add_test(self, tid):
        """Adds a test to the list."""
        self.testlist.add_test(tid)

    def _on_build(self):
        """Event handler for the build button."""
        tests = self.testlist.all_tests
        if tests:
            build.build(tests, self.path, self.folder_depth)
            self.testlist.clear()

    def _on_remove(self):
        """Event handler for the remove button."""
        for tid in self.testlist.selected_tests:
            self.testlist.remove_test(tid)
