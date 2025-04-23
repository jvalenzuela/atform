# Unit tests for the label module.


from tests import utils
import atform
from atform import label
from atform.error import UserScriptError
import string
import unittest


class LabelString:
    """Base class for testing various label strings."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string label."""
        with self.assertRaises(UserScriptError):
            self.create_label(42)

    def test_empty(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(UserScriptError):
            self.create_label("")

    def test_blank(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(UserScriptError):
            self.create_label(string.whitespace)

    def test_invalid_first_character(self):
        """Confirm exception for a label with an invalid first character."""
        invalid = set(string.printable)

        # Exclude valid characters.
        invalid.difference_update(string.ascii_letters)
        invalid.remove("_")

        for c in invalid:
            with self.subTest(c=c), self.assertRaises(UserScriptError):
                self.create_label(c + "foo")

    def test_invalid_following_character(self):
        """Confirm exception for a label with an invalid character after the first."""
        invalid = set(string.printable)

        # Exclude valid characters.
        invalid.difference_update(string.ascii_letters)
        invalid.difference_update(string.digits)
        invalid.difference_update("_")

        for c in invalid:
            with self.subTest(c=c), self.assertRaises(UserScriptError):
                self.create_label("foo" + c)

    def test_nonascii(self):
        """Confirm exception for a label containing non-ASCII characters."""
        with self.assertRaises(UserScriptError):
            self.create_label("foo\u00dfar")

    def test_valid_single_character(self):
        """Confirm a valid single-character label is accepted."""
        valid = set(string.ascii_letters)
        valid.add("_")

        for c in valid:
            utils.reset()
            with self.subTest(c=c):
                self.create_label(c)

    def test_valid_multi_character(self):
        """Confirm a valid multi-character label is accepted."""
        valid = set(string.ascii_letters)
        valid.update(string.digits)
        valid.add("_")

        for c in valid:
            utils.reset()
            with self.subTest(c=c):
                self.create_label("foo" + c)


class TestId(LabelString, unittest.TestCase):
    """Tests for labels assigned to a test."""

    def create_label(self, lbl):
        atform.add_test("title", label=lbl)


class ProcedureStep(LabelString, unittest.TestCase):
    """Tests for labels assigned to a procedure step."""

    def create_label(self, lbl):
        atform.add_test("title", procedure=[{"text": "step", "label": lbl}])


class Resolve(unittest.TestCase):
    """Unit tests for the resolve() function."""

    def setUp(self):
        utils.reset()

    def test_undefined_label(self):
        """Confirm exception for a string with an undefined label."""
        with self.assertRaises(UserScriptError):
            label.resolve("$foo", {})

    def test_invalid_identifier(self):
        """Confirm exception for a string with an invalid identifier."""
        with self.assertRaises(UserScriptError):
            label.resolve("$ foo", {})

    def test_no_identifiers(self):
        """Confirm a string with no identifiers is returned unmodified."""
        s = "foo"
        self.assertEqual(s, label.resolve(s, {}))

    def test_replacement(self):
        """Confirm labels are replaced with their IDs."""
        mapping = {
            "spam": "foo",
            "eggs": "bar",
        }
        self.assertEqual("foo bar", label.resolve("$spam $eggs", mapping))


class Duplicate(unittest.TestCase):
    """Duplicate label detection tests."""

    def setUp(self):
        utils.reset()

    def test_id(self):
        """Confirm exception for duplicate test ID labels."""
        atform.add_test("t1", label="foo")
        with self.assertRaises(UserScriptError):
            atform.add_test("t2", label="foo")

    def test_procedure_step(self):
        """Confirm exception for duplicate procedure step labels."""
        with self.assertRaises(UserScriptError):
            atform.add_test(
                "test",
                procedure=[
                    {"text": "spam", "label": "foo"},
                    {"text": "eggs", "label": "foo"},
                ],
            )

    def test_procedure_step_id(self):
        """Confirm exception for a duplicate procedure step and test ID label defined in the same test."""
        atform.add_test(
            "test",
            label="foo",
            procedure=[{"text": "spam", "label": "foo"}],
        )
        t = utils.get_test_content()
        with self.assertRaises(UserScriptError):
            t.pregenerate()

    def test_procedure_step_previous_id(self):
        """Confirm exception for a procedure step label duplicating a test ID label defined in a previous test."""
        atform.add_test("t1", label="foo")
        atform.add_test("t2", procedure=[{"text": "spam", "label": "foo"}])
        t2 = utils.get_test_content()
        with self.assertRaises(UserScriptError):
            t2.pregenerate()

    def test_id_previous_procedure_step(self):
        """Confirm exception for a test ID label duplicating a procedure step label defined in a previous test."""
        atform.add_test("t1", procedure=[{"text": "spam", "label": "foo"}])
        t1 = utils.get_test_content()
        atform.add_test("t2", label="foo")
        with self.assertRaises(UserScriptError):
            t1.pregenerate()


class IdReplacementBefore(unittest.TestCase):
    """Tests validating test ID label replacement where the label is defined before the placeholder."""

    def setUp(self):
        utils.reset()
        atform.add_test("title", label="label")

    def test_objective(self):
        """Confirm placeholder is replaced in the objective."""
        atform.add_test("title", objective="$label")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.objective)

    def test_precondition(self):
        """Confirm placeholder is replaced in the preconditions."""
        atform.add_test("title", preconditions=["$label"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.preconditions[0])

    def test_procedure_step_string(self):
        """Confirm placeholder is replaced in string procedure steps."""
        atform.add_test("title", procedure=["$label"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[0].text)

    def test_procedure_step_dict(self):
        """Confirm placeholder is replaced in dict procedure steps."""
        atform.add_test("title", procedure=[{"text": "$label"}])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[0].text)


class IdReplacementSame(unittest.TestCase):
    """Tests validating test ID label replacement where the label is defined in the same test as the placeholder."""

    def setUp(self):
        utils.reset()

    def test_objective(self):
        """Confirm placeholder is replaced in the objective."""
        atform.add_test("title", label="label", objective="$label")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.objective)

    def test_precondition(self):
        """Confirm placeholder is replaced in the preconditions."""
        atform.add_test("title", label="label", preconditions=["$label"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.preconditions[0])

    def test_procedure_step_string(self):
        """Confirm placeholder is replaced in string procedure steps."""
        atform.add_test("title", label="label", procedure=["$label"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[0].text)

    def test_procedure_step_dict(self):
        """Confirm placeholder is replaced in dict procedure steps."""
        atform.add_test("title", label="label", procedure=[{"text": "$label"}])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[0].text)


class IdReplacementAfter(unittest.TestCase):
    """Tests validating test ID replacement where the label is defined after the placeholder."""

    def setUp(self):
        utils.reset()

    def test_objective(self):
        """Confirm placeholder is replaced in the objective."""
        atform.add_test("title", objective="$label")
        t = utils.get_test_content()
        atform.add_test("title", label="label")
        t.pregenerate()
        self.assertEqual("2", t.objective)

    def test_precondition(self):
        """Confirm placeholder is replaced in the preconditions."""
        atform.add_test("title", preconditions=["$label"])
        t = utils.get_test_content()
        atform.add_test("title", label="label")
        t.pregenerate()
        self.assertEqual("2", t.preconditions[0])

    def test_procedure_step_string(self):
        """Confirm placeholder is replaced in string procedure steps."""
        atform.add_test("title", procedure=["$label"])
        t = utils.get_test_content()
        atform.add_test("title", label="label")
        t.pregenerate()
        self.assertEqual("2", t.procedure[0].text)

    def test_procedure_step_dict(self):
        """Confirm placeholder is replaced in dict procedure steps."""
        atform.add_test("title", procedure=[{"text": "$label"}])
        t = utils.get_test_content()
        atform.add_test("title", label="label")
        t.pregenerate()
        self.assertEqual("2", t.procedure[0].text)


class ProcedureStepScope(unittest.TestCase):
    """Tests validating the scope of procedure step labels."""

    def setUp(self):
        utils.reset()

    def test_independence(self):
        """Confirm the same label defined in different tests maintain independent values."""
        atform.add_test("t1", procedure=[{"text": "$label", "label": "label"}])
        t1 = utils.get_test_content()

        atform.add_test(
            "t2",
            procedure=[
                "step1",
                {"text": "$label", "label": "label"},
            ],
        )
        t2 = utils.get_test_content()

        t1.pregenerate()
        t2.pregenerate()

        self.assertEqual("1", t1.procedure[0].text)
        self.assertEqual("2", t2.procedure[1].text)

    def test_undefined(self):
        """Confirm exception from a placeholder for a label defined in a different test."""
        atform.add_test("t1", procedure=[{"text": "spam", "label": "label"}])
        atform.add_test("t2", procedure=["$label"])
        t2 = utils.get_test_content()
        with self.assertRaises(UserScriptError):
            t2.pregenerate()


class ProcedureStepReplacement(unittest.TestCase):
    """Tests validating procedure step label replacement text."""

    def setUp(self):
        utils.reset()

    def test_objective(self):
        """Confirm placeholder is replaced in the objective."""
        atform.add_test(
            "title",
            objective="$label",
            procedure=[{"text": "text", "label": "label"}],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.objective)

    def test_precondition(self):
        """Confirm placeholder is replaced in the preconditions."""
        atform.add_test(
            "title",
            preconditions=["$label"],
            procedure=[{"text": "text", "label": "label"}],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.preconditions[0])

    def test_previous_procedure_step_string(self):
        """Confirm placeholder defined in a previous step is replaced in a string procedure step."""
        atform.add_test(
            "title",
            procedure=[
                {"text": "spam", "label": "label"},
                "$label",
            ],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[1].text)

    def test_previous_procedure_step_dict(self):
        """Confirm placeholder defined in a previous step is replaced in a dict procedure step."""
        atform.add_test(
            "title",
            procedure=[
                {"text": "spam", "label": "label"},
                {"text": "$label"},
            ],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[1].text)

    def test_same_procedure_step(self):
        """Confirm placeholder defined in the same step is replaced."""
        atform.add_test(
            "title",
            procedure=[{"text": "$label", "label": "label"}],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("1", t.procedure[0].text)

    def test_later_procedure_step_string(self):
        """Confirm placeholder defined in a later step is replaced in a string procedure step."""
        atform.add_test(
            "title",
            procedure=[
                "$label",
                {"text": "spam", "label": "label"},
            ],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("2", t.procedure[0].text)

    def test_later_procedure_step_dict(self):
        """Confirm placeholder defined in a later step is replaced in a dict procedure step."""
        atform.add_test(
            "title",
            procedure=[
                {"text": "$label"},
                {"text": "spam", "label": "label"},
            ],
        )
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("2", t.procedure[0].text)
