Organization
============

By default, testgen will automatically number tests with increasing integers,
a simple approach that may be insufficient. Most projects will need
additional organizational levels to separate related test procedures into
sections, and testgen can be configured to use multiple integer fields for
numbering tests, e.g., 5.1 or 1.8.9. Any quantity of fields can be used,
although practical values are between two and four. The only stipulation
regarding numbering is all test procedures must use the same format,
i.e., *every* test will be numbered with the same quantity of fields.

When using two or more numbering fields, testgen refers to each field as a
level, with the first, or highest level, as level zero, increasing up to
the number of configured levels minus one. For example, configuring
three levels, tests will be numbered *x.y.z*; where *x* is level zero, *y* is
level one, and *z* is level two.

The following example shows the two, primary commands for sectioning:
:py:func:`testgen.set_id_depth` and
:py:func:`testgen.section`:

.. literalinclude:: examples/section.py
