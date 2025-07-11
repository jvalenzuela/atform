# Miscellaneous unit test utilities.


import atform
from atform import label
import collections
import contextlib
import io
from PIL import Image
import unittest
from unittest.mock import patch


# Limit the number of worker processes spawned during unit tests.
# This patch remains throughout all unit tests; see comment on patched
# constant for additional detail.
patch("atform.parallelbuild.Builder.MAX_WORKERS", new=1).start()


def reset():
    """Resets the atform package back to its initial state.

    This is used because many atform modules store configuration state
    in global variables, which are only initialized when first imported,
    while unit test cases require this initial condition many times
    after a single import.
    """
    atform.state.init()
    atform.cache.data = None
    atform.vcs.version = None

    # The image cache needs to be reset separately as it is not stored
    # in the state module.
    atform.image.load.cache_clear()


def get_test_content():
    """Retrieves the content of the most recently created test."""
    ids = sorted(atform.state.tests.keys())
    return atform.state.tests[ids[-1]]


def mock_build(test, *args):
    """Dummy PDF build function to inhibit generating actual output files."""
    return {test.id: 1}


def no_pdf_output(method):
    """Test case decorator to prevent generating unnecessary output files."""

    @patch("atform.gen.pdf.build", new=mock_build)
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)

    return wrapper


def disable_idlock(method):
    """Test case decorator to disable all ID lock file operations."""

    def wrapper(self, *args, **kwargs):
        with patch("atform.idlock.verify", return_value=None):
            method(self, *args, **kwargs)

    return wrapper


def mock_argv(args):
    """Generates a simulated set of command line arguments.

    Typically used to patch sys.argv.
    """
    # A dummy script name is inserted as argv[0] to support tests that
    # run the example scripts via runpy, which alters argv[0]. This first
    # item is stripped off before actual argument parsing.
    argv = [""]
    argv.extend(args.split())
    return argv


def no_args(method):
    """Test case decorator to simulate no command line arguments.

    This needs to be used for tests that call generate() and are not otherwise
    patching sys.argv with an explicit set of mock arguments because the
    original sys.argv will not contain valid arguments during unit testing.
    """

    def wrapper(self, *args, **kwargs):
        with patch("sys.argv", mock_argv("")):
            method(self, *args, **kwargs)

    return wrapper


@contextlib.contextmanager
def mock_image(fmt, size, include_dpi=True):
    """Context manager for simulating a mock image file."""
    # Generate an in-memory image.
    img = Image.new(mode="RGB", size=size)
    kwargs = {"format": fmt}
    if include_dpi:
        kwargs["dpi"] = (100, 100)
    buf = io.BytesIO()
    img.save(buf, **kwargs)
    buf.seek(0)

    # Path open() in the image module to return the in-memory image.
    open_patch = patch("atform.image.OPEN", return_value=buf)
    open_patch.start()

    try:
        yield
    finally:
        open_patch.stop()


class ContentAreaException(unittest.TestCase):
    """
    Base class for testing functions only available in the setup area to
    ensure an exception is raised when called outside of setup.
    """

    def setUp(self):
        reset()

    def test_after_test_created(self):
        """Confirm exception if called after a test is created."""
        atform.add_test("title")
        with self.assertRaises(atform.error.UserScriptError):
            self.call()

    def test_after_section(self):
        """Confirm exception if called after a section is created."""
        atform.set_id_depth(2)
        atform.section(1)
        with self.assertRaises(atform.error.UserScriptError):
            self.call()


def click_button(mock_button, text):
    """Simulates clicking a Tk button.

    Requires tk.Button to have been patched with a Mock, and the button
    action defined with the command parameter instead of bind().
    """
    for _args, kwargs in mock_button.call_args_list:
        if kwargs["text"] == text:
            kwargs["command"]()


def set_checkbox(parent, text, state):
    """Sets the state of a Tk checkbox widget."""
    checkbox = find_widget_by_text(parent, text)
    if state:
        checkbox.select()
    else:
        checkbox.deselect()


def find_widget_by_text(parent, text):
    """Locates a Tk widget by its statically assigned text."""
    config = parent.config()
    try:
        if config["text"][-1] == text:
            return parent
    except KeyError:
        pass

    for child in parent.winfo_children():
        widget = find_widget_by_text(child, text)
        if widget is not None:
            return widget

    return None


def find_widget_by_class(parent, cls_name):
    """Locates a Tk widget by class name."""
    if parent.winfo_class() == cls_name:
        return parent

    for child in parent.winfo_children():
        widget = find_widget_by_class(child, cls_name)
        if widget is not None:
            return widget

    return None
