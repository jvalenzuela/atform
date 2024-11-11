# Unit tests for the content module.


from tests import utils
import string
import atform
import unittest


class Title(unittest.TestCase):
    """Unit tests for test titles."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string title."""
        with self.assertRaises(SystemExit):
            atform.Test(99)

    def test_empty(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(SystemExit):
            atform.Test("")

    def test_blank(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.Test(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        t = atform.Test(string.whitespace + "Spam" + string.whitespace)
        self.assertEqual("Spam", t.title)

    def test_keyword_only(self):
        """Confirm any argument after title must be via keyword."""
        with self.assertRaises(TypeError):
            atform.Test("title", "foo")


class LabelReplacement(object):
    """
    Base class for testing label replacement in each type of content
    where label placeholders are supported. Subclasses must create
    a test with the label applied to the target object, e.g., test or
    procedure step, and define what the label replacement text should be.
    """

    LABEL = "TheLabel"
    PLACEHOLDER = f"spam ${LABEL} eggs"

    def setUp(self):
        utils.reset()
        self.make_labeled_test()

    def assertReplacement(self, text):
        """Verifies correct placeholder replacement in the given text."""
        self.assertEqual(f"spam {self.REPLACEMENT} eggs", text)

    def test_objective(self):
        """Confirm placeholder is replaced in the objective."""
        t = atform.Test("title", objective=self.PLACEHOLDER)
        t._pregenerate()
        self.assertReplacement(t.objective)

    def test_precondition(self):
        """Confirm placeholder is replaced in the preconditions."""
        t = atform.Test("title", preconditions=[self.PLACEHOLDER])
        t._pregenerate()
        self.assertReplacement(t.preconditions[0])

    def test_procedure_step_string(self):
        """Confirm placeholder is replaced in string procedure steps."""
        t = atform.Test("title", procedure=[self.PLACEHOLDER])
        t._pregenerate()
        self.assertReplacement(t.procedure[0].text)

    def test_procedure_step_dict(self):
        """Confirm placeholder is replaced in dict procedure steps."""
        t = atform.Test("title", procedure=[{"text":self.PLACEHOLDER}])
        t._pregenerate()
        self.assertReplacement(t.procedure[0].text)


class TestLabelReplacement(LabelReplacement, unittest.TestCase):
    """Unit tests for test identifier label replacement."""

    REPLACEMENT = "1.2"

    def make_labeled_test(self):
        """Creates a labeled test."""
        atform.set_id_depth(2)
        atform.Test("Some other test")
        atform.Test("Referenced Test", label=self.LABEL)


class ProcedureStepLabelReplacement(LabelReplacement, unittest.TestCase):
    """Unit tests for procedure step label replacement."""

    REPLACEMENT = "2"

    def make_labeled_test(self):
        """Creates a labeled procedure step."""
        atform.Test("Referenced Test", procedure=[
            "Step foo.",
            {"text":"Target step.", "label":self.LABEL},
            "Step bar."
        ])


class ForwardLabelReplacement(unittest.TestCase):
    """Unit tests for label replacement where the placeholder preceeds the label."""

    def setUp(self):
        utils.reset()

    def test_test(self):
        """Confirm replacement for a labeled test."""
        t = atform.Test("title", objective="$TheLabel")
        atform.Test("target", label="TheLabel")
        t._pregenerate()
        self.assertEqual("2", t.objective)

    def test_procedure_step(self):
        """Confirm replacement for a labeled procedure step."""
        t = atform.Test("title", procedure=[
            "$TheLabel",
            {"text":"foo", "label":"TheLabel"}
        ])
        t._pregenerate()
        self.assertEqual("2", t.procedure[0].text)


class FieldBase(object):
    """Base class for field arguments of Test."""

    def setUp(self):
        utils.reset()
        atform.add_field("f1", 42, "f1")
        atform.add_field("f2", 99, "f2", False)
        atform.add_field("f3", 10, "f3")

    def verify_next_test(self):
        """Confirm the next test contains the originally-defined fields."""
        t = atform.Test("title")
        self.assertEqual([("f1", 42), ("f3", 10)], t.fields)

    def test_type(self):
        """Verify exception if the argument is not a list."""
        with self.assertRaises(SystemExit):
            self.make_test("f1")

    def test_item_type(self):
        """Verify exception if an item is not a string."""
        with self.assertRaises(SystemExit):
            self.make_test([99])

    def test_undefined_item(self):
        """Verify exception if an item is not a defined field name."""
        with self.assertRaises(SystemExit):
            self.make_test(["foo"])


class IncludeFields(FieldBase, unittest.TestCase):
    """Tests for the include_fields argument of Test."""

    def make_test(self, fields):
        """Creates a test with a given list of include_fields."""
        return atform.Test("title", include_fields=fields)

    def test_add_inactive(self):
        """Confirm including an inactive field adds it to the test."""
        t = self.make_test(["f2"])
        self.assertEqual([
            ("f1", 42),
            ("f2", 99),
            ("f3", 10),
            ], t.fields)

    def test_add_active(self):
        """Confirm including an active field has no effect."""
        t = self.make_test(["f1"])
        self.assertEqual([
            ("f1", 42),
            ("f3", 10),
            ], t.fields)

    def test_isolate(self):
        """Confirm included fields do not affect later tests."""
        self.make_test(["f2"])
        self.verify_next_test()


class ExcludeFields(FieldBase, unittest.TestCase):
    """Tests for the exclude_fields argument of Test."""

    def make_test(self, fields):
        """Creates a test with a given list of exclude_fields."""
        return atform.Test("title", exclude_fields=fields)

    def test_remove_active(self):
        """Confirm excluding an active field removes it from the test."""
        t = self.make_test(["f1"])
        self.assertEqual([
            ("f3", 10),
            ], t.fields)

    def test_remove_inactive(self):
        """Confirm excluding an inactive field has no effect."""
        t = self.make_test(["f2"])
        self.assertEqual([
            ("f1", 42),
            ("f3", 10),
            ], t.fields)

    def test_isolate(self):
        """Confirm excluded fields do not affect later tests."""
        self.make_test(["f1"])
        self.verify_next_test()


class ActiveFields(FieldBase, unittest.TestCase):
    """Tests for the active_fields argument of Test."""

    def make_test(self, fields):
        """Creates a test with a given list of active_fields."""
        return atform.Test("title", active_fields=fields)

    def test_override(self):
        """Confirm the given fields override the active fields."""
        t = self.make_test(["f2"])
        self.assertEqual([
            ("f2", 99),
            ], t.fields)

    def test_isolate(self):
        """Confirm active fields do not affect later tests."""
        self.make_test(["f2"])
        self.verify_next_test()


class Objective(unittest.TestCase):
    """Unit tests for test objectives."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string objective."""
        with self.assertRaises(SystemExit):
            atform.Test("title", objective=42)

    def test_empty(self):
        """Confirm exception for an empty objective."""
        with self.assertRaises(SystemExit):
            atform.Test("title", objective="")

    def test_blank(self):
        """Confirm exception for an objective containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.Test("title", objective=string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        t = atform.Test("title",
                        objective=string.whitespace + "Spam" + string.whitespace)
        self.assertEqual("Spam", t.objective)


class References(unittest.TestCase):
    """Unit tests for test references."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-dict references."""
        with self.assertRaises(SystemExit):
            atform.Test("title", references=[])

    def test_label_type(self):
        """Confirm exception for non-string labels."""
        with self.assertRaises(SystemExit):
            atform.Test("title", references={42: ["a"]})

    def test_empty_label(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(SystemExit):
            atform.Test("title", references={"": ["a"]})

    def test_blank_label(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.Test("title", references={string.whitespace: ["a"]})

    def test_label_strip(self):
        """Confirm surrounding whitespace is removed from labels."""
        atform.add_reference_category("refs", "refs")
        t = atform.Test("title", references={
            string.whitespace + "refs" + string.whitespace: ["a"]})
        self.assertIn("refs", t.references)

    def test_undefined_label(self):
        """Confirm exception for an unknown label."""
        with self.assertRaises(SystemExit):
            atform.Test("title", references={"foo": ["a"]})

    def test_ref_type(self):
        """Confirm exception for a non-list reference value."""
        atform.add_reference_category("refs", "refs")
        with self.assertRaises(TypeError):
            atform.Test("title", references={"refs": "spam"})

    def test_ref_item_type(self):
        """Confirm exception for a non-string reference items."""
        atform.add_reference_category("refs", "refs")
        with self.assertRaises(SystemExit):
            atform.Test("title", references={"refs": [42]})

    def test_duplicate_ref(self):
        """Confirm exception for duplicate references."""
        atform.add_reference_category("refs", "refs")
        with self.assertRaises(SystemExit):
            atform.Test("title", references={"refs": ["a", "a"]})

    def test_ignore_empty_ref(self):
        """Confirm empty references are ignored."""
        atform.add_reference_category("refs", "refs")
        t = atform.Test("title", references={"refs": ["a", "", ""]})
        self.assertEqual(["a"], t.references["refs"])

    def test_ignore_blank_ref(self):
        """Confirm references containing only whitespace are ignored."""
        atform.add_reference_category("refs", "refs")
        t = atform.Test("title", references={
            "refs": [string.whitespace, "spam", string.whitespace]})
        self.assertEqual(["spam"], t.references["refs"])

    def test_strip_ref(self):
        """Confirm surrounding whitespace is removed from references."""
        atform.add_reference_category("refs", "refs")
        t = atform.Test("title", references={
            "refs": [string.whitespace + "foo" + string.whitespace]})
        self.assertEqual(["foo"], t.references["refs"])

    def test_ref_order(self):
        """Confirm references are stored in original order."""
        atform.add_reference_category("refs", "refs")
        t = atform.Test("title", references={
            "refs": ["a", "b", "c"]})
        self.assertEqual(["a", "b", "c"], t.references["refs"])

    def test_multiple_categories(self):
        """Confirm storage of multiple reference categories."""
        atform.add_reference_category("Numbers", "num")
        atform.add_reference_category("Letters", "alpha")
        t = atform.Test("title", references={
            "num": ["1", "2", "3"],
            "alpha": ["a", "b", "c"]})
        self.assertEqual(["1", "2", "3"], t.references["num"])
        self.assertEqual(["a", "b", "c"], t.references["alpha"])


class StringList(object):
    """Base class for testing a parameter that accepts a list of strings."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-list."""
        with self.assertRaises(SystemExit):
            self.call("spam")

    def test_item_type(self):
        """Confirm exception for a non-string list item."""
        with self.assertRaises(SystemExit):
            self.call([42])

    def test_empty(self):
        """Confirm exception for an empty item."""
        with self.assertRaises(SystemExit):
            self.call([""])

    def test_blank(self):
        """Confirm exception for an item containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.call([string.whitespace])

    def test_strip(self):
        """Confirm surrounding whitespace is removed from list items."""
        t = self.call([string.whitespace + "Foo" + string.whitespace])
        self.assertEqual("Foo", getattr(t, self.parameter_name)[0])

    def call(self, value):
        """Calls Test() with a given parameter value."""
        args = {self.parameter_name: value}
        return atform.Test("title", **args)


class Equipment(StringList, unittest.TestCase):
    """Unit tests for test equipment."""
    parameter_name = "equipment"


class Preconditions(StringList, unittest.TestCase):
    """Unit tests for test preconditions."""
    parameter_name = "preconditions"


class ProcedureList(unittest.TestCase):
    """Unit tests for the procedure list."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-list.."""
        with self.assertRaises(SystemExit):
            atform.Test("test", procedure="spam")


class ProcedureStepBase(object):
    """Base class for procedure step tests."""

    def setUp(self):
        utils.reset()

    def make_step(self, step):
        """Creates a test with a given procedure step."""
        return atform.Test("test", procedure=[step])

    def make_field(self, field):
        """Creates a test with a given procedure step field."""
        return self.make_step({
            "text":"text",
            "fields":[field],
        })


class ProcedureStepString(ProcedureStepBase, unittest.TestCase):
    """Unit tests for string procedure steps."""

    def test_type(self):
        """Confirm exception for a non-string."""
        with self.assertRaises(SystemExit):
            self.make_step(42)

    def test_empty(self):
        """Confirm exception for an empty string."""
        with self.assertRaises(SystemExit):
            self.make_step("")

    def test_blank(self):
        """Confirm exception for a string containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_step(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the string."""
        t = self.make_step(string.whitespace + "Foo" + string.whitespace)
        self.assertEqual("Foo", t.procedure[0].text)


class ProcedureStepDict(ProcedureStepBase, unittest.TestCase):
    """Unit tests for dictionary procedure steps."""

    def test_unknown_key(self):
        """Confirm exception for an undefined key."""
        with self.assertRaises(SystemExit):
            self.make_step({"text":"spam", "foo":"bar"})


class ProcedureStepDictText(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step dict text key."""

    def test_missing(self):
        """Confirm exception if text key is missing."""
        with self.assertRaises(SystemExit):
            self.make_step({})

    def test_type(self):
        """Confirm exception if text is not a string."""
        with self.assertRaises(SystemExit):
            self.make_step({"text":99})

    def test_empty(self):
        """Confirm exception if text is empty."""
        with self.assertRaises(SystemExit):
            self.make_step({"text":""})

    def test_blank(self):
        """Confirm exception if text contains only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_step({"text":string.whitespace})

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        test = self.make_step({
            "text":string.whitespace + "foo" + string.whitespace
        })
        self.assertEqual("foo", test.procedure[0].text)


class ProcedureStepFields(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field definitions."""

    def test_type(self):
        """Confirm exception for a non-list fields key."""
        with self.assertRaises(SystemExit):
            self.make_step({"text":"text", "fields":"not a list"})

    def test_item_type(self):
        """Confirm exception for a non-tuple list item."""
        with self.assertRaises(SystemExit):
            self.make_field("not a tuple")

    def test_empty_item(self):
        """Confirm exception for an empty field tuple."""
        with self.assertRaises(SystemExit):
            self.make_field(())

    def test_too_long(self):
        """Confirm exception for a field definition with too many items."""
        with self.assertRaises(SystemExit):
            self.make_field(("field", 1, "suffix", 42))


class ProcedureStepFieldTitle(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field title."""

    def test_type(self):
        """Confirm exception for a non-string field title."""
        with self.assertRaises(SystemExit):
            self.make_field((None, 1))

    def test_empty(self):
        """Confirm exception for an empty field title."""
        with self.assertRaises(SystemExit):
            self.make_field(("", 1))

    def test_blank(self):
        """Confirm exception for a field title containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_field((string.whitespace, 1))

    def test_strip(self):
        """Confirm surrounding whitespace is removed from field titles."""
        t = self.make_field((string.whitespace + "foo" + string.whitespace, 1))
        self.assertEqual("foo", t.procedure[0].fields[0].title)


class ProcedureStepFieldLength(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field length."""

    def test_type(self):
        """Confirm exception for a non-integer length."""
        with self.assertRaises(SystemExit):
            self.make_field(("field", "42"))

    def test_missing(self):
        """Confirm exception for a missing length."""
        with self.assertRaises(SystemExit):
            self.make_field(("field",))

    def test_invalid_length(self):
        """Confirm exception for a length less than one."""
        for i in [-1, 0]:
            with self.subTest(i=i), self.assertRaises(SystemExit):
                self.make_field(("field", i))


class ProcedureStepFieldSuffix(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field suffix."""

    def test_type(self):
        """Confirm exception for a non-string suffix."""
        with self.assertRaises(SystemExit):
            self.make_field(("field", 1, 42))

    def test_empty(self):
        """Confirm exception for an empty suffix."""
        with self.assertRaises(SystemExit):
            self.make_field(("field", 1, ""))

    def test_blank(self):
        """Confirm exception for a suffix containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_field(("field", 1, string.whitespace))

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the suffix."""
        t = self.make_field(
            ("field", 1, string.whitespace + "foo" + string.whitespace))
        self.assertEqual("foo", t.procedure[0].fields[0].suffix)


class TestProjectInfo(unittest.TestCase):
    """Unit tests for project information stored in a Test() instance."""

    def setUp(self):
        utils.reset()

    def test_capture(self):
        """Confirm accurate information is captured when instantiated."""
        info = {"project":"foo", "system":"spam"}
        atform.set_project_info(**info)
        t = atform.Test("A test")
        self.assertEqual(info, t.project_info)

    def test_update_between_tests(self):
        """Confirm system information changes do not affect existing tests."""
        atform.set_project_info(project="foo", system="bar")
        t1 = atform.Test("Test 1")

        atform.set_project_info(project="spam", system="eggs")
        t2 = atform.Test("Test 2")

        self.assertEqual({"project":"foo", "system":"bar"}, t1.project_info)
        self.assertEqual({"project":"spam", "system":"eggs"}, t2.project_info)


class Generate(unittest.TestCase):
    """Unit tests for the generate() function."""

    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(SystemExit):
            atform.generate(42)


class GenerateFolderDepth(unittest.TestCase):
    """Unit tests for the folder_depth parameter of generate()."""

    def setUp(self):
        utils.reset()

    def test_invalid_type(self):
        """Confirm exception for a non-integer argument."""
        with self.assertRaises(SystemExit):
            atform.generate(folder_depth="foo")

    def test_negative(self):
        """Confirm exception for a negative argument."""
        with self.assertRaises(SystemExit):
            atform.generate(folder_depth=-1)

    def test_too_large(self):
        """Confirm exception for values greater than or equal to the id depth."""
        atform.set_id_depth(3)
        for i in [3, 4]:
            with self.subTest(i=i):
                with self.assertRaises(SystemExit):
                    atform.generate(folder_depth=i)
