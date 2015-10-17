# -*- coding: utf-8 -*-

from unittest import TestCase
import sys

from yaml_rulz.list_handler import ListHandler


SEPARATOR = ":"

FLAT_YAML = {
    "root:not_a_list": "foo",
    "root:simple_list:0:name": "John Doe",
    "root:simple_list:0:email": "john@doe.gov",
    "root:simple_list:1:name": "Jane Doe",
    "root:simple_list:1:skype": "janedoe",
    "root:nested:but_not_a_list": "bar",
}

LIST_TYPES = {
    "root:simple_list:0:name": "John Doe",
    "root:simple_list:0:email": "john@doe.gov",
    "root:simple_list:1:name": "Jane Doe",
    "root:simple_list:1:skype": "janedoe",
}

GROUPS = {
    "root:simple_list": {
        ":0": {
            ":name": "John Doe",
            ":email": "john@doe.gov",
        },
        ":1": {
            ":name": "Jane Doe",
            ":skype": "janedoe",
        }
    }
}

PROTOTYPES = [
    {
        ":email": "john@doe.gov",
        ":name": "John Doe"
    },
    {
        ":name": "Jane Doe",
        ":skype": "janedoe"
    }
]


class TestListHandler(TestCase):

    def test_list_handler_without_prototypes_generation(self):
        handler = ListHandler(FLAT_YAML, SEPARATOR, False)
        self.assertEqual(LIST_TYPES, handler.list_types)
        self.assertEqual(GROUPS, handler.groups)
        self.assertEqual([], handler.prototypes)

    def test_list_handler_finds_all_prototypes_for_path(self):
        handler = ListHandler(FLAT_YAML, SEPARATOR, True)
        self.__assert_lists_equal(PROTOTYPES, handler.get_all_prototypes_for_path("root:simple_list"))

    def test_list_handler_finds_prototypes_for_path_and_items(self):
        handler = ListHandler(FLAT_YAML, SEPARATOR, True)
        find_this = {
            ":name": "", ":email": ""
        }
        self.__assert_lists_equal([PROTOTYPES[0]], handler.get_matching_prototypes("root:simple_list", find_this))

    def __assert_lists_equal(self, expected, tested):
        if sys.version_info[0] == 3 and sys.version_info[1] >= 1:
            self.assertListEqual(expected, tested)
        else:
            self.assertItemsEqual(expected, tested)
