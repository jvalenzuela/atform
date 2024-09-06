# Unit tests for the image module.


from tests import utils
import atform
import io
import os
import unittest
import PIL


def make_image_file(img, **kwargs):
    """Generates a buffer containing a mock image file."""
    buf = io.BytesIO()
    img.save(buf, **kwargs)
    return buf


class AddLogo(unittest.TestCase):
    """Unit tests for the add_logo() function."""

    def setUp(self):
        utils.reset()

    def test_multiple_call(self):
        """Confirm exception if called more than once."""
        img = PIL.Image.new(mode="RGB", size=(100, 100))
        f = make_image_file(img, format="JPEG", dpi=(100, 100))
        atform.add_logo(f)
        with self.assertRaises(SystemExit):
            atform.add_logo(f)

    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(SystemExit):
            atform.add_logo(42)

    def test_file_not_found(self):
        """Confirm exception if path points to a nonexistent file."""
        with self.assertRaises(SystemExit):
            atform.add_logo("spam")

    def test_non_image(self):
        """Confirm exception for a file that is not an image format."""
        with self.assertRaises(SystemExit):
            atform.add_logo("foo".encode())

    def test_not_jpeg(self):
        """Confirm exception if the image file is not a JPEG."""
        img = PIL.Image.new(mode="RGB", size=(100, 100))
        f = make_image_file(img, format="PNG", dpi=(100, 100))
        with self.assertRaises(SystemExit):
            atform.add_logo(f)

    def test_no_dpi(self):
        """Confirm exception if the image file lacks DPI metadata."""
        img = PIL.Image.new(mode="RGB", size=(100, 100))
        f = make_image_file(img, format="JPEG")
        with self.assertRaises(SystemExit):
            atform.add_logo(f)

    def test_too_wide(self):
        """Confirm exception if the image is too wide."""
        img = PIL.Image.new(mode="RGB", size=(205, 100))
        f = make_image_file(img, format="JPEG", dpi=(100, 100))
        with self.assertRaises(SystemExit):
            atform.add_logo(f)

    def test_too_high(self):
        """Confirm exception of the image is too high."""
        img = PIL.Image.new(mode="RGB", size=(100, 155))
        f = make_image_file(img, format="JPEG", dpi=(100, 100))
        with self.assertRaises(SystemExit):
            atform.add_logo(f)


class AddLogoContentAreaException(utils.ContentAreaException):
    """
    Tests to confirm exceptions when calling add_logo() outside of the
    setup area.
    """

    @staticmethod
    def call():
        img = PIL.Image.new(mode="RGB", size=(100, 100))
        f = make_image_file(img, format="JPEG", dpi=(100, 100))
        atform.add_logo(f)
