"""GUI status bar implementation."""

import tkinter as tk

from . import common
from . import tkwidget
from .. import vcs


# Indicator background color conveying a condition that may require attention.
# Ref ANSI safety orange.
WARNING_BACKGROUND = "#ff7900"


class StatusBar(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Parent widget enclosing the entire status bar."""

    def __init__(self, parent):
        super().__init__(
            parent,
            borderwidth=2,
            relief=tk.RIDGE,
        )
        self.pack(fill=tk.X)

        # Indicator widget classes, not instances, ordered left to right.
        items = [
            Vcs,
        ]

        for cls in items:
            self._add_item(cls)
            self._add_sep()

    def _add_item(self, item_cls):
        """Appends an indicator widget."""
        item = item_cls(self)
        item.pack(side=tk.LEFT, ipadx=common.SMALL_PAD)

    def _add_sep(self):
        """Appends a vertical separator."""
        sep = tkwidget.Separator(self, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, fill=tk.Y)


class Vcs(tkwidget.Label):  # pylint: disable=too-many-ancestors
    """Version control status display item."""

    def __init__(self, parent):
        if vcs.version is None:
            text = "No VCS"
        else:
            text = f"VCS: {vcs.version}"
        super().__init__(parent, text=text)
        if vcs.version == "draft":
            self.configure(background=WARNING_BACKGROUND)
