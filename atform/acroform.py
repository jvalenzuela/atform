"""PDF form fields.

This module implements ReportLab Flowables containing an AcroForm field.
"""

from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.flowables import Flowable


from .textstyle import (
    point,
    stylesheet,
)


class Checkbox(Flowable):
    """A custom flowable that generates a form checkbox."""

    # Height and width of the box.
    SIZE = 0.25 * inch

    def wrap(self, *_args):
        """Returns the size of the flowable.

        Callback method required for Flowables; called by Platypus.
        """
        return (self.SIZE, self.SIZE)

    def draw(self):
        """Places the flowable onto the canvas.

        Callback method required for Flowables; called by Platypus.
        """
        self.canv.acroForm.checkbox(
            size=self.SIZE,
            relative=True,
        )


class TextEntry(Flowable):
    """Creates an Acroform for entering a single line of text."""

    # Coefficient applied to the font size to calculate box height; set
    # to accommodate descenders.
    HEIGHT_FACTOR = 1.3

    # Additional horizontal size to account for the non-adjustable padding
    # integral to the field.
    EXTRA_WIDTH = 4 * point

    def __init__(self, width, tooltip=None):
        super().__init__()
        self.style = stylesheet["TextField"]
        self.tooltip = tooltip
        self.width = self._calc_width(width)
        self.height = self.style.fontSize * self.HEIGHT_FACTOR

    def _calc_width(self, width):
        """Computes the horizontal size from the width argument.

        The width argument can be provided in two ways:
         - If an integer, width will the sized to hold the same character
           repeated that many times.
         - If a string, width will be sized to hold it.
        """

        # Build the template string from which width will be computed.
        try:
            # Integer width argument; use em dashes for the template.
            template = width * "\u2014"
        except TypeError:
            template = width  # String width argument.

        return self.EXTRA_WIDTH + stringWidth(
            template,
            self.style.fontName,
            self.style.fontSize,
        )

    def wrap(self, *_args):
        """Returns the size of the flowable.

        Callback method required for Flowables; called by Platypus.
        """
        return (self.width, self.height)

    def draw(self):
        """Places the flowable onto the canvas.

        Callback method required for Flowables; called by Platypus.
        """
        self.canv.acroForm.textfield(
            width=self.width,
            height=self.height,
            fontName=self.style.fontName,
            fontSize=self.style.fontSize,
            borderWidth=0,
            relative=True,
            tooltip=self.tooltip,
        )
