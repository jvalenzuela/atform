"""This module contains the entry point for the GUI and top-level window."""

import tkinter as tk

from . import buildlist
from . import common
from . import diffwidget
from . import selectlist
from . import selectref
from . import preview
from . import searchwidget
from .. import state
from . import tkwidget


def run(path, folder_depth):
    """Launches the GUI."""
    app = Application(path, folder_depth)
    app.mainloop()


class Application(tkwidget.Tk):
    """Top-level window containing the entire GUI."""

    def __init__(self, path, folder_depth):
        super().__init__()
        self._set_title()
        self._create_panels(path, folder_depth)

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
        """Creates the top-level panels."""
        select = self._create_select_tabs()
        select.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        pview = preview.Preview(self)
        pview.pack(side=tk.LEFT, fill=tk.Y, padx=common.LARGE_PAD)

        build = buildlist.BuildList(self, path, folder_depth)
        build.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

    def _create_select_tabs(self):
        """Creates the Select panel and child tabs."""
        frame = tkwidget.LabelFrame(self, text="Select")
        tabs = tkwidget.Notebook(frame)
        tabs.pack(fill=tk.BOTH, expand=tk.TRUE)

        tabs.add(selectlist.SelectList(tabs), text="List")
        tabs.add(searchwidget.Search(tabs), text="Search")
        tabs.add(diffwidget.Diff(tabs), text="Diff")
        tabs.add(selectref.SelectRef(tabs), text="Refs")

        return frame
