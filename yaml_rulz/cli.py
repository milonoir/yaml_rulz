#!/usr/bin/env python

from __future__ import print_function
from argparse import ArgumentParser
import json
import sys

from prettytable import PrettyTable

from yaml_rulz.errors import YAMLHandlerError
from yaml_rulz.validator import YAMLValidator


TABLE_HEADER = ["Severity", "Message", "Schema", "Criterion", "Resource", "Value", "Ref"]


def main():
    args = __parse_arguments()
    has_errors, issues = __read_files_and_call_validator(args.schema, args.resource, args.exclusions)
    if args.raw:
        print(json.dumps(issues, indent=2))
    else:
        __print_error_report(issues)
    if has_errors:
        sys.exit(1)


def __print_error_report(issues):
    table = PrettyTable(TABLE_HEADER)
    for column in TABLE_HEADER:
        table.align[column] = "l"
    for issue in issues:
        table.add_row(
            [issue.get(issue_key.lower()) if issue_key in TABLE_HEADER[:-1]
             else "*" if issue.get(issue_key.lower()) else "" for issue_key in TABLE_HEADER]
        )
    table.sortby = "Severity"
    print(table)


def __read_files_and_call_validator(schema_file, resource_file, exclusions_file):
    schema = __read_file(schema_file)
    resource = __read_file(resource_file)
    exclusions = __read_file(exclusions_file) if exclusions_file else None
    try:
        validator = YAMLValidator(schema, resource, exclusions)
    except YAMLHandlerError as exc:
        print(exc)
        sys.exit(1)
    else:
        return validator.get_validation_issues()


def __parse_arguments():
    argument_parser = ArgumentParser(prog="yaml_rulz")
    argument_parser.add_argument("schema", help="YAML schema file")
    argument_parser.add_argument("resource", help="YAML resource file to be validated")
    argument_parser.add_argument("-x", "--exclusions", help="Exclusions file (optional)")
    argument_parser.add_argument("-r", "--raw", help="Prints the raw error dictionary", action="store_true")
    return argument_parser.parse_args()


def __read_file(filename):
    try:
        with open(filename, "r") as handler:
            return handler.read()
    except (IOError, OSError) as exc:
        print(exc)
        sys.exit(1)


if __name__ == "__main__":
    main()  # pragma: nocover
