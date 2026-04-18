# Unit tests for the content module.


from tests import utils
import atform
import contextlib
import io
import unittest
from unittest.mock import patch


class Generate(unittest.TestCase):
    """Unit tests for the generate() function."""

    @utils.disable_idlock
    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.generate(path=42)

    @utils.disable_idlock
    @utils.no_args
    @patch("concurrent.futures.Future.result")
    def test_cli_build_error(self, mock_result):
        """Confirm CLI build errors are output to standard error."""
        # Actual build errors cannot be mocked because they are raised in
        # worker processes, i.e., a patch made here would not propagate to
        # the worker process. Instead, Future.result() is mocked
        # to raise the exception that would come back from the worker
        # process.
        mock_result.side_effect = atform.pdf.doc.BuildError("spam")
        atform.add_test("foo")
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            atform.generate()
            self.assertEqual("spam", stderr.getvalue().strip())


class GenerateFolderDepth(unittest.TestCase):
    """Unit tests for the folder_depth parameter of generate()."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    def test_invalid_type(self):
        """Confirm exception for a non-integer argument."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.generate(folder_depth="foo")

    @utils.disable_idlock
    def test_negative(self):
        """Confirm exception for a negative argument."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.generate(folder_depth=-1)

    @utils.disable_idlock
    def test_too_large(self):
        """Confirm exception for values greater than or equal to the id depth."""
        atform.set_id_depth(3)
        for i in [3, 4]:
            with self.subTest(i=i):
                with self.assertRaises(atform.error.UserScriptError):
                    atform.generate(folder_depth=i)
