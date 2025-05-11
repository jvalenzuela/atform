"""Miscellaneous GUI items."""

import tkinter as tk
from tkinter import ttk


# Event sequence used to bind mouse left clicks.
LEFT_CLICK = "<ButtonRelease-1>"


def add_vertical_scrollbar(parent, target):
    """Creates a vertical scroll bar for a given target widget.

    The target widget and scroll bar are packed into the given parent frame.
    """
    scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=target.yview)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    target["yscrollcommand"] = scroll.set
