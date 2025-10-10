"""Top-level frame containing the list of tests that will be built."""

from collections.abc import Iterable
import os
import tkinter as tk
from tkinter import filedialog
from typing import Optional

from . import build
from . import common
from ..id import IdType
from .. import misc
from . import testlist
from . import tkwidget


def add(ids: Iterable[IdType]) -> None:
    """Adds tests to the build list."""
    assert isinstance(BuildList.instance, BuildList)  # Type narrowing assertion.
    for id_ in ids:
        BuildList.instance.add_test(id_)


class BuildList(tkwidget.LabelFrame):  # pylint: disable=too-many-ancestors
    """Top-level frame containing all components."""

    instance: Optional[BuildList] = None

    def __init__(self, parent: tk.Frame, path: str, folder_depth: int) -> None:
        super().__init__(parent, text="Build")
        self.testlist = testlist.TestList(self)
        self._add_remove_button()
        self.path = self._add_path(path)
        self.folder_depth = self._add_folder_depth(folder_depth)
        self._add_build_button()

        # Store this instance so the build list is accessible at module level.
        BuildList.instance = self

    def _add_remove_button(self) -> None:
        """Creates the remove selected button."""
        btn = tkwidget.Button(
            self,
            text="Remove Selected",
            command=self._on_remove,
        )
        btn.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

    def _add_path(self, path: str) -> tk.StringVar:
        """Creates the path entry field."""
        frame = tkwidget.Frame(self)
        frame.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

        lbl = tkwidget.Label(frame, text="Path")
        lbl.pack(side=tk.LEFT)

        var = tkwidget.StringVar()
        var.set(path)

        entry = tkwidget.Entry(
            frame,
            textvariable=var,
        )
        entry.pack(
            side=tk.LEFT,
            expand=tk.TRUE,
            fill=tk.X,
            padx=common.SMALL_PAD,
        )

        btn = tkwidget.Button(
            frame,
            text="...",
            command=self._on_path_click,
        )
        btn.pack(side=tk.RIGHT)

        return var

    def _add_folder_depth(self, folder_depth: int) -> tk.IntVar:
        """Creates the folder depth selector.

        The Spinbox widget is created as read-only so it can only be adjusted
        via the up and down buttons. As this control is likely to be used
        sparingly for small increments, prohibiting direct entry removes the
        need for a validation function.
        """
        frame = tkwidget.Frame(self)
        frame.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

        lbl = tkwidget.Label(frame, text="Folder Depth")
        lbl.pack(side=tk.LEFT)

        var = tkwidget.IntVar()
        var.set(folder_depth)

        to = misc.max_folder_depth()
        spin = tkwidget.Spinbox(
            frame,
            textvariable=var,
            from_=0,
            to=to,
            width=len(str(to)) + 1,  # Fit largest value plus some extra space.
            state="readonly",
        )
        spin.pack(side=tk.LEFT, padx=common.SMALL_PAD)

        return var

    def _add_build_button(self) -> None:
        """Creates the build PDFs button."""
        btn = tkwidget.Button(
            self,
            text="Build PDFs",
            command=self._on_build,
        )
        btn.pack(fill=tk.X, padx=common.SMALL_PAD, pady=common.SMALL_PAD)

    def add_test(self, tid: IdType) -> None:
        """Adds a test to the list."""
        self.testlist.add_test(tid)

    def _on_build(self) -> None:
        """Event handler for the build button."""
        tests = self.testlist.all_tests
        if tests:
            build.build(tests, self.path.get(), self.folder_depth.get())
            self.testlist.clear()

    def _on_remove(self) -> None:
        """Event handler for the remove button."""
        for tid in self.testlist.selected_tests:
            self.testlist.remove_test(tid)

    def _on_path_click(self) -> None:
        """Event handler for the path select button."""
        path = filedialog.askdirectory(
            title="PDF Output Folder",
            initialdir=os.getcwd(),
        )
        if path:
            self.path.set(path)
