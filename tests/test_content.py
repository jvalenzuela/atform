# Unit tests for the content module.


from tests import utils
import atform
import unittest


class Generate(unittest.TestCase):
    """Unit tests for the generate() function."""

    @utils.disable_idlock
    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(SystemExit):
            atform.generate(path=42)


class GenerateFolderDepth(unittest.TestCase):
    """Unit tests for the folder_depth parameter of generate()."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    def test_invalid_type(self):
        """Confirm exception for a non-integer argument."""
        with self.assertRaises(SystemExit):
            atform.generate(folder_depth="foo")

    @utils.disable_idlock
    def test_negative(self):
        """Confirm exception for a negative argument."""
        with self.assertRaises(SystemExit):
            atform.generate(folder_depth=-1)

    @utils.disable_idlock
    def test_too_large(self):
        """Confirm exception for values greater than or equal to the id depth."""
        atform.set_id_depth(3)
        for i in [3, 4]:
            with self.subTest(i=i):
                with self.assertRaises(SystemExit):
                    atform.generate(folder_depth=i)
