.. _setup:

Document Setup
==============

Several options are available in the script setup area to tailor
test documents to a specific project. Unless otherwise noted,
these options can *only* be
specified in the setup area, and affect all tests equally.

A graphic image, such as a project or company logo,
can be placed in the title block of each test document using
:py:func:`atform.add_logo`. Refer to the API reference
documentation for supported image formats.

Test procedures can be configured to include an area to record personnel
involved with the execution, review, or approval of a completed procedure.
The :py:func:`atform.add_signature` function creates a set of fields
in the Approval section where the person performing that role
can provide their name, signature, etc.

.. literalinclude:: examples/setup.py
   :caption: setup.py


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
   :caption: project_info.py


.. _env_fields:

Environment Fields
------------------

It is often necessary to record information about the environment in which
the test procedure is performed. Common examples of this type of
contextual data are software version, machine number, or facility area.
Data entry fields for the test executor to enter this type of information
can be added to test procedures with the :py:func:`atform.add_field`
function.

By default, every field will be present on all tests, but it is also
possible to customize the fields applied to each test procedure.
Every field must first be defined with :py:func:`atform.add_field`,
regardless of how many tests it will be applied to. Once defined, the
``include_fields``, ``exclude_fields``, and ``active_fields`` parameters
of :py:func:`atform.add_test` can be used to adjust the fields
listed on a single test. To change the fields on a number of consecutive
tests, :py:func:`atform.set_active_fields` can be used throughout the
content area to alter the default fields. The :file:`field.py` example
demonstrates how to define fields and alter the fields appearing on
each test procedure.

.. literalinclude:: examples/field.py
   :caption: field.py
