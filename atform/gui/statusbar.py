
import tkinter as tk

from . import common
from . import tkwidget
from .. import vcs


class StatusBar(tkwidget.Frame):

    def __init__(self, parent):
        super().__init__(parent, borderwidth=2, relief=tk.SUNKEN)
        self.pack(fill=tk.X)

        items = [
            Vcs,
            Vcs,
        ]

        for i, cls in enumerate(items, start=1):
            self._add_item(cls)

            # Add a separator after each item except the last.
            if i < len(items):
                self._add_sep()

 
    def _add_item(self, item_cls):
        """ """
        item = item_cls(self)
        item.grid(row=0, column=self.next_column, ipadx=common.SMALL_PAD)

    def _add_sep(self):
        """Appends a vertical separator."""
        sep = tkwidget.Separator(self, orient=tk.VERTICAL)
        sep.grid(
            row=0,
            column=self.next_column,
            sticky=tk.NS,
        )

    @property
    def next_column(self):
        """Returns the next available grid column."""
        return self.grid_size()[0]


class Vcs(tkwidget.Label):
    """ """

    def __init__(self, parent):
        if vcs.version is None:
            text = "No VCS"
        else:
            text = f"VCS: {vcs.version}"
        super().__init__(parent, text=text)
        if vcs.version == "draft":
            self.configure(background="#ff7900")
