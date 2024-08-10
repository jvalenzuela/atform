Referencing
===========

Many tests are associated with external documentation, such as analyses
or drawings, and should bear some identifying link
to these resources. Adding references to tests is a two-step
process, starting with defining reference categories using
:py:func:`atform.add_reference_category` in the setup area. With categories
defined, the references argument of :py:class:`atform.Test` is then available
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
standard Python dictionary. Exporting that data into
any standard file format, such as CSV, is easily accomplished with regular
Python utilities.

The cross-reference dictionary is acquired by calling the
:py:func:`atform.get_xref` function in the output section of the script.
It may be called before or after :py:func:`atform.generate`, but
must appear after all tests are defined with
:py:class:`atform.Test`.

Cross-references are structured into two levels. Keys for the top-level
dictionary returned by :py:func:`atform.get_xref` are labels identifying
the reference category as defined with
:py:func:`atform.add_reference_category`. Values are second-level
dictionaries keyed by references applied via the
:code:`references` parameteter of :py:class:`atform.Test`.
Values of the final dictionary are lists of test ID numbers given that
reference. Here is an example of querying the cross-reference dictionary:

.. literalinclude:: examples/snip.py
   :start-after: xref_dict_start
   :end-before: xref_dict_end

The following :file:`xref.py` listing illustrates a simple example
where cross-references are written to a CSV file:

.. literalinclude:: examples/xref.py
