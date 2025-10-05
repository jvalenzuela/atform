"""Global data storage.

This module stores all data, e.g. configuration and test content, accumulated
during execution of the user script(s).

All access to storage attributes in this module must be by importing this
entire module like:

import state

state.<attr>

Do not import individual attributes with the from clause:

from state import <attr>

The reason is unit tests frequently reload this module to remove all content;
the import from clause creates a reference to the underlying object
in the local namespace, which does not get reinitialized during a reload,
causing unit test failure.
"""

import collections


# Names identifying which fields will be applied to the next test.
active_fields = set()


# The user-defined copyright notice string.
copyright_ = None  # pylint: disable=invalid-name


# Numeric ID assigned to the most recent test; stored as a list instead
# of a tuple because items in this list are incremented as tests and
# sections are created.
current_id = [0]


# All defined fields, keyed by name, and ordered as added by add_field().
fields = collections.OrderedDict()


# Globally accessible labels.
labels = {}


# Hash of the the user-specified logo image file.
logo_hash = None  # pylint: disable=invalid-name


# All tests keyed by ID tuple.
tests = {}


# The current project information set by the most recent call to
# set_project_info().
project_info = {}


# Reference category titles, keyed by label. Stored as an ordered
# dictionary because the order the categories are created defines
# the order they are listed in the output documents.
ref_titles = collections.OrderedDict()


# Section titles, keyed by ID tuple.
section_titles = {}


# Signature titles, in the order they were defined.
signatures = []


# Mapping of image hash to ReportLab Image object.
images = {}
