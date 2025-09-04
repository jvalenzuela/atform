"""Interactive GUI tests.

This module contains unit tests impossible or impractical to perform
automatically with the usual assert methods. Instead, each test case
launches the GUI for manual verification.
"""

import concurrent.futures
import functools
import queue
import tkinter as tk
import traceback
import unittest
from unittest.mock import Mock, patch

import atform
from .. import utils


class InteractiveGuiTestCase(unittest.TestCase):
    """Base class for interactive GUI tests.

    Launches the GUI and creates a top-level pass/fail dialog.
    """

    def setUp(self):
        utils.reset()
        self.failed = False

    def start_gui(self, run=True, root=None, instruction=None, buttons=True):
        """Creates the test info dialog and optionally runs the GUI mainloop."""
        if root:
            self.root = root
        else:
            with patch("atform.cache.data", new={}):
                self.root = atform.gui.app.Application(".", 0)

        dialog = tk.Toplevel()
        dialog.transient(root)
        self.add_test_info(dialog, instruction)
        if buttons:
            self.add_buttons(dialog)
        if run:
            self.root.mainloop()

    def add_test_info(self, dialog, instruction):
        """Adds the unit test's information to the dialog."""
        items = [self.id(), self.shortDescription()]
        if instruction:
            items.append(instruction)
        for text in items:
            label = tk.Label(dialog, text=text)
            label.pack(anchor=tk.NW)

    def add_buttons(self, dialog):
        """Creates the pass/fail buttons."""
        frame = tk.Frame(dialog)
        frame.pack()

        pass_ = tk.Button(frame, text="Pass", command=self.on_pass)
        pass_.pack(side=tk.LEFT, padx=10)

        fail = tk.Button(frame, text="Fail", command=self.on_fail)
        fail.pack(side=tk.RIGHT, padx=10)

    def on_pass(self):
        """Handler for the pass button."""
        self.root.destroy()

    def on_fail(self):
        """Handler for the fail button."""
        self.failed = True
        self.root.destroy()

    def tearDown(self):
        if self.failed:
            self.fail("Fail button pressed.")


class TestList(InteractiveGuiTestCase):
    """Tests for the TestList widget."""

    def create_testlist(self):
        """Creates the TestList widget and root window."""
        root = tk.Tk()
        tl = atform.gui.testlist.TestList(root)
        return root, tl

    def test_id_column_width(self):
        """Confirm the select list ID column is wide enough to accommodate the test ID."""
        atform.set_id_depth(3)
        atform.section(1, id=42)
        atform.section(2, id=99)
        atform.skip_test(id=999)
        atform.add_test("title")
        root, tl = self.create_testlist()
        tl.add_test((42, 99, 999))
        self.start_gui(root=root)

    def test_total_count(self):
        """Confirm correct total count display."""
        root, tl = self.create_testlist()
        tl.controls.counts.total.set(42)
        self.start_gui(
            root=root,
            instruction="Verify total count is equal to 42.",
        )

    def test_selected_count(self):
        """Confirm correct selected count display."""
        root, tl = self.create_testlist()
        tl.controls.counts.sel.set(42)
        self.start_gui(
            root=root,
            instruction="Verify selected count is equal to 42.",
        )

    def test_preview(self):
        """Confirm a test is displayed in the Preview window when clicked on in the list of tests.

        This is a manual test because the preview action is bound to
        Treeview tags, which are not easily simulated.
        """
        atform.add_test("title")
        self.start_gui()

    @patch("atform.gui.preview.show")
    def test_multiple_select(self, *_mocks):
        """Confirm multiple items can be simultaneously selected."""
        for i in range(1, 11):
            atform.add_test(f"test {i}")
        root, tl = self.create_testlist()
        for i in range(1, 11):
            tl.add_test((i,))
        self.start_gui(
            root=root,
            instruction="Ensure multiple items can be selected using Shift & Control.",
        )


class Resize(InteractiveGuiTestCase):
    """Window resizing tests."""

    def test_horizontal(self):
        """Confirm correct horizontal resizing."""
        atform.add_test("title")
        self.start_gui(
            instruction="Stretch the window horizontally and ensure the test list title columns and Build path entry expand.",
        )

    def test_vertical(self):
        """Stretch the window vertically and ensure the test lists and preview areas expand."""
        atform.add_test("title")
        self.start_gui()


