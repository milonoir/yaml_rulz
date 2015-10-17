# -*- coding: utf-8 -*-

import yaml

from yaml_rulz.errors import YAMLHandlerError
from yaml_rulz.list_handler import ListHandler


DEFAULT_SEPARATOR = ":"


class YAMLHandlerBase(object):

    def __init__(self, yml_content, separator):
        self.separator = separator
        self.dict_yml = self._parse_yml(yml_content)
        self.flat_yml = self._get_flat_dict()

    def _get_flat_dict(self):
        return dict(self._flatten_items(self.dict_yml.items(), parent=""))

    def _flatten_items(self, items, parent):
        flattened_items = []
        for key, value in items:
            prefix = parent + str(key)
            if isinstance(value, list):
                flattened_items.extend(self._flatten_items(list(enumerate(value)), parent=prefix+self.separator))
            elif isinstance(value, dict):
                flattened_items.extend(self._flatten_items(value.items(), parent=prefix+self.separator))
            else:
                flattened_items.append((prefix, value))
        return flattened_items

    def _parse_yml(self, yml_content):
        raise NotImplementedError


class TemplateHandler(YAMLHandlerBase):

    def __init__(self, yml_content, separator=DEFAULT_SEPARATOR):
        super(TemplateHandler, self).__init__(yml_content, separator)
        self.list_handler = ListHandler(self.flat_yml, separator, has_prototypes=True)

    def _parse_yml(self, yml_content):
        try:
            return yaml.load(yml_content)
        except yaml.YAMLError as exc:
            raise YAMLHandlerError("Error in template\n" + str(exc))


class ResourceHandler(YAMLHandlerBase):

    def __init__(self, yml_content, separator=DEFAULT_SEPARATOR):
        super(ResourceHandler, self).__init__(yml_content, separator)
        self.list_handler = ListHandler(self.flat_yml, separator, has_prototypes=False)

    def _parse_yml(self, yml_content):
        try:
            return yaml.load(yml_content)
        except yaml.YAMLError as exc:
            raise YAMLHandlerError("Error in resource\n" + str(exc))
