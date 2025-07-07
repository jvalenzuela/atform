"""User interface panel for the diff selection tab."""

import tkinter as tk

from . import buildlist
from .. import cache
from . import common
from . import diff
from . import tkwidget


class Diff(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Frame containing the diff selection widgets."""

    def __init__(self, parent):
        super().__init__(parent)
        if diff.load():
            self._create_version()
            self._create_summary_table()
        else:
            lbl = tkwidget.Label(
                self,
                text="No cached content found; comparison unavailable.",
            )
            lbl.pack(pady=common.SMALL_PAD)

    def _create_version(self):
        """Creates a label listing the version of the cached content."""
        version = cache.data["vcs"]
        if version is not None:
            lbl = tkwidget.Label(
                self,
                text=f"Differences relative to: {version}",
            )
            lbl.pack(pady=common.SMALL_PAD)

    def _create_summary_table(self):
        """Creates widgets itemizing the types of changes."""
        frame = tkwidget.Frame(self)
        frame.pack(pady=common.SMALL_PAD)

        self._create_summary_row(frame, "Changed", diff.CHANGED)
        self._create_summary_row(frame, "New", diff.NEW)
        self._create_summary_row(frame, "Unmodified", diff.SAME)

    def _create_summary_row(self, parent, label, target_ids):
        """Creates widgets for a specific category of changes."""
        row = parent.grid_size()[1]  # Allocate the next unused row.

        lbl = tkwidget.Label(parent, text=f"{label} Tests:")
        lbl.grid(
            column=0,
            row=row,
            sticky=tk.E,
        )

        count = tkwidget.Label(parent, text=str(len(target_ids)))
        count.grid(
            column=1,
            row=row,
            sticky=tk.W,
        )

        btn = tkwidget.Button(
            parent,
            text=f"Add {label} Tests To Build",
            command=lambda: buildlist.add(target_ids),
        )
        btn.grid(
            column=2,
            row=row,
            sticky=tk.EW,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )
