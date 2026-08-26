"""
This module handles the details of dispatching selected tests to be built
along with a pop-up dialog displaying build progress and results.

To avoid blocking the main GUI thread waiting for build results, a queue is
used to interface between build futures and the GUI. A callback is
attached to each future which sends the completed test ID back to the
GUI via the queue. The GUI then periodically polls this queue to acquire
progress updates.

Wrapper classes from tkwidget are not used in this module because
the tkinter Dialog defined here is tested differently from the normal
unit tests, and does not suffer from the problems tkwidget addresses.
"""

import queue
import string
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import simpledialog

from . import common
from .. import pdf
from .. import parallelbuild


def build(tids, root, folder_depth):
    """Launches the PDF build process and dialog."""
    with parallelbuild.Builder() as builder:
        done_q = queue.SimpleQueue()

        futures = {}
        for id_ in tids:
            future = builder.submit_test(id_, root, folder_depth)
            futures[id_] = future

            # Add a callback to each future to place the completed test ID
            # into the queue. This callback lambda is called in a thread
            # belonging to the process executor, not the main GUI thread.
            future.add_done_callback(lambda f, id_=id_: done_q.put(id_))

        Dialog(builder, futures, done_q)


class Dialog(simpledialog.Dialog):  # pylint: disable=too-many-instance-attributes
    """Modal pop-up dialog displaying progress and results."""

    # Time, in milliseconds, between checking for completed builds and
    # updating the progress display.
    POLL_INTERVAL = 250

    def __init__(self, builder, futures, done_q):
        self.builder = builder
        self.futures = futures
        self.done_q = done_q
        self.poll_id = None  # Initial dummy value to address Pylint W0201.
        super().__init__(None, title="ATFORM Build")

    def body(self, master):
        self.msg = self._create_msg(master)
        self.msg.set("Building PDF(s).")
        self.progress = Progress(master, len(self.futures))
        self.errors = self._create_error_list(master)
        self._reset_poll()
        master.bind("<Destroy>", self._on_close)

    def _create_msg(self, parent):
        """Creates the main message text display widget."""
        var = tk.StringVar()
        label = tk.Label(parent, textvariable=var)
        label.pack(anchor=tk.NW)
        return var

    def _create_error_list(self, parent):
        """Creates the text area for printing errors."""
        frame = ttk.LabelFrame(parent, text="Errors")
        frame.pack(fill=tk.BOTH, expand=tk.TRUE)
        text = ScrolledText(frame, state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=tk.TRUE)
        return text

    def buttonbox(self):
        return

    def _poll(self):
        """Polls the queue to see if any tests have been completed.

        Scheduled for periodic execution by after().
        """
        while True:
            try:
                id_ = self.done_q.get_nowait()
            except queue.Empty:
                break

            try:
                self.builder.process_result(self.futures[id_])
            except pdf.BuildError as e:
                self._print_error(e)

            self.progress.step()

        if self.progress.done:
            self.msg.set("PDF generation complete.")
        else:
            self._reset_poll()

    def _reset_poll(self):
        """Schedules the next poll update."""
        self.poll_id = self.after(self.POLL_INTERVAL, self._poll)

    def _print_error(self, e):
        """Appends an error message to the error display."""
        self.errors.configure(state=tk.NORMAL)
        self.errors.insert(tk.END, f"{e}\n")
        self.errors.configure(state=tk.DISABLED)

    def _on_close(self, _event=None):
        """Handler for the window closing event."""
        if not self.progress.done:
            self.after_cancel(self.poll_id)
            for f in self.futures.values():
                f.cancel()


class Progress(tk.Frame):
    """Container holding widgets displaying the number of completed tests."""

    def __init__(self, parent, total):
        super().__init__(parent)
        self.total = total
        self.remain = total
        self.pack(fill=tk.X, pady=common.SMALL_PAD)

        self.bar_var = tk.IntVar()
        pbar = ttk.Progressbar(self, maximum=total, variable=self.bar_var)
        pbar.pack(side=tk.LEFT, fill=tk.X, expand=tk.TRUE)

        self.msg = tk.StringVar()
        self.msg_tpl = string.Template(f"$done/{total}")

        # Set the message width to accommodate a full count.
        width = len(self.msg_tpl.substitute(done=total))

        label = tk.Label(self, textvariable=self.msg, width=width, anchor=tk.E)
        label.pack(side=tk.LEFT)

        self.msg.set(self.msg_tpl.substitute(done=0))

    def step(self):
        """Increments the current progress."""
        self.remain -= 1
        done = self.total - self.remain
        self.bar_var.set(done)
        self.msg.set(self.msg_tpl.substitute(done=done))

    @property
    def done(self):
        """Returns True when all tests have been completed."""
        return self.remain == 0
