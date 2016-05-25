import re


RE_NUMBER = r"\d+"
RE_EOL = r"$"
RE_LIST_TYPE = r"(^|{0})(\d+)({0}|$)"
RE_LIST_ITEM_SPLITTER = r"(^.*{0})(.*$)"


class ListHandler(object):

    def __init__(self, flat_yml, separator):
        self.separator = separator
        self.list_item_regexp = re.escape(separator) + RE_NUMBER
        self.list_type_regexp = RE_LIST_TYPE.format(separator)
        self.list_types = dict(self._filter_list_types(flat_yml))
        self.groups = self._generate_groups()

    def _filter_list_types(self, flat_yml):
        for key, value in flat_yml.items():
            if re.search(self.list_type_regexp, key):
                yield key, value

    def _generate_groups(self):
        flat_yml_copy = dict(self.list_types.items())
        groups = {}
        for key in self.list_types:
            if key in flat_yml_copy:
                parent = self._get_parent_from_key(key)
                similar_items = self._get_items_starting_with(parent, flat_yml_copy)
                flat_yml_copy = self._remove_items_from_dict(similar_items, flat_yml_copy)
                groups[parent] = dict([(key, value) for key, value in similar_items])
        return groups

    def _get_items_starting_with(self, parent, flat_yaml):
        return [(key, value) for key, value in flat_yaml.items()
                if parent == self._get_parent_from_key(key)]

    def _get_parent_from_key(self, key):
        return re.split(RE_LIST_ITEM_SPLITTER.format(self.list_item_regexp), key)[1]

    @staticmethod
    def _remove_items_from_dict(removable, target_dict):
        for item in removable:
            if item[0] in target_dict:
                del target_dict[item[0]]
        return target_dict
