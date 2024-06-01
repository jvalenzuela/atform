# Unit tests for the id module.


from tests import utils
import testgen
import unittest


class GetId(unittest.TestCase):
    """Unit tests for the get_id() function."""

    def setUp(self):
        utils.reset()

    def test_single_depth_increment(self):
        """Confirm single-level IDs are properly incremented."""
        for i in range(1, 4):
            self.assertEqual((i,), testgen.id.get_id())

    def test_multi_depth_increment(self):
        """Confirm multi-level IDs are properly incremented."""
        testgen.id.set_id_depth(3)
        for i in range(1, 4):
            self.assertEqual((1, 1, i), testgen.id.get_id())

    def test_level_initialization(self):
        """Confirm levels that have been reset are initialized to 1."""
        testgen.id.set_id_depth(3)
        testgen.id.current_id = [2, 0, 0] # Simulate a level 0 increment.
        self.assertEqual((2, 1, 1), testgen.id.get_id())


class Section(unittest.TestCase):
    """Unit tests for the section() function."""

    def setUp(self):
        utils.reset()

    def test_level_type(self):
        """Confirm an exception is raised for a non-integer level."""
        testgen.set_id_depth(2)
        with self.assertRaises(TypeError):
            testgen.section('0')

    def test_level_nonsection_single(self):
        """Confirm an exception is raised for a level that is not a section for single-level IDs."""
        with self.assertRaises(ValueError):
            testgen.section(0)

    def test_level_nonsection_multi(self):
        """Confirm an exception is raised for a level that is not a section for multi-level IDs."""
        testgen.set_id_depth(2)
        with self.assertRaises(ValueError):
            testgen.section(1)

    def test_level_outside_depth(self):
        """Confirm an exception is raised for a level beyond the ID depth."""
        testgen.set_id_depth(2)
        for level in [-1, 2]:
            with self.assertRaises(ValueError):
                testgen.section(level)

    def test_id_type(self):
        """Confirm an exception is raised if id is not an integer."""
        testgen.set_id_depth(2)
        with self.assertRaises(TypeError):
            testgen.section(0, id='42')

    def test_id_backwards(self):
        """Confirm an exception is raised for id values of previous sections."""
        testgen.set_id_depth(2)
        testgen.section(0, id=3)
        for id in range(-1, 4):
            with self.assertRaises(ValueError):
                testgen.section(0, id=id)

    def test_title_type(self):
        """Confirm an exception is raised if title is not a string."""
        testgen.set_id_depth(2)
        with self.assertRaises(TypeError):
            testgen.section(0, title=42)

    def test_level_increment(self):
        """Confirm the section level is incremented if id is omitted."""
        testgen.set_id_depth(2)
        testgen.section(0)
        self.assertEqual((1, 1), testgen.id.get_id())
        testgen.section(0)
        self.assertEqual((2, 1), testgen.id.get_id())

    def test_set_specific_id(self):
        """Confirm section level is set to a specific value if id is given."""
        testgen.set_id_depth(2)
        testgen.section(0, id=42)
        self.assertEqual((42, 1), testgen.id.get_id())

    def test_reset_numbering(self):
        """Confirm numbering of further subsections are reset."""
        testgen.set_id_depth(3)

        testgen.id.current_id = [42, 78, 100]
        testgen.section(1)
        self.assertEqual((42, 79, 1), testgen.id.get_id())

        testgen.id.current_id = [42, 78, 100]
        testgen.section(0)
        self.assertEqual((43, 1, 1), testgen.id.get_id())

    def test_no_title(self):
        """Confirm no title is saved if title is omitted."""
        testgen.set_id_depth(2)
        testgen.section(0)
        self.assertNotIn((1,), testgen.id.section_titles)

    def test_empty_title(self):
        """Confirm no title is saved if title is an empty string."""
        testgen.set_id_depth(2)
        testgen.section(0, title='')
        self.assertNotIn((1,), testgen.id.section_titles)

    def test_blank_title(self):
        """Confirm no title is saved if title is all whitespace."""
        testgen.set_id_depth(2)
        testgen.section(0, title='\n\r\t ')
        self.assertNotIn((1,), testgen.id.section_titles)

    def test_title_store(self):
        """Confirm the title is saved."""
        testgen.set_id_depth(2)
        testgen.section(0, title='spam')
        self.assertEqual('spam', testgen.id.section_titles[(1,)])

    def test_title_strip(self):
        """Confirm the saved title is stripped of surrounding whitespace."""
        testgen.set_id_depth(2)
        testgen.section(0, title='\nfoo\t \r ')
        self.assertEqual('foo', testgen.id.section_titles[(1,)])


class SetIdDepth(unittest.TestCase):
    """Unit tests for the set_id_depth() function."""

    def setUp(self):
        utils.reset()

    def test_non_integer_levels(self):
        """Confirm an exception is raised for non-integer argument."""
        with self.assertRaises(TypeError):
            testgen.set_id_depth('1')

    def test_levels_leq_zero(self):
        """Confirm an exception is raised for arguments less than 1."""
        for level in [-1, 0]:
            with self.assertRaises(ValueError):
                testgen.id.set_id_depth(level)

    def test_after_test_created(self):
        """Confirm an exception is raised if called after creating tests."""
        testgen.id.current_id = [2] # Simulate a generated test.
        with self.assertRaises(RuntimeError):
            testgen.set_id_depth(2)

    def test_set_current_id(self):
        """Confirm the current ID is correctly updated."""
        testgen.set_id_depth(3)
        self.assertEqual([0] * 3, testgen.id.current_id)
