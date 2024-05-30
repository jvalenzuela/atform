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
        testgen.id.next_id = [2] # Simulate a generated test.
        with self.assertRaises(RuntimeError):
            testgen.set_id_depth(2)

    def test_set_next_id(self):
        """Confirm the next ID is correctly updated."""
        testgen.set_id_depth(3)
        self.assertEqual([1] * 3, testgen.id.next_id)
