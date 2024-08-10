Document Setup
==============

Several options are available in the script setup area to tailor
test documents to a specific project. These options can *only* be
specified in the setup area, and affect all tests equally.

The environment in which a test is executed often needs to be recorded
by the person executing the test. Common examples of this type of
information are system software version, or vehicle number. The
:py:func:`atform.add_field` function creates a field
where such contextual data may be entered.

Test procedures can be configured to include an area to record personnel
involved with the execution, review, or approval of a completed procedure.
The :py:func:`atform.add_signature` function creates a set of fields
in the Approval section where the person performing that role
can provide their name, signature, etc.

.. literalinclude:: examples/setup.py


.. _project_info:

Project Information
-------------------

Metadata describing the scope of the test procedures, such as the
project name, can be defined with :py:func:`atform.set_project_info`,
and is typically used in the setup area. This function can also be used
repeatedly throughout the content area to change information
among test procedures. In other words, project information is applied
to tests until the next time the function is called.

The example below demonstrates a series of test procedures for
multiple systems within a single project, where the tests for each
system occupy a dedicated section. The start of each section
includes a call to :py:func:`atform.set_project_info`
to update the system name.

.. literalinclude:: examples/project_info.py
