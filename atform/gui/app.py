"""This module contains the entry point for the GUI and top-level window."""

import tkinter as tk
from tkinter import ttk

from . import buildlist
from . import diffwidget
from . import selectlist
from . import selectref
from . import selectterm
from . import preview
from . import searchwidget
from . import statusbar
from .. import state
from . import tkwidget


def run(path, folder_depth):
    """Launches the GUI."""
    app = Application(path, folder_depth)
    config_style()
    app.mainloop()


def config_style():
    """Applies ttk style modifications."""
    style = ttk.Style()

    # For buttons with multi-line text.
    style.configure("TButton", justify=tk.CENTER)


class Application(tkwidget.Tk):
    """Top-level window containing the entire GUI."""

    def __init__(self, path, folder_depth):
        super().__init__()
        self._set_title()
        self._create_panels(path, folder_depth)
        statusbar.StatusBar(self)

    def _set_title(self):
        """Sets the window title."""
        title = "ATFORM"

        # Append the project name, if any.
        try:
            prj = state.project_info["project"]
        except KeyError:
            pass
        else:
            title += f" - {prj}"

        self.title(title)

    def _create_panels(self, path, folder_depth):
        """Creates the top-level panels.

        PanedWindow weights are assigned to allocate horizontal space
        equally among the select and build panels; the preview window
        remains unaffected as it is fixed to the page width.
        """
        panes = tkwidget.PanedWindow(orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=tk.TRUE)

        select = self._create_select_tabs(panes)
        panes.add(select, weight=1)

        pview = preview.Preview(panes)
        panes.add(pview, weight=0)

        build = buildlist.BuildList(panes, path, folder_depth)
        panes.add(build, weight=1)

    def _create_select_tabs(self, parent):
        """Creates the Select panel and child tabs."""
        frame = tkwidget.LabelFrame(parent, text="Select")
        tabs = tkwidget.Notebook(frame)
        tabs.pack(fill=tk.BOTH, expand=tk.TRUE)

        tabs.add(selectlist.SelectList(tabs), text="List")
        tabs.add(searchwidget.Search(tabs), text="Search")
        tabs.add(diffwidget.Diff(tabs), text="Diff")
        tabs.add(selectref.SelectRef(tabs), text="Refs")
        tabs.add(selectterm.SelectTerm(tabs), text="Terms")

        return frame
