"""Test document previewer."""

import functools
import io
import tkinter as tk

import pymupdf
from reportlab.lib.units import toLength

from .. import addtest
from . import common
from .. import pdf
from . import tkwidget


def show(tid):
    """Shows a given test in the preview window."""
    Preview.instance.show(tid)


class Preview(tkwidget.LabelFrame):  # pylint: disable=too-many-ancestors
    """Top-level widget housing all preview elements.

    This object is intended to be a singleton, i.e., only one instance is
    allowed.
    """

    def __init__(self, parent):
        super().__init__(parent, text="Preview")
        self.pages = PageDisplay(self)
        self.pages.pack(fill=tk.Y, expand=tk.TRUE)
        self.src_location = Location(self)
        self.src_location.pack(anchor=tk.NW)

        # Store this instance so the previewer is accessible at module level.
        Preview.instance = self

    def show(self, tid):
        """Diplays test content for a given ID."""
        test = addtest.tests[tid]
        self.pages.show(tid)
        self.src_location.show(test)


class PageDisplay(tkwidget.Frame):  # pylint: disable=too-many-ancestors
    """Widget displaying page content."""

    # PDF conversion resolution. Chosen to provide reasonable legibility of
    # regular text.
    DPI = 75

    # Amount of vertical space in pixels to leave between pages.
    PAGE_SEP = 10

    def __init__(self, parent):
        super().__init__(parent)

        # Initialize the PDF generation module.
        pdf.init(pdf.build_init_data())

        self.canvas = tkwidget.Canvas(
            self,
            width=self._canvas_width,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.Y)
        common.add_vertical_scrollbar(self, self.canvas)

    @property
    def _canvas_width(self):
        """Computes the canvas width required to contain a single page."""
        return int(self.DPI * pdf.layout.PAGE_SIZE[0] / toLength("1 in"))

    def show(self, tid):
        """Displays pages of the given test."""
        self._clear()
        for i, page in enumerate(self._page_images(tid)):
            y = i * (page.height() + self.PAGE_SEP)
            self.canvas.create_image((0, y), anchor=tk.NW, image=page)
        self._reset_scroll()

    def _clear(self):
        """Empties the canvas."""
        self.canvas.delete(tk.ALL)

    @functools.cache  # pylint: disable=method-cache-max-size-none
    def _page_images(self, tid):
        """Generates a set of images of the pages for a given test."""
        # Build the PDF to an in-memory buffer.
        buf = io.BytesIO()
        pdf.build(addtest.tests[tid], 1, buf)

        # Convert the PDF to a set of raster images, one per page.
        doc = pymupdf.Document(stream=buf)
        pixmaps = [page.get_pixmap(dpi=self.DPI) for page in doc.pages()]

        # ppm output format per PyMuPDF recommendation, ref:
        # https://pymupdf.readthedocs.io/en/latest/pixmap.html#pixmapoutput
        return [tk.PhotoImage(data=pm.tobytes("ppm")) for pm in pixmaps]

    def _reset_scroll(self):
        """Updates the scrollbar based on the displayed pages."""
        # Limit the scroll region to the displayed pages.
        region = self.canvas.bbox(tk.ALL)
        self.canvas.config(scrollregion=region)

        # Reset the view back to the first page.
        self.canvas.yview(tk.MOVETO, 0)


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
