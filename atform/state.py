"""Global data storage.

This module stores all data, e.g. configuration and test content, accumulated
during execution of the user script(s). It is implemented as a set of
global variables initialized by a function, as opposed to direct assignment
in the module namespace, to support unit testing, which requires the entire
module to be reinitialized for each test case.

All access to storage attributes in this module must be by importing this
entire module like:

import state

state.<attr>

Do not import individual attributes with the from clause:

from state import <attr>

The reason is the from clause creates a reference to the underlying object
in the local namespace, which does not get reinitialized in init(), causing
unit test failure.
"""

import collections


def init():
    """Initializes all default values."""
    # Suppress this message as all global variables are initially created
    # by this function.
    # pylint: disable=global-variable-undefined

    # Names identifying which fields will be applied to the next test.
    global active_fields
    active_fields = set()

    # The user-defined copyright notice string.
    global copyright_
    copyright_ = None

    # Fields assigned to the most recent test.
    global current_id
    current_id = [0]

    # All defined fields, keyed by name, and ordered as added by add_field().
    global fields
    fields = collections.OrderedDict()

    # Target ids keyed by label.
    global labels
    labels = {}

    # ReportLab Image object containing the user-specified logo.
    global logo
    logo = None

    # All Test() instances in the order they were created.
    global tests
    tests = []

    # The current project information set by the most recent call to
    # set_project_info().
    global project_info
    project_info = {}

    # Reference category titles, keyed by label.
    global ref_titles
    ref_titles = {}

    # Section titles, keyed by ID tuple.
    global section_titles
    section_titles = {}

    # Signature titles, in the order they were defined.
    global signatures
    signatures = []


init()
