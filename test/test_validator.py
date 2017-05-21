from unittest import TestCase

from yaml_rulz.validator import YAMLValidator


SCHEMA_CONTENT = r"""
---
root:
  key_a: "~ exactly this"
  key_b: "@ num | > 15"
  key_c: "> root:key_b"
"""

RESOURCE_WITH_ISSUES = r"""
---
root:
  key_a: exactly that
  key_b: 6
  key_c: 2
"""

RESOURCE_ALL_OK = r"""
---
root:
  key_a: exactly this
  key_b: 16
  key_c: 20
"""

EXCLUSIONS = r"""
root:key_a
"""

ISSUES = [
    {"resource": "root:key_a",
     "severity": "Warning",
     "value": "exactly that",
     "criterion": "exactly this",
     "schema": "root:key_a",
     "message": "Regular expression mismatch", "ref": False},
    {"criterion": 6,
     "message": "Value must be greater than criterion",
     "ref": True,
     "resource": "root:key_c",
     "severity": "Error",
     "schema": "root:key_b",
     "value": 2},
    {"criterion": "15",
     "message": "Value must be greater than criterion",
     "ref": False,
     "resource": "root:key_b",
     "severity": "Error",
     "schema": "root:key_b",
     "value": 6},
]


class TestValidator(TestCase):

    maxDiff = None

    def test_validator_without_issues(self):
        has_errors, issues = self.__create_validator_and_get_result(RESOURCE_ALL_OK)
        self.assertFalse(has_errors)
        self.assertEqual([], issues)

    def test_validator_with_issues(self):
        has_errors, issues = self.__create_validator_and_get_result(RESOURCE_WITH_ISSUES, EXCLUSIONS)
        self.assertTrue(has_errors)
        try:
            self.assertItemsEqual(ISSUES, issues)
        except AttributeError:
            self.assertEqual(len(ISSUES), len(issues))
            for issue in ISSUES:
                self.assertIn(issue, issues)

    @staticmethod
    def __create_validator_and_get_result(resource, exclusions=None):
        validator = YAMLValidator(SCHEMA_CONTENT, resource, exclusions)
        return validator.get_validation_issues()
