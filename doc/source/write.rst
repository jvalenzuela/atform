Writing Tests
=============

.. _labels:

Labels
------

Occasionally a test procedure will have some manner of relationship to, or
dependency on another test, such that it is desirable to explicitly
identify the related procedure. Manually typing the target test's identifier
can be error-prone as the automatic numbering process means the assigned
identifiers are not immediately evident. This is especially difficult
when tests are actively being added and the assigned numbers are not
yet firmly established.

To help mitigate this difficulty, test procedures can be assigned a
label that can be used in lieu of the test's numeric identifier. Labels are
defined by the author and remain constant regardless of test numbering,
therefore using a label always yields a correct reference,
even if the labeled test is reassigned a different number.

The first step in this approach is to assign a label to a test with
the ``label`` parameter of :py:class:`testgen.Test`.
Labels are simple strings, typically an abbreviated description of the test.
As an example, for a test titled "Zone 42 Contactor",
a suitable label would be ``z42ctr``. Labels may only contain letters,
numbers, and underscore; they are also case-sensitive, e.g., ``Z42_A``
is different from ``z42_a``. One final stipulation is a label must
be unique.

Once assigned to a test, a label can be used in content strings by
inserting a placeholder where the labeled test's assigned number
should appear. Placeholders use the format :samp:`${label}` where
*label* is the label assigned to the target test. testgen will
automatically replace placeholders with their respective test number
when generating output. Placeholders can be used in any of the following
content:

* Objective
* Preconditions
* Procedure

This next example demonstrates use of labels and placeholders.

.. literalinclude:: examples/label.py
