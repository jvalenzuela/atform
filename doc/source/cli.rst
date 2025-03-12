Command Line Options
====================

Running the top-level script with no additional options specified on the
command line will generate PDFs for all defined tests. The time required to
build a complete document set for large projects can
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

.. code-block:: console

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

Using sets of identifiers to generate only specific tests does not
affect metadata assembled by |project_name|, such as cross-references and
labels. All references and labels are correctly resolved regardless of which
output PDFs are generated.
