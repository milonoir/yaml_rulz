import yaml

from yaml_rulz.errors import YAMLHandlerError
from yaml_rulz.list_handler import ListHandler


class YAMLHandlerBase(object):

    role = ""

    def __init__(self, yml_content, separator=":"):
        self.separator = separator
        parsed_yml = self._import_yml(yml_content)
        self.flat_yml = self._get_flat_dict(parsed_yml)
        self.list_handler = ListHandler(self.flat_yml, separator)
        self.scalars = dict(
            [(key, value) for key, value in self.flat_yml.items() if key not in self.list_handler.list_types]
        )

    def _get_flat_dict(self, parsed_yml):
        if isinstance(parsed_yml, dict):
            return dict(self._flatten_items(parsed_yml.items(), parent=""))
        return dict(self._flatten_items([("", parsed_yml)], parent=""))

    def _flatten_items(self, items, parent):
        flattened_items = []
        for key, value in items:
            prefix = parent + str(key)
            if isinstance(value, list):
                flattened_items.append((prefix, []))
                flattened_items.extend(self._flatten_items(list(enumerate(value)), parent=prefix+self.separator))
            elif isinstance(value, dict):
                flattened_items.extend(self._flatten_items(value.items(), parent=prefix+self.separator))
            else:
                flattened_items.append((prefix, value))
        return flattened_items

    def _import_yml(self, yml_content):
        try:
            return yaml.load(yml_content)
        except yaml.YAMLError as exc:
            raise YAMLHandlerError("Error in {0}\n{1}".format(self.role, exc))


class SchemaHandler(YAMLHandlerBase):

    role = "schema"


class ResourceHandler(YAMLHandlerBase):

    role = "resource"
