Writing Tests
=============


.. _format:

Formatting
----------

Unlike many document systems, |project_name| does not have features
to significantly alter the docment format, such as typeface or font size.
This omission is intentional, relieving the test author from selecting and
maintaining consistent typography; |project_name| will handle the task of
formatting content in a uniform manner.

The Python strings passed to |project_name| serve as the source for output PDF
content, however, they do not dictate how that content is formatted.
Part of the PDF creation process handled by |project_name| involves flowing
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

The :py:func:`atform.format_text` provides a method to adjust the
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
a function with a semantically significant name, such as :code:`tagName()`,
is much clearer than :code:`atform.format_text()`. Second, it is easy
to ensure similar content is presented in a uniform manner because
the format for a given type of content is defined in a single place.

Item lists can be created with :py:func:`atform.bullet_list`.
This function is not needed to arrange items normally presented as bullet
lists, such as the those passed to the :code:`preconditions` or
:code:`equipment`
parameters of :py:class:`atform.Test`; |project_name| automatically
formats that content in an appropriate list.
The :py:func:`atform.bullet_list` function should only be used where a
secondary list is necessary.

This following sample script demonstrates these formatting concepts:

.. literalinclude:: examples/format.py


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
the :code:`label` parameter of :py:class:`atform.Test`.
Labels are simple strings, typically an abbreviated description of the test.
As an example, for a test titled "Zone 42 Contactor",
a suitable label would be ``z42ctr``. Labels may only contain letters,
numbers, and underscore; they are also case-sensitive, e.g., ``Z42_A``
is different from ``z42_a``. One final stipulation is a label must
be unique.

Once assigned to a test, a label can be used in content strings by
inserting a placeholder where the labeled test's assigned number
should appear. Placeholders use the format :samp:`${label}` where
*label* is the label assigned to the target test. |project_name| will
automatically replace placeholders with their respective test number
when generating output. Placeholders can be used in any of the following
content:

* Objective
* Preconditions
* Procedure

This next example demonstrates use of labels and placeholders.

.. literalinclude:: examples/label.py


.. _procedure:

Procedure
---------

The :code:`procedure` parameter of :py:class:`atform.Test` contains the
main content of a test: the actions that must be performed and validated.
These actions are organized into a list which will be automatically
enumerated in the output; do not incorporate step numbers into
the action text.

Each item in the procedure list is a single step, and may be given in
one of two different forms: string or dictionary. A string is suitable
if the step only needs instructional text whereas a dictionary
allows additional information to be included along with the main text.
A procedure step dictionary must have a :code:`'text'` key holding a string
with the instructional text; all other keys are optional.

The :code:`'fields'` key in a step dictionary will add data entry fields
to record information as part of the step, such as a measurement result,
and must be a list where each item is a tuple in the form
:samp:`({title}, {length}, {suffix})` defining a single field.
*title* is a string
describing data to be recorded; *length* is the maximum number of
characters the field should accommodate. *suffix* is an optional
string to place after the field, typically used to denote units.

The procedure list may contain both string and dictionary items as the
following example illustrates:

.. literalinclude:: examples/procedure.py
