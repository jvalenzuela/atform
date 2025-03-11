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


class ErrorBase:
    """Base class for testing errors with user-specified images."""

    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(SystemExit):
            self.call(42)

    def test_file_not_found(self):
        """Confirm exception if path points to a nonexistent file."""
        with self.assertRaises(SystemExit):
            self.call("spam")

    def test_non_image(self):
        """Confirm exception for a file that is not an image format."""
        with self.assertRaises(SystemExit):
            self.call("foo".encode())

    def test_unsupported_format(self):
        """Confirm exception if the image file is not a supported format."""
        img = PIL.Image.new(mode="RGB", size=(1, 1))
        f = make_image_file(img, format="BMP", dpi=(100, 100))
        with self.assertRaises(SystemExit):
            self.call(f)

    def test_supported_formats(self):
        """Confirm supported image formats are accepted."""
        img = PIL.Image.new(mode="RGB", size=(1, 1))
        for fmt in atform.image.FORMATS:
            with self.subTest(fmt=fmt):
                f = make_image_file(img, format=fmt, dpi=(100, 100))
                utils.reset()
                self.call(f)

    def test_no_dpi(self):
        """Confirm exception if the image file lacks DPI metadata."""
        img = PIL.Image.new(mode="RGB", size=(1, 1))
        for fmt in atform.image.FORMATS:
            with self.subTest(fmt=fmt):
                f = make_image_file(img, format=fmt)
                utils.reset()
                with self.assertRaises(SystemExit):
                    self.call(f)

    def test_too_large(self):
        """Confirm exception if the image is too large.

        This test is only run with JPEG images because DPI information
        for PNG images is metric, making it impossible to generate images
        of max size + 1 pixel.
        """
        sizes = [
            (self.TOO_WIDE, 1),
            (1, self.TOO_HIGH),
            (self.TOO_WIDE, self.TOO_HIGH),
        ]
        for size in sizes:
            with self.subTest(size=size):
                img = PIL.Image.new(mode="RGB", size=size)
                f = make_image_file(img, format="JPEG", dpi=(100, 100))
                with self.assertRaises(SystemExit):
                    self.call(f)


class AddLogo(unittest.TestCase, ErrorBase):
    """Unit tests for the add_logo() function."""

    # Excessive image sizes required by ErrorBase, assuming 100 DPI.
    TOO_WIDE = 201
    TOO_HIGH = 151

    def setUp(self):
        utils.reset()

    def call(self, img):
        """ErrorBase callback method adding a logo with a given image."""
        atform.add_logo(img)

    def test_multiple_call(self):
        """Confirm exception if called more than once."""
        img = PIL.Image.new(mode="RGB", size=(1, 1))
        f = make_image_file(img, format="JPEG", dpi=(100, 100))
        atform.add_logo(f)
        with self.assertRaises(SystemExit):
            atform.add_logo(f)


class ProcedureStep(unittest.TestCase, ErrorBase):
    """Tests for procedure step images."""

    # Excessive image sizes required by ErrorBase, assuming 100 DPI.
    TOO_WIDE = 501
    TOO_HIGH = 301

    def setUp(self):
        utils.reset()

    def call(self, img):
        """ErrorBase callback method creating a test procedure with a given image."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "text",
                    "image": img,
                }
            ],
        )

    def test_cache(self):
        """Confirm the same image path given to multiple procedure steps yield the same image object."""
        step = {
            "text": "step",
            "image": os.path.join("tests", "images", "procedure", "small.jpg"),
        }

        atform.add_test("t1", procedure=[step, step])
        t1 = utils.get_test_content()

        atform.add_test("t2", procedure=[step])
        t2 = utils.get_test_content()

        self.assertIs(t1.procedure[0].image, t1.procedure[1].image)
        self.assertIs(t1.procedure[0].image, t2.procedure[0].image)


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
