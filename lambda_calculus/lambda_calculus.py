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
    must_fail_file = "lambda_calculus_must_fail.json"
    with open(must_fail_file) as fp:
        must_fail = json.load(fp)
    count_progs = 0
    count_failed = 0
    for node in must_fail:
        count_progs += 1
        for prog in node:
            try:
                jsonschema.validate(instance=prog, schema=schema)
                print("\tFAIL", prog)
                count_failed += 1
            except jsonschema.exceptions.ValidationError:
                print("\tPASS")
    print(f"1 + {count_progs} tests, {count_failed} failures")


def dict_update (d, u):
    _d = d.copy()
    _d.update(u)
    return _d


def err (*a):
    raise Exception(*a)


def apply_lambda (lam, p, b):
    b = dict_update(b, lam[1])
    lam = lam[0]
    print("apply:", repr(lam), p, b )
    if isinstance(lam, str):
        return b[lam]


def apply_expr (e, b):
    return {
        str:  lambda: (b[e], b),
        dict: lambda: (e["."], dict_update(b, {e["λ"]: e["."]})),
        list: lambda: (apply_lambda(apply_expr(e[0], b)(), e[1:], b), b)
    }.get(type(e), lambda: err(type(e), e, b))


def run_test (prog):
    for expr in prog:
        print("expr", expr)
        bindings = {}
        e1, bindings = apply_expr(expr, bindings)()
        print(e1)
        print(bindings)
        # do = {
        #     str: lambda s: s in bindings,
        #     dict: lambda n, b: bindings.update({n: None})
        # }.get(type(expr), None)
        # print(expr)
        # print(do)
        # print(bindings)


def main():
    schema_file = "lambda_calculus.schema.json"
    good_instance_file = "lambda_calculus_test.json"
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

    run_test(instance)
    # must_fails(schema)


if __name__ == '__main__':
    main()
