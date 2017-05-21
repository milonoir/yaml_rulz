from unittest import TestCase

from yaml_rulz.rulebook import OmitRule
from yaml_rulz.rulebook import BooleanRule
from yaml_rulz.rulebook import GreaterThanRule
from yaml_rulz.rulebook import LessThanRule
from yaml_rulz.rulebook import RegExpRule
from yaml_rulz.rulebook import PredefinedRegExpRule
from yaml_rulz.rulebook import UniquenessRule


RULE_KEY = "sample:key"
REFERRED_KEY = "other:key"

OMIT_CRITERION = "example"
OMIT_RESOURCE = {
    RULE_KEY: "whatever"
}

BOOLEAN_TRUE_CRITERIA = ["true", "yes", "on"]
BOOLEAN_TRUE_RESOURCE = {
    RULE_KEY: True
}
BOOLEAN_FALSE_CRITERIA = ["false", "no", "off"]
BOOLEAN_FALSE_RESOURCE = {
    RULE_KEY: False
}

GREATER_THAN_CRITERIA_OK = ["99", "0", "90/10+1"]
GREATER_THAN_CRITERIA_FAIL = ["100", "101", "(90/10+1)*20"]
GREATER_THAN_RESOURCE = {
    RULE_KEY: "100"
}

LESS_THAN_CRITERIA_OK = ["101", "924", "1000 + 1000 / 2"]
LESS_THAN_CRITERIA_FAIL = ["100", "-20", "10*4"]
LESS_THAN_RESOURCE = {
    RULE_KEY: "100"
}

REGEXP_RULE_OK = ["^(\\w+)(://)(\\w+)(\\.example\\.com)"]
REGEXP_RULE_FAIL = ["^https://.*"]
REGEXP_RULE_RESOURCE = {
    RULE_KEY: "http://mail.example.com"
}

PREDEF_REGEXP_CRITERIA = ["num", "ipv4", "ipv4_cidr", "ipv6", "ipv6_cidr"]
PREDEF_REGEXP_RESOURCE_OK = {
    "num": [
        {RULE_KEY: "0"},
        {RULE_KEY: "14135"},
        {RULE_KEY: "-12349"},
    ],
    "ipv4": [
        {RULE_KEY: "0.0.0.0"},
        {RULE_KEY: "255.255.255.255"},
        {RULE_KEY: "192.168.0.11"},
    ],
    "ipv4_cidr": [
        {RULE_KEY: "0.0.0.0/0"},
        {RULE_KEY: "255.255.255.255/32"},
        {RULE_KEY: "192.168.0.11/16"},
    ],
    "ipv6": [
        {RULE_KEY: "2001:cdba:0000:0000:0000:0000:3257:9652"},
        {RULE_KEY: "2001:cdba:0:0:0:0:3257:9652"},
        {RULE_KEY: "2001:cdba::3257:9652"},
    ],
    "ipv6_cidr": [
        {RULE_KEY: "2001:cdba:0000:0000:0000:0000:3257:9652/48"},
        {RULE_KEY: "2001:cdba:0:0:0:0:3257:9652/128"},
        {RULE_KEY: "2001:cdba::3257:9652/8"},
    ],
}
PREDEF_REGEXP_RESOURCE_FAIL = {
    "num": [
        {RULE_KEY: "16b"},
        {RULE_KEY: "14.13.5"},
        {RULE_KEY: "-12/349"},
    ],
    "ipv4": [
        {RULE_KEY: "0.0.0.0/3"},
        {RULE_KEY: "259.255.255.255"},
        {RULE_KEY: "192.168.0.341"},
    ],
    "ipv4_cidr": [
        {RULE_KEY: "0.0.0.0/99"},
        {RULE_KEY: "255.255.255.255/32/2"},
        {RULE_KEY: "192.168.0.611/16"},
    ],
    "ipv6": [
        {RULE_KEY: "2001:cdba:0000:0000:0000:0000:3257:9652:9294"},
        {RULE_KEY: "2001:cdba:0:0:0:0:3257:9652/1"},
        {RULE_KEY: "2001:cdba::3257::9652"},
    ],
    "ipv6_cidr": [
        {RULE_KEY: "2001:cdba:0000:0000:0000:0000:3257:9652/192"},
        {RULE_KEY: "2001:cdbg:0:0:0:0:3257:9652/128"},
        {RULE_KEY: "2001:cdba::3257:9652/ff"},
    ],
}

UNIQUENESS_CRITERION = [".*:key"]
UNIQUENESS_RESOURCE_OK = {
    REFERRED_KEY: "100",
    RULE_KEY: "71",
}
UNIQUENESS_RESOURCE_FAIL = {
    REFERRED_KEY: "100",
    RULE_KEY: "100",
}