class Preview(InteractiveGuiTestCase):
    """Preview window tests."""

    def start_preview(self):
        """Launches a Preview instance showing the test content."""
        root = tk.Tk()
        pv = atform.gui.preview.Preview(root)
        pv.pack()
        atform.gui.preview.show((1,))
        self.start_gui(root=root)

    def test_title(self):
        """Confirm correct title display."""
        atform.add_test("This is the title")
        self.start_preview()

    def test_objective(self):
        """Confirm correct objective display."""
        atform.add_test(
            "title",
            objective="""
            This is the first paragraph. Lorem ipsum dolor sit amet, consectetur
            adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
            magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
            ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
            irure dolor in reprehenderit in voluptate velit esse cillum dolore
            eu fugiat nulla pariatur.

            This is the second paragraph. Lorem ipsum dolor sit amet, consectetur
            adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
            magna aliqua. Duis at tellus at urna condimentum mattis pellentesque
            id. Aliquam nulla facilisi cras fermentum odio. Viverra ipsum nunc
            aliquet bibendum enim facilisis gravida neque convallis. Tempor orci
            eu lobortis elementum nibh tellus molestie nunc. Porttitor rhoncus
            dolor purus non enim praesent elementum facilisis leo.
            """,
        )
        self.start_preview()

    def test_references(self):
        """Confirm correct references display."""
        atform.add_reference_category("ref1", "r1")
        atform.add_reference_category("ref2", "r2")
        atform.add_test(
            "title",
            objective="Two reference categories, each with two references.",
            references={"r1": ["foo", "bar"], "r2": ["spam", "eggs"]},
        )
        self.start_preview()

    def test_environment(self):
        """Confirm correct environment fields display."""
        atform.add_field("Field 1", 3, "f1")
        atform.add_field("Field 2", 3, "f2")
        atform.add_test(
            "title",
            objective="Verify two environment fields.",
        )
        self.start_preview()

    def test_equipment(self):
        """Confirm correct Equipment list display."""
        atform.add_test(
            "title",
            equipment=[
                "The first equipment.",
                """The second equipment with multiple paragraphs.
                Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                sed do eiusmod tempor incididunt ut labore et dolore magna
                aliqua. Eros in cursus turpis massa tincidunt dui ut ornare
                lectus. Fringilla urna porttitor rhoncus dolor purus.
                Enim blandit volutpat maecenas volutpat.

                The second paragraph. Laoreet suspendisse interdum consectetur
                libero id faucibus nisl tincidunt. Donec et odio pellentesque
                diam. Posuere sollicitudin aliquam ultrices sagittis orci a
                scelerisque purus semper. Volutpat blandit aliquam etiam erat.
                Sed faucibus turpis in eu mi bibendum neque. At risus viverra
                adipiscing at. Amet consectetur adipiscing elit ut aliquam
                purus. Magna sit amet purus gravida.
                """,
                "The last equipment.",
            ],
        )
        self.start_preview()

    def test_preconditions(self):
        """Confirm correct Precondition list display."""
        atform.add_test(
            "title",
            preconditions=[
                "The first precondition.",
                """The second precondition with multiple paragraphs. Lorem ipsum
            dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Eros in
            cursus turpis massa tincidunt dui ut ornare lectus. Fringilla
            urna porttitor rhoncus dolor purus. Enim blandit volutpat
            maecenas volutpat.

            The second paragraph. Laoreet suspendisse interdum consectetur
            libero id faucibus nisl tincidunt. Donec et odio pellentesque diam.
            Posuere sollicitudin aliquam ultrices sagittis orci a scelerisque
            purus semper. Volutpat blandit aliquam etiam erat. Sed faucibus
            turpis in eu mi bibendum neque. At risus viverra adipiscing at.
            Amet consectetur adipiscing elit ut aliquam purus. Magna sit amet
            purus gravida.
            """,
                "The last precondition.",
            ],
        )
        self.start_preview()

    def test_procedure(self):
        """Confirm a test's procedure is displayed."""
        atform.add_test(
            "title",
            procedure=[
                """
            This is a procedure step with a single paragraph created
            as a simple string. Lorem ipsum dolor sit amet,
            consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua. Viverra
            aliquet eget sit amet tellus. Pharetra vel turpis nunc eget
            lorem dolor sed viverra ipsum. Libero justo laoreet sit
            amet cursus sit amet dictum sit. In dictum non consectetur a.
            """,
                """
            This is a procedure step with multiple paragraphs created
            as a simple string. Lorem ipsum dolor sit amet,
            consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua. Viverra
            aliquet eget sit amet tellus. Pharetra vel turpis nunc eget
            lorem dolor sed viverra ipsum. Libero justo laoreet sit
            amet cursus sit amet dictum sit. In dictum non consectetur a.

            This is the second paragraph. Dolor sit amet consectetur
            adipiscing elit pellentesque habitant. Vel fringilla est
            ullamcorper eget nulla facilisi etiam dignissim diam.
            Vitae proin sagittis nisl rhoncus mattis rhoncus. Nulla
            at volutpat diam ut venenatis tellus. Nisi porta lorem
            mollis aliquam.
            """,
                {
                    "text": """
                This is a procedure step with a single paragraph created
                as a dictionary. Lorem ipsum dolor sit amet,
                consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Viverra
                aliquet eget sit amet tellus.
                """
                },
                {
                    "text": """
                This is a procedure step with multiple paragraphs created
                as a dictionary. Lorem ipsum dolor sit amet,
                consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Viverra
                aliquet eget sit amet tellus.

                This is the second paragraph. Dolor sit amet consectetur
                adipiscing elit pellentesque habitant. Vel fringilla est
                ullamcorper eget nulla facilisi etiam dignissim diam.
                Vitae proin sagittis nisl rhoncus mattis rhoncus.
                Nulla at volutpat diam ut venenatis tellus. Nisi porta
                lorem mollis aliquam.
                """
                },
                {
                    "text": """
                This is a procedure step with a single data entry field
                with no suffix.
                """,
                    "fields": [
                        ("A Field", 10),
                    ],
                },
                {
                    "text": """
                This is a procedure step with a single data entry field
                with a suffix.
                """,
                    "fields": [
                        ("Spam Eggs", 10, "Foo Bar"),
                    ],
                },
                {
                    "text": """
                This is a procedure step with multiple data entry fields,
                all with suffixes.
                """,
                    "fields": [
                        ("Spam", 10, "Eggs"),
                        ("A Long Title", 3, "Bar"),
                    ],
                },
            ],
        )
        self.start_preview()

    def test_location(self):
        """Confirm location specified in objective."""
        line = traceback.extract_stack(limit=1)[0].lineno + 1
        atform.add_test(
            "title", objective=f"Confirm preview location is {__file__}, line {line}."
        )
        self.start_preview()


