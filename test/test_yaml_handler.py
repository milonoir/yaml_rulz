from unittest import TestCase

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from yaml_rulz.yaml_handler import YAMLHandlerBase
from yaml_rulz.yaml_handler import YAMLHandlerError


INVALID_YAML = """
---
root:
  key: value
   other_key: other_value
"""
VALID_YAML = """
---
root:
  scalars:
    key_a: value_a
    key_b: value_b
  list:
    - item1
    - item2
  nested_list:
    - id: id1
      inner_list:
        - key1: value1
          key2: value2
        - key1: value1
          key2: value2
    - id: id2
      inner_list:
        - key3: value3
          key4: value4
        - key3: value3
          key4: value4
"""
VALID_YAML_SCALARS = {
    "root:scalars:key_a": "value_a",
    "root:scalars:key_b": "value_b",
    "root:list": [],
    "root:nested_list": [],
}
VALID_YAML_LIST_TYPES = {
    "root:list:0": "item1",
    "root:list:1": "item2",
    "root:nested_list:0:id": "id1",
    "root:nested_list:0:inner_list": [],
    "root:nested_list:0:inner_list:0:key1": "value1",
    "root:nested_list:0:inner_list:0:key2": "value2",
    "root:nested_list:0:inner_list:1:key1": "value1",
    "root:nested_list:0:inner_list:1:key2": "value2",
    "root:nested_list:1:id": "id2",
    "root:nested_list:1:inner_list": [],
    "root:nested_list:1:inner_list:0:key3": "value3",
    "root:nested_list:1:inner_list:0:key4": "value4",
    "root:nested_list:1:inner_list:1:key3": "value3",
    "root:nested_list:1:inner_list:1:key4": "value4",
}


class TestYAMLHandler(TestCase):

    def test_syntax_error_in_yaml_throws_exception(self):
        self.assertRaises(YAMLHandlerError, YAMLHandlerBase, INVALID_YAML)

    @patch("yaml_rulz.yaml_handler.ListHandler")
    def test_handler_with_valid_yaml(self, list_handler_mock):
        list_handler_mock.return_value.list_types = VALID_YAML_LIST_TYPES
        all_data = VALID_YAML_SCALARS.copy()
        all_data.update(VALID_YAML_LIST_TYPES)
        handler = YAMLHandlerBase(VALID_YAML)
        self.assertEqual(VALID_YAML_SCALARS, handler.scalars)
        self.assertEqual(all_data, handler.flat_yml)