class TestRulebook(TestCase):

    def test_rule_errors(self):
        rule_errors = [
            (BooleanRule, "tue"),
            (GreaterThanRule, "not number"),
            (LessThanRule, "a124"),
            (PredefinedRegExpRule, "ipv5"),
        ]
        for error in rule_errors:
            rule_class, criterion = error
            rule = rule_class(RULE_KEY, RULE_KEY, criterion)
            result = rule.match(OMIT_RESOURCE)
            self.assertEqual("Error in given criterion", result["message"])

    def test_omit_rule_always_matches(self):
        rule = OmitRule(RULE_KEY, RULE_KEY, OMIT_CRITERION)
        self.assertEqual(None, rule.match(OMIT_RESOURCE))

    def test_boolean_rule_true_positive(self):
        self.__assert_rule(BooleanRule, BOOLEAN_TRUE_CRITERIA, BOOLEAN_TRUE_RESOURCE, None)

    def test_boolean_rule_true_negative(self):
        self.__assert_rule(BooleanRule, BOOLEAN_TRUE_CRITERIA, BOOLEAN_FALSE_RESOURCE,
                           self.__generate_rule_error_dict)

    def test_boolean_rule_false_positive(self):
        self.__assert_rule(BooleanRule, BOOLEAN_FALSE_CRITERIA, BOOLEAN_FALSE_RESOURCE, None)

    def test_boolean_rule_false_negative(self):
        self.__assert_rule(BooleanRule, BOOLEAN_FALSE_CRITERIA, BOOLEAN_TRUE_RESOURCE,
                           self.__generate_rule_error_dict)

    def test_greater_than_rule_positive(self):
        self.__assert_rule(GreaterThanRule, GREATER_THAN_CRITERIA_OK, GREATER_THAN_RESOURCE, None)

    def test_greater_than_rule_negative(self):
        self.__assert_rule(GreaterThanRule, GREATER_THAN_CRITERIA_FAIL, GREATER_THAN_RESOURCE,
                           self.__generate_rule_error_dict)

    def test_less_than_rule_positive(self):
        self.__assert_rule(LessThanRule, LESS_THAN_CRITERIA_OK, LESS_THAN_RESOURCE, None)

    def test_less_than_rule_negative(self):
        self.__assert_rule(LessThanRule, LESS_THAN_CRITERIA_FAIL, LESS_THAN_RESOURCE,
                           self.__generate_rule_error_dict)

    def test_regexp_rule_positive(self):
        self.__assert_rule(RegExpRule, REGEXP_RULE_OK, REGEXP_RULE_RESOURCE, None)

    def test_regexp_rule_negative(self):
        self.__assert_rule(RegExpRule, REGEXP_RULE_FAIL, REGEXP_RULE_RESOURCE,
                           self.__generate_rule_error_dict)

    def test_predef_regexp_rule(self):
        for definition in PREDEF_REGEXP_CRITERIA:
            for resource in PREDEF_REGEXP_RESOURCE_OK.get(definition):
                self.__assert_rule(PredefinedRegExpRule, [definition], resource, None)
            for resource in PREDEF_REGEXP_RESOURCE_FAIL.get(definition):
                self.__assert_rule(PredefinedRegExpRule, [definition], resource,
                                   self.__generate_rule_error_dict)

    def test_uniqueness_positive(self):
        self.__assert_rule(UniquenessRule, UNIQUENESS_CRITERION, UNIQUENESS_RESOURCE_OK, None)

    def test_uniqueness_negative(self):
        self.__assert_rule(UniquenessRule, UNIQUENESS_CRITERION, UNIQUENESS_RESOURCE_FAIL,
                           self.__generate_referred_rule_error_dict)

    def __assert_rule(self, rule_class, criteria, resource, error_generator_callback):
        for criterion in criteria:
            rule = rule_class(RULE_KEY, RULE_KEY, criterion)
            self.assertEqual(None if not error_generator_callback else error_generator_callback(rule, resource),
                             rule.match(resource))

    @staticmethod
    def __generate_rule_error_dict(rule, resource):
        return {
            "schema": RULE_KEY,
            "resource": RULE_KEY,
            "criterion": rule.criterion,
            "value": resource.get(RULE_KEY),
            "message": rule.error_msg,
            "severity": "Error",
            "ref": False,
        }

    @staticmethod
    def __generate_referred_rule_error_dict(rule, resource):
        return {
            "schema": REFERRED_KEY,
            "resource": RULE_KEY,
            "criterion": resource.get(REFERRED_KEY),
            "value": resource.get(RULE_KEY),
            "message": rule.error_msg,
            "severity": "Error",
            "ref": True,
        }
