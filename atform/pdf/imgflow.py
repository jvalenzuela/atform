"""This module converts raw image data into ReportLab flowables."""

import collections
import io

import PIL
from reportlab.lib.units import inch
import reportlab.platypus


# Raw image data keyed by hash. This is the same content as the image.images
# dict, but populated by doc.init() to accommodate running in a worker process.
IMAGES = {}


# Data type for storing two-dimensional sizes.
ImageSize = collections.namedtuple("ImageSize", ["width", "height"])


def get_flowable(hash_, max_size):
    """Converts raw image data into a ReportLab image flowable."""
    buf = io.BytesIO(IMAGES[hash_])
    size = calculate_size(buf, max_size)
    return reportlab.platypus.Image(
        buf,
        width=size.width * inch,
        height=size.height * inch,
    )


def calculate_size(buf, max_size):
    """Computes the target image size to fit within a maximum size.

    Uses one of the following methods:

    1. The image's physical size cannot be determined if it contains no DPI
       information, so it is unconditionally scaled to the maximum size.

    2. The original size is retained if it fits within the maximum size.

    3. The image is scaled to the maximum size.

    The original aspect ratio is preserved during any scaling.
    """
    img = PIL.Image.open(buf)

    # PNG formats require calling load() to ensure EXIF data is available
    # in the info attribute. The call is unconditional for simplicity as
    # there's no downside to callling it regardless of format.
    img.load()

    try:
        dpi = ImageSize(*[float(i) for i in img.info["dpi"]])

    # No DPI information available, use method 1.
    except KeyError:
        size = ImageSize(float(img.width), float(img.height))
        return scale_to_max(size, max_size)

    size = ImageSize(img.width / dpi.width, img.height / dpi.width)

    # Original size fits, use method 2.
    if (size.width <= max_size.height) and (size.height <= max_size.height):
        return size

    return scale_to_max(size, max_size)


def scale_to_max(size, max_size):
    """Scales a size to a maximum physical size."""
    width_ratio = max_size.width / size.width
    height_ratio = max_size.height / size.height
    scale = min(width_ratio, height_ratio)
    return ImageSize(size.width * scale, size.height * scale)
