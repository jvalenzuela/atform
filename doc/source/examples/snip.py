# This file contains small examples that are just a few lines, as opposed to
# an entire, stand-alone script. The purpose for placing these into a
# separate Python script, instead of listing them directly in the
# document source, is to ensure they actually work. All examples, including
# this script, are run by the unit test framework, so any errors will
# be caught by unit tests. Unit tests do not validate any specific
# output from this script, only that it runs without raising any
# exceptions.
#
# Selected lines are included in the document via :start-after:
# and :end-before: options to the literalinclude directive.


import atform


# Setup for the xref dictionary listing.
atform.add_reference_category("fmea", "fmea")
atform.add_test("xref", references={"fmea": ["fm42"]})

# xref_dict_start
xref = atform.get_xref()

# Test IDs assigned "fm42" in the "fmea" reference category.
test_list = xref["fmea"]["fm42"]
# xref_dict_end
