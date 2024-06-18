# This module contains the implementation for listing external references.


from . import misc


# Category titles, keyed by label.
titles = {}


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@misc.setup_only
def add_reference_category(title, label):
    """
    Creates a topic for listing external references. This
    function does not create any actual references; they must be
    added to each test individually with the references argument of
    :py:class:`testgen.Test`. This function is only available in the setup
    area of the script before any tests or sections are created.

    ::

        # This will create references titled 'Safety Functions' that can
        # be added to tests via the 'sf' label.
        testgen.add_reference_category('Safety Functions', 'sf')

        # Create a test listing safety functions SF1 and SF2.
        testgen.Test('A Test With References',
            references={'sf':['SF1', 'SF2']})

    :param str title: The full name of the category that will be displayed
                      on the test documents.
    :param str label: A shorthand abbreviation to identify this category
                      when adding references to individual tests. Must be
                      unique across all reference categories.
    :raises TypeError: If title or label is not a string.
    :raises ValueError: If the title or label is blank, or the label is
                        already used by another category.
    :raises RuntimeError: If this function is called after any tests or
                          sections have been created.
    """
    global titles

    # Validate title.
    if not isinstance(title, str):
        raise TypeError('Reference title must be a string.')
    title_stripped = title.strip()
    if not title_stripped:
        raise ValueError('Reference title must not be blank.')

    # Validate label.
    if not isinstance(label, str):
        raise TypeError('Reference label must be a string.')
    label_stripped = label.strip()
    if not label_stripped:
        raise ValueError('Reference label must not be blank.')
    if label_stripped in titles:
        raise ValueError("Duplicate reference label: {0}".format(
            label_stripped))

    titles[label_stripped] = title_stripped
