import atform


######################################################################
# Setup
######################################################################

# atform.add_reference_category() is used in the setup area to define
# reference categories that may appear in tests.
atform.add_reference_category("Safety Functions", "sf")
atform.add_reference_category("FMEA", "fmea")


######################################################################
# Content
######################################################################

atform.add_test(
    "A Test With References",
    # The references argument is where references for each test are
    # specified.
    references={
        "sf": ["SF17", "SF24"],
        "fmea": ["FM1.9", "FM5.3"],
    },
)

atform.add_test(
    "A Test With Few References",
    # Reference categories that do not apply can be omitted.
    # Only fmea references are relevant to this test; there are
    # no sf references.
    references={
        "fmea": ["FM6.8"],
    },
)

# Tests with no references can simply omit the references parameter.
atform.add_test("A Test Without References")


######################################################################
# Output
######################################################################

atform.generate()
