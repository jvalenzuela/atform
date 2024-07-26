# This module implements the objects storing test procedure content as it is
# created.


from . import id
from . import label
from . import misc
from . import pdf
from . import ref
from . import vcs
import collections


# All Test() instances in the order they were created.
tests = []


# Container to hold normalized procedure step field definitions. This is
# not part of the public API as fields are defined via normal tuples, which
# are then validated to create instances of this named tuple.
ProcedureStepField = collections.namedtuple(
    'ProcedureStepField',
    ['title', 'length', 'suffix'],
)


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


class Test(object):
    """Creates a single test procedure.

    Numeric identifiers will be incrementally assigned to each test in the
    order they appear.

    Args:
        title (str): A short phrase describing the test procedure, that is
            combined with the automatically-assigned numeric ID to identify
            this specific test.
        label (str, optional): An identifier for use in content strings to
            refer back to this test. See :ref:`labels`.
        objective (str, optional): A longer narrative, possibly spanning
            several sentences or paragraphs, describing the intent of the
            test procedure.
        references (dict, optional): References associated with this test.
            Keys must be labels defined with
            :py:func:`testgen.add_reference_category`; values are a list of
            strings containing references for that category.
        equipment (list[str], optional): A list of equipment required to
            perform the procedure; will be rendered as a bullet list under
            a dedicated section heading.
        preconditions (list[str], optional): A list of conditions that must be
            met before the procedure can commence.
        procedure (list[str or dict], optional): A list of procedure steps to
            be output as an enumerated list. See :ref:`procedure`.

    Raises:
        KeyError
        TypeError
        ValueError
    """

    def __init__(self,
                 title,
                 label=None,
                 objective=None,
                 references={},
                 equipment=[],
                 preconditions=[],
                 procedure=[],
                 ):
        global tests
        self.id = id.get_id()
        self.title = misc.nonempty_string('Title', title)
        self._store_label(label)
        self.objective = self._validate_objective(objective)
        self.references = self._validate_refs(references)
        self.equipment = self._validate_equipment(equipment)
        self.preconditions = self._validate_string_list('Preconditions',
                                                        preconditions)
        self.procedure = self._validate_procedure(procedure)

        # The current project information is captured using copy() because
        # the project information dictionary may change for later tests;
        # copy() ensures this instance's values are unaffected.
        self.project_info = misc.project_info.copy()

        tests.append(self)

    def _store_label(self, lbl):
        """Assigns this test to a given label."""
        if lbl is not None:
            id_string = id.to_string(self.id)
            try:
                label.add(lbl, id_string)
            except Exception as e:
                e.add_note("Invalid label assigned to test {0} {1}.".format(
                    id_string, self.title))
                raise e

    def _validate_objective(self, obj):
        """Validates the objective parameter."""
        if obj is not None:
            return misc.nonempty_string('Objective', obj)

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
        label = misc.nonempty_string('Reference label', label)

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

    def _validate_equipment(self, equip):
        """Validates the equipment parameter."""
        return self._validate_string_list('Equipment', equip)

    def _validate_procedure(self, lst):
        """Validates the procedure parameter."""
        if not isinstance(lst, list):
            raise TypeError('Procedure must be a list.')
        return [self._validate_procedure_step(step) for step in lst]

    def _validate_procedure_step(self, step):
        """Validates a dictionary defining a single procedure step."""
        # Convert a string to a dict with text key.
        if isinstance(step, str):
            step = {'text': step}

        elif not isinstance(step, dict):
            raise TypeError(
                'A procedure step must be either a string or dictionary.')

        try:
            text = step['text']
        except KeyError:
            raise KeyError(
                "A procedure step dictionary must have a 'text' key.")
        step['text'] = misc.nonempty_string("Procedure step text", text)

        try:
            fields = step['fields']
        except KeyError:
            pass
        else:
            step['fields'] = self._validate_procedure_step_fields(fields)

        self._check_procedure_step_keys(step)
        return step

    def _check_procedure_step_keys(self, step):
        """Checks a procedure step dictionary for undefined keys."""
        allowed = {
            'text',
            'fields',
        }
        undefined = set(step.keys()).difference(allowed)
        if undefined:
            raise KeyError(
                "Procedure step dictionary contains undefined key(s): "
                "{0}".format(', '.join([str(i) for i in undefined])))

    def _validate_procedure_step_fields(self, fields):
        """Validates the list of field definitions."""
        if not isinstance(fields, list):
            raise TypeError('Procedure step fields must be a list.')
        return [self._create_procedure_step_field(f) for f in fields]

    def _create_procedure_step_field(self, tpl):
        """
        Converts a raw procedure step field definition tuple into a
        named tuple.
        """
        if not isinstance(tpl, tuple):
            raise TypeError('Procedure step fields list items must be tuples.')

        # Validate the required items: title and length.
        try:
            raw_title = tpl[0]
            raw_length = tpl[1]
        except IndexError:
            raise ValueError(
                'Procedure step field tuples must have at least two members: '
                'title and length.')
        else:
            title = misc.nonempty_string(
                'Procedure step field title',
                raw_title
            )
            length = misc.validate_field_length(raw_length)

        # Validate suffix, providing a default vaule if omitted.
        try:
            raw = tpl[2]
        except IndexError:
            suffix = ''
        else:
            suffix = misc.nonempty_string('Procedure step field suffix', raw)

        if len(tpl) > 3:
            raise ValueError(
                'Procedure step field tuples may not exceed three members: '
                'title, length, and suffix.')

        return ProcedureStepField(title, length, suffix)

    def _validate_string_list(self, name, lst):
        """Checks a list to ensure it contains only non-empty/blank strings."""
        if not isinstance(lst, list):
            raise TypeError("{0} must be a list of strings.".format(name))
        return [misc.nonempty_string("{0} item".format(name), s) for s in lst]

    def _pregenerate(self):
        """
        Performs tasks that need to occur after all tests have been defined,
        but before actual output is generated.
        """
        self._resolve_labels()

    def _resolve_labels(self):
        """Replaces label placeholders with their target IDs."""
        if self.objective:
            self.objective = label.resolve(self.objective)
        self.preconditions = [label.resolve(pc) for pc in self.preconditions]
        [step.update({'text': label.resolve(step['text'])})
         for step in self.procedure]


def generate(path='pdf'):
    """Builds PDF output files for all defined tests.

    Should be called once near the end of the script after tests have been
    created with :py:class:`testgen.Test`.

    .. warning::

        The generated tests will *overwrite* files in the output directory.
        Any content in the output directory that needs to be preserved
        must be copied elsewhere before generating output documents.

    Args:
        path (str, optional): Output directory where PDFs will be saved.

    Raises:
        KeyError
        TypeError
        ValueError
    """
    if not isinstance(path, str):
        raise TypeError('Output path must be a string.')
    [t._pregenerate() for t in tests]

    try:
        git = vcs.Git()
    except vcs.NoVersionControlError:
        draft = False
        version = None
    else:
        draft = not git.clean
        version = git.version

    [pdf.TestDocument(t, path, draft, version) for t in tests]
