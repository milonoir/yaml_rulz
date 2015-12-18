from unittest import TestCase

from yaml_rulz.list_handler import ListHandler


TEST_FLAT_YML_LIST_TYPES = {
    "ericsson:shelf:0:id": "@ num",
    "ericsson:shelf:0:management:address": "@ ipv4",
    "ericsson:shelf:0:management:username": "username",
    "ericsson:shelf:0:management:password": "password",
    "ericsson:shelf:0:blade": [],
    "ericsson:shelf:0:blade:0:id": "@ num",
    "ericsson:shelf:0:blade:0:nic_assignment": "~ whatever",
    "ericsson:shelf:0:blade:1:id": "@ num",
    "ericsson:shelf:0:blade:1:nic_assignment": "~ whatever",
    "ericsson:shelf:0:blade:1:cic:id": "@ num",
    "ericsson:shelf:0:blade:2:id": "@ num",
    "ericsson:shelf:0:blade:2:nic_assignment": "~ whatever",
    "ericsson:shelf:0:blade:2:cic:id": "@ num",
    "ericsson:shelf:0:blade:2:cinder": "",
    "ericsson:shelf:1:id": "@ num",
    "ericsson:shelf:1:blade": [],
    "ericsson:shelf:1:blade:0:id": "@ num",
    "ericsson:shelf:1:blade:0:nic_assignment": "~ whatever",
    "ericsson:simple_list:0": "~ foo",
    "ericsson:simple_list:1": "~ bar",
}
TEST_FLAT_YML_SCALARS = {
    "ericsson:shelf": [],
}
TEST_FLAT_YML = TEST_FLAT_YML_SCALARS.copy()
TEST_FLAT_YML.update(TEST_FLAT_YML_LIST_TYPES)
TEST_GROUPS = {
    "ericsson:shelf:0": {
        "ericsson:shelf:0:id": "@ num",
        "ericsson:shelf:0:blade": [],
        "ericsson:shelf:0:management:address": "@ ipv4",
        "ericsson:shelf:0:management:password": "password",
        "ericsson:shelf:0:management:username": "username",
    },
    "ericsson:shelf:1": {
        "ericsson:shelf:1:id": "@ num",
        "ericsson:shelf:1:blade": [],
    },
    "ericsson:shelf:0:blade:0": {
        "ericsson:shelf:0:blade:0:nic_assignment": "~ whatever",
        "ericsson:shelf:0:blade:0:id": "@ num",
    },
    "ericsson:shelf:0:blade:1": {
        "ericsson:shelf:0:blade:1:nic_assignment": "~ whatever",
        "ericsson:shelf:0:blade:1:id": "@ num",
        "ericsson:shelf:0:blade:1:cic:id": "@ num",
    },
    "ericsson:shelf:0:blade:2": {
        "ericsson:shelf:0:blade:2:nic_assignment": "~ whatever",
        "ericsson:shelf:0:blade:2:cinder": "",
        "ericsson:shelf:0:blade:2:id": "@ num",
        "ericsson:shelf:0:blade:2:cic:id": "@ num",
    },
    "ericsson:shelf:1:blade:0": {
        "ericsson:shelf:1:blade:0:nic_assignment": "~ whatever",
        "ericsson:shelf:1:blade:0:id": "@ num",
    },
    "ericsson:simple_list:0": {
        "ericsson:simple_list:0": "~ foo",
    },
    "ericsson:simple_list:1": {
        "ericsson:simple_list:1": "~ bar",
    },
}


class TestListHandler(TestCase):

    def setUp(self):
        self.handler = ListHandler(TEST_FLAT_YML, ":")

    def test_list_handler_init(self):
        self.assertEqual(TEST_FLAT_YML_LIST_TYPES, self.handler.list_types)
        self.assertEqual(TEST_GROUPS, self.handler.groups)
