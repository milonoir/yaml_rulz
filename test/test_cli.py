try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from unittest import TestCase

try:
    from mock import mock_open
    from mock import patch
except ImportError:
    from unittest.mock import mock_open
    from unittest.mock import patch

from yaml_rulz.cli import main
from yaml_rulz.errors import YAMLHandlerError


DUMMY_FILE_CONTENT = "dummy"
EMPTY_TABLE = """+----------+---------+--------+-----------+----------+-------+-----+
| Severity | Message | Schema | Criterion | Resource | Value | Ref |
+----------+---------+--------+-----------+----------+-------+-----+
+----------+---------+--------+-----------+----------+-------+-----+
"""
EMPTY_RAW = """[]
"""
TABLE_WITH_ISSUE = """+----------+-----------------------------------+---------------------+-----------+---------------\
------+-------+-----+
| Severity | Message                           | Schema              | Criterion | Resource            | Value | Ref |
+----------+-----------------------------------+---------------------+-----------+---------------------+-------+-----+
| Error    | Value must be less than criterion | root:less_than_rule | 1500      | root:less_than_rule | 1500  |     |
+----------+-----------------------------------+---------------------+-----------+---------------------+-------+-----+
"""
RAW_WITH_ISSUE = '[\n  {\n    "resource": "root:less_than_rule", \n    "severity": "Error", \n    "value": 1500, \n' \
                 '    "criterion": "1500", \n    "schema": "root:less_than_rule", \n    "message": "Value must be ' \
                 'less than criterion", \n    "ref": false\n  }\n]\n'
ISSUE = [
    {
        "criterion": "1500",
        "message": "Value must be less than criterion",
        "ref": False,
        "resource": "root:less_than_rule",
        "severity": "Error",
        "schema": "root:less_than_rule",
        "value": 1500,
    },
]


class ArgsNameSpace(object):

    schema = None
    resource = None
    exclusions = None
    raw = None

    def __init__(self, schema, resource, exclusions=None, raw=False):
        self.schema = schema
        self.resource = resource
        self.exclusions = exclusions
        self.raw = raw


class TestCLI(TestCase):
    # pylint: disable = no-member, too-many-instance-attributes

    def setUp(self):
        self.argparser_patcher = patch("yaml_rulz.cli.ArgumentParser")
        self.argparser_mock = self.argparser_patcher.start()
        self.validator_patcher = patch("yaml_rulz.cli.YAMLValidator")
        self.validator_mock = self.validator_patcher.start()
        self.stdout_patcher = patch("sys.stdout", new_callable=StringIO)
        self.stdout_mock = self.stdout_patcher.start()
        self.file_open_patcher = patch("yaml_rulz.cli.open", mock_open(read_data=DUMMY_FILE_CONTENT))
        self.file_open_mock = self.file_open_patcher.start()

    def tearDown(self):
        self.argparser_patcher.stop()
        self.validator_patcher.stop()
        self.stdout_patcher.stop()
        self.file_open_patcher.stop()

    def test_cli_prints_empty_table_when_no_issues(self):
        self.__setup_mocks(ArgsNameSpace("schema", "resource"), (False, []))
        main()
        self.assertEqual(EMPTY_TABLE, self.stdout_mock.getvalue())

    def test_cli_prints_raw_empty_list_when_no_issues(self):
        self.__setup_mocks(ArgsNameSpace("schema", "resource", None, True), (False, []))
        main()
        self.assertEqual(EMPTY_RAW, self.stdout_mock.getvalue())

    def test_cli_prints_issues_in_table(self):
        self.__setup_mocks(ArgsNameSpace("schema", "resource"), (True, ISSUE))
        self.assertRaises(SystemExit, main)
        self.assertEqual(TABLE_WITH_ISSUE, self.stdout_mock.getvalue())

    def test_cli_prints_issues_in_raw_format(self):
        self.__setup_mocks(ArgsNameSpace("schema", "resource", None, True), (True, ISSUE))
        self.assertRaises(SystemExit, main)
        self.assertEqual(
            sorted([line.strip(", ") for line in RAW_WITH_ISSUE.splitlines()]),
            sorted([line.strip(", ") for line in self.stdout_mock.getvalue().splitlines()])
        )

    def test_cli_handles_validator_exceptions(self):
        self.validator_mock.side_effect = YAMLHandlerError
        self.argparser_mock.return_value.parse_args.return_value = ArgsNameSpace("schema", "resource")
        self.assertRaises(SystemExit, main)
        self.assertFalse(self.validator_mock.return_value.get_validation_issues.called)

    def test_cli_handles_file_io_errors(self):
        self.file_open_mock.side_effect = IOError
        self.assertRaises(SystemExit, main)
        self.assertFalse(self.validator_mock.return_value.get_validation_issues.called)

    def __setup_mocks(self, args_ns, val_issues):
        self.argparser_mock.return_value.parse_args.return_value = args_ns
        self.validator_mock.return_value.get_validation_issues.return_value = val_issues
