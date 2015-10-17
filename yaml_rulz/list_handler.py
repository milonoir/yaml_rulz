# -*- coding: utf-8 -*-

from collections import defaultdict
import re


NUMBER_REGEXP = r"\d+"


class ListHandler(object):

    def __init__(self, flat_yml, separator, has_prototypes):
        self._separator = separator
        self._list_item_regexp = re.escape(separator) + NUMBER_REGEXP
        self.list_types = self._filter_list_types(flat_yml)
        self.groups = self._generate_groups()
        self.prototypes = self._generate_prototypes() if has_prototypes else []

    def get_all_prototypes_for_path(self, path):
        return self.prototypes.get(self._indices_to_numbers(path), [])

    def get_matching_prototypes(self, path, items):
        candidates = self.get_all_prototypes_for_path(path)
        return [prototype for prototype in candidates if sorted(prototype.keys()) == sorted(items.keys())]

    def iterate_groups(self):
        for path, lists in self.groups.items():
            for index, single_list in lists.items():
                yield path, index, single_list

    def _filter_list_types(self, flat_yml):
        return {key: value for key, value in flat_yml.items() if self._is_list_type(key)}

    def _is_list_type(self, key):
        return True if re.search(self._list_item_regexp, key) else False

    def _indices_to_numbers(self, string):
        return re.sub(self._list_item_regexp, self._separator + NUMBER_REGEXP, string)

    def _generate_prototypes(self):
        prototypes = defaultdict(list)
        for path, _, single_list in self.iterate_groups():
            regexp_path = self._indices_to_numbers(path)
            prototypes[regexp_path].append(single_list)
        return prototypes

    def _generate_groups(self):
        result = defaultdict(lambda: defaultdict(dict))
        for key, value in self.list_types.items():
            index = re.findall(self._list_item_regexp, key)
            path, list_item = key.rsplit(index[-1], 1)
            result[path][index[-1]][list_item] = value
        return result
