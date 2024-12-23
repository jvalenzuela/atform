"""Objects to store test procedure content."""


import os

from . import error
from . import id as id_
from . import field
from . import label as label_
from . import misc
from . import pdf
from . import procedure as procedure_
from . import state
from . import vcs


def build_path(tid, root, depth):
    """Constructs a path where a test's output PDF will be written.

    The path will consist of the root, followed by a folder per
    section number limited to depth, e.g., <root>/<x>/<y> for an ID x.y.z
    and depth 2. The final number in an ID is not translated to a folder.
    """
    folders = [root]

    # Append a folder for each section level.
    for i, section_id in enumerate(tid[:depth]):

        # Include the section number and title if the section has a title.
        try:
            section = state.section_titles[tid[: i + 1]]
            section_folder = f"{section_id} {section}"

        # Use only the section number if the section has no title.
        except KeyError:
            section_folder = str(section_id)

        folders.append(section_folder)

    return os.path.join(*folders)


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
# This class intentionally offers many keyword arguments to allow the
# resulting test document to be completely populated via __init__().
# pylint: disable=too-many-arguments
class Test:
    """Creates a single test procedure.

    Numeric identifiers will be incrementally assigned to each test in the
    order they appear.

    .. seealso:: :ref:`write`

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
        self.id = id_.get_id()
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
            self.procedure = procedure_.validate(procedure)
        except error.UserScriptError as e:
            self._add_exception_context(e)

        # The current project information is captured using copy() because
        # the project information dictionary may change for later tests;
        # copy() ensures this instance's values are unaffected.
        self.project_info = state.project_info.copy()

        state.tests.append(self)

    def _store_label(self, lbl):
        """Assigns this test to a given label."""
        if lbl is not None:
            id_string = id_.to_string(self.id)
            label_.add(lbl, id_string)

    @staticmethod
    def _validate_objective(obj):
        """Validates the objective parameter."""
        if obj is not None:
            return misc.nonempty_string("Objective", obj)
        return None

    def _validate_refs(self, refs):
        """Validates the references parameter."""
        if refs is None:
            refs = {}
        elif not isinstance(refs, dict):
            raise error.UserScriptError(
                f"Invalid references data type: {type(refs).__name__}",
                "References must be a dictionary.",
            )

        return dict([self._validate_ref_category(label, refs[label])
                     for label in refs])

    @staticmethod
    def _validate_ref_category(label, refs):
        """Validates a single reference category and associated references."""
        label = misc.nonempty_string("Reference label", label)

        # Ensure the label has been defined by add_reference_category().
        try:
            state.ref_titles[label]
        except KeyError as e:
            raise error.UserScriptError(
                f"Invalid reference label: {label}",
                """Use a reference label that has been previously defined
                with atform.add_reference_category.""",
            ) from e

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


        return label, validated_refs

    def _validate_equipment(self, equip):
        """Validates the equipment parameter."""
        return self._validate_string_list("Equipment", equip)


    @staticmethod
    def _validate_string_list(name, lst):
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

    @error.external_call
    def pregenerate(self):
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
                self.objective = label_.resolve(self.objective)
            except error.UserScriptError as e:
                e.add_field("Test Section", "Objective")
                raise

        for i, item in enumerate(self.preconditions):
            try:
                self.preconditions[i] = label_.resolve(item)
            except error.UserScriptError as e:
                e.add_field("Precondition Item", i+1)
                raise

        for i, step in enumerate(self.procedure, start=1):
            try:
                step.resolve_labels()
            except error.UserScriptError as e:
                e.add_field("Procedure Step", i)
                raise

    def _add_exception_context(self, e):
        """Adds information identifying this test to a UserScriptError."""
        try:
            self.title
        except AttributeError:
            pass
        else:
            e.add_field("Test Title", self.title)

        e.add_field("Test ID", id_.to_string(self.id))
        raise e


@error.exit_on_script_error
def generate(path="pdf", folder_depth=0):
    """Builds PDF output files for all defined tests.

    Should be called once near the end of the script after tests have been
    created with :py:class:`atform.Test`.

    .. warning::

        The generated tests will *overwrite* files in the output directory.
        Any content in the output directory that needs to be preserved
        must be copied elsewhere before generating output documents.

    Args:
        path (str, optional): Output directory where PDFs will be saved.
        folder_depth (int, optional): The number of test ID levels used to
            create section folders. For example, if ``folder_depth`` is 2,
            all PDFs will be output into section subfolders two deep,
            such as :file:`1/2/1.2.3.4 Test.pdf`.

            Must be greater than or equal to 0, and less than the ID
            depth set with :py:func:`atform.set_id_depth`.
    """
    if not isinstance(path, str):
        raise error.UserScriptError(
            "Output path must be a string.",
        )

    for t in state.tests:
        t.pregenerate()

    if not isinstance(folder_depth, int):
        raise error.UserScriptError(
            "Folder depth must be an integer.",
        )

    max_depth = len(state.current_id) - 1
    if (folder_depth < 0) or (folder_depth > max_depth):
        if max_depth:
            remedy = f"""
            The folder depth must be within 0 and {max_depth}, inclusive.
            """
        else:
            remedy = """
            atform.set_id_depth() must first be called to increase the
            number of test identifier fields before folder_depth can
            be increased beyond zero.
            """
        raise error.UserScriptError(
            "Invalid folder depth value.",
            remedy,
        )

    try:
        git = vcs.Git()
    except vcs.NoVersionControlError:
        version = None
    else:
        version = git.version if git.clean else "draft"

    for t in state.tests:
        test_path = build_path(t.id, path, folder_depth)
        pdf.TestDocument(t, test_path, version)
