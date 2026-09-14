"""
This module implements the GUI tab allowing test selection based on their
association with defined terms.
"""

import tkinter as tk

from . import buildlist
from . import common
from . import scrolltree
from .. import term
from . import tkwidget


class SelectTerm(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Top-level panel containing all widgets."""

    def __init__(self, parent):
        super().__init__(parent)
        tree = self._create_list()
        self._create_add_button(tree)

    def _create_list(self):
        """Creates the treeview widget listing all terms."""
        frame = tkwidget.Frame(self)
        tree = TermList(frame)
        frame.pack(
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
            fill=tk.BOTH,
            expand=tk.TRUE,
        )
        return tree

    def _create_add_button(self, tree):
        """Creates the add to build button."""
        btn = tkwidget.Button(
            self,
            text="Add Selected Terms To Build",
            command=lambda: buildlist.add(tree.selected_tests),
        )
        btn.pack(
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
            fill=tk.X,
        )


class TermList(scrolltree.ScrollTree):  # pylint: disable=too-many-ancestors
    """Tree listing all terms."""

    def __init__(self, parent):
        super().__init__(parent, columns=["qty"])

        # Sets of test ID tuples associated with each tree item;
        # keyed by tree item ID(iid).
        self.tests = {}

        self._config_columns()
        self._populate()
        self.fit_columns()

    def _config_columns(self):
        """Configures the treeview columns."""
        self.heading("#0", text="Term", anchor=tk.W)
        self.heading("qty", text="Test Qty", anchor=tk.W)
        self.column("qty", stretch=tk.FALSE)

    def _populate(self):
        """Populates the list with all defined terms."""
        for label in sorted(term.terms, key=lambda lbl: term.terms[lbl].raw):
            self._add_term(label)

    def _add_term(self, label):
        """Adds a single term to the list."""
        # Gather the test IDs associated with the term.
        support_tests = term.supporting_tests[label]
        use_tests = term.used_terms[label]
        term_tests = support_tests.union(use_tests)

        # Add the items to the treeview.
        term_iid = self.insert(
            "",
            tk.END,
            text=term.terms[label].raw,
            values=[str(len(term_tests))],
        )
        support_iid = self.insert(
            term_iid,
            tk.END,
            text="Support",
            values=[str(len(support_tests))],
        )
        use_iid = self.insert(
            term_iid,
            tk.END,
            text="Use",
            values=[str(len(use_tests))],
        )

        self.tests[support_iid] = support_tests
        self.tests[use_iid] = use_tests
        self.tests[term_iid] = term_tests

    @property
    def selected_tests(self):
        """Returns test IDs associated with the selected terms."""
        test_ids = set()
        for iid in self.selection():
            test_ids.update(self.tests[iid])
        return test_ids
