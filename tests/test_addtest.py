"""Tests for the add_test() API."""

import copy
import string
import traceback
import unittest
from unittest.mock import patch

import atform
from tests import utils


class Title(unittest.TestCase):
    """Unit tests for test titles."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string title."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test(99)

    def test_empty(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("")

    def test_blank(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        atform.add_test(string.whitespace + "Spam" + string.whitespace)
        t = utils.get_test_content()
        self.assertEqual("Spam", t.title)

    def test_keyword_only(self):
        """Confirm any argument after title must be via keyword."""
        with self.assertRaises(TypeError):
            atform.add_test("title", "foo")


class Terms(unittest.TestCase):
    """Tests for the supported terms argument."""

    def setUp(self):
        utils.reset()

    def test_non_list(self):
        """Confirm exception for a value that is not a list."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", terms="foo")

    def test_item_type(self):
        """Confirm exception for a list item that is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", terms=[42])

    def test_undefined(self):
        """Confirm exception for a list item that is not a label."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", terms=["foo"])

    def test_non_term(self):
        """Confirm exception for a label that does not refer to a term."""
        atform.add_test("t1", label="not_a_term")
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", terms="not_a_term")

    def test_duplicate(self):
        """Confirm exception for duplicate list items."""
        atform.add_term("term", "term")
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", terms=["term", "term"])


