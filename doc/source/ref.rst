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
