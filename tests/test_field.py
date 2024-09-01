# Unit tests for the field module.


from tests import utils
import atform
import string
import unittest


class AddField(unittest.TestCase):
    """Misc tests for add_field()."""

    def setUp(self):
        utils.reset()

    def test_order(self):
        """Confirm fields maintain the order in which they were defined."""
        atform.add_field("spam", 42, "a")
        atform.add_field("eggs", 5, "b")
        atform.add_field("foo", 99, "c")
        t = atform.Test("title")
        self.assertEqual([
            ("spam", 42),
            ("eggs", 5),
            ("foo", 99),
            ], t.fields)


class AddFieldContentAreaException(utils.ContentAreaException):
    """
    Tests to confirm exceptions when calling add_field() outside of
    the setup area.
    """

    @staticmethod
    def call():
        atform.add_field("foo", 1, "foo")


class AddFieldTitle(unittest.TestCase):
    """Unit tests for the add_field() title parameter."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception if title is not a string."""
        with self.assertRaises(SystemExit):
            atform.add_field(100, 1, "f")

    def test_empty(self):
        """Confirm exception if title is empty."""
        with self.assertRaises(SystemExit):
            atform.add_field("", 1, "f")

    def test_blank(self):
        """Confirm exception if title contains only whitespace."""
        with self.assertRaises(SystemExit):
            atform.add_field(string.whitespace, 1, "f")

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the title."""
        atform.add_field(
            string.whitespace + "foo bar" + string.whitespace,
            1,
            "f",
        )
        t = atform.Test("title")
        self.assertEqual("foo bar", t.fields[0].title)


class AddFieldLength(unittest.TestCase):
    """Tests for the add_field() length argument."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception if length is not an integer."""
        with self.assertRaises(SystemExit):
            atform.add_field("foo", "1", "f")

    def test_out_of_range(self):
        """Confirm exception for lengths less than one."""
        with self.assertRaises(SystemExit):
            atform.add_field("foo", 0, "f")


class AddFieldName(unittest.TestCase):
    """Tests for the add_field() name argument."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string name."""
        with self.assertRaises(SystemExit):
            atform.add_field("title", 1, 0)

    def test_empty(self):
        """Confirm exception for an empty name."""
        with self.assertRaises(SystemExit):
            atform.add_field("title", 1, "")

    def test_blank(self):
        """Confirm exception for a name containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.add_field("title", 1, string.whitespace)

    def test_duplicate(self):
        """Confirm exception for a duplicate name."""
        atform.add_field("title", 1, "foo")
        with self.assertRaises(SystemExit):
            atform.add_field("foo", 1, "foo")


class AddFieldActive(unittest.TestCase):
    """Tests for the add_field() active argument."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Verify exception if not a boolean."""
        for i in [0, 1, ""]:
            utils.reset()
            with self.subTest(i=i), self.assertRaises(SystemExit):
                atform.add_field("title", 1, "foo", i)

    def test_default(self):
        """Verify field is active if omitted."""
        atform.add_field("f1", 1, "f1")
        t = atform.Test("title")
        self.assertEqual([("f1", 1)], t.fields)

    def test_false(self):
        """Verify field is inactive if false."""
        atform.add_field("f1", 1, "f1", False)
        t = atform.Test("title")
        self.assertEqual([], t.fields)


class SetActiveFieldsBase(object):
    """Base class for testing set_active_fields()."""

    def setUp(self):
        utils.reset()
        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2", False)
        atform.add_field("f3", 1, "f3")

    def assert_test_fields(self, *args):
        """Confirms fields assigned to the next test."""
        t = atform.Test("title")
        self.assertEqual(args, tuple([f.title for f in t.fields]))

    def test_type(self):
        """Verify exception if the argument is not a list."""
        with self.assertRaises(SystemExit):
            self.call("f1")

    def test_item_type(self):
        """Verify exception if an item is not a string."""
        with self.assertRaises(SystemExit):
            self.call([42])

    def test_undefined_item(self):
        """Verify exception if an item is not a defined field name."""
        with self.assertRaises(SystemExit):
            self.call(["foo"])


class SetActiveFieldsInclude(SetActiveFieldsBase, unittest.TestCase):
    """Tests for the include argument of set_active_fields()."""

    @staticmethod
    def call(arg):
        """Calls set_active_fields with a given include argument."""
        atform.set_active_fields(include=arg)

    def test_add_inactive(self):
        """Confirm listing a currently-inactive field adds it to a test."""
        self.call(["f2"])
        self.assert_test_fields("f1", "f2", "f3")

    def test_add_active(self):
        """Confirm listing a currently-active field has no effect."""
        self.call(["f1"])
        self.assert_test_fields("f1", "f3")


class SetActiveFieldsExclude(SetActiveFieldsBase, unittest.TestCase):
    """Tests for the exclude argument of set_active_fields()."""

    @staticmethod
    def call(arg):
        """Calls set_active_fields with a given exclude argument."""
        atform.set_active_fields(exclude=arg)

    def test_remove_active(self):
        """Confirm excluded fields are not listed in tests."""
        self.call(["f1"])
        self.assert_test_fields("f3")

    def test_remove_inactive(self):
        """Confirm removing a currently-inactive field has no effect."""
        self.call(["f2"])
        self.assert_test_fields("f1", "f3")


class SetActiveFieldsActive(SetActiveFieldsBase, unittest.TestCase):
    """Tests for the active argument of set_active_fields()."""

    @staticmethod
    def call(arg):
        """Calls set_active_fields with a given active argument."""
        atform.set_active_fields(active=arg)

    def test_replace(self):
        """Confirm the listed fields replace the active fields."""
        self.call(["f2"])
        self.assert_test_fields("f2")
