from itertools import chain
import re

from yaml_rulz.rulebook import get_rule_response_dict
from yaml_rulz.rulebook import BooleanRule
from yaml_rulz.rulebook import GreaterThanRule
from yaml_rulz.rulebook import LessThanRule
from yaml_rulz.rulebook import OmitRule
from yaml_rulz.rulebook import PredefinedRegExpRule
from yaml_rulz.rulebook import RegExpRule
from yaml_rulz.rulebook import UniquenessRule
from yaml_rulz.yaml_handler import ResourceHandler
from yaml_rulz.yaml_handler import TemplateHandler


WARNING_SEVERITY = "Warning"
MISSING_RESOURCE = "Item is missing from resource"
MISSING_TEMPLATE = "No rules were found for resource"
MISSING_PROTOTYPE = "No matching prototype was found"
RULE_SEPARATOR_REGEXP = r"\s+\|\s+"
EOL_REGEXP = r"$"


class YAMLValidator(object):

    known_rule_tokens = {
        "*": OmitRule,
        "?": BooleanRule,
        ">": GreaterThanRule,
        "<": LessThanRule,
        "~": RegExpRule,
        "@": PredefinedRegExpRule,
        "!": UniquenessRule,
    }

    def __init__(self, template_content, resource_content, exclusions_content=None):
        self.template_handler = TemplateHandler(template_content)
        self.resource_handler = ResourceHandler(resource_content)
        self.exclusions = YAMLValidator._import_exclusions(exclusions_content)

    def get_validation_issues(self):
        issues = [issue for issue in chain(
            self._find_missing_resource_scalars(),
            self._find_missing_template_scalars(),
            self._validate_scalars(),
            self._validate_lists(),
        )]
        return self._update_severity(issues)

    def _update_severity(self, issues):
        has_errors = False
        for issue in issues:
            if self._is_excluded(issue["template"]) or self._is_excluded(issue["resource"]):
                issue["severity"] = WARNING_SEVERITY
            else:
                has_errors = True
        return has_errors, issues

    def _is_excluded(self, key):
        try:
            for exc in self.exclusions:
                if re.match(exc, key):
                    return True
            return False
        except TypeError:
            return False

    def _find_missing_resource_scalars(self):
        for issue in self._yield_missing_scalar_error(self.template_handler,
                                                      self.resource_handler,
                                                      MISSING_RESOURCE):
            yield issue

    def _find_missing_template_scalars(self):
        for issue in self._yield_missing_scalar_error(self.resource_handler,
                                                      self.template_handler,
                                                      MISSING_TEMPLATE):
            yield issue

    def _validate_rules(self, flat_template, flat_resource):
        for resource_key in flat_resource:
            key_mask = self._key_to_mask(self.resource_handler, resource_key)
            for template_key in flat_template:
                if re.match(key_mask + EOL_REGEXP, template_key):
                    rule_chain = self._split_rules(flat_template[template_key])
                    for rule_expression in rule_chain:
                        rule = self._get_rule(template_key, resource_key, rule_expression)
                        # Whole resource must be passed to match() because of possible references in rules
                        result = rule.match(self.resource_handler.flat_yml)
                        if result:
                            yield result

    def _validate_scalars(self):
        for result in self._validate_rules(self.template_handler.scalars, self.resource_handler.scalars):
            yield result

    def _validate_lists(self):
        for resource_path, resource in self.resource_handler.list_handler.groups.items():
            # Collect prototypes
            path_mask = self._key_to_mask(self.resource_handler, resource_path)
            prototype_candidates = [
                prototype_groups
                for template_path, prototype_groups in self.template_handler.list_handler.groups.items()
                if re.match(path_mask + EOL_REGEXP, template_path)
            ]
            prototypes = self._filter_matching_prototypes(resource, prototype_candidates)
            if not prototypes:
                yield get_rule_response_dict(
                    template=prototype_candidates,
                    resource=resource_path,
                    message=MISSING_PROTOTYPE,
                )
            # Evaluate prototypes
            prototype_failure_count = 0
            prototype_failures = []
            for prototype in prototypes:
                result = [failure for failure in self._validate_rules(prototype, resource)]
                if result:
                    prototype_failures.extend(result)
                    prototype_failure_count += 1
            if prototype_failure_count >= len(prototypes):
                for failure in prototype_failures:
                    yield failure

    def _filter_matching_prototypes(self, resource, prototypes):
        matching_prototypes = []
        masked_resource_keys = [self._key_to_mask(self.template_handler, key) for key in resource.keys()]
        for prototype in prototypes:
            masked_prototype_keys = [self._key_to_mask(self.template_handler, key) for key in prototype.keys()]
            if set(masked_prototype_keys) == set(masked_resource_keys):
                if re.search(self.template_handler.list_handler.list_item_regexp + EOL_REGEXP, list(prototype)[0]):
                    for key, value in prototype.items():
                        matching_prototypes.append({key: value})
                else:
                    matching_prototypes.append(prototype)
        return matching_prototypes

    def _get_rule(self, template_key, resource_key, rule_expression):
        try:
            token, criterion = rule_expression.split(" ", 1)
        except (ValueError, AttributeError):
            return OmitRule(template_key, resource_key, None)
        else:
            if token in self.known_rule_tokens:
                return self.known_rule_tokens[token](template_key, resource_key, criterion)
            else:
                return OmitRule(template_key, resource_key, None)

    @staticmethod
    def _yield_missing_scalar_error(outer_handler, inner_handler, message):
        for key in outer_handler.scalars:
            if key not in inner_handler.scalars:
                yield get_rule_response_dict(
                    template=key if outer_handler.role == "template" else None,
                    resource=key if outer_handler.role == "resource" else None,
                    message=message,
                )

    @staticmethod
    def _import_exclusions(exclusions_content):
        if not exclusions_content:
            return []
        else:
            return [exc.strip() for exc in exclusions_content.splitlines() if exc]

    @staticmethod
    def _split_rules(rule_chain):
        return re.split(RULE_SEPARATOR_REGEXP, str(rule_chain))

    @staticmethod
    def _key_to_mask(handler, key):
        return re.sub(handler.list_handler.list_item_regexp, handler.list_handler.list_item_regexp, key)
