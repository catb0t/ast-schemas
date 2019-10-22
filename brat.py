#! /usr/bin/env python3
import json
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


def main():
    schema_file = "brat.schema.json"
    instance_file = "brat_test.json"  # "brat_test.json"
    with open(schema_file, "r") as fp:
        schema = json.load(fp)
    with open(instance_file, "r") as fp:
        instance = json.load(fp)

    try:
        jsonschema.validate(schema=schema, instance=instance)
    except jsonschema.exceptions.ValidationError as ex:
        print("bad INSTANCE")
        pprint_jscexc(ex)

    except jsonschema.exceptions.SchemaError as ex:
        print("bad SCHEMA")
        pprint_jscexc(ex)


if __name__ == '__main__':
    main()
