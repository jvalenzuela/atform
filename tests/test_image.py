# Unit tests for the image module.


from tests import utils
import atform
import io
import os
import unittest
from unittest.mock import patch


class ErrorBase:
    """Base class for testing errors with user-specified images."""

    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            self.call(42)

    def test_file_not_found(self):
        """Confirm exception if path points to a nonexistent file."""
        with self.assertRaises(atform.error.UserScriptError):
            self.call("spam")

    def test_non_image(self):
        """Confirm exception for a file that is not an image format."""
        with self.assertRaises(atform.error.UserScriptError):
            buf = io.BytesIO(b"foo bar")
            with patch("atform.image.open", return_value=buf):
                self.call("")

    def test_unsupported_format(self):
        """Confirm exception if the image file is not a supported format."""
        with self.assertRaises(atform.error.UserScriptError):
            with utils.mock_image("BMP", (1, 1)):
                self.call("")


class AddLogo(unittest.TestCase, ErrorBase):
    """Unit tests for the add_logo() function."""

    def setUp(self):
        utils.reset()

    def call(self, img):
        """ErrorBase callback method adding a logo with a given image."""
        atform.add_logo(img)

    def test_multiple_call(self):
        """Confirm exception if called more than once."""
        with utils.mock_image("JPEG", (1, 1)):
            atform.add_logo("")
        with self.assertRaises(atform.error.UserScriptError):
            with utils.mock_image("JPEG", (1, 1)):
                atform.add_logo("")


class ProcedureStep(unittest.TestCase, ErrorBase):
    """Tests for procedure step images."""

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

        self.assertIs(t1.procedure[0].image_hash, t1.procedure[1].image_hash)
        self.assertIs(t1.procedure[0].image_hash, t2.procedure[0].image_hash)


class AddLogoContentAreaException(utils.ContentAreaException):
    """
    Tests to confirm exceptions when calling add_logo() outside of the
    setup area.
    """

    @staticmethod
    def call():
        with utils.mock_image("JPEG", (100, 100)):
            atform.add_logo("")
