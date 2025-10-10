"""
This module implements a widget displaying a heirarchial tree allowing the
user to select specific tests.
"""

from collections.abc import Iterable
from typing import Optional

import tkinter as tk

from . import common
from . import preview
from .. import id as id_
from .. import state
from . import tkwidget


class TestList(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Top-level widget housing the entire list and associated buttons."""

    # Number of pixels per ID field allocated to the ID column width;
    # empirically derived to fit an ID with the format xx.yy.zzz.
    ID_COLUMN_FACTOR = 40

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self._add_tree()
        self.controls = ControlPanel(self)
        self.controls.pack(side=tk.LEFT, fill=tk.Y)
        self.pack(fill=tk.BOTH, expand=tk.TRUE)

    def _add_tree(self) -> None:
        """Creates the tree view widget."""
        frame = tk.Frame(self)
        frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)
        self.tree = TupleTreeview(
            frame,
            columns=["Title"],
        )
        self.tree.heading("#0", text="ID", anchor=tk.W)
        self.tree.heading("Title", text="Title", anchor=tk.W)
        self.tree.column(
            "#0",
            stretch=tk.FALSE,
            width=len(state.current_id) * self.ID_COLUMN_FACTOR,
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self.tree.tag_bind("preview", "<ButtonRelease-1>", self._preview)
        common.add_vertical_scrollbar(frame, self.tree)

    def add_test(self, tid: id_.IdType) -> None:
        """Adds a test to the listing."""
        if self.tree.ttv_exists(tid):
            return

        self._add_parents(tid)
        parent = tid[:-1]
        index = self._calc_index(tid)
        title = state.tests[tid].title
        self.tree.ttv_insert(
            parent,
            index,
            tid,
            text=id_.to_string(tid),
            values=[title],
            tags="preview",
        )
        self.tree.ttv_see(tid)
        self.controls.counts.adjust_total(1)

    def _add_parents(self, tid: id_.IdType) -> None:
        """Creates all required parent items for a given test ID."""
        for i in range(len(tid) - 1):
            current_tid = tid[: i + 1]

            if not self.tree.ttv_exists(current_tid):
                parent = current_tid[:-1]
                index = self._calc_index(current_tid)
                try:
                    title = state.section_titles[current_tid]
                except KeyError:
                    title = ""
                self.tree.ttv_insert(
                    parent,
                    index,
                    current_tid,
                    text=id_.to_string(current_tid),
                    values=[title],
                )

    def _calc_index(self, tid: id_.IdType) -> int:
        """Computes the index to insert a given test or section ID."""
        parent = tid[:-1]
        siblings = list(self.tree.ttv_get_children(parent))
        siblings.append(tid)
        siblings.sort()
        return siblings.index(tid)

    def remove_test(self, tid: id_.IdType) -> None:
        """Revoves a test from the listing."""
        if not self.tree.ttv_exists(tid):
            return

        self.tree.ttv_delete(tid)
        self.controls.counts.adjust_total(-1)

        # Remove any parent sections that are now empty after the target
        # test has been deleted.
        for i in range(1, len(tid)):
            parent_id = tid[:-i]
            if self.tree.ttv_get_children(parent_id):
                break
            self.tree.ttv_delete(parent_id)

    def _preview(self, _event: tk.Event) -> None:
        """Event handler for clicks on a test item to dispatch a preview."""
        tid = self.tree.ttv_focus()

        # Even though this callback is bound to test items only, it is
        # possible for Treeview.focus() to return a section or subsection
        # when simultaneously selecting a section and a test. The preview
        # dispatch is therefore filtered for test IDs only to prevent
        # non-test IDs from being previewed.
        if len(tid) == len(state.current_id):
            preview.show(tid)

    @property
    def selected_tests(self) -> set[id_.IdType]:
        """Gets IDs for all selected tests."""
        return self._get_tests(self.tree.ttv_selection())

    @property
    def all_tests(self) -> set[id_.IdType]:
        """Gets IDs for all listed tests, regardless of selection."""
        return self._get_tests(self.get_descendants())

    def clear(self) -> None:
        """Removes all items."""
        cnt = len(self.all_tests)
        self.controls.counts.adjust_total(-cnt)
        self.tree.ttv_delete(*self.tree.ttv_get_children())

    def unselect_all(self) -> None:
        """Unselects all items."""
        self.tree.ttv_selection_set()

    def _get_tests(self, parents: Iterable[id_.IdType]) -> set[id_.IdType]:
        """Gets all test IDs under a given set of parent IDs."""
        tids = set()
        for tid in parents:
            tids.add(tid)
            tids.update(self.get_descendants(tid))

        # Filter only test IDs, which are are leaf nodes, i.e., without
        # children.
        return {tid for tid in tids if not self.tree.ttv_get_children(tid)}

    def get_descendants(self, tid: id_.IdType=()) -> set[id_.IdType]:
        """Gets all items under a given item."""
        children = set()
        for c in self.tree.ttv_get_children(tid):
            children.add(c)
            children.update(self.get_descendants(c))
        return children


class TupleTreeview(tkwidget.Treeview):  # pylint: disable=too-many-ancestors
    """
    Treeview subclass that adds a set of ttv_<method> wrappers translating
    integer ID tuples to strings for use as item IDs(iid). These wrappers
    are not implemented as overrides to avoid Liskov substitution principle
    violations reported by some static analysis tools, e.g., Mypy, due to
    differing call signatures.
    """

    # Mapping between ID tuples and strings. It is symmetrical in that two
    # entries exist for each ID: a string key with a tuple value, and a
    # tuple key with a string value. It is stored in the class because
    # the strings are always a representation of the ID tuples, which are
    # the same for every instance, so a single mapping can serve all instances.
    ids = {
        # Add root entries as the root node is never explicitly added.
        "": (),
        (): "",
        # This None-None mapping supports methods with optional item
        # parameters, i.e., item=None, allowing the None value to pass
        # through to the underlying API call.
        None: None,
    }

    def ttv_delete(self, *items):
        """Wrapper for delete()."""
        # IDs are explicitly not deleted from the internal tuple/string
        # mapping as it is simpler to retain all ID mappings, and allows
        # the single mapping to continue to serve all instances.
        iids = [self.ids[i] for i in items]
        self.delete(*iids)

    def ttv_exists(self, item):
        """Wrapper for exists()."""
        # This method may receive an undefined item ID, i.e., testing for an
        # item that has not yet been inserted, so the return value in that
        # case overrides the original API call.
        try:
            iid = self.ids[item]
        except KeyError:
            return False
        return self.exists(iid)

    def ttv_focus(self):
        """Wrapper for focus()."""
        return self.ids[self.focus()]

    def ttv_get_children(self, item=None):
        """Wrapper for get_children()."""
        return [self.ids[i] for i in self.get_children(self.ids[item])]

    def ttv_insert(self, parent, index, iid, **kwargs):
        """Wrapper for insert()."""
        # Add mappings for the new ID if it doesn't already exist.
        try:
            str_iid = self.ids[iid]
        except KeyError:
            str_iid = str(iid)
            self.ids[str_iid] = iid
            self.ids[iid] = str_iid

        self.insert(self.ids[parent], index, str_iid, **kwargs)

    def ttv_item(self, item, *args, **kwargs):
        """Wrapper for item()."""
        return self.item(self.ids[item], *args, **kwargs)

    def ttv_see(self, item):
        """Wrapper for see()."""
        self.see(self.ids[item])

    def ttv_selection(self):
        """Wrapper for selection()."""
        return tuple(self.ids[i] for i in self.selection())

    def ttv_selection_set(self, *items):
        """Wrapper for selection_set()."""
        iids = [self.ids[i] for i in items]
        self.selection_set(*iids)


class ControlPanel(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Container holding the buttons and count widgets."""

    def __init__(self, testlist):
        super().__init__(testlist)
        self.testlist = testlist

        self._add_button("Expand All", tk.TOP)
        self._add_button("Collapse All", tk.TOP)

        self.counts = Counts(self, testlist)
        self.counts.pack(side=tk.BOTTOM)

        self._add_button("Invert Selection", tk.BOTTOM)
        self._add_button("Unselect All", tk.BOTTOM)
        self._add_button("Select All", tk.BOTTOM)

    def _add_button(self, text, side):
        """Creates a single button."""
        # Convert the button text to snake case to match a method name.
        snake = text.lower().replace(" ", "_")
        func = getattr(self, f"_on_{snake}")

        btn = tkwidget.Button(
            self,
            text=text,
            command=func,
        )
        btn.pack(
            fill=tk.X,
            side=side,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )

    def _on_expand_all(self):
        """Event handler for the Expand All Button."""
        for iid in self.testlist.get_descendants():
            self.testlist.tree.ttv_see(iid)

    def _on_collapse_all(self):
        """Event handler for the Collapse All Button."""
        for iid in self.testlist.get_descendants():
            self.testlist.tree.ttv_item(iid, open=tk.FALSE)

    def _on_select_all(self):
        """Event handler for the Select All button."""
        self.testlist.tree.ttv_selection_set(*self.testlist.get_descendants())

    def _on_unselect_all(self):
        """Event handler for the Unselect All button."""
        self.testlist.unselect_all()

    def _on_invert_selection(self):
        """Event handler for the Invert Selection button."""
        unselected = self.testlist.all_tests.difference(self.testlist.selected_tests)
        self.testlist.tree.ttv_selection_set(*unselected)


class Counts(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Widgets displaying treeview item quantities."""

    def __init__(self, parent, testlist):
        super().__init__(parent)
        self.testlist = testlist
        testlist.tree.bind("<<TreeviewSelect>>", self._on_select_change)
        self.total = self._add_field("Total", 0)
        self.sel = self._add_field("Selected", 1)

    def _add_field(self, title, row):
        """Creates a count field."""
        label = tkwidget.Label(self, text=f"{title}:")
        label.grid(row=row, column=0, sticky=tk.E)

        var = tkwidget.IntVar()
        value = tk.Label(self, textvariable=var)
        value.grid(row=row, column=1, sticky=tk.W)

        return var

    def adjust_total(self, amount):
        """Adjusts the total count."""
        prev = self.total.get()
        self.total.set(prev + amount)

    def _on_select_change(self, _event):
        """Event handler for tree selection changes."""
        self.sel.set(len(self.testlist.selected_tests))
