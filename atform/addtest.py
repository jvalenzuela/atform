"""This module contains the add_test() API and ancilliary validation functions."""

import dataclasses

from . import error
from . import field
from . import id as id_
from . import label as label_
from . import misc
from . import procedure as procedure_
from . import state


@dataclasses.dataclass
# This is a data class intended to contain all attributes required to populate
# a single test document.
# pylint: disable=too-many-instance-attributes
class TestContent:
    """Storage class containing test document content."""

    id: tuple
    title: str
    fields: list
    objective: str
    references: list
    equipment: list
    preconditions: list
    procedure: list
    project_info: dict
    call_frame: error.CallFrame
    labels: dict
    copyright: str
    signatures: list
    logo_hash: bytes

    @property
    def full_name(self):
        """String containing the combination of ID and title."""
        return " ".join((id_.to_string(self.id), self.title))

    def pregenerate(self):
        """
        Performs tasks that need to occur after all tests have been defined,
        but before actual output is generated.
        """
        try:
            self._build_label_mapping()
            self._resolve_labels()
        except error.UserScriptError as e:
            # Set the exception's call frame to the call to add_test() where
            # this test was defined, instead of the API that called this method.
            e.call_frame = self.call_frame

            add_exception_context(e, self.id, self.title)

    def _resolve_labels(self):
        """Replaces label placeholders with their target IDs."""
        if self.objective:
            try:
                self.objective = label_.resolve(self.objective, self.labels)
            except error.UserScriptError as e:
                e.add_field("Test Section", "Objective")
                raise

        for i, item in enumerate(self.preconditions):
            try:
                self.preconditions[i] = label_.resolve(item, self.labels)
            except error.UserScriptError as e:
                e.add_field("Precondition Item", i + 1)
                raise

        for i, step in enumerate(self.procedure, start=1):
            try:
                step.resolve_labels(self.labels)
            except error.UserScriptError as e:
                e.add_field("Procedure Step", i)
                raise

    def _build_label_mapping(self):
        """Updates label mapping to include globally-defined labels."""
        # Check for duplicate labels defined in the global scope.
        globals_ = set(state.labels.keys())
        locals_ = set(self.labels.keys())
        dups = globals_.intersection(locals_)
        try:
            dup = dups.pop()
        except KeyError:
            self.labels.update(state.labels)
        else:
            raise error.UserScriptError(
                f"Duplicate label: {dup}",
                f"""
                The label "{dup}" has been defined in multiple places, with the
                values "{state.labels[dup]}" and "{self.labels[dup]}".
                Select a label name that is not used elsewhere.
                """,
            )

    def __eq__(self, other):
        """Equality implementation for detecting content differences.

        This is used for the --diff option, and specifically excludes the
        following fields:

        call_frame: Used only for generating error messages; not relevant
                    for comparing test content.

        labels: Differences in labels are detected by evaluating the strings
                where placeholders are used after placeholders are replaced
                with their targets, so comparing the label mapping is unnecessary
                and can yield false-positives, e.g., label name change but
                still points to the same target.
        """
        return (
            self.id == other.id
            and self.title == other.title
            and self.fields == other.fields
            and self.objective == other.objective
            and self.references == other.references
            and self.equipment == other.equipment
            and self.preconditions == other.preconditions
            and self.procedure == other.procedure
            and self.project_info == other.project_info
            and self.copyright == other.copyright
            and self.signatures == other.signatures
            and self.logo_hash == other.logo_hash
        )


@dataclasses.dataclass
class Reference:
    """Storage for a single reference category and assigned items."""

    label: str
    title: str
    items: list

    def __eq__(self, other):
        """Equality implementation for detecting differences.

        Excludes the label as it is not included in the output PDF, avoiding
        false-positive change detection if the label for a reference is changed but
        the title and items remain the same.
        """
        return self.title == other.title and self.items == other.items


def validate_objective(obj):
    """Validates the objective parameter."""
    if obj is not None:
        return misc.nonempty_string("Objective", obj)
    return None


def validate_refs(refs):
    """Validates the references parameter."""
    if refs is None:
        refs = {}
    elif not isinstance(refs, dict):
        raise error.UserScriptError(
            f"Invalid references data type: {type(refs).__name__}",
            "References must be a dictionary.",
        )

    valid = [validate_ref_category(*ref) for ref in refs.items()]

    # Once all categories and items have been validated, sort them
    # them according to the order the categories were defined.
    categories = list(state.ref_titles.keys())
    valid.sort(key=lambda r: categories.index(r.label))

    return valid


