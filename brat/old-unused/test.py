#! /usr/bin/env python3
import json
import pprint
import sys
import jsonschema
from jsonschema import exceptions as jsonschema_exceptions
import brat


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


def run_instance(instance):
    print(brat.nodes_values(instance))


def negative_test(schema, instance):  # noqa
    count_progs = 0
    count_failed = 0
    count_missed = 0
    for node in instance:
        if isinstance(node, list):
            for prog in node:
                count_progs += 1
                print("  Must Fail:", prog)
                try:
                    jsonschema.validate(instance=prog, schema=schema)
                    count_failed += 1
                except jsonschema_exceptions.ValidationError:
                    print("\tDid Not Fail!")
                    count_missed += 1
        elif (isinstance(node,
              dict) and "_comment" in node and node["_comment"]):
            print("\n" + node["_note"] + ":\n")
        else:
            raise ValueError(node)
    print(f"1 + {count_progs} tests, {count_failed} correct failures, \
          {count_missed} missed failures")


def positive_test(schema, instance):
    try:
        jsonschema.validate(schema=schema, instance=instance)
    except jsonschema_exceptions.ValidationError as ex:
        print("bad INSTANCE")
        pprint_jscexc(ex)
        sys.exit(2)
    except jsonschema_exceptions.SchemaError as ex:
        print("bad SCHEMA")
        pprint_jscexc(ex)
        sys.exit(2)


def main():
    # schema_file = "brat.schema.json"
    # with open(schema_file, "r") as fp:
    #     schema = json.load(fp)

    # good_instance_file = "tests/test.json"
    # with open(good_instance_file, "r") as fp:
    #     good_instance = json.load(fp)

    # positive_test(schema, good_instance)

    # bad_instance_file = "tests/invalid_instances.json"
    # with open(bad_instance_file) as fp:
    #     bad_instance = json.load(fp)

    # negative_test(schema, bad_instance)

    with open("programs/" + sys.argv[1] + ".json") as fp:
        prog = json.load(fp)
    run_instance(prog)


if __name__ == '__main__':
    main()
