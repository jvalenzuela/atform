# Miscellaneous unit test utilities.


import atform
from atform import label
import collections
import contextlib
import copy
import importlib
import io
from PIL import Image
import tkinter as tk
import unittest
from unittest.mock import patch


# Limit the number of worker processes spawned during unit tests.
# This patch remains throughout all unit tests; see comment on patched
# constant for additional detail.
patch("atform.parallelbuild.Builder.MAX_WORKERS", new=1).start()


# Attributes outside the state module that also need to be reverted back
# to their initial values during reset.
INIT_ATTRS = [
    (atform.addtest, "tests"),
    (atform.cache, "data"),
    (atform.field, "fields"),
    (atform.id, "section_titles"),
    (atform.image, "images"),
    (atform.vcs, "version"),
]


# Generate a copy of all init attribute values to serve as a template
# when resetting back to the original state.
INIT_VALUES = [copy.copy(getattr(*attr)) for attr in INIT_ATTRS]


def reset():
    """Resets the atform package back to its initial state.

    This is used because many atform modules store configuration state
    in global variables, which are only initialized when first imported,
    while unit test cases require this initial condition many times
    after a single import.
    """
    importlib.reload(atform.state)

    # Reset attributes outside the state module.
    for i, attr in enumerate(INIT_ATTRS):
        setattr(*attr, copy.copy(INIT_VALUES[i]))

    # The image cache needs to be reset separately as it is not stored
    # as a traditional attribute.
    atform.image.load.cache_clear()


def get_test_content():
    """Retrieves the content of the most recently created test."""
    ids = sorted(atform.addtest.tests.keys())
    return atform.addtest.tests[ids[-1]]


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
    open_patch = patch("atform.image.open", return_value=buf)
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


def click_button(parent, text):
    """Simulates clicking a Tk button.

    The target button is located by searching for matching text.
    """
    btn = find_widget_by_text(parent, text)
    btn.invoke()


def set_checkbox(parent, text, state):
    """Sets the state of a Tk checkbox widget."""
    checkbox = find_widget_by_text(parent, text)
    current = "selected" in checkbox.state()
    if state != current:
        checkbox.invoke()


def set_entry_text(parent, text):
    """Populates a Tk Entry widget with a given string.

    Assumes only one Entry widget within the given parent.
    """
    entry = find_widget_by_class(parent, "TEntry")
    entry.delete(0, tk.END)
    entry.insert(tk.END, text)


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