def validate_ref_category(label, refs):
    """Validates a single reference category and associated references."""
    label = misc.nonempty_string("Reference label", label)

    # Ensure the label has been defined by add_reference_category().
    try:
        title = state.ref_titles[label]
    except KeyError as e:
        raise error.UserScriptError(
            f"Invalid reference label: {label}",
            """Use a reference label that has been previously defined
            with atform.add_reference_category.""",
        ) from e

    # Check the list of references for this category.
    validated_refs = []

    if not isinstance(refs, list):
        raise error.UserScriptError(
            f'Invalid type for "{label}" references: {type(refs).__name__}',
            "References for a given category must be contained in a list.",
        )

    for reference in refs:
        try:
            if not isinstance(reference, str):
                raise error.UserScriptError(
                    f"Invalid reference list item data type: {type(reference).__name__}",
                    "Items in the list for a reference category must be strings.",
                )
            reference = reference.strip()

            # Reject duplicate references.
            if reference in validated_refs:
                raise error.UserScriptError(
                    f"Duplicate reference: {reference}",
                    "Ensure all references within a category are unique.",
                )

        except error.UserScriptError as e:
            e.add_field("Reference Category", label)
            raise

        # Ignore blank/empty references.
        if reference:
            validated_refs.append(reference)

    return Reference(label, title, validated_refs)


def validate_string_list(name, lst):
    """Checks a list to ensure it contains only non-empty/blank strings."""
    if lst is None:
        lst = []
    elif not isinstance(lst, list):
        raise error.UserScriptError(
            f"{name} must be a list of strings.",
        )
    items = []
    for i, s in enumerate(lst, start=1):
        try:
            items.append(misc.nonempty_string(f"{name} list item", s))
        except error.UserScriptError as e:
            e.add_field(f"{name} item #", i)
            raise
    return items


def add_exception_context(e, tid, title):
    """Adds information identifying a test to a UserScriptError."""
    if title:
        e.add_field("Test Title", title)
    e.add_field("Test ID", id_.to_string(tid))
    raise e


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
# This function intentionally offers many keyword arguments to allow the
# resulting test document to be completely populated via arguments.
# pylint: disable=too-many-arguments
def add_test(
    title,
    *,
    label=None,
    include_fields=None,
    exclude_fields=None,
    active_fields=None,
    objective=None,
    references=None,
    equipment=None,
    preconditions=None,
    procedure=None,
):
    """Creates a single test procedure.

    Numeric identifiers will be incrementally assigned to each test in the
    order they appear.

    .. seealso:: :ref:`write`

    Args:
        title (str): A short phrase describing the test procedure, that is
            combined with the automatically-assigned numeric ID to identify
            this specific test. Must not be blank.
        label (str, optional): An identifier for use in content strings to
            refer back to this test; may not be blank. See :ref:`labels`.
        include_fields (list[str], optional): Names of fields to add to
            this test; provides the same behavior as the ``include`` parameter
            of :py:func:`atform.set_active_fields` while only affecting
            this test. See :py:func:`atform.add_field`.
        exclude_fields (list[str], optional): Names of fields to remove
            from this test; provides the same behavior as the ``exclude`` parameter
            of :py:func:`atform.set_active_fields` while only affecting
            this test. See :py:func:`atform.add_field`.
        active_fields (list[str], optional): Names of fields to apply
            to this test; provides the same behavior as the ``active`` parameter
            of :py:func:`atform.set_active_fields` while only affecting
            this test. See :py:func:`atform.add_field`.
        objective (str, optional): A longer narrative, possibly spanning
            several sentences or paragraphs, describing the intent of the
            test procedure. Must not be blank.
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
    content = {}
    content["copyright"] = state.copyright_
    content["signatures"] = state.signatures
    content["logo_hash"] = state.logo_hash

    # Capture the current API call frame so the location where this test was
    # defined can be referenced in exceptions raised in later API calls
    # that result from this test's content, e.g., label resolution.
    content["call_frame"] = error.api_call_frame

    content["id"] = id_.get_id()
    content["labels"] = {}

    # The current project information is captured using copy() because
    # the project information dictionary may change for later tests;
    # copy() ensures this instance's values are unaffected.
    project_info = state.project_info.copy()

    try:
        content["title"] = misc.nonempty_string("Title", title)
        content["fields"] = field.get_active_fields(
            include_fields,
            exclude_fields,
            active_fields,
        )
        content["objective"] = validate_objective(objective)
        content["references"] = validate_refs(references)
        content["equipment"] = validate_string_list("Equipment", equipment)
        content["preconditions"] = validate_string_list("Preconditions", preconditions)
        content["procedure"] = procedure_.validate(procedure, content["labels"])
        content["project_info"] = project_info

        if label is not None:
            id_string = id_.to_string(content["id"])
            label_.add(label, id_string)

    except error.UserScriptError as e:
        try:
            title = content["title"]
        except KeyError:
            title = None
        add_exception_context(e, content["id"], title)

    state.tests[content["id"]] = TestContent(**content)
