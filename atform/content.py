# This module implements the objects storing test procedure content as it is
# created.


from . import error
from . import id
from . import field
from . import label
from . import misc
from . import pdf
from . import ref
from . import vcs
import collections


# All Test() instances in the order they were created.
tests = []


class ProcedureStep(object):
    """Object containing all user-provided content for a single procedure step.

    This is not created directly by the user, but is instantiated using
    an item, string or dict, from the procedure parameter list of Test.
    """

    def __init__(self, raw, num):
        data = self._normalize_type(raw)
        self.text = self._validate_text(data)
        self.fields = self._validate_fields(data)
        self._validate_label(data, num)
        self._check_undefined_keys(data)

    @staticmethod
    def _normalize_type(raw):
        """Normalizes the raw data into a dict."""
        # Convert a string to a dict with text key.
        if isinstance(raw, str):
            normalized = {"text": raw}

        elif isinstance(raw, dict):
            normalized = raw

        else:
            raise error.UserScriptError(
                f"Invalid procedure step data type: {type(raw).__name__}",
                "A procedure step must be a string or dictionary.",
            )

        return normalized

    @staticmethod
    def _check_undefined_keys(data):
        """Raises an exception for any unconsumed keys."""
        if data:
            keys = [str(k) for k in data.keys()]
            raise error.UserScriptError(
                "Undefined procedure step dictionary key(s): {0}".format(
                    ", ".join(keys)
                ))

    @staticmethod
    def _validate_text(data):
        """Validates the text key."""
        try:
            text = data.pop("text")
        except KeyError:
            raise error.UserScriptError(
                'A procedure step dictionary must have a "text" key.',
                """Add a "text" key with a string value containing
                instructions for the step.""",
            )
        return misc.nonempty_string("Procedure step text", text)

    def _validate_fields(self, data):
        """Validates the fields key."""
        tpls = data.pop("fields", [])
        if not isinstance(tpls, list):
            raise error.UserScriptError(
                f"""
                Invalid procedure step fields data type:
                {type(tpls).__name__}
                """,
                "Procedure step fields must be a list.",
            )

        fields = []
        for i in range(len(tpls)):
            try:
                fields.append(self._create_field(tpls[i]))
            except error.UserScriptError as e:
                e.add_field("Procedure Step Field #", i+1)
                raise
        return fields

    @staticmethod
    def _create_field(tpl):
        """
        Converts a raw procedure step field definition tuple into a
        named tuple.
        """
        if not isinstance(tpl, tuple):
            raise error.UserScriptError(
                f"""
                Invalid procedure step field list item data type:
                {type(tpl).__name__}
                """,
                """
                Each item in the list of fields for a procedure step must
                be a tuple.
                """,
            )

        # Validate the required items: title and length.
        try:
            raw_title = tpl[0]
            raw_length = tpl[1]
        except IndexError:
            raise error.UserScriptError(
                """
                Procedure step field tuple is too short.
                """,
                """
                A tuple defining a data entry field for a procedure step
                must have at least two members: title and length.
                """,
            )
        else:
            title = misc.nonempty_string(
                "Procedure step field title",
                raw_title
            )
            length = misc.validate_field_length(raw_length)

        # Validate suffix, providing a default value if omitted.
        try:
            raw = tpl[2]
        except IndexError:
            suffix = ""
        else:
            suffix = misc.nonempty_string("Procedure step field suffix", raw)

        if len(tpl) > 3:
            raise error.UserScriptError(
                """
                Procedure step field tuple is too long.
                """,
                """
                A tuple defining a data entry field for a procedure step
                may not exceed three members: title, length, and suffix.
                """,
            )

        return ProcedureStepField(title, length, suffix)

    @staticmethod
    def _validate_label(data, num):
        """Creates a label referencing this step."""
        try:
            lbl = data.pop("label")

        # Label is optional; do nothing if omitted.
        except KeyError:
            pass

        else:
            label.add(lbl, str(num))

    def resolve_labels(self):
        """Replaces label placeholders with their target IDs."""
        self.text = label.resolve(self.text)


