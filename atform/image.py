"""Handling for user-provided image files.

All images are stored in the global state dictionary, keyed by the image
file hash. Using a hash value allows the image to be stored in, and compared
with the cache file without storing the entire image data in the cache file.
"""

import functools
import hashlib
import io

import PIL

from . import error
from . import misc
from . import state


# Allowable image formats.
FORMATS = ["JPEG", "PNG"]


# Type alias for hashes used to identify specific images.
ImageHashType = bytes


# Mapping of all loaded images.
#
# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
images: dict[ImageHashType, bytes] = {}


@functools.cache
def load(path):
    """Loads and validates an image file."""
    # BytesIO are allowed to support unit testing.
    if not isinstance(path, str) and not isinstance(path, io.BytesIO):
        raise error.UserScriptError(
            f"Invalid path data type: {type(path).__name__}",
            "Path to the image file must be a string.",
        )

    try:
        with open(path, "rb") as f:
            raw = f.read()
            img_hash = calc_hash(raw)
            image = PIL.Image.open(f, formats=FORMATS)

            # Ensures the entire image is loaded into memory so the
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

    images[img_hash] = raw
    return img_hash


def calc_hash(raw):
    """Computes the hash of an image file."""
    h = hashlib.blake2b()
    h.update(raw)
    return h.digest()


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

    state.logo_hash = load(path)
