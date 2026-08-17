"""
This module implements items for handling Treeview instances used in
combination with scroll bars.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from . import tkwidget


class ScrollTree(tkwidget.Treeview):  # pylint: disable=too-many-ancestors
    """Treeview subclass adding scroll bars and related sizing functionality.

    The approach to horizontal sizing is column widths are set to accommodate
    all item content, which is always known in advance. This may be quite wide,
    e.g., for a long test title, so the parent widget, typically a Frame,
    is configured to not size according to the tree's requested size, with
    the horizontal scroll bar providing access to excess width.
    """

    # Initial width of the parent, in pixels. The intent is to provide an
    # initial minimum if the geometry manager doesn't enlarge the parent to
    # fit excess space. The actual value is chosen empirically.
    INITIAL_WIDTH = 200

    # Number of pixels an item is indented from its parent. Defined as a
    # constant as it is not accessible as a style option in the bundled
    # Tcl version. Equal to the default value per:
    #
    # https://www.tcl-lang.org/man/tcl8.6/TkCmd/ttk_treeview.htm#M82
    INDENT = 20

    # Number of pixels added to a column width to accommodate the horizontal
    # padding on each side of the text. This value doesn't appear to be
    # available via a ttk style option, so it is set empirically via this
    # constant.
    COLUMN_XPAD = 10

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Only the tree and horizontal scroll bar are horizontally resizeable.
        parent.columnconfigure(0, weight=1)

        # Only the tree and vertical scroll bar are vertically resizeable.
        parent.rowconfigure(0, weight=1)

        # Size propagation is disabled to prevent the parent from being
        # excessively enlarged to accommodate wide tree columns.
        parent.configure(width=self.INITIAL_WIDTH)
        parent.grid_propagate(0)

        self.grid(row=0, column=0, sticky=tk.NSEW)
        self._add_xscroll(parent)
        self._add_yscroll(parent)

    def _add_xscroll(self, parent):
        """Creates the horizontal scrollbar."""
        scroll = tkwidget.Scrollbar(parent, orient=tk.HORIZONTAL)
        scroll["command"] = self.xview
        self["xscrollcommand"] = scroll.set
        scroll.grid(row=1, column=0, sticky=tk.EW)

    def _add_yscroll(self, parent):
        """Creates the vertical scrollbar."""
        scroll = tkwidget.Scrollbar(parent, orient=tk.VERTICAL)
        scroll["command"] = self.yview
        self["yscrollcommand"] = scroll.set
        scroll.grid(row=0, column=1, sticky=tk.NS)

    def fit_columns(self):
        """Sets the width of all columns to fit their content.

        Must be called after the tree is populated as the column widths are
        computed based on column text.
        """
        indent = self._get_indent(1)
        self._fit_tree_column(indent)

        col = 0
        while True:
            try:
                self.column(col)
            except tk.TclError:  # No more columns.
                break
            self._fit_column_width(col, indent.keys())
            col += 1

    def _get_indent(self, indent, item=None):
        """Gets the indentation distance for every item."""
        indents = {}
        for child in self.get_children(item):
            indents[child] = indent * self.INDENT

            # Recursively acquire child items.
            indents.update(self._get_indent(indent + 1, child))

        return indents

    def _fit_tree_column(self, indent):
        """Sets the tree column width to fit all items."""
        font = self._get_font()
        txt = {iid: self.item(iid, option="text") for iid in indent.keys()}
        widths = [font.measure(txt[iid]) + ind for iid, ind in indent.items()]

        # Include the width of the heading to ensure the heading text will fit.
        widths.append(self._get_header_title_width("#0"))

        width = max(widths) + self.COLUMN_XPAD
        self.set_column_width("#0", width)

    def _fit_column_width(self, cid, iids):
        """Sets the column width to fit content for a non-tree column."""
        font = self._get_font("Cell")
        values = [self.set(iid, cid) for iid in iids]
        widths = [font.measure(s) for s in values]

        # Include the width of the heading to ensure the heading text will fit.
        widths.append(self._get_header_title_width(cid))

        width = max(widths) + self.COLUMN_XPAD
        self.set_column_width(cid, width)

    def _get_header_title_width(self, cid):
        """Computes the width of a column's header text."""
        font = self._get_font("Heading")
        title = self.heading(cid, option="text")
        return font.measure(title)

    def _get_font(self, element=None):
        """Acquires the font used for a given element."""
        style = ttk.Style()
        path = "Treeview"
        if element:
            path += f".{element}"
        name = style.lookup(path, "font")
        return tkfont.nametofont(name)

    def set_column_width(self, cid, width):
        """Wrapper for column() to define the width.

        Stretch is disabled because the width is always set to accommodate
        the widest item, making horizontal resizing is unnecessary.
        """
        self.column(cid, width=width, stretch=tk.FALSE)
