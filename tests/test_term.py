"""Tests for the term data model constructed in TestContent instances.

These tests serve to ensure terms used in the public API are correctly
collated into structures for use by the PDF output module.
"""

import unittest

import atform
from tests import utils


class Replacement(unittest.TestCase):
    """Tests verifying labels are replaced with their associated text."""

    def setUp(self):
        utils.reset()
        atform.add_term("foo", "term")

    def test_objective(self):
        """Confirm replacement in the objective."""
        atform.add_test("title", objective="$term")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("foo", t.objective)

    def test_preconditions(self):
        """Confirm replacment in the preconditions."""
        atform.add_test("title", preconditions=["$term"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("foo", t.preconditions[0])

    def test_procedure(self):
        """Confirm replacement in the procedure."""
        atform.add_test("title", procedure=["$term"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("foo", t.procedure[0].text)


class Use(unittest.TestCase):
    """Tests verifying use of a term is detected in various content areas."""

    def setUp(self):
        utils.reset()
        atform.add_term("term", "term")
        atform.add_test("support", supports_terms=["term"])

    def test_objective(self):
        """Confirm term use is detected in the objective."""
        atform.add_test("use", objective="$term")
        self.assert_use()

    def test_preconditions(self):
        """Confirm term use is detected in the preconditions."""
        atform.add_test("use", preconditions=["$term"])
        self.assert_use()

    def test_procedure(self):
        """Confirm term use is detected in the procedure."""
        atform.add_test("use", procedure=["$term"])
        self.assert_use()

    def assert_use(self):
        """Verifies term use was detected.

        Detection is implied by the use test(most-recently created)
        referencing the supporting test.
        """
        use = utils.get_test_content()
        use.pregenerate()
        self.assertEqual("1 support", use.supported_terms["term"][0])


class Support(unittest.TestCase):
    """Tests verifying supported term references."""

    def setUp(self):
        utils.reset()
        atform.add_term("term1", "term1")
        atform.add_term("term2", "term2")

    def test_unused(self):
        """Confirm a term unused by a test is not referenced."""
        atform.add_test("title")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual({}, t.supported_terms)

    def test_unsupported(self):
        """Confirm a term used but notsupported is not referenced."""
        atform.add_test("title", objective="$term1")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual({}, t.supported_terms)

    def test_supported_unused(self):
        """Confirm a supported term not used in a test is not referenced."""
        atform.add_test("support", supports_terms=["term1"])
        atform.add_test("title")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual({}, t.supported_terms)

    def test_support_before_use(self):
        """Confirm a supporting test preceeding the use test is listed."""
        atform.add_test("support", supports_terms=["term1"])
        atform.add_test("use", objective="$term1")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual({"term1": ["1 support"]}, t.supported_terms)

    def test_support_after_use(self):
        """Confirm a supporting test following the use test is listed."""
        atform.add_test("use", objective="$term1")
        t = utils.get_test_content()
        atform.add_test("support", supports_terms=["term1"])
        t.pregenerate()
        self.assertEqual({"term1": ["2 support"]}, t.supported_terms)

    def test_support_self_reference(self):
        """Confirm a supporting test does not reference itself."""
        atform.add_test("support", supports_terms=["term1"], objective="$term1")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual({}, t.supported_terms)

    def test_multiple_support(self):
        """Confirm multiple tests supporting the same term are referenced by the use test."""
        atform.add_test("support1", supports_terms=["term1"])
        atform.add_test("support2", supports_terms=["term1"])
        atform.add_test("use", objective="$term1")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual(
            {"term1": ["1 support1", "2 support2"]},
            t.supported_terms,
        )

    def test_mutual_support(self):
        """Confirm multiple tests supporting and using the same term reference each other."""
        atform.add_test("t1", supports_terms=["term1"], objective="$term1")
        t1 = utils.get_test_content()
        atform.add_test("t2", supports_terms=["term1"], objective="$term1")
        t2 = utils.get_test_content()
        t1.pregenerate()
        t2.pregenerate()
        self.assertEqual({"term1": ["2 t2"]}, t1.supported_terms)
        self.assertEqual({"term1": ["1 t1"]}, t2.supported_terms)

    def test_multiple_terms(self):
        """Confirm multiple supported terms used by a single test are referenced."""
        atform.add_test("support1", supports_terms=["term1"])
        atform.add_test("support2", supports_terms=["term2"])
        atform.add_test("title", objective="$term1 $term2")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual(
            {
                "term1": ["1 support1"],
                "term2": ["2 support2"],
            },
            t.supported_terms,
        )


class SupportListingOrder(unittest.TestCase):
    """Tests verifying correct order of supported term references."""

    def setUp(self):
        utils.reset()

    def test_terms(self):
        """Verify terms are sorted according to their unformatted text."""
        atform.add_term("zspam", "spam", typeface="monospace")
        atform.add_term("eggs", "eggs", font="bold")
        atform.add_term("afoo", "foo", typeface="sansserif")
        atform.add_test("support", supports_terms=["spam", "eggs", "foo"])
        atform.add_test("title", objective="$spam $foo $eggs")
        t = utils.get_test_content()
        t.pregenerate()
        terms = list(t.supported_terms.keys())
        self.assertIn("afoo", terms[0])
        self.assertIn("eggs", terms[1])
        self.assertIn("zspam", terms[2])

    def test_tests(self):
        """Verify tests supporting a term are sorted according to ID."""
        atform.add_term("term", "term")
        atform.add_test("support spam", supports_terms=["term"])
        atform.add_test("support eggs", supports_terms=["term"])
        atform.add_test("support foo", supports_terms=["term"])
        atform.add_test("title", objective="$term")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual(
            ["1 support spam", "2 support eggs", "3 support foo"],
            t.supported_terms["term"],
        )
