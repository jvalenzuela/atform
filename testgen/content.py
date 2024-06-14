# This module implements the objects storing test procedure content as it is
# created.


from . import id
from . import pdf
from . import ref


# All Test() instances in the order they were created.
tests = []


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


class Test(object):
    """
    Creates a single test procedure. Numeric identifiers will be incrementally
    assigned to each test in the order they appear. Only the title parameter
    is required, allowing tests to be initially outlined, then filled in with
    more detail at a later time. The listing below contains a complete example:

    ::

        # A test with title only.
        testgen.Test('A Preliminary Test')

        # The next test with more detail.
        testgen.Test('Walking The Dog',
            objective=\"""
            To provide one's pet with exercise and an opportunity to
            relieve itself.
            \""",

            # These references assume 'sf' and 'fmea' have been configured
            # as reference categories.
            references={
                'sf':['SF1', 'SF2'],
                'fmea':['FM-1', 'FM-2'],
            },

            preconditions=[
                "Own a dog.",
                "Two or more hours have elapsed since the last walk."
            ],
            procedure=[
                "Secure leash to collar.",
                "Open door."
            ]
        )

    :param str title: A short phrase describing the test procedure, that
                      is combined with the automatically-assigned numeric
                      ID to identify this specific test.
    :param str objective: An optional, longer narrative, possibly spanning
                          several sentences or paragraphs, describing the
                          intent of the test procedure.
    :param dict references: References associated with this test. Dictionary
                            keys must be a category label defined with
                            :any:`testgen.add_reference_category`; dictionary
                            values are a list of strings containing references
                            for that category.
    :param list[str] preconditions: An optional list of conditions that must
                                    be met before the procedure can commence.
    :param list[str] procedure: An optional list of procedure steps to be
                                output as an enumerated list. Do not include
                                the step number in each item, e.g.,
                                ``'1. The first step...'``; steps will be
                                automatically numbered based on their
                                list order.
    :raises TypeError: If the title or objective is not a string. Also if
                       preconditions or procedure is not a list, or any
                       item within those lists is not a string.
    :raises TypeError: If references is not a dictionary.
    :raises TypeError: If a references key(category label) is not a string.
    :raises TypeError: If a reference item in a category is not a string.
    :raises ValueError: If any strings provided to title, objective,
                        preconditions, or procedure are empty.
    :raises ValueError: If references contains an empty key(category label).
    :raises Valueerror: If references contains a key(category label) that
                        has not been defined by
                        :any:`testgen.add_reference_category`.
    :raises ValueError: If a reference category contains duplicate
                        references.
    """

    def __init__(self,
                 title,
                 objective=None,
                 references={},
                 preconditions=[],
                 procedure=[],
                 ):
        global tests
        self.id = id.get_id()
        self.title = self._nonempty_string('Title', title)
        self.objective = self._validate_objective(objective)
        self.references = self._validate_refs(references)
        self.preconditions = self._validate_string_list('Preconditions',
                                                        preconditions)
        self.procedure = self._validate_string_list('Procedure', procedure)
        tests.append(self)

    def _validate_objective(self, obj):
        """Validates the objective parameter."""
        if obj is not None:
            return self._nonempty_string('Objective', obj)

    def _validate_refs(self, refs):
        """Validates the references parameter."""
        if not isinstance(refs, dict):
            raise TypeError('References must be a dictionary.')

        validated = {}
        [validated.update(self._validate_ref_category(label, refs[label]))
         for label in refs]
        return validated

    def _validate_ref_category(self, label, refs):
        """Validates a single reference category and associated references."""
        label = self._nonempty_string('Reference label', label)

        # Ensure the label has been defined by add_reference_category().
        try:
            ref.titles[label]
        except KeyError:
            raise ValueError("Invalid reference label: {0}.".format(
                label))

        # Check the list of references for this category.
        validated_refs = []
        for reference in refs:
            if not isinstance(reference, str):
                raise TypeError(
                    "References for '{0}' category must be strings.".format(
                        label))
            reference = reference.strip()

            # Reject duplicate references.
            if reference in validated_refs:
                raise ValueError("Duplicate '{0}' reference: {1}".format(
                    label, reference))

            # Ignore blank/empty references.
            if reference:
                validated_refs.append(reference)


        return {label: validated_refs}

    def _validate_string_list(self, name, lst):
        """Checks a list to ensure it contains only non-empty/blank strings."""
        if not isinstance(lst, list):
            raise TypeError("{0} must be a list of strings.".format(name))
        return [self._nonempty_string("{0} item".format(name), s) for s in lst]

    def _nonempty_string(self, name, s):
        """Checks a string to ensure it is not empty or blank."""
        if not isinstance(s, str):
            raise TypeError("{0} must be a string.".format(name))
        stripped = s.strip()
        if not stripped:
            raise ValueError("{0} cannot be empty.".format(name))
        return stripped


def generate(path='pdf'):
    """
    Builds PDF output files for all defined tests. Should be called once
    near the end of the script after tests have been created with
    :py:class:`Test(...)<Test>`.

    :param str path: Optional path to an output directory.
    :raises TypeError: If path is not a string.
    """
    if not isinstance(path, str):
        raise TypeError('Output path must be a string.')
    [pdf.TestDocument(t, path) for t in tests]