class SearchQueryEntry(InteractiveGuiTestCase):
    """Tests for the search tab query entry field."""

    def setUp(self):
        super().setUp()
        self.root = tk.Tk()
        search = atform.gui.searchwidget.Search(self.root)
        search.pack()

    @patch("atform.gui.searchwidget.buildlist")
    @patch("atform.gui.searchwidget.search.search")
    def test_enter_shortcut(self, mock_search, *_mocks):
        """Confirm pressing enter executes a search."""
        utils.set_entry_text(self.root, "foo")
        self.start_gui(
            root=self.root,
            instruction="Select the query entry to give it focus, press Enter, then close the search window.",
            buttons=False,
        )
        mock_search.assert_called_once()


class SearchResultMessage(InteractiveGuiTestCase):
    """Tests for the search tab result message label."""

    def setUp(self):
        super().setUp()
        self.root = tk.Tk()
        search = atform.gui.searchwidget.Search(self.root)
        search.pack()

    def test_no_query(self):
        """Confirm message reporting an empty query."""
        self.click_add()
        self.start_gui(
            root=self.root,
        )

    def test_no_sections(self):
        """Confirm message reporting no sections are selected."""
        for section in atform.gui.search.SECTIONS:
            utils.set_checkbox(self.root, section, False)
        utils.set_entry_text(self.root, "foo")
        self.click_add()
        self.start_gui(
            root=self.root,
            instruction="Confirm message reports no sections are selected.",
        )

    @patch("atform.gui.searchwidget.buildlist")
    @patch("atform.gui.searchwidget.search.search")
    def test_match_count(self, mock_search, *_mocks):
        """Confirm message reports number of matches."""
        mock_search.return_value = set(range(42))
        utils.set_entry_text(self.root, "foo")
        self.click_add()
        self.start_gui(
            root=self.root,
            instruction="Confirm message reports 42 matches.",
        )

    def test_clear(self):
        """Confirm message is cleared after altering the query string."""
        self.click_add()
        self.start_gui(
            root=self.root,
            instruction="Confirm the result message clears when typing in the query field.",
        )

    def click_add(self):
        """Simulates clicking the add button."""
        utils.click_button(self.root, "Add Matching Tests To Build")


