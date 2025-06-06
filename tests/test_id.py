# Unit tests for the id module.


from tests import utils
import atform
import unittest


class GetId(unittest.TestCase):
    """Unit tests for the get_id() function."""

    def setUp(self):
        utils.reset()

    def test_single_depth_increment(self):
        """Confirm single-level IDs are properly incremented."""
        for i in range(1, 4):
            with self.subTest(i=i):
                self.assertEqual((i,), atform.id.get_id())

    def test_multi_depth_increment(self):
        """Confirm multi-level IDs are properly incremented."""
        atform.id.set_id_depth(3)
        for i in range(1, 4):
            with self.subTest(i=i):
                self.assertEqual((1, 1, i), atform.id.get_id())

    def test_level_initialization(self):
        """Confirm levels that have been reset are initialized to 1."""
        atform.id.set_id_depth(3)
        atform.state.current_id = [2, 0, 0]  # Simulate a level 1 increment.
        self.assertEqual((2, 1, 1), atform.id.get_id())


class Section(unittest.TestCase):
    """Unit tests for the section() function."""

    def setUp(self):
        utils.reset()

    def test_level_type(self):
        """Confirm an exception is raised for a non-integer level."""
        atform.set_id_depth(2)
        with self.assertRaises(atform.error.UserScriptError):
            atform.section("0")

    def test_level_nonsection_single(self):
        """Confirm an exception is raised for a level that is not a section for single-level IDs."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.section(1)

    def test_level_nonsection_multi(self):
        """Confirm an exception is raised for a level that is not a section for multi-level IDs."""
        atform.set_id_depth(2)
        with self.assertRaises(atform.error.UserScriptError):
            atform.section(2)

    def test_level_outside_depth(self):
        """Confirm an exception is raised for a level beyond the ID depth."""
        atform.set_id_depth(2)
        for level in [0, 3]:
            with self.assertRaises(atform.error.UserScriptError):
                atform.section(level)

    def test_id_type(self):
        """Confirm an exception is raised if id is not an integer."""
        atform.set_id_depth(2)
        with self.assertRaises(atform.error.UserScriptError):
            atform.section(0, id="42")

    def test_id_backwards(self):
        """Confirm an exception is raised for id values of previous sections."""
        atform.set_id_depth(2)
        atform.section(1, id=3)
        for id in range(-1, 4):
            with self.subTest(id=id), self.assertRaises(atform.error.UserScriptError):
                atform.section(1, id=id)

    def test_title_type(self):
        """Confirm an exception is raised if title is not a string."""
        atform.set_id_depth(2)
        with self.assertRaises(atform.error.UserScriptError):
            atform.section(1, title=42)

    def test_level_increment(self):
        """Confirm the section level is incremented if id is omitted."""
        atform.set_id_depth(2)
        atform.section(1)
        self.assertEqual((1, 1), atform.id.get_id())
        atform.section(1)
        self.assertEqual((2, 1), atform.id.get_id())

    def test_set_specific_id(self):
        """Confirm section level is set to a specific value if id is given."""
        atform.set_id_depth(2)
        atform.section(1, id=42)
        self.assertEqual((42, 1), atform.id.get_id())

    def test_reset_numbering(self):
        """Confirm numbering of further subsections are reset."""
        atform.set_id_depth(3)

        atform.state.current_id = [42, 78, 100]
        atform.section(2)
        self.assertEqual((42, 79, 1), atform.id.get_id())

        atform.state.current_id = [42, 78, 100]
        atform.section(1)
        self.assertEqual((43, 1, 1), atform.id.get_id())

    def test_no_title(self):
        """Confirm no title is saved if title is omitted."""
        atform.set_id_depth(2)
        atform.section(1)
        self.assertNotIn((1,), atform.state.section_titles)

    def test_invalid_title(self):
        """Confirm exception for a title that is not a valid folder name.

        The list of invalid characters varies widely among operating
        systems, so this test uses a single character universally
        rejected.
        """
        atform.set_id_depth(2)
        with self.assertRaises(atform.error.UserScriptError):
            atform.section(1, title="/")

    def test_title_store(self):
        """Confirm the title is saved."""
        atform.set_id_depth(2)
        atform.section(1, title="spam")
        self.assertEqual("spam", atform.state.section_titles[(1,)])


class SetIdDepth(unittest.TestCase):
    """Unit tests for the set_id_depth() function."""

    def setUp(self):
        utils.reset()

    def test_non_integer_levels(self):
        """Confirm an exception is raised for non-integer argument."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.set_id_depth("1")

    def test_levels_leq_zero(self):
        """Confirm an exception is raised for arguments less than 1."""
        for level in [-1, 0]:
            with self.subTest(level=level), self.assertRaises(
                atform.error.UserScriptError
            ):
                atform.id.set_id_depth(level)

    def test_set_current_id(self):
        """Confirm the current ID is correctly updated."""
        atform.set_id_depth(3)
        self.assertEqual([0] * 3, atform.state.current_id)


class SetIdDepthContentAreaException(utils.ContentAreaException):
    """
    Tests to confirm exceptions when calling set_id_depth() outside of
    the setup area.
    """

    @staticmethod
    def call():
        atform.set_id_depth(2)


class SkipTest(unittest.TestCase):
    """Unit tests for the skip_test() function."""

    def setUp(self):
        utils.reset()

    def test_id_type(self):
        """Confirm exception if id is not an integer."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.skip_test("10")

    def test_invalid_id(self):
        """Confirm exception for invalid id values."""
        for id in [-1, 0]:
            with self.subTest(id=id), self.assertRaises(atform.error.UserScriptError):
                atform.skip_test(id)

    def test_zero_distance_first(self):
        """Confirm exception when skipping to the first test in a section."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.skip_test(1)

    def test_zero_distance(self):
        """Confirm exception when skipping to what would be the next test."""
        atform.state.current_id = [
            42,
        ]
        with self.assertRaises(atform.error.UserScriptError):
            atform.skip_test(43)

    def test_back_one(self):
        """Confirm exception when skipping to the immediately-previous test."""
        atform.state.current_id = [
            42,
        ]
        with self.assertRaises(atform.error.UserScriptError):
            atform.skip_test(42)

    def test_back_multipe(self):
        """Confirm exception when trying to skip back multiple tests."""
        atform.state.current_id = [
            42,
        ]
        with self.assertRaises(atform.error.UserScriptError):
            atform.skip_test(10)

    def test_first_implicit(self):
        """Confirm implicitly skipping the first test in a section(.1)."""
        atform.skip_test()
        self.assertEqual((2,), atform.id.get_id())

    def test_first_explicit(self):
        """Confirm explicitly skipping the first tests in a section."""
        atform.skip_test(42)
        self.assertEqual((42,), atform.id.get_id())

    def test_middle_implicit(self):
        """Confirm implicitly skipping one test from the middle of a section."""
        atform.state.current_id = [
            42,
        ]
        atform.skip_test()
        self.assertEqual((44,), atform.id.get_id())

    def test_middle_explicit(self):
        """Confirm skipping to a specific test from the middle of a section."""
        atform.state.current_id = [
            42,
        ]
        atform.skip_test(50)
        self.assertEqual((50,), atform.id.get_id())

    def test_static_section_implicit(self):
        """Confirm implicitly skipping one test does not affect the section."""
        atform.set_id_depth(2)
        atform.skip_test()
        self.assertEqual((1, 2), atform.id.get_id())

    def test_static_section_explicit(self):
        """Confirm skipping to a specific test does not affect the section."""
        atform.set_id_depth(2)
        atform.skip_test(42)
        self.assertEqual((1, 42), atform.id.get_id())
