"""Miscellaneous GUI items."""

import tkinter as tk
from tkinter import ttk

from . import tkwidget


# Geometry manager padding sizes.
SMALL_PAD = 5
LARGE_PAD = 20


def add_vertical_scrollbar(parent: tk.Frame, target: ttk.Treeview) -> None:
    """Creates a vertical scroll bar for a given target widget.

    The target widget and scroll bar are packed into the given parent frame.
    """
    scroll = tkwidget.Scrollbar(
        parent,
        orient=tk.VERTICAL,
        command=target.yview,
    )
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    target["yscrollcommand"] = scroll.set
