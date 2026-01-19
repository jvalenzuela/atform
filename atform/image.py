"""Handling for user-provided image files.

All images are stored in the global state dictionary, keyed by the image
file hash. Using a hash value allows the image to be stored in, and compared
with the cache file without storing the entire image data in the cache file.
"""

import collections
import functools
import hashlib
import io
from typing import BinaryIO

import PIL

from . import error
from . import misc
from . import state


# Data type for storing two-dimensional sizes.
ImageSize = collections.namedtuple("ImageSize", ["width", "height"])


# Data and metadata for a single image.
Image = collections.namedtuple("Image", ["size", "data"])


# Largest allowable logo image size, in inches.
MAX_LOGO_SIZE = ImageSize(2.0, 1.5)


# Allowable image formats.
FORMATS = ["JPEG", "PNG"]


# Type alias for hashes used to identify specific images.
ImageHashType = bytes


# Mapping of all loaded images.
#
# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
images: dict[ImageHashType, Image] = {}


@functools.cache
def load(path: str, max_size: ImageSize) -> ImageHashType:
    """Loads and validates an image file."""
    # BytesIO are allowed to support unit testing.
    if not isinstance(path, str) and not isinstance(path, io.BytesIO):
        raise error.UserScriptError(
            f"Invalid path data type: {type(path).__name__}",
            "Path to the image file must be a string.",
        )

    try:
        with open(path, "rb") as f:
            img_hash = calc_hash(f)
            image = PIL.Image.open(f, formats=FORMATS)

            # PNG formats require calling load() to ensure EXIF data is available
            # in the info attribute. The call is unconditional for simplicity as
            # there's no downside to callling it regardless of format.
            # This also ensures the entire image is loaded into memory so the
            # source file object can be closed.
            image.load()
    except FileNotFoundError as e:
        raise error.UserScriptError(
            f"Image file not found: {path}",
        ) from e
    except PIL.UnidentifiedImageError as e:
        raise error.UserScriptError(
            f"Unsupported image format: {path}",
            f"""
            Image file must be one of the following
            formats: {', '.join(FORMATS)}
            """,
        ) from e

    try:
        dpi_raw = image.info["dpi"]
    except KeyError as e:
        raise error.UserScriptError(
            "No DPI information found in image file.",
            "Ensure the image file has embedded DPI metadata.",
        ) from e

    # Ensure DPI values are floats.
    dpi = ImageSize(*[float(i) for i in dpi_raw])

    size = ImageSize(image.width / dpi.width, image.height / dpi.height)

    if (size.width > max_size.width) or (size.height > max_size.height):
        raise error.UserScriptError(
            f"Image is too large: {path}",
            f"""
            Reduce the image size to within {max_size.width} inch
            wide and {max_size.height} inch high.
            """,
        )

    images[img_hash] = convert_image(image, size, dpi)
    return img_hash


def calc_hash(file: BinaryIO) -> ImageHashType:
    """Computes the hash of an image file."""
    h = hashlib.blake2b()
    h.update(file.read())
    return h.digest()


def convert_image(image: PIL.Image.Image, size: ImageSize, dpi: ImageSize) -> Image:
    """Converts a PIL Image into an Image named tuple."""
    buf = io.BytesIO()
    args = {
        "format": image.format,
        "dpi": dpi,
    }
    if image.format == "JPEG":
        args["quality"] = "keep"
    image.save(buf, **args)
    return Image(size=size, data=buf.getvalue())


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_logo(path: str) -> None:
    """Selects an image file to be used as the logo.

    The logo will appear on the first page of every test in the
    upper-left corner. Maximum size is |max_logo_width| inches wide by
    |max_logo_height| inches high.

    .. seealso:: :ref:`setup` and :ref:`image`

    Args:
        path (str): Path to the image file relative to the top-level script
            executed to generate test documents.
    """
    if state.logo_hash:
        raise error.UserScriptError(
            "Duplicate logo definition.",
            """
            atform.add_logo() can only be called once to define a single
            logo image.
            """,
        )

    state.logo_hash = load(path, MAX_LOGO_SIZE)
