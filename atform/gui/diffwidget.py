"""User interface panel for the diff selection tab."""

from collections.abc import Collection

import tkinter as tk

from . import buildlist
from .. import cache
from . import common
from . import diff
from ..id import IdType
from . import tkwidget


class Diff(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Frame containing the diff selection widgets."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        diff_result = diff.load()
        if diff_result:
            self._create_version()
            self._create_summary_table(diff_result)
        else:
            lbl = tkwidget.Label(
                self,
                text="No cached content found; comparison unavailable.",
            )
            lbl.pack(pady=common.SMALL_PAD)

    def _create_version(self) -> None:
        """Creates a label listing the version of the cached content."""
        version = cache.data["vcs"]
        if version is not None:
            lbl = tkwidget.Label(
                self,
                text=f"Differences relative to: {version}",
            )
            lbl.pack(pady=common.SMALL_PAD)

    def _create_summary_table(self, diff_result) -> None:
        """Creates widgets itemizing the types of changes."""
        frame = tkwidget.Frame(self)
        frame.pack(pady=common.SMALL_PAD)

        self._create_summary_row(frame, "Changed", diff_result.changed)
        self._create_summary_row(frame, "New", diff_result.new)
        self._create_summary_row(frame, "Unmodified", diff_result.same)

    def _create_summary_row(
        self,
        parent: tk.Misc,
        label: str,
        target_ids: Collection[IdType],
    ) -> None:
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
