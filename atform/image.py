# This module handles processing user-provided images.


import collections
import io

import PIL
from reportlab.lib.units import inch
from reportlab.platypus import Image

from . import error
from . import misc
from . import state


# Data type for storing two-dimensional sizes.
ImageSize = collections.namedtuple('ImageSize', ['width', 'height'])


# Largest allowable logo image size, in inches.
MAX_LOGO_SIZE = ImageSize(2.0, 1.5)


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_logo(path):
    """Selects an image file to be used as the logo.

    The logo will appear on the first page of every test in the
    upper-left corner.

    The image must be a JPEG file with embedded metadata specifying DPI,
    and may not exceed |max_logo_width| inches wide by |max_logo_height|
    inches high. |project_name| will not scale or crop the image; the onus is
    on the user to construct a logo suitable for presentation within
    the allowable area.

    .. seealso:: :ref:`setup`

    Args:
        path (str): Path to the image file.
    """
    if state.logo:
        raise error.UserScriptError(
            "Duplicate logo definition.",
            """
            atform.add_logo() can only be called once to define a single
            logo image.
            """,
        )

    # BytesIO are allowed to support unit testing.
    if not isinstance(path, str) and not isinstance(path, io.BytesIO):
        raise error.UserScriptError(
            f"Invalid path data type: {type(path).__name__}",
            "Path to the logo image file must be a string.",
        )

    try:
        image = PIL.Image.open(path, formats=["JPEG"])
    except FileNotFoundError as e:
        raise error.UserScriptError(
            f"Logo image file not found: {path}",
        ) from e
    except PIL.UnidentifiedImageError as e:
        raise error.UserScriptError(
            f"Unsupported logo image format: {path}",
            "Logo image file must be a JPEG.",
        ) from e
    try:
        dpi_raw = image.info["dpi"]
    except KeyError as e:
        raise error.UserScriptError(
            "No DPI information found in logo image file.",
            "Ensure the logo image file has embedded DPI metadata."
        ) from e

    # Ensure DPI values are floats.
    dpi = ImageSize(*[float(i) for i in dpi_raw])

    size = ImageSize(
        image.width / dpi.width,
        image.height / dpi.height
    )

    if ((size.width > MAX_LOGO_SIZE.width)
        or (size.height > MAX_LOGO_SIZE.height)):
        raise error.UserScriptError(
            f"""
            Logo image is too large:
            {size.width:.3} x {size.height:.3} (inch)""",
            f"""
            Reduce the logo image size to within {MAX_LOGO_SIZE.width} inch
            wide and {MAX_LOGO_SIZE.height} inch high.
            """,
        )

    # Dump the JPEG data to an in-memory buffer and convert to a Reportlab
    # Image object.
    buf = io.BytesIO()
    image.save(
        buf,
        format="JPEG",
        quality="keep",
        dpi=dpi,
    )
    state.logo = Image(
        buf,
        width=size.width*inch,
        height=size.height*inch,
    )