# Container to hold normalized procedure step field definitions. This is
# not part of the public API as fields are defined via normal tuples, which
# are then validated to create instances of this named tuple.
ProcedureStepField = collections.namedtuple(
    "ProcedureStepField",
    ["title", "length", "suffix"],
)


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
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
        include_fields (list[str], optional): Names of fields to add to
            this test. See :py:func:`atform.add_field`.
        exclude_fields (list[str], optional): Names of fields to remove
            from this test. See :py:func:`atform.add_field`.
        active_fields (list[str], optional): Names of fields to apply
            to this test. See :py:func:`atform.add_field`.
        objective (str, optional): A longer narrative, possibly spanning
            several sentences or paragraphs, describing the intent of the
            test procedure.
        references (dict, optional): A mapping from category labels
            defined with :py:func:`atform.add_reference_category`
            to lists of reference strings for that category.
            For example, ``{"C1":["rA", "rB"]}`` would result in references
            ``"rA"`` and ``"rB"`` to be listed under the ``"C1"`` category.
            See :ref:`ref`.
        equipment (list[str], optional): A list of equipment required to
            perform the procedure; will be rendered as a bullet list under
            a dedicated section heading.
        preconditions (list[str], optional): A list of conditions that must be
            met before the procedure can commence.
        procedure (list[str or dict], optional): A list of procedure steps to
            be output as an enumerated list. See :ref:`procedure`.
    """

    def __init__(self,
                 title,
                 label=None,
                 include_fields=[],
                 exclude_fields=[],
                 active_fields=None,
                 objective=None,
                 references={},
                 equipment=[],
                 preconditions=[],
                 procedure=[],
                 ):
        global tests
        self.id = id.get_id()
        try:
            self.title = misc.nonempty_string("Title", title)
            self._store_label(label)
            self.fields = field.get_active_fields(
                include_fields,
                exclude_fields,
                active_fields,
            )
            self.objective = self._validate_objective(objective)
            self.references = self._validate_refs(references)
            self.equipment = self._validate_equipment(equipment)
            self.preconditions = self._validate_string_list("Preconditions",
                                                            preconditions)
            self.procedure = self._validate_procedure(procedure)
        except error.UserScriptError as e:
            self._add_exception_context(e)

        # The current project information is captured using copy() because
        # the project information dictionary may change for later tests;
        # copy() ensures this instance's values are unaffected.
        self.project_info = misc.project_info.copy()

        tests.append(self)

    def _store_label(self, lbl):
        """Assigns this test to a given label."""
        if lbl is not None:
            id_string = id.to_string(self.id)
            label.add(lbl, id_string)

    @staticmethod
    def _validate_objective(obj):
        """Validates the objective parameter."""
        if obj is not None:
            return misc.nonempty_string("Objective", obj)

    def _validate_refs(self, refs):
        """Validates the references parameter."""
        if not isinstance(refs, dict):
            raise error.UserScriptError("References must be a dictionary.")
            raise error.UserScriptError(
                f"Invalid references data type: {type(refs).__name__}",
                "References must be a dictionary.",
            )

        validated = {}
        [validated.update(self._validate_ref_category(label, refs[label]))
         for label in refs]
        return validated

    @staticmethod
    def _validate_ref_category(label, refs):
        """Validates a single reference category and associated references."""
        label = misc.nonempty_string("Reference label", label)

        # Ensure the label has been defined by add_reference_category().
        try:
            ref.titles[label]
        except KeyError:
            raise error.UserScriptError(
                f"Invalid reference label: {label}",
                """Use a reference label that has been previously defined
                with atform.add_reference_category.""",
            )

        # Check the list of references for this category.
        validated_refs = []

        if not isinstance(refs, list):
            raise TypeError(
                f'Reference items for "{label}" category must be contained '
                "in a list")

        for reference in refs:
            try:
                if not isinstance(reference, str):
                    raise error.UserScriptError(
                        f"""
                        Invalid reference list item data type:
                        {type(reference).__name__}
                        """,
                        """
                        Items in the list for a reference category
                        must be strings.
                        """,
                    )
                reference = reference.strip()

                # Reject duplicate references.
                if reference in validated_refs:
                    raise error.UserScriptError(
                        f"Duplicate reference: {reference}",
                        """Ensure all references within a category are
                        unique."""
                    )

            except error.UserScriptError as e:
                e.add_field("Reference Category", label)
                raise

            # Ignore blank/empty references.
            if reference:
                validated_refs.append(reference)


        return {label: validated_refs}

    def _validate_equipment(self, equip):
        """Validates the equipment parameter."""
        return self._validate_string_list("Equipment", equip)

    @staticmethod
    def _validate_procedure(lst):
        """Validates the procedure parameter."""
        if not isinstance(lst, list):
            raise error.UserScriptError("Procedure must be a list.")
        steps = []
        for i in range(len(lst)):
            num = i + 1 # Step numbers are one-based.
            try:
                steps.append(ProcedureStep(lst[i], num))
            except error.UserScriptError as e:
                e.add_field("Procedure Step", num)
                raise
        return steps

    @staticmethod
    def _validate_string_list(name, lst):
        """Checks a list to ensure it contains only non-empty/blank strings."""
        if not isinstance(lst, list):
            raise error.UserScriptError(
                f"{name} must be a list of strings.",
            )
        items = []
        for i in range(len(lst)):
            try:
                items.append(misc.nonempty_string(f"{name} list item", lst[i]))
            except error.UserScriptError as e:
                e.add_field(f"{name} item #", i+1)
                raise
        return items

    @error.external_call
    def _pregenerate(self):
        """
        Performs tasks that need to occur after all tests have been defined,
        but before actual output is generated.
        """
        try:
            self._resolve_labels()
        except error.UserScriptError as e:
            self._add_exception_context(e)

    def _resolve_labels(self):
        """Replaces label placeholders with their target IDs."""
        if self.objective:
            try:
                self.objective = label.resolve(self.objective)
            except error.UserScriptError as e:
                e.add_field("Test Section", "Objective")
                raise

        for i in range(len(self.preconditions)):
            try:
                self.preconditions[i] = label.resolve(self.preconditions[i])
            except error.UserScriptError as e:
                e.add_field("Precondition Item", i+1)
                raise

        for i in range(len(self.procedure)):
            try:
                self.procedure[i].resolve_labels()
            except error.UserScriptError as e:
                e.add_field("Procedure Step", i+1)
                raise

    def _add_exception_context(self, e):
        """Adds information identifying this test to a UserScriptError."""
        try:
            self.title
        except AttributeError:
            pass
        else:
            e.add_field("Test Title", self.title)

        e.add_field("Test ID", id.to_string(self.id))
        raise e


@error.exit_on_script_error
def generate(path="pdf"):
    """Builds PDF output files for all defined tests.

    Should be called once near the end of the script after tests have been
    created with :py:class:`atform.Test`.

    .. warning::

        The generated tests will *overwrite* files in the output directory.
        Any content in the output directory that needs to be preserved
        must be copied elsewhere before generating output documents.

    Args:
        path (str, optional): Output directory where PDFs will be saved.
    """
    if not isinstance(path, str):
        raise error.UserScriptError(
            "Output path must be a string.",
        )
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
