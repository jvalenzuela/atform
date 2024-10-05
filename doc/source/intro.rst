Introduction
============

The Acceptance Test Form package, or |project_name|, is software intended
for writing test procedures, which often
requires significant repetition, iteration, or other similar
time-consuming and error-prone tasks where computers excel.
This software employs the Python programming language to help alleviate
these burdens, such as formatting and
ensuring consistency across duplicate material, freeing the author to focus
on content.

While the test author will need to write what are in fact small Python
programs to use this system, no previous experience with Python or
other programming language is required.
Only elementary Python knowledge is needed to use |project_name|,
much of which can be gleaned from the examples in this guide.
Furthermore, Python's popularity means a wealth of information is
available online, all of which is directly
applicable as |project_name| is a normal Python package, and does not alter or
limit the language in any way.


.. _install:

Installation
------------

|project_name| is compatible with any operating system on which the
requisite Python version listed below is available, including
Windows, Linux, and macOS.

The Python programming language, within version 3.7 to 3.11 inclusive,
must be installed,
and is available from `<https://python.org>`_. Make sure Python is
added to the system path; the relevant Windows installation option
is shown below:

.. image:: images/python_install.png
   :align: center

The |project_name| package can be installed after Python by opening a
command prompt and executing the following command. A functioning Internet
connection is required as this will automatically download the package in
addition to installing it.

.. code-block:: text

   pip install atform

The git version control system is optional, needed only to use the
features described in :ref:`vcs`. Any 2.x git release is acceptable,
but *must* be the standard git command line interface, or CLI, available
from `<https://git-scm.com>`_.
Furthermore, git must be installed into the system path. The image
below shows the Windows installation dialog selecting the requisite
path option:

.. image:: images/git_path.png
   :align: center

Testing to ensure git is properly installed can be done by running
:command:`git --version` in a command prompt, which should yield
something like :samp:`git version {x.y.z}`.


.. _upgrade:

Upgrading
---------

The version numbers assigned to |project_name| releases are
constructed to help convey what type of changes can be expected in a release.
Versions take the form of two integers separated
by a period, :samp:`{major}.{minor}`. The major version is incremented
for changes that are not backwards compatible, i.e., upgrading to a different
major version *may* require modifying existing scripts. The minor version is
incremented for changes that are backwards compatible within the same
major version; scripts will not need to be altered to work with a newer
minor version. However, a minor version may introduce new features
that do not affect existing functionality, but require script changes to
use the new features. New minor versions may also introduce changes altering
the output format.

The following commands can be used to manage, upgrade, or revert
|project_name| installations:

.. code-block:: console

   # Display the currently installed version.
   pip show atform

   # Upgrading an existing installation to the latest version.
   pip install -U atform

   # Install a specific version, overwriting any existing installation;
   # replace major and minor with the desired version.
   pip install -I atform==major.minor

The :py:func:`atform.require_version` function is available
to document which version of |project_name| should be used in a project.


Getting Started
---------------

Writing tests involves creating a set of Python scripts containing
procedure content, e.g., title, procedure steps, etc. These scripts are
then executed with Python to generate the output PDFs.

An important concept to note is these scripts are plain text files and do
not contain formatting, such as font selection or table configuration.
The |project_name| package will handle formatting the output PDFs; the author need
only provide content and structure, i.e., what is in the tests and how
they are organized.

As Python scripts are regular text files, they can be created and edited
with any text editor, however, it is *strongly* recommended to use an editor
with integrated Python support. Another significant feature when selecting an
editor is the ability to provide contextual help, which will display the
same documentation presented in the :ref:`api` section of this manual
directly in the editor window when each command is used. Having
the necessary documentation immediately and automatically available
while writing tests is quite convenient.
Many editors supporting Python are freely-available;
:numref:`tbl_ides` lists some popular ones.

.. _tbl_ides:
.. list-table:: Python Editors
   :header-rows: 1

   * - Name
     - URL
     - Context Help
   * - Notepad++
     - `<https://notepad-plus-plus.org/>`_
     - No
   * - Sublime Text
     - `<https://www.sublimetext.com/>`_
     - Yes
   * - Visual Studio Code
     - `<https://code.visualstudio.com/>`_
     - Yes
   * - PyCharm
     - `<https://www.jetbrains.com/pycharm/>`_
     - Yes

The Python installation also includes a simple, yet functional editor, IDLE,
although it does not feature context help. One note about IDLE is
it starts in an interactive window, showing something like this:

.. code-block:: text

   Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18)
   Type "help", "copyright", "credits" or "license()" for more information.
   >>>

The interactive window is for running Python commands one at a time as they
are entered, not editing scripts saved to files. Use the
:menuselection:`File --> New` menu
to open a new editor window for creating a script that will be saved to disk.

Below is a minimal example to illustrate the basic layout of an |project_name|
script. All examples in this manual are fully-functional, and are attached
to this PDF so they may be
used as initial templates for writing actual test procedures.

.. literalinclude:: examples/minimal.py
   :caption: minimal.py

This example contains three tests, containing only a
title and automatically-assigned number, yet is sufficient to demonstrate
the entire workflow from source script to output PDF.
Obviously, test procedures will require much more detail,
which can be provided by additional parameters to :py:class:`atform.Test`.

Executing this script with Python will yield the output files, one PDF per
test procedure. Most Python editors or integrated development
environments(IDEs) have features to run scripts from within the editor.
If integrated execution is not an option, running Python from the command line
is always available regardless of how the scripts are created and edited.
Open a command prompt, navigate to the folder where
the script is stored, then execute the following command:

.. code-block:: text

   python minimal.py

If the requisite software was installed successfully, the output PDFs will
be created in the :file:`pdf` folder within the same location as the
source script.
