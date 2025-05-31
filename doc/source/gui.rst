.. _gui:

Graphical User Interface
========================

|project_name| includes a graphical user interface, or *GUI*, that can
be used to selectively build PDFs. The GUI is optional, enabled
via the ``--gui`` :ref:`command line option <cli_gui>`;
no script modification is necessary to use the GUI.

.. image:: images/gui/gui.png
   :align: center

The GUI is actually launched by :py:func:`atform.generate`,
which does not return until the GUI is closed. If the script contains
code after :py:func:`atform.generate`, such as exporting metadata to
external files, that code will not be executed until the GUI
terminates.


.. _gui_select:

Select
------

The left panel contains a set of tabs, each providing a method for
finding tests to be built.


.. _gui_select_list:

List
^^^^

The :guilabel:`List` tab presents all defined tests sorted according to
their numeric identifier, and organized into a heirarchy if sections have
been enabled with :py:func:`atform.set_id_depth`.
Tests can be selected via mouse click; multiple selections can be made
using the typical :kbd:`Control` and :kbd:`Shift` mouse click combinations.
Selecting a section implicitly includes all contained subsections and tests.
Clicking the :guilabel:`Add Selected Tests To Build` button will add
all selected tests added to the :guilabel:`Build` list.

In addition to toggling the selection, clicking on a test in the list will
also display that test in the :ref:`gui_preview` window.


.. _gui_preview:

Preview
-------

The center panel displays test content, updated automatically by selecting
tests in the :ref:`gui_select_list` and :ref:`gui_build` windows.

Presentation in the :guilabel:`Preview` window does *not* reflect
formatting in PDF output. This window is intended only as a rudimentary
display to aid in test selection.

Along with displaying a test's content, the location of the
:py:func:`atform.add_test` function call that created the test appears
at the bottom of the :guilabel:`Preview` window.


.. _gui_build:

Build
-----

The right-most panel lists tests queued for PDF generation. Initially
empty; it is populated using the :ref:`gui_select` panel.

Once the desired tests have been added to the :guilabel:`Build` list,
the :guilabel:`Build PDFs` button will start the process of generating
PDFs. All tests listed in the :guilabel:`Build` panel will be built,
regardless of which, if any, are selected. To remove items from this list,
select them in the same manner as the :ref:`gui_select_list` panel,
and click the :guilabel:`Remove Selected` button.

A pop-up dialog will appear while building output documents, displaying
progress and any errors. The build process may be cancelled by either
clicking the :guilabel:`Cancel` button or closing the pop-up dialog.

The :guilabel:`Build` list will be cleared after building, allowing
the process to repeat for another set of tests.
