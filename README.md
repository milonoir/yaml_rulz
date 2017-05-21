YAML Rulz!
==========

A YAML validator written in Python.

[![][travis img]][travis]
[![][codecov img]][codecov]

Check the validity of your yaml files in three steps:

1. Create new yaml schema files or turn your yaml files into schemas by using simple rules without
breaking the original structure.
2. Optionally, exclude certain keys or subsections from validation.
3. Run the validator.


Terminology
-----------

- Key: In a yaml structure a key identifies a node (or leaf) in the tree structure.
- Value: The data stored in yaml keys.
- List items: Denoted by a hyphen (`-`) it can be a set of single values without keys or subsections (subtrees).
- Rules: Special string values parsed by the validator.
- Schema: A special yaml file where the values are rules.
- Resource: A common yaml file whose validity is checked by the validator.
- Exclusions: List of keys or subsections in the resource whose validity will not be checked.
- Prototypes: List items in schemas; resource list items should match one of these.


Rules
-----

A rule consists of a __token__ and a __criterion__. See tokens in the _Rulebook_ section. For example:

`~ ETC/Utc` where the tilde (`~`) character is a known __token__ and the string `ETC/Utc` is a valid __criterion__ for
that rule.

Rules can be chained together by using the pipe (`|`) separator character:

`> 24 | ! .*:vlan_tag` which checks if the given number is greater than 24 and also validates uniqueness. Note that the
colon character (`:`) is the default separator in the yaml handlers.


Rulebook
--------

List of rules:

- __Omission__ (`*`): This rule always evaluates to `True`. If no rule is given then validator defaults to this rule.
- __Boolean__ (`?`): Use this rule for validating boolean values. Criterion can be any of `true`, `yes`, `on` and
`false`, `no`, `off` for `True` and `False` values respectively. The evaluation of the criterion is case insensitive.
- __Greater/Less than__ (`>` / `<`): Both the criterion and resource data will be evaluated and compared. Only numbers
or mathematical expressions can be used. The evaluated criterion is always exclusive.
- __RegExp__ (`~`): Validates against a regular expression. Note that backslash (`\`) is an escape character in yaml
files so it must be always doubled.
- __Pre-defined RegExp__ (`@`): Validates against a common pre-defined regular expression, e.g.: IPv4, IPv6, etc.
- __Uniqueness__ (`!`): This one is different from the others above. The criterion here is always a regular expression
which should match multiple keys in the resource. Their values are collected and each of them must be unique in the
collection.


Cross reference
---------------

__Boolean__ and __Greater/Less than__ rules are able to use other resource keys' values as criteria. If the original
criterion is a regular expression that matches to one or more keys in the resource then validation will be performed
by using their values as criteria (just like how __Uniqueness__ works). The validation stops at the first failure.


Exclusions
----------

It is possible that there are minor deviations between resources for a given schema. In this case certain subsections
might fail in the validation. The validator, however, can be configured not to fail. Validation issues for keys or
subsections matching to regular expressions listed in a so-called __exclusions file__ will count as warnings instead
of errors. The validator returns with exit code 0 if there were only warnings.

Consider the following schema:

```yaml
---
base:
 section_a:
   name: "* name of section A"
   location: "* location of section A"
 section_b:
   name: "* name of section B"
   location: "* location of section B"
```

For example one of your resources lacks `section_b` for some reason. Since the schema contains it the validator
would think that it is missing. To prevent this validation error you have to pass an exclusion file to the validator
in which you put a regular expression matching `section_b`:

```
base:section_b
```

Let's say that one of your resources have both sections, but lacks all `location` keys. Your exclusion file should
look like this:

```
base:section.*:location
```

Note that the colon character (`:`) is the default separator in the yaml handlers.


List validation
---------------

List types are handled differently. Each list item in the schema will be a __prototype__ item of that list it
belongs to. A prototype is also a bunch of key-value pairs, thus the values contain rules. When the validator
encounters the same list in the resource it tries to find a matching prototype. First it looks if there is a prototype
with the same key set, then rule validation follows. The order or list item validation might be different each time.


Output
------

There are two types of representation available for displaying validation results. Default is printing a table to
stdout:

```
+----------+-----------------------------------+---------------------+-----------+---------------------+-------+-----+
| Severity | Message                           | Schema              | Criterion | Resource            | Value | Ref |
+----------+-----------------------------------+---------------------+-----------+---------------------+-------+-----+
| Error    | Value must be less than criterion | root:less_than_rule | 1500      | root:less_than_rule | 1500  |     |
+----------+-----------------------------------+---------------------+-----------+---------------------+-------+-----+
```

If `raw` flag is set, then results are printed to stdout in JSON format:

```javascript
[
  {
    'criterion': '1500',
    'message': 'Value must be less than criterion',
    'ref': false,
    'resource': 'root:less_than_rule',
    'severity': 'Error',
    'schema': 'root:less_than_rule',
    'value': 1500
  }
]
```

Explanation:

- __Severity__: `Error` or `Warning` depending on whether resource key is excluded or not. Validator returns with exit
code 1 if there is at least one issue with `Error` severity.
- __Message__: Textual explanation of the issue.
- __Schema__: Key in the schema file.
- __Criterion__: Validation was performed against this value.
- __Resource__: Key in the resource file.
- __Value__: Value for the resource key.
- __Ref__: If there is an asterisk (`*`) here, then criterion is taken from a cross referenced resource key and
`Schema` field indicates which.


License
-------
YAML Rulz! is made available under the [MIT License].


Credits
-------
YAML Rulz! is written and managed by Milan Boleradszki.


[travis]:https://travis-ci.org/milonoir/yaml_rulz
[travis img]:https://api.travis-ci.org/milonoir/yaml_rulz.svg?branch=master
[codecov img]:https://codecov.io/github/milonoir/yaml_rulz/coverage.svg?branch=master
[codecov]:https://codecov.io/github/milonoir/yaml_rulz?branch=master
[MIT License]:http://www.opensource.org/licenses/mit-license.php
