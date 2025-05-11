.. _cli:

Command Line Options
====================

Running the top-level script with no additional options provided on the
command line will generate PDFs for all defined tests. This section
describes command line options to curtail the number of output files
for various purposes.

The options presented here are not mutually-exclusive; they can be
combined to generate PDFs for the intersection of all options, i.e.,
only tests that satisfy all options will be created. As an example,
providing the options ``--diff 5-6`` will only output tests that have
changed with IDs between 5 and 6.

Using options to generate only specific tests does not
affect metadata assembled by |project_name|, such as cross-references and
labels. All references and labels are correctly resolved regardless of which
output PDFs are generated.


.. _cli_id:

Numeric IDs
-----------

The time required to build a complete document set for large projects can
be inconvenient, especially for tasks involving only a small subset of tests.
For cases where building all tests is unnecessary, |project_name|
can be configured to reduce the quantity of generated PDFs by listing
desired test identifiers in the command line after the script name.

Specifying test identifers in the command line uses the same format they
appear in the output PDFs: one or more integers separated by periods.
If :py:func:`atform.set_id_depth` has been used to create sections, an entire
section can be selected by abbreviating the identifier to include only
the desired section. For example, if the ID depth is 3, listing ``5.9``
on the command line will include all section 5.9 content, i.e., tests
5.9.1, ..., 5.9.\ *x*.

A range of tests can be specified using the start and end identifiers
separated by a hyphen, such as ``3.5-3.9``. Ranges are inclusive, meaning they
include the starting and ending identifiers, and can use any combination of
full-length identifiers to select a specific test or section IDs.

Complex selections can be assembled by listing multiple IDs and ranges
separated by spaces. Do not use commas, semicolons, or any other
punctuation between each ID or range.

Below are some examples demonstrating various ways to select sets
of tests to generate. All examples assume the top-level script is
named :file:`main.py` and :py:func:`atform.set_id_depth` has been used to
set the identifier depth to 3.

.. code-block:: doscon

   # Generate a single test: 3.7.1
   python main.py 3.7.1

   # Generate tests 5.1.1 through 5.1.10
   python main.py 5.1.1-5.1.10

   # Generate sections 2.7 through 4, and test 9.5.7
   python main.py 2.7-4 9.5.7


Identifiers provided on the command line need not exactly match existing
tests and sections. For example, the range ``5-99`` in a project
with only sections 1 through 10 is ok; that range will simply limit the
output to sections 5 through 10.


Content Differences
-------------------

The ``--diff`` option causes |project_name| to build PDFs only for
tests that have changed since the last time the script was run.
While not strictly required, this function is intended for use with
script files maintained by a version control system.
Use of this option is outlined below:

#. Check out the original version.

#. Run the script normally *without* the ``--diff`` option. The purpose
   is to update the cache file with the test content; any PDFs
   resulting from this step are irrelevant because |project_name| compares
   content from the cache file, not PDFs. This means
   options described in :ref:`cli_id` can be used to make this step run
   very quickly as limiting the output does not affect cache file generation.

#. Check out the version containing changes relative to the original;
   typically a newer version.

#. Optionally, delete the PDF output directory. Any existing files
   in that folder will be overwritten as necessary, yet this serves to
   help identify altered tests as they will be the only files in the
   output folder if it is first cleared.

#. Run the script with the ``--diff`` option to build only tests
   different relative to the version checked out at the start of this
   procedure.

This option may generate more tests than expected due to how |project_name|
compares tests. All content contributing to output PDFs is evaluated, not just
the information provided to :py:func:`atform.add_test`. This includes
global items affecting all tests, such as the logo and copyright notice.
Furthermore, the :ref:`format` section describes how spaces within strings
may not affect PDF output, yet spacing changes are categorized as a difference.


.. _cli_gui:

Graphical User Interface
------------------------

The ``--gui`` option launches the interface described in :ref:`gui`,
and overrides any other command line options.
