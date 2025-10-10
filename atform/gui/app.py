"""This module contains the entry point for the GUI and top-level window."""

import tkinter as tk

from . import buildlist
from . import common
from . import diffwidget
from . import selectlist
from . import selectref
from . import preview
from . import searchwidget
from . import statusbar
from .. import state
from . import tkwidget


def run(path: str, folder_depth: int) -> None:
    """Launches the GUI."""
    app = Application(path, folder_depth)
    app.mainloop()


class Application(tkwidget.Tk):
    """Top-level window containing the entire GUI."""

    def __init__(self, path: str, folder_depth: int) -> None:
        super().__init__()
        self._set_title()
        self._create_panels(path, folder_depth)
        statusbar.StatusBar(self)

    def _set_title(self) -> None:
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

    def _create_panels(self, path: str, folder_depth: int) -> None:
        """Creates the top-level panels."""
        frame = tkwidget.Frame(self)
        frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        select = self._create_select_tabs(frame)
        select.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        pview = preview.Preview(frame)
        pview.pack(side=tk.LEFT, fill=tk.Y, padx=common.LARGE_PAD)

        build = buildlist.BuildList(frame, path, folder_depth)
        build.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

    def _create_select_tabs(self, parent: tkwidget.Frame) -> tkwidget.LabelFrame:
        """Creates the Select panel and child tabs."""
        frame = tkwidget.LabelFrame(parent, text="Select")
        tabs = tkwidget.Notebook(frame)
        tabs.pack(fill=tk.BOTH, expand=tk.TRUE)

        tabs.add(selectlist.SelectList(tabs), text="List")
        tabs.add(searchwidget.Search(tabs), text="Search")
        tabs.add(diffwidget.Diff(tabs), text="Diff")
        tabs.add(selectref.SelectRef(tabs), text="Refs")

        return frame
