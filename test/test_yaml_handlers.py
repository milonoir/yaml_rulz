# -*- coding: utf-8 -*-

from unittest import TestCase

from yaml_rulz.errors import YAMLHandlerError
from yaml_rulz.yaml_handlers import YAMLHandlerBase
from yaml_rulz.yaml_handlers import ResourceHandler
from yaml_rulz.yaml_handlers import TemplateHandler


SEPARATOR = ":"

INVALID_YAML_CONTENT = """
---
foo: bar
 nested:
    foo: bar
"""

YAML_CONTENT = """
---
foo: bar
nested:
    foo: bar
    list:
        - foo
        - bar
"""

YAML_FLAT = {
    "foo": "bar",
    "nested:foo": "bar",
    "nested:list:0": "foo",
    "nested:list:1": "bar",
}


class TestYamlHandlers(TestCase):

    def test_handler_initialization(self):
        for handler_class in (ResourceHandler, TemplateHandler):
            handler = handler_class(yml_content=YAML_CONTENT)
            self.assertEqual(YAML_FLAT, handler.flat_yml)

    def test_handler_initialization_fails(self):
        for handler_class in (ResourceHandler, TemplateHandler):
            with self.assertRaises(YAMLHandlerError):
                handler_class(yml_content=INVALID_YAML_CONTENT)

    def test_base_handler_initialization_is_not_allowed(self):
        with self.assertRaises(NotImplementedError):
            YAMLHandlerBase(yml_content=YAML_CONTENT, separator=SEPARATOR)
