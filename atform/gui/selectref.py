"""
This module creates a panel where tests can be added to the build list
based on assigned references.
"""

import tkinter as tk

from .. import addtest
from . import buildlist
from . import common
from .. import state
from . import tkwidget


class SelectRef(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Top-level panel containing all widgets."""

    def __init__(self, parent):
        super().__init__(parent)
        tree = self._create_ref_list()
        self._create_add_button(tree)

    def _create_ref_list(self):
        """Creates the reference list."""
        frame = tkwidget.Frame(self)
        tree = RefList(frame)
        tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=tk.TRUE,
        )
        common.add_vertical_scrollbar(frame, tree)
        frame.pack(
            fill=tk.BOTH,
            expand=tk.TRUE,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )
        return tree

    def _create_add_button(self, tree):
        """Creates the add to build button."""
        btn = tkwidget.Button(
            self,
            text="Add Selected References To Build",
            command=lambda: buildlist.add(tree.selected_tests),
        )
        btn.pack(
            fill=tk.X,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )


class RefList(tkwidget.Treeview):  # pylint: disable=too-many-ancestors
    """
    Treeview listing all defined reference categories and their child
    reference items.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            columns=["qty"],
        )
        self.heading("#0", text="Category/Item", anchor=tk.W)
        self.heading("qty", text="Test Qty", anchor=tk.W)
        self.column("qty", stretch=tk.FALSE)

        # Set of test IDs for each tree item, including both parent categories
        # and child items, keyed by tree item ID.
        self.tests = {}

        self._populate()

    def _populate(self):
        """Adds all reference categories and items to the tree."""
        refs = get_refs()
        for lbl in state.ref_titles:
            # Add the parent category.
            cat_iid = self.insert(
                "",
                tk.END,
                text=state.ref_titles[lbl],
            )
            self.tests[cat_iid] = set()

            # Add child items.
            for itm in sorted(refs[lbl].keys()):
                itm_tests = refs[lbl][itm]
                iid = self.insert(
                    cat_iid,
                    tk.END,
                    text=itm,
                    values=[str(len(itm_tests))],
                )
                self.tests[iid] = itm_tests
                self.tests[cat_iid].update(itm_tests)

            # Set the parent category test count now that all child
            # items have been added.
            self.item(cat_iid, values=[str(len(self.tests[cat_iid]))])

    @property
    def selected_tests(self):
        """Returns test IDs associated with selected items."""
        tests = set()
        for iid in self.selection():
            tests.update(self.tests[iid])
        return tests


def get_refs():
    """Assembles tests organized by reference.

    Returns a nested dictionary:
    dict[<ref category label>][<ref item>] = set(<test IDs>)
    """
    refs = {lbl: {} for lbl in state.ref_titles}

    for test in addtest.tests.values():
        for ref in test.references:
            cat = refs[ref.label]
            for item in ref.items:
                try:
                    cat[item].add(test.id)
                except KeyError:
                    cat[item] = {test.id}

    return refs
