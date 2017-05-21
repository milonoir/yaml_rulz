import re

from yaml_rulz.errors import RuleError


YAML_TRUE_REGEXP = r"^(true|yes|on)$"
YAML_FALSE_REGEXP = r"^(false|no|off)$"
YAML_KEY_REGEXP = r"^[\w\d:.*+-\\]+$"
NUM_REGEXP = r"-?\d+"
EOL_REGEXP = r"$"
IPV4_REGEXP = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
IPV6_REGEXP = r"(" \
              r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|" \
              r"([0-9a-fA-F]{1,4}:){1,7}:|" \
              r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|" \
              r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|" \
              r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|" \
              r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|" \
              r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|" \
              r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|" \
              r":((:[0-9a-fA-F]{1,4}){1,7}|:)|" \
              r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|" \
              r"::(ffff(:0{1,4}){0,1}:){0,1}" \
              r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}" \
              r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|" \
              r"([0-9a-fA-F]{1,4}:){1,4}:" \
              r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}" \
              r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
CIDR_32 = r"/(([0-9])|([1-2][0-9])|(3[0-2]))"
CIDR_128 = r"/(([0-9]{1,2})|(1[0-1][0-9])|(12[0-8]))"
ERROR_IN_CRITERION = "Error in given criterion"
ERROR_SEVERITY = "Error"


def raise_rule_error(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise RuleError
    return wrapped


def get_rule_response_dict(schema=None, resource=None, criterion=None,  # pylint: disable = too-many-arguments
                           value=None, message=None, ref=None):
    return {
        "schema": schema,
        "resource": resource,
        "criterion": criterion,
        "value": value,
        "message": message,
        "severity": ERROR_SEVERITY,
        "ref": ref,
    }


class RuleBase(object):

    error_msg = ""

    def __init__(self, schema_key, resource_key, criterion):
        self.schema_key = schema_key
        self.resource_key = resource_key
        self.criterion = str(criterion)

    def match(self, resource):
        value = resource.get(self.resource_key)
        self._resolve_references(resource)
        if isinstance(self.criterion, dict):
            if self.resource_key in self.criterion:
                del self.criterion[self.resource_key]
            for location, criterion in self.criterion.items():  # pylint: disable = no-member
                result = self._get_evaluation_result(location, self.resource_key, criterion, value, True)
                if result:
                    return result
        else:
            return self._get_evaluation_result(self.schema_key, self.resource_key, self.criterion, value, False)

    def _get_evaluation_result(self, schema, resource, criterion, value, ref):  # pylint: disable = too-many-arguments
        try:
            if not self._evaluate(criterion, value):
                return get_rule_response_dict(schema=schema,
                                              resource=resource,
                                              criterion=criterion,
                                              value=value,
                                              message=self.error_msg,
                                              ref=ref)
        except RuleError:
            return get_rule_response_dict(schema=schema,
                                          criterion=criterion,
                                          message=ERROR_IN_CRITERION,
                                          ref=ref)

    def _resolve_references(self, resource):
        search_result = []
        for key, value in resource.items():
            if re.match(self.criterion, key):
                search_result.append((key, value))
        self.criterion = dict(search_result) or self.criterion

    def _evaluate(self, criterion, value):
        raise NotImplementedError  # pragma: nocover


class OmitRule(RuleBase):

    def _evaluate(self, criterion, value):
        return True


class BooleanRule(RuleBase):

    error_msg = "Boolean mismatch"

    @staticmethod
    def _eval_criterion(criterion):
        patterns = {
            re.compile(YAML_TRUE_REGEXP, re.IGNORECASE): True,
            re.compile(YAML_FALSE_REGEXP, re.IGNORECASE): False,
        }
        for pattern in patterns:
            if re.match(pattern, criterion):
                return patterns[pattern]
        raise RuleError

    @raise_rule_error
    def _evaluate(self, criterion, value):
        return self._eval_criterion(criterion) == value


class GreaterThanRule(RuleBase):

    error_msg = "Value must be greater than criterion"

    @raise_rule_error
    def _evaluate(self, criterion, value):
        return eval(str(criterion)) < eval(str(value))


class LessThanRule(RuleBase):

    error_msg = "Value must be less than criterion"

    @raise_rule_error
    def _evaluate(self, criterion, value):
        return eval(str(criterion)) > eval(str(value))


class RegExpRule(RuleBase):

    error_msg = "Regular expression mismatch"

    # Regexp-based rules should not try to resolve references
    def _resolve_references(self, resource):
        pass  # pragma: nocover

    @raise_rule_error
    def _evaluate(self, criterion, value):
        return re.match(criterion, str(value)) is not None


class PredefinedRegExpRule(RegExpRule):

    error_msg = "Predefined regular expression mismatch"

    @staticmethod
    def _eval_criterion(criterion):
        patterns = {
            "num": NUM_REGEXP + EOL_REGEXP,
            "ipv4": IPV4_REGEXP + EOL_REGEXP,
            "ipv4_cidr": IPV4_REGEXP + CIDR_32 + EOL_REGEXP,
            "ipv6": IPV6_REGEXP + EOL_REGEXP,
            "ipv6_cidr": IPV6_REGEXP + CIDR_128 + EOL_REGEXP,
        }
        if criterion in patterns:
            return patterns[criterion]
        raise RuleError

    @raise_rule_error
    def _evaluate(self, criterion, value):
        return re.match(self._eval_criterion(criterion), str(value)) is not None


class UniquenessRule(RuleBase):

    error_msg = "Duplicated value"

    @raise_rule_error
    def _evaluate(self, criterion, value):
        return str(criterion) != str(value)
