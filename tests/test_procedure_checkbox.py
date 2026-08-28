"""Unit tests for the function disabling procedure AcroForm checkboxes."""

import unittest

import atform
from atform.error import UserScriptError
from tests import utils


class DuplicateCall(unittest.TestCase):
    """Test to verify duplicae call exception."""

    def setUp(self):
        utils.reset()

    def test_duplicate_call(self):
        """Confirm exception when called more than once."""
        atform.set_procedure_checkbox_plain()
        with self.assertRaises(UserScriptError):
            atform.set_procedure_checkbox_plain()


class ContentArea(utils.ContentAreaException):
    """Tests to verify calling outside the setup area."""

    @staticmethod
    def call():
        atform.set_procedure_checkbox_plain()