class FieldBase(object):
    """Base class for field arguments of Test."""

    def setUp(self):
        utils.reset()
        atform.add_field("f1", 42, "f1")
        atform.add_field("f2", 99, "f2", active=False)
        atform.add_field("f3", 10, "f3")

    def verify_next_test(self):
        """Confirm the next test contains the originally-defined fields."""
        atform.add_test("title")
        t = utils.get_test_content()
        self.assertEqual([("f1", 42), ("f3", 10)], t.fields)

    def test_type(self):
        """Verify exception if the argument is not a list."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_test("f1")

    def test_item_type(self):
        """Verify exception if an item is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_test([99])

    def test_undefined_item(self):
        """Verify exception if an item is not a defined field name."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_test(["foo"])

    def test_argument_unchanged(self):
        """Confirm the list provided to the argument remains unchanged."""
        arg = ["f1", "f2", "f3"]
        cpy = list(arg)
        self.make_test(arg)
        self.assertEqual(arg, cpy)


class IncludeFields(FieldBase, unittest.TestCase):
    """Tests for the include_fields argument of Test."""

    def make_test(self, fields):
        """Creates a test with a given list of include_fields."""
        atform.add_test("title", include_fields=fields)

    def test_add_inactive(self):
        """Confirm including an inactive field adds it to the test."""
        self.make_test(["f2"])
        t = utils.get_test_content()
        self.assertEqual(
            [
                ("f1", 42),
                ("f2", 99),
                ("f3", 10),
            ],
            t.fields,
        )

    def test_add_active(self):
        """Confirm including an active field has no effect."""
        self.make_test(["f1"])
        t = utils.get_test_content()
        self.assertEqual(
            [
                ("f1", 42),
                ("f3", 10),
            ],
            t.fields,
        )

    def test_isolate(self):
        """Confirm included fields do not affect later tests."""
        self.make_test(["f2"])
        self.verify_next_test()


class ExcludeFields(FieldBase, unittest.TestCase):
    """Tests for the exclude_fields argument of Test."""

    def make_test(self, fields):
        """Creates a test with a given list of exclude_fields."""
        atform.add_test("title", exclude_fields=fields)

    def test_remove_active(self):
        """Confirm excluding an active field removes it from the test."""
        self.make_test(["f1"])
        t = utils.get_test_content()
        self.assertEqual(
            [
                ("f3", 10),
            ],
            t.fields,
        )

    def test_remove_inactive(self):
        """Confirm excluding an inactive field has no effect."""
        self.make_test(["f2"])
        t = utils.get_test_content()
        self.assertEqual(
            [
                ("f1", 42),
                ("f3", 10),
            ],
            t.fields,
        )

    def test_isolate(self):
        """Confirm excluded fields do not affect later tests."""
        self.make_test(["f1"])
        self.verify_next_test()


class ActiveFields(FieldBase, unittest.TestCase):
    """Tests for the active_fields argument of Test."""

    def make_test(self, fields):
        """Creates a test with a given list of active_fields."""
        atform.add_test("title", active_fields=fields)

    def test_override(self):
        """Confirm the given fields override the active fields."""
        self.make_test(["f2"])
        t = utils.get_test_content()
        self.assertEqual(
            [
                ("f2", 99),
            ],
            t.fields,
        )

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
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", objective=42)

    def test_empty(self):
        """Confirm exception for an empty objective."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", objective="")

    def test_blank(self):
        """Confirm exception for an objective containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", objective=string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        atform.add_test(
            "title", objective=string.whitespace + "Spam" + string.whitespace
        )
        t = utils.get_test_content()
        self.assertEqual("Spam", t.objective)


class References(unittest.TestCase):
    """Unit tests for test references."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-dict references."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references=[])

    def test_label_type(self):
        """Confirm exception for non-string labels."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={42: ["a"]})

    def test_empty_label(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={"": ["a"]})

    def test_blank_label(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={string.whitespace: ["a"]})

    def test_label_strip(self):
        """Confirm surrounding whitespace is removed from labels."""
        atform.add_reference_category("refs", "refs")
        atform.add_test(
            "title", references={string.whitespace + "refs" + string.whitespace: ["a"]}
        )
        t = utils.get_test_content()
        self.assertEqual("refs", t.references[0].label)

    def test_undefined_label(self):
        """Confirm exception for an unknown label."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={"foo": ["a"]})

    def test_ref_type(self):
        """Confirm exception for a non-list reference value."""
        atform.add_reference_category("refs", "refs")
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={"refs": "spam"})

    def test_ref_item_type(self):
        """Confirm exception for a non-string reference items."""
        atform.add_reference_category("refs", "refs")
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={"refs": [42]})

    def test_duplicate_ref(self):
        """Confirm exception for duplicate references."""
        atform.add_reference_category("refs", "refs")
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("title", references={"refs": ["a", "a"]})

    def test_ignore_empty_ref(self):
        """Confirm empty references are ignored."""
        atform.add_reference_category("refs", "refs")
        atform.add_test("title", references={"refs": ["a", "", ""]})
        t = utils.get_test_content()
        self.assertEqual(["a"], t.references[0].items)

    def test_ignore_blank_ref(self):
        """Confirm references containing only whitespace are ignored."""
        atform.add_reference_category("refs", "refs")
        atform.add_test(
            "title", references={"refs": [string.whitespace, "spam", string.whitespace]}
        )
        t = utils.get_test_content()
        self.assertEqual(["spam"], t.references[0].items)

    def test_strip_ref(self):
        """Confirm surrounding whitespace is removed from references."""
        atform.add_reference_category("refs", "refs")
        atform.add_test(
            "title",
            references={"refs": [string.whitespace + "foo" + string.whitespace]},
        )
        t = utils.get_test_content()
        self.assertEqual(["foo"], t.references[0].items)

    def test_ref_order(self):
        """Confirm references are stored in original order."""
        atform.add_reference_category("refs", "refs")
        atform.add_test("title", references={"refs": ["a", "b", "c"]})
        t = utils.get_test_content()
        self.assertEqual(["a", "b", "c"], t.references[0].items)

    def test_multiple_categories(self):
        """Confirm storage and order of multiple reference categories."""
        atform.add_reference_category("Numbers", "num")
        atform.add_reference_category("Letters", "alpha")
        atform.add_reference_category("Stooges", "stg")
        atform.add_test(
            "title",
            references={
                # Categories in different order than definitions.
                "stg": ["Larry", "Moe", "Curly"],
                "num": ["1", "2", "3"],
                "alpha": ["a", "b", "c"],
            },
        )
        t = utils.get_test_content()

        self.assertEqual(3, len(t.references))

        self.assertEqual("num", t.references[0].label)
        self.assertEqual("Numbers", t.references[0].title)
        self.assertEqual(["1", "2", "3"], t.references[0].items)

        self.assertEqual("alpha", t.references[1].label)
        self.assertEqual("Letters", t.references[1].title)
        self.assertEqual(["a", "b", "c"], t.references[1].items)

        self.assertEqual("stg", t.references[2].label)
        self.assertEqual("Stooges", t.references[2].title)
        self.assertEqual(["Larry", "Moe", "Curly"], t.references[2].items)

    def test_argument_unchanged(self):
        """Confirm the given dictionary remains unchanged."""
        atform.add_reference_category("ref", "ref")
        arg = {"ref": ["spam", "eggs"]}
        cpy = copy.deepcopy(arg)  # Deep copy to capture nested compound objects.
        atform.add_test("title", references=arg)
        self.assertEqual(arg, cpy)


