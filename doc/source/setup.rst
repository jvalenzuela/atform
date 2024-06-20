Document Setup
==============

Several options are available in the script setup area to tailor the
test documents to a specific project. These options can *only* be
specified in the setup area, and affect all tests equally,
removing the need to duplicate such information manually.

The environment in which a test is executed often needs to be recorded
by the person executing the test. Common examples of this type of
information are system software version, or vehicle number. The
:py:func:`testgen.add_field` function creates a field
where such contextual data may be entered.

Test procedures can be configured to include an area to record personnel
involved with the execution, review, or approval of a completed procedure.
The :py:func:`testgen.add_signature` function creates a set of fields
in the Approval section where the person performing that role
can provide their name, signature, etc.

.. literalinclude:: examples/setup.py
