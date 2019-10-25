#! /usr/bin/env python3
import json
import sys
import pprint
import jsonschema


def pprint_jscexc (ex):
    pprint.pprint({
        "message": ex.message,
        "schema": ex.schema,
        "instance": ex.instance,
        "context": ex.context,
        "cause": ex.cause,
        "validator": ex.validator,
        "validator_value": ex.validator_value,
        "relative_schema_path": ex.relative_schema_path,
        "absolute_schema_path": ex.absolute_schema_path,
        "relative_path": ex.relative_path,
        "absolute_path": ex.absolute_path,
    })


def must_fails(schema):  # noqa
    must_fail_file = "brat_must_fail.json"
    with open(must_fail_file) as fp:
        must_fail = json.load(fp)
    count_progs = 0
    count_failed = 0
    for node in must_fail:
        if isinstance(node, list):
            count_progs += 1
            for prog in node:
                try:
                    jsonschema.validate(instance=prog, schema=schema)
                    print("\tFAIL", prog)
                    count_failed += 1
                except jsonschema.exceptions.ValidationError:
                    print("\tPASS")
        elif isinstance(node, dict) and node["_comment"]:
            print(node["_note"])
        else:
            raise ValueError(node)
    print(f"1 + {count_progs} tests, {count_failed} failures")


def main():
    schema_file = "brat.schema.json"
    good_instance_file = "brat_test.json"
    with open(schema_file, "r") as fp:
        schema = json.load(fp)
    with open(good_instance_file, "r") as fp:
        instance = json.load(fp)

    try:
        jsonschema.validate(schema=schema, instance=instance)
    except jsonschema.exceptions.ValidationError as ex:
        print("bad INSTANCE")
        pprint_jscexc(ex)
        sys.exit(2)
    except jsonschema.exceptions.SchemaError as ex:
        print("bad SCHEMA")
        pprint_jscexc(ex)
        sys.exit(2)

    must_fails(schema)


if __name__ == '__main__':
    main()
