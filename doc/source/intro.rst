Introduction
============

The testgen software is intended for writing test procedures, which often
requires significant repitition, iteration, or other similar
time-consuming and error-prone tasks where computers excel.
This software employs the Python programming language to help alleviate
these burdens, such as formatting and
ensuring consistency across duplicate material, freeing the author to focus
on content.

While the test author will need to write what are in fact small Python
programs to use this system, no previous experience with Python or
other programming language is required.
Only elementary Python knowledge is needed to use the testgen package,
much of which can be gleaned from the examples in this guide.
Furthermore, Python's popularity means a wealth of information is
available online, all of which will be directly
applicable as testgen is a normal Python package, and does not alter or
limit the language in any way.


Installation
------------

The Python programming language, version 3.6 or later, must be installed,
and is available from `<https://python.org>`_. Make sure to select the
add Python to the path option from the installation dialog:

.. image:: images/python_install.png

The testgen package can be installed after Python using the following
procedure:

#. The testgen package is distributed as an attachment embedded into this
   PDF manual. Save the .whl file to a convenient location on
   your computer.

#. Open a command prompt and navigate to the directory where the .whl
   file was saved.

#. The Python package manager, pip, is used to install the testgen package,
   and requires a functional Internet connection. Use the following
   command executed in the command prompt::

     pip install testgen-0.0.0-py3-none-any.whl

   If testgen is already installed, use the ``-U`` option to upgrade to a
   newer version::

     pip install -U testgen-0.0.0-py3-none-any.whl

#. Delete the .whl file; it is not required after installation.