class StringList(object):
    """Base class for testing a parameter that accepts a list of strings."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-list."""
        with self.assertRaises(atform.error.UserScriptError):
            self.call("spam")

    def test_item_type(self):
        """Confirm exception for a non-string list item."""
        with self.assertRaises(atform.error.UserScriptError):
            self.call([42])

    def test_empty(self):
        """Confirm exception for an empty item."""
        with self.assertRaises(atform.error.UserScriptError):
            self.call([""])

    def test_blank(self):
        """Confirm exception for an item containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            self.call([string.whitespace])

    def test_strip(self):
        """Confirm surrounding whitespace is removed from list items."""
        self.call([string.whitespace + "Foo" + string.whitespace])
        t = utils.get_test_content()
        self.assertEqual("Foo", getattr(t, self.parameter_name)[0])

    def test_list_unchanged(self):
        """Confirm the given list is not modified."""
        arg = ["foo", "bar"]
        cpy = list(arg)
        self.call(arg)
        self.assertEqual(arg, cpy)

    def call(self, value):
        """Calls Test() with a given parameter value."""
        args = {self.parameter_name: value}
        atform.add_test("title", **args)


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
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_test("test", procedure="spam")

    def test_argument_unchanged(self):
        """Confirm the given list and included objects remain unchanged."""
        arg = [
            "foo",
            {
                "text": "spam",
                "fields": [
                    ("f1", 1),
                    ("f2", 2),
                ],
            },
        ]
        cpy = copy.deepcopy(arg)  # Deep copy to capture nested compound objects.
        atform.add_test("test", procedure=arg)
        self.assertEqual(arg, cpy)


class ProcedureStepBase(object):
    """Base class for procedure step tests."""

    def setUp(self):
        utils.reset()

    def make_step(self, step):
        """Creates a test with a given procedure step."""
        atform.add_test("test", procedure=[step])

    def make_field(self, field):
        """Creates a test with a given procedure step field."""
        self.make_step(
            {
                "text": "text",
                "fields": [field],
            }
        )


class ProcedureStepString(ProcedureStepBase, unittest.TestCase):
    """Unit tests for string procedure steps."""

    def test_type(self):
        """Confirm exception for a non-string."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step(42)

    def test_empty(self):
        """Confirm exception for an empty string."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step("")

    def test_blank(self):
        """Confirm exception for a string containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the string."""
        self.make_step(string.whitespace + "Foo" + string.whitespace)
        t = utils.get_test_content()
        self.assertEqual("Foo", t.procedure[0].text)


class ProcedureStepDict(ProcedureStepBase, unittest.TestCase):
    """Unit tests for dictionary procedure steps."""

    def test_unknown_key(self):
        """Confirm exception for an undefined key."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step({"text": "spam", "foo": "bar"})