class Diff(InteractiveGuiTestCase):
    """Tests for the Diff panel."""

    def setUp(self):
        super().setUp()
        self.root = tk.Tk()

    @patch("atform.gui.diffwidget.diff.load", return_value=False)
    def test_no_cache(self, *_mocks):
        """Confirm panel contains only a message stating no cache data is available."""
        diff = atform.gui.diffwidget.Diff(self.root)
        diff.pack()
        self.start_gui(root=self.root)

    @patch("atform.cache.data", new={"vcs": None, "tests": {}})
    def test_no_vcs(self):
        """Confirm panel does not contain cached version information."""
        diff = atform.gui.diffwidget.Diff(self.root)
        diff.pack()
        self.start_gui(root=self.root)

    @patch("atform.cache.data", new={"vcs": "foo", "tests": {}})
    def test_cached_version(self):
        """Confirm cached version is listed correctly."""
        diff = atform.gui.diffwidget.Diff(self.root)
        diff.pack()
        self.start_gui(
            root=self.root,
            instruction="Confirm cached version is foo.",
        )

    @patch("atform.cache.data", new={"vcs": None})
    @patch("atform.gui.diff.load", return_value=True)
    @patch("atform.gui.diff.CHANGED", new=set(range(42)))
    @patch("atform.gui.diff.NEW", new=set(range(99)))
    @patch("atform.gui.diff.SAME", new=set(range(10)))
    def test_diff_counts(self, *_mocks):
        """Confirm correct diff counts."""
        diff = atform.gui.diffwidget.Diff(self.root)
        diff.pack()
        self.start_gui(
            root=self.root,
            instruction="Confirm counts: changed=42, new=99, unmodified=10.",
        )


class Refs(InteractiveGuiTestCase):
    """Tests for the Refs selection panel."""

    def test_resize_horizontal(self):
        """Confirm proper horizontal resizing."""
        self.start_gui(
            instruction="Enlarge the window horizontally and ensure the Refs tab Category/Item column and add button fill the horizontal space.",
        )

    def test_resize_vertical(self):
        """Confirm proper vertical resizing."""
        self.start_gui(
            instruction="Enlarge the window vertically and ensure the Refs tab listing fills the vertical space.",
        )

    def test_scroll(self):
        """Verify operation of the reference listing vertical scroll bar."""
        atform.add_reference_category("Refs", "refs")
        atform.add_test(
            "title",
            references={"refs": [str(x) for x in range(50)]},
        )
        root = tk.Tk()
        ref = atform.gui.selectref.SelectRef(root)
        ref.pack()
        self.start_gui(root=root)

    def test_select(self):
        """Confirm correct item selection mode."""
        atform.add_reference_category("Refs", "refs")
        atform.add_test(
            "title",
            references={"refs": [str(x) for x in range(10)]},
        )
        root = tk.Tk()
        ref = atform.gui.selectref.SelectRef(root)
        ref.pack()
        self.start_gui(
            root=root,
            instruction="Confirm multiple items can be selected simultaneously.",
        )


