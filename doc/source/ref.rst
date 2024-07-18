Referencing
===========

Many tests are associated with external documentation, such as analyses
or drawings, and should bear some identifying link
to these related resources. Adding references to tests is a two-step
process, starting with defining the reference categories using
:py:func:`testgen.add_reference_category` in the setup area. With categories
defined, the references argument of :py:class:`testgen.Test` is then available
to specify references for each test procedure. The sample below shows
test procedures with two reference categories:

.. literalinclude:: examples/ref.py


.. _xref:

Cross-References
----------------

References applied to test procedures can be collated by |project_name| into
a cross-reference, listing every test assigned a given reference.
Such a cross-reference is often needed for tasks related to the test
procedures; having this information automatically generated
removes the need to manually duplicate it, and helps ensure
consistency with the actual tests.

Projects vary widely in the type of references and in the desired
cross-reference format, therefore, |project_name| itself does *not* create any
type of cross-reference file, but rather presents the infomation as a
standard Python data structure: a dictionary. Exporting that data into
any standard file format, such as CSV, is easily accomplished with regular
Python utilities.

The cross-reference dictionary is acquired by calling the
:py:func:`testgen.get_xref` function in the output section of the script.
It may be called before or after :py:func:`testgen.generate`, but
must appear after all tests are defined with
:py:class:`testgen.Test`.

The following :file:`xref.py` listing illustrates a simple example
where cross-references are written to a CSV file:

.. literalinclude:: examples/xref.py
