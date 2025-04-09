.. _meta:

Metadata
========

In addition to outputting PDF documents, |project_name| can provide
supplimentary information often useful for ancillary tasks. Similar to
the API described in :ref:`xref`, these functions do not directly generate
any type of file, but rather present information as simple Python
structures to be evaluated or exported to suit a project's specific requirements.

The :py:func:`atform.list_tests` function lists the numeric identifier and title
of every defined test. :numref:`listtest.py` demonstrates exporting this
data to a CSV file.

.. literalinclude:: examples/listtest.py
   :caption: Excerpt of listtest.py.
   :name: listtest.py
   :start-after: # begin-listing

