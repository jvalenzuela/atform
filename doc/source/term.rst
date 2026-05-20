.. _term:

Terms
=====

Systems under test often employ identifiers representing significant
conditions to be validated by the test procedures. Typical identifiers
are names of variables or tags. When an identifier represents a system
state appearing in many tests, it may be desirable to factor verification
of the common state into a dedicated test procedure, simplifying other
tests by requiring them to only verify the representative identifier.
|project_name| can assist in using these identifiers, hereafter referred to
as *terms*.

Terms are initially configured in the script setup area with
the :py:func:`atform.add_term` function to assign a label to the term's
literal text, and optionally apply special formatting.
The example below assigns the label ``myTerm`` to the term ``foo42``,
and specifies it should appear in bold sans-serif.

.. literalinclude:: examples/term.py
   :caption: Excerpt of term.py defining a new term.
   :start-after: # begin-add-term
   :end-before: # end-add-term

Any number of terms may be created provided they are unique in both
text and label. Whitespace within the text incurs additional
processing that bears consideration when ensuring terms are unique.
Surrounding whitespace is removed, e.g., ``"foo"`` and ``" foo "``
will be considered identical. Consecutive whitespace within the text
is normalized to single space. To illustrate using the ``·`` symbol as a
visible representation of a whitespace, ``"foo·bar"`` and ``"foo···bar"``
will both be converted internally to the same term, ``"foo·bar"``.

The scope of uniqueness extends to labels assigned
to other items described in :ref:`labels`; term labels must be unique
throughout the entire project. Once defined, terms
may be used in tests via their label by applying the same ``$`` prefix
outlined in :ref:`labels`, as demonstrated in the next example.

.. literalinclude:: examples/term.py
   :caption: Excerpt of term.py using a term in a test.
   :start-after: # begin-use-term
   :end-before: # end-use-term

A test may support a term by demonstrating system behavior in response to
the term such that other tests can use the term in lieu of repeating
the demonstrated behavior. |project_name| cannot automatically infer a
test supports a term, therefore support must be explicitly
input via the ``supports_terms`` parameter of :py:func:`atform.add_test`,
which accepts a list of labels identifying terms supported by the test.
Continuing with the ``myTerm`` example, the listing below defines a
supporting test.

.. literalinclude:: examples/term.py
   :caption: A test supporting a term; excerpt of term.py.
   :start-after: # begin-support-term
   :end-before: # end-support-term

Labels listed in the ``supports_terms`` argument are *not* prefixed with ``$``;
enter them exactly as defined with :py:func:`atform.add_term`.
A test may support any number of terms, likewise a term may be
supported by multiple tests.

Using a supported term in a test is automatically detected, and will
cause the output PDF to include a listing of supported terms and the tests that
support them. An exception is the supporting test itself, which will
typically use the term it supports, however, it will not reference itself
as supporting the term.
