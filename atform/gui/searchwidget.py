"""Frontend interface for test content searches."""

import tkinter as tk

from . import buildlist
from . import common
from . import search
from . import tkwidget


class Search(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Top-level widget containing the entire search panel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.search = search.TestContentSearch()
        self.entry = self._create_text_entry()
        self.result_msg = self._create_result_message()
        self.combine = self._create_combination_select()
        self.match_case = self._create_case_match()
        self.sections = SectionSelect(self)
        self._create_add_button()

    def _create_text_entry(self):
        """Creates the search text entry field."""
        entry = tkwidget.Entry(
            self,
            validate="key",
            validatecommand=self._validate_text,
        )
        entry.pack(
            fill=tk.X,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )
        entry.bind("<KeyPress-Return>", self._add)
        return entry

    def _validate_text(self):
        """Text entry validation function.

        Called each time the text content is altered. Serves only to clear
        the result message; the text is unconditionally considered valid.
        """
        self.result_msg.set("")
        return tk.TRUE

    def _create_case_match(self):
        """Creates the case-sensitive option."""
        var = tkwidget.BooleanVar()
        cbox = tkwidget.Checkbutton(
            self,
            text="Case-sensitive",
            variable=var,
        )
        cbox.pack(anchor=tk.W)
        return var

    def _create_result_message(self):
        """Creates a label displaying the match result."""
        var = tkwidget.StringVar()
        label = tkwidget.Label(self, textvariable=var)
        label.pack(anchor=tk.W)
        return var

    def _create_combination_select(self):
        """Creates the any/all combination selectors."""
        frame = tkwidget.Frame(self)
        frame.pack(anchor=tk.W)
        var = tkwidget.IntVar()

        and_button = tkwidget.Radiobutton(
            frame,
            text="Match all",
            variable=var,
            value=search.Grouping.ALL,
        )
        and_button.pack(side=tk.LEFT)

        or_button = tkwidget.Radiobutton(
            frame,
            text="Match any",
            variable=var,
            value=search.Grouping.ANY,
        )
        or_button.pack(side=tk.LEFT, padx=common.LARGE_PAD)

        var.set(search.Grouping.ALL)  # Set initial selection.
        return var

    def _create_add_button(self):
        """Creates the add button."""
        btn = tkwidget.Button(
            self,
            text="Add Matching Tests To Build",
            command=self._add,
        )
        btn.pack(
            fill=tk.X,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )

    def _add(self, _event=None):
        """Handler for the add button and text field Enter keypresses."""
        text = self.entry.get().strip()
        sections = self.sections.selected
        if not text:
            self.result_msg.set("Query text is blank.")
        elif not sections:
            self.result_msg.set("No sections enabled to search.")
        else:
            matches = self.search.search(
                text,
                sections,
                self.combine.get(),
                self.match_case.get(),
            )
            buildlist.add(matches)
            self.result_msg.set(f"Matched {len(matches)} test(s).")


class SectionSelect(tkwidget.LabelFrame):  # pylint: disable=too-many-ancestors
    """Panel of checkboxes allowing test section selection."""

    def __init__(self, parent):
        super().__init__(parent, text="Sections")
        self.pack(
            fill=tk.X,
            padx=common.SMALL_PAD,
            pady=common.SMALL_PAD,
        )
        self.vars = [self._add_checkbox(s) for s in search.SECTIONS]

    def _add_checkbox(self, label):
        """Creates a single checkbox for a section."""
        var = tkwidget.StringVar()
        var.set(label)  # Checkbox is initially checked.
        cbox = tkwidget.Checkbutton(
            self,
            text=label,
            offvalue="",
            onvalue=label,
            variable=var,
        )
        cbox.pack(anchor=tk.W)
        return var

    @property
    def selected(self):
        """Returns a set of selected sections."""
        return {v.get() for v in self.vars if v.get()}
