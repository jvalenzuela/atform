# Unit tests for the id module.


from tests import utils
import testgen
import unittest


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
