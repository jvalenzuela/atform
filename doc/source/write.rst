.. _write:

Writing Tests
=============


.. _procedure:

Procedure
---------

The :code:`procedure` parameter of :py:func:`atform.add_test` contains the
main content of a test: the steps that must be performed and validated.
These actions are organized into a list which will be automatically
enumerated in the output; do not incorporate step numbers into
the action text.

Each item in the procedure list is a single step, and may be given in
one of two different forms: string or dictionary. A string is suitable
if the step only needs instructional text whereas a dictionary
allows additional information as listed in :numref:`tbl-procstepdict`
to be included along with the main text.

.. _tbl-procstepdict:
.. list-table:: Procedure Step Dictionary Entries
   :header-rows: 1
   :widths: 15, 15, 55, 15

   * - Key
     - Value Type
     - Description
     - Required
   * - ``"label"``
     - string
     - A label that can be used to reference this step number.
       See :ref:`labels`.
     - No
   * - ``"text"``
     - string
     - The instructions for the step.
     - Yes
   * - ``"fields"``
     - list(tuple)
     - Data entry fields, one tuple per field, to record information
       as part of the step, such as a measurement result.
       See :numref:`tbl-procstepfieldtpl`.
     - No

.. _tbl-procstepfieldtpl:
.. list-table:: Procedure Step Data Entry Field Tuple
   :header-rows: 1
   :widths: 10, 15, 60, 15

   * - Index
     - Value Type
     - Description
     - Required
   * - 0
     - string
     - The field title.
     - Yes
   * - 1
     - integer
     - Maximum number of characters the field should accommodate.
     - Yes
   * - 2
     - string
     - A suffix to place after the field, typically used to denote units.
     - No

The procedure list may contain both string and dictionary items as the
following example illustrates:

.. literalinclude:: examples/procedure.py
   :caption: procedure.py


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
the :code:`label` parameter of :py:func:`atform.add_test`.
Labels are strings, typically an abbreviated description of the test.
As an example, for a test titled "Zone 42 Contactor",
a suitable label may be ``z42ctr``. Labels must begin with a letter
or underscore, optionally followed by letters,
numbers, and underscore; they are also case-sensitive, e.g., ``Z42_A``
is different from ``z42_a``.

Individual procedure steps may also be given labels; the typical use
is so other steps within the same procedure can refer to the labeled step.
Procedure step labels use the same format as test labels, and are
replaced with the procedure step number.
See :ref:`procedure` for details on applying labels to procedure steps.

All labels, regardless of what they are applied to, must be unique
throughout the entire project. For example, a label assigned to a test
cannot be used for another test *or* procedure step.

Once assigned, a label can be used in content strings by
inserting a placeholder where the label's replacement text
should appear. Placeholders use the format :samp:`${label}` where
*label* is the label assigned to the target test or procedure step.
|project_name| will automatically replace placeholders
when generating output. Placeholders can be used in any of the following
content:

* Objective
* Preconditions
* Procedure

This next example demonstrates use of labels and placeholders.

.. literalinclude:: examples/label.py
   :caption: label.py


.. _format:

Formatting
----------

Unlike many document systems, |project_name| does not have features
to significantly alter the docment format, such as typeface or font size.
This omission is intentional, relieving the author from selecting and
maintaining consistent typography; |project_name| will handle the task of
formatting content in a uniform manner.

The Python strings passed to |project_name| serve as the source for output PDF
content, however, they do not dictate how that content is formatted.
Part of the |project_name| PDF creation process involves flowing
the source text onto the available page area, i.e., adjusting spacing between
letters and words, and breaking long lines into shorter ones.
The result will contain the same words as the original string, yet will
likely differ in appearance. This means source strings can be created
without regard as to how they will be formatted in the output;
strings may be broken into separate lines, typically with Python's
triple-quote syntax, without causing unwanted impact to the output.

One area where the author must include some formatting information is
paragraph separation. Content for each procedure topic,
such as the Objective, is provided with a single string, therefore,
a mechanism is required to delimit multiple paragraphs.
To start a new paragraph simply insert one or more blank lines in the
same string, then begin the next paragraph; |project_name| automatically
implements indentation, so any additional spaces or tabs at the start
of a paragraph do not affect the output. The following strings may contain
multiple paragraphs:

* Objective
* Equipment list items
* Preconditions list items
* Procedure list items

The :py:func:`atform.format_text` function provides a method to adjust the
way text is formatted. This function is *not* intended to make significant
alterations to the document layout, but rather to format short words
or phrases within normal text that are semantically distinct enough to merit
visual differentiation.
A common case is presenting a variable name or output message that
needs to be matched verbatim.

While using :py:func:`atform.format_text` is an effective way to denote
significant text, it is not recommended to use that function directly
in test content. The best approach for formatting special terms is to
define a function for a specific type of content, with a name
reflecting the type of content for which it is intended. The new function
can then use :py:func:`atform.format_text` internally to apply the
desired formatting. The benefits to this approach are twofold. First,
a function with a semantically significant name, such as :code:`tag_name()`,
is much clearer than :code:`atform.format_text()`. Second, it
ensures like content is presented uniformly because
the format for a given type of content is defined in a single place.

Item lists can be created with :py:func:`atform.bullet_list`.
This function is not needed to arrange items normally presented as bullet
lists, such as the those passed to the :code:`preconditions` or
:code:`equipment`
parameters of :py:func:`atform.add_test`; |project_name| automatically
formats that content in an appropriate list.
The :py:func:`atform.bullet_list` function should only be used where a
secondary list is necessary.

This following sample script demonstrates these formatting concepts:

.. literalinclude:: examples/format.py
   :caption: format.py