def nonmodal_dialog(method):
    """
    Test method decorator to prevent the build dialog from being set modal,
    thereby allowing access to the pass/fail buttons.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with patch("atform.gui.build.Dialog.grab_set"):
            method(self, *args, **kwargs)

    return wrapper


def mock_futures(quantity):
    """Generates a set of mock Future objects for testing the build dialog."""
    return {i: Mock(spec=concurrent.futures.Future) for i in range(quantity)}


class BuildDialog(InteractiveGuiTestCase):
    """Build pop-up dialog unit tests."""

    def setUp(self):
        super().setUp()
        self.builder = Mock(spec=atform.parallelbuild.Builder)
        self.done_q = queue.SimpleQueue()

    @nonmodal_dialog
    def test_total_count(self):
        """Confirm correct total count."""
        self.start_gui(
            run=False,
            instruction="Confirm progress total count is 42.",
        )
        atform.gui.build.Dialog(self.builder, mock_futures(42), self.done_q)

    @nonmodal_dialog
    def test_build_message(self):
        """Confirm correct message during build process."""
        self.start_gui(
            run=False,
            instruction="Verify message indicates build is in process.",
        )
        futures = mock_futures(1)
        atform.gui.build.Dialog(self.builder, futures, self.done_q)

    @nonmodal_dialog
    def test_completion_message(self):
        """Confirm correct message when build is complete."""
        self.start_gui(
            run=False,
            instruction="Verify message indicates build is finished.",
        )
        futures = mock_futures(1)
        self.done_q.put(0)
        atform.gui.build.Dialog(self.builder, futures, self.done_q)

    @nonmodal_dialog
    def test_error_message(self):
        """Confirm error messages are correctly displayed."""
        self.done_q.put(0)
        self.start_gui(
            run=False,
            instruction="Verify error window displays 'Error message.'",
        )
        with patch.object(self.builder, "process_result") as mock:
            mock.side_effect = atform.pdf.BuildError("Error message.")
            atform.gui.build.Dialog(self.builder, mock_futures(2), self.done_q)

    def test_cancel(self):
        """Confirm all futures are cancelled if the dialog is closed before all tests are built."""
        self.start_gui(
            run=False,
            instruction="Close the build dialog via the title bar button.",
            buttons=False,
        )
        futures = mock_futures(3)
        atform.gui.build.Dialog(self.builder, futures, self.done_q)
        self.root.destroy()
        for f in futures.values():
            self.assertEqual("cancel", f.method_calls[0][0])

    @nonmodal_dialog
    def test_progress(self):
        """Confirm correct progress bar operation."""
        self.start_gui(
            run=False,
            instruction="Verify progress bar operates normally and completes at 50.",
        )
        futures = mock_futures(50)
        i = 0
        interval = 250

        def step():
            """Simulates a build completion."""
            nonlocal i
            if i < len(futures):
                self.done_q.put(i)
                i += 1
                self.root.after(interval, step)

        self.root.after(interval, step)
        atform.gui.build.Dialog(self.builder, futures, self.done_q)

    def test_process_results(self):
        """Confirm completed futures are processed by the builder."""
        self.start_gui(
            run=False,
            buttons=False,
            instruction="Close the build dialog.",
        )
        futures = mock_futures(1)
        self.done_q.put(0)
        with patch.object(self.builder, "process_result") as mock:
            atform.gui.build.Dialog(self.builder, futures, self.done_q)
            self.root.destroy()
            mock.assert_called_once_with(futures[0])


class StatusBar(InteractiveGuiTestCase):
    """Status bar tests."""

    def test_size(self):
        """Verify status bar sizing."""
        self.start_gui(
            instruction="Ensure the status bar occupies the entire width and stretches horizontally.",
        )

    @patch("atform.gui.statusbar.vcs.version", new=None)
    def test_no_vcs(self):
        """Verify VCS indicator when no version control is present."""
        root = tk.Tk()
        sb = atform.gui.statusbar.StatusBar(root)
        sb.pack()
        self.start_gui(
            root=root,
            instruction="Verify VCS status indicates no version control.",
        )

    @patch("atform.gui.statusbar.vcs.version", new="draft")
    def test_vcs_draft(self):
        """Verify VCS indicator when uncommitted changes are present."""
        root = tk.Tk()
        sb = atform.gui.statusbar.StatusBar(root)
        sb.pack()
        self.start_gui(
            root=root,
            instruction="Verify VCS status indicates draft with an orange background.",
        )

    @patch("atform.gui.statusbar.vcs.version", new="0123456")
    def test_vcs_clean(self):
        """Verify VCS indicator when working directory is clean."""
        root = tk.Tk()
        sb = atform.gui.statusbar.StatusBar(root)
        sb.pack()
        self.start_gui(
            root=root,
            instruction="Verify VCS status contains a 7-digit SHA1.",
        )

    @patch("atform.idlock.lockfile_current", new=False)
    def test_idlock_stale(self):
        """Verify ID lock indicator when the lock file is stale."""
        root = tk.Tk()
        sb = atform.gui.statusbar.StatusBar(root)
        sb.pack()
        self.start_gui(
            root=root,
            instruction="Confirm ID Lock indicator shows stale with an orange background.",
        )

    @patch("atform.idlock.lockfile_current", new=True)
    def test_idlock_ok(self):
        """Verify ID lock indicator when the lock file is current."""
        root = tk.Tk()
        sb = atform.gui.statusbar.StatusBar(root)
        sb.pack()
        self.start_gui(
            root=root,
            instruction="Confirm ID Lock indicator shows ok with a normal background.",
        )
