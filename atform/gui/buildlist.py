"""Top-level frame containing the list of tests that will be built."""

import tkinter as tk
from tkinter import ttk

from . import build
from . import common
from . import testlist


def add(ids):
    """Adds tests to the build list."""
    for id_ in ids:
        BuildList.instance.add_test(id_)


class BuildList(ttk.LabelFrame):  # pylint: disable=too-many-ancestors
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
        btn = tk.Button(self, text="Remove Selected")
        btn.bind(common.LEFT_CLICK, self._on_remove)
        btn.pack(fill=tk.X)

        btn = tk.Button(self, text="Build PDFs")
        btn.bind(common.LEFT_CLICK, self._on_build)
        btn.pack(fill=tk.X)

    def add_test(self, tid):
        """Adds a test to the list."""
        self.testlist.add_test(tid)

    def _on_build(self, _event):
        """Event handler for the build button."""
        tests = self.testlist.all_tests
        if tests:
            build.build(tests, self.path, self.folder_depth)
            self.testlist.clear()

    def _on_remove(self, _event):
        """Event handler for the remove button."""
        for tid in self.testlist.selected_tests:
            self.testlist.remove_test(tid)