class ProcedureStepDictText(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step dict text key."""

    def test_missing(self):
        """Confirm exception if text key is missing."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step({})

    def test_type(self):
        """Confirm exception if text is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step({"text": 99})

    def test_empty(self):
        """Confirm exception if text is empty."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step({"text": ""})

    def test_blank(self):
        """Confirm exception if text contains only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step({"text": string.whitespace})

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        self.make_step({"text": string.whitespace + "foo" + string.whitespace})
        test = utils.get_test_content()
        self.assertEqual("foo", test.procedure[0].text)


class ProcedureStepFields(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field definitions."""

    def test_type(self):
        """Confirm exception for a non-list fields key."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_step({"text": "text", "fields": "not a list"})

    def test_item_type(self):
        """Confirm exception for a non-tuple list item."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field("not a tuple")

    def test_empty_item(self):
        """Confirm exception for an empty field tuple."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(())

    def test_too_long(self):
        """Confirm exception for a field definition with too many items."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("field", 1, "suffix", 42))


class ProcedureStepFieldTitle(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field title."""

    def test_type(self):
        """Confirm exception for a non-string field title."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field((None, 1))

    def test_empty(self):
        """Confirm exception for an empty field title."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("", 1))

    def test_blank(self):
        """Confirm exception for a field title containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field((string.whitespace, 1))

    def test_strip(self):
        """Confirm surrounding whitespace is removed from field titles."""
        self.make_field((string.whitespace + "foo" + string.whitespace, 1))
        t = utils.get_test_content()
        self.assertEqual("foo", t.procedure[0].fields[0].title)


class ProcedureStepFieldLength(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field length."""

    def test_type(self):
        """Confirm exception for a non-integer length."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("field", "42"))

    def test_missing(self):
        """Confirm exception for a missing length."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("field",))

    def test_invalid_length(self):
        """Confirm exception for a length less than one."""
        for i in [-1, 0]:
            with self.subTest(i=i), self.assertRaises(atform.error.UserScriptError):
                self.make_field(("field", i))


class ProcedureStepFieldSuffix(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field suffix."""

    def test_type(self):
        """Confirm exception for a non-string suffix."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("field", 1, 42))

    def test_empty(self):
        """Confirm exception for an empty suffix."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("field", 1, ""))

    def test_blank(self):
        """Confirm exception for a suffix containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            self.make_field(("field", 1, string.whitespace))

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the suffix."""
        self.make_field(("field", 1, string.whitespace + "foo" + string.whitespace))
        t = utils.get_test_content()
        self.assertEqual("foo", t.procedure[0].fields[0].suffix)


class TestProjectInfo(unittest.TestCase):
    """Unit tests for project information captured during add_test()."""

    def setUp(self):
        utils.reset()

    def test_capture(self):
        """Confirm accurate information is captured when instantiated."""
        info = {"project": "foo", "system": "spam"}
        atform.set_project_info(**info)
        atform.add_test("A test")
        t = utils.get_test_content()
        self.assertEqual(info, t.project_info)

    def test_update_between_tests(self):
        """Confirm system information changes do not affect existing tests."""
        atform.set_project_info(project="foo", system="bar")
        atform.add_test("Test 1")
        t1 = utils.get_test_content()

        atform.set_project_info(project="spam", system="eggs")
        atform.add_test("Test 2")
        t2 = utils.get_test_content()

        self.assertEqual({"project": "foo", "system": "bar"}, t1.project_info)
        self.assertEqual({"project": "spam", "system": "eggs"}, t2.project_info)


class CallFrame(unittest.TestCase):
    """Tests for the call frame captured during calls to add_test()."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    def test_post_call_exception(self):
        """Confirm an exception due to test content raised after a test is defined points to the original add_test() call."""
        # Define a test with an undefined label that will raise an
        # exception later.
        before = traceback.extract_stack()[-1]
        atform.add_test("title", objective="$undefined")
        after = traceback.extract_stack()[-1]

        with self.assertRaises(atform.error.UserScriptError) as cm:
            atform.generate()

        # Verify the exception call frame points to where the test was defined.
        call_frame = cm.exception.call_frame
        self.assertGreater(call_frame.lineno, before.lineno)
        self.assertLess(call_frame.lineno, after.lineno)
        self.assertEqual(call_frame.filename, before.filename)
