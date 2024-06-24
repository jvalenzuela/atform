Automation
==========

The examples thus far have been written so each appearance of
:py:class:`testgen.Test` yields a single test procedure populated with
the content of literal strings given as arguments, which
is often sufficient, however, the Python environment offers
many options that become especially powerful when tasked with
duplicate or iterative material. This chapter contains examples for
handling common cases easily automated with simple idioms.
The key concept is testgen scripts are regular Python, so any valid
Python construct can be used to call testgen functions or create the
content passed to those functions.

The next example addresses a common procedure step widely used in many
test procedures. Copying and pasting the string containing this
procedure step is undesireable for reasons already stated.
Instead, a variable is created to store the string, which is
then used wherever the string is needed, ensuring all instances of the
text are identical, and requiring only a single modification if the
step needs to be altered.

.. literalinclude:: examples/variable.py

Another case for automation is a system containing several
instances of a common component, each of which needs to be tested separately.
The test procedures would be largely identical, varying only slightly
to accommodate the unique parameters of each component.
Python and testgen can be used to compose a single template that
automatically outputs tests tailored for each component. To accomplish this,
a function is defined with parameters for items that differ in each
instance, with the call to :py:class:`testgen.Test` contained inside
the function using content created by using the parameters. The function
is then called in the content area to generate a uniform test for each
component.

.. literalinclude:: examples/iterate.py

Test procedures often need to incorporate content from an external
source. A common example is alarm messages, where messages are defined
in some other system, but also need to appear in the test procedures.
If the alarm messages can be stored or exported into a
structured format, such as CSV or XML, then
importing that content for use with testgen is a simple affair.

One important note is testgen itself does *not* implement any type of
data import functionality. A general purpose data import system
within testgen would be impractical as the type of data and format
varies greatly among projects. Python, however, is capable of accessing
just about any type of structured file format, making custom import
functionality in testgen unnecessary; external content can be imported
using existing Python features.

The alarms.csv file attached to this PDF is a sample export containing
alarm messages. The example script below reads the csv file and creates
some tests including alarm messages from the csv file. The script and csv
file need to reside in the same folder to work properly.

.. literalinclude:: examples/alarm.py

For the sake of brevity these examples are each a single file
with features such as variables or functions that help automate
creating tests in the content area. An additional consideration is
necessary when organzing tests into multiple files as described in
the :doc:`Organization<org>` chapter. Items defined in the top-level
file are not available in lower-level, imported scripts for the same
reason every script needs an ``import testgen`` statement at the beginning.
The solution to this is to locate any user-defined functionality in a
separate file, which is then imported into every script in addition to
the testgen module.

Using the alarm example above, if that feature was needed for tests
in multiple scripts, move the following content from alarm.py
into a separate file called common.py:

.. literalinclude:: examples/alarm.py
   :lines: 6-28

Every script needing alarm content would then import it in addition
to testgen at the top.

::

   import testgen
   from common import *

The different import statement form, ``from common import *``
instead of ``import common``, is used to simplify the syntax needed to
use items defined in common.py. With this type of import statement
items can be used just as if they were defined in the same file.

The scripts presented in this chapter illustrate simple methods to
automate tasks that would otherwise be labor-intensive. The cases and
solutions are not comprehensive, but are representative of common
situations that arise when writing test procedures, and hopefully
provide a suitable starting point for addressing the needs of actual
projects.
