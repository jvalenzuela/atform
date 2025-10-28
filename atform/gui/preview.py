"""Test document previewer."""

import functools
import re
import tkinter as tk
import tkinter.font as tkfont

from .. import state
from ..pdf import paragraph
from . import tkwidget


def show(tid):
    """Shows a given test in the preview window."""
    Preview.instance.show(tid)


def skip_if_empty(func):
    """
    Decorator for methods generating section content to omit the section
    if it would be empty.
    """

    @functools.wraps(func)
    def wrapper(self, data, *args, **kwargs):
        if data:
            func(self, data, *args, **kwargs)

    return wrapper


class Preview(tkwidget.LabelFrame):  # pylint: disable=too-many-ancestors
    """Top-level widget housing all preview elements.

    This object is intended to be a singleton, i.e., only one instance is
    allowed.
    """

    # Width of the text display, in characters. Chosen based on
    # general recommendations for readability.
    TEXT_WIDTH = 60

    def __init__(self, parent):
        super().__init__(parent, text="Preview")
        self.title = self._create_title()
        self.text = self._create_text()
        self.src_location = Location(self)
        self.src_location.pack(anchor=tk.NW)
        self._configure_tags()

        # Store this instance so the previewer is accessible at module level.
        Preview.instance = self

    def _create_title(self):
        """Creates a title bar displaying the test ID/title."""
        var = tkwidget.StringVar()
        font = tkfont.Font(weight=tkfont.BOLD)
        label = tkwidget.Label(self, textvariable=var, font=font)
        label.pack(anchor=tk.NW)
        return var

    def _create_text(self):
        """Creates the text window displaying test content."""
        text = tkwidget.ScrolledText(self, state=tk.DISABLED, width=self.TEXT_WIDTH)
        text.pack(fill=tk.Y, expand=tk.TRUE)
        return text

    def _configure_tags(self):
        """Creates formatting tags used in the text widget."""
        font = tkfont.Font(weight=tkfont.BOLD, underline=1)
        self.text.tag_config("section", font=font)

    def show(self, tid):
        """Diplays test content for a given ID."""
        test = state.tests[tid]
        self.title.set(test.full_name)
        self.src_location.show(test)

        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        self._objective(test.objective)
        self._references(test.references)
        self._environment(test.fields)
        self._equipment(test.equipment)
        self._preconditions(test.preconditions)
        self._procedure(test.procedure)

        self.text.configure(state=tk.DISABLED)

    def _section(self, title):
        """Creates a section header."""
        # Add leading space to all sections except the first.
        if self.text.tag_ranges("section"):
            self._skip_line()

        self._append_text(f"{title.title()}\n", "section")

    @skip_if_empty
    def _objective(self, obj):
        """Adds the Objective section."""
        self._section("Objective")
        text = normalize_text(obj)
        self._append_text(text)

    @skip_if_empty
    def _references(self, refs):
        """Adds the References section."""
        self._section("References")
        for i, ref in enumerate(refs):
            # Add vertical space above each item, except the first.
            if i:
                self._skip_line()

            items = ", ".join(ref.items)
            self._append_text(f"{ref.title}: {items}")

    @skip_if_empty
    def _environment(self, fields):
        """Adds the Environment section."""
        self._section("Environment")
        for f in fields:
            self._append_text(f"{f.title} ___\n")

    @skip_if_empty
    def _equipment(self, items):
        """Adds the Equipment section."""
        self._section("Equipment")
        self._bullet_list(items)

    @skip_if_empty
    def _preconditions(self, items):
        """Adds the Preconditions section."""
        self._section("Preconditions")
        self._bullet_list(items)

    @skip_if_empty
    def _procedure(self, steps):
        """Adds the Procedure section."""
        self._section("Procedure")
        for i, step in enumerate(steps, start=1):
            # Add vertical space above each step, except the first.
            if i > 1:
                self._skip_line()

            text = normalize_text(step.text)
            self._append_text(f"{i}. {text}")

            for f in step.fields:
                self._append_text(f"\n{f.title} ___ {f.suffix}")

    def _bullet_list(self, items):
        """Adds a bullet list to the text display."""
        for i, text in enumerate(items):
            # Add vertical space above each step, except the first.
            if i:
                self._skip_line()

            text = normalize_text(text)
            self._append_text(f"\u2022 {text}")

    def _append_text(self, text, tag=None):
        """Adds a string to the end of the text display."""
        # Convert any tag into a tuple.
        if tag:
            tag = (tag,)

        self.text.insert(tk.END, text, tag)

    def _skip_line(self):
        """Appends a empty line."""
        self._append_text("\n\n")


def normalize_text(s):
    """Separates paragraphs with a blank line and collapses whitespace."""
    paragraphs = [re.sub(r"\s+", " ", p) for p in paragraph.split_paragraphs(s)]
    return "\n\n".join(paragraphs)


class Location(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Widgets to display source file location."""

    def __init__(self, parent):
        super().__init__(parent)
        self.row = 0
        self.file = self._add_field("File")
        self.lineno = self._add_field("Line Number")

    def _add_field(self, title):
        """Adds a set of widgets to display a single value."""
        label = tkwidget.Label(self, text=f"{title}:")
        label.grid(row=self.row, column=0, sticky=tk.E)

        var = tkwidget.StringVar()
        value = tkwidget.Label(self, textvariable=var)
        value.grid(row=self.row, column=1, sticky=tk.W)

        self.row += 1
        return var

    def show(self, test):
        """Displays the source location of a given test."""
        self.file.set(test.call_frame.filename)
        self.lineno.set(str(test.call_frame.lineno))
