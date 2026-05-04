# Unit tests for the id module.


from tests import utils
import atform
import unittest


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
        atform.section(1)
        atform.skip_test()
        self.assertEqual((1, 2), atform.id.get_id())

    def test_static_section_explicit(self):
        """Confirm skipping to a specific test does not affect the section."""
        atform.section(1)
        atform.skip_test(42)
        self.assertEqual((1, 42), atform.id.get_id())
