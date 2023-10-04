import pprint
import inspect
import unittest
import re

import jsonschema

from ..schema_data import linear_selection_by


def pprint_jscexc(ex):
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


def validate(schema, instance):
    try:
        jsonschema.validate(schema=schema, instance=instance)
        return True
    except jsonschema.exceptions.ValidationError as ex:
        print("bad INSTANCE")
        pprint_jscexc(ex)
        return False
    except jsonschema.exceptions.SchemaError as ex:
        print("bad SCHEMA")
        pprint_jscexc(ex)
        return False


def read_segmented_brat(fp):
    c = fp.read()
    assert c.count('==========') == 2
    return c.split('\n==========\n')


def read_segmented_brat_dir(tests_dir):
    programs = dict()
    for f in sorted(tests_dir.glob('*.brat')):
        with open(f) as fp:
            mode, input, output = read_segmented_brat(fp)
            programs[f.stem] = {"path": f,
                                "mode": mode,
                                "parse_input": input,
                                "deparse_output": output}
    return programs


def all_eq(self, msg, rest):
    import itertools
    for comb in itertools.combinations(rest, 2):
        self.assertEqual(comb[0], comb[1])
    return True


def apply_variance_to_normal_objects(objs, variance):
    if not variance:
        return objs
    delete = variance.get('__delete')
    if delete:
        del variance['__delete']
    varied_objs = []
    for obj in objs:
        if delete:
            varied = linear_selection_by(obj, lambda a: a[0] not in delete)
        else:
            varied = obj.copy()
        varied.update(variance)
        varied_objs.append(varied)

    return varied_objs


def _sourceFinder(f):
    return inspect.findsource(f)[1]


def suiteFactory(
        *testcases,
        testSorter=None,
        suiteMaker=unittest.makeSuite,
        newTestSuite=unittest.TestSuite):
    """
    make a test suite from test cases, or generate test suites from test cases.
    *testcases     = TestCase subclasses to work on
    testSorter     = sort tests using this function over sorting by line number
    suiteMaker     = should quack like unittest.makeSuite.
    newTestSuite   = should quack like unittest.TestSuite.
    """

    if testSorter is None:
        def ln(tc, f): return getattr(tc, f).__code__.co_firstlineno
        def testSorter(tc, a, b): return ln(tc, a) - ln(tc, b)

    test_suite = newTestSuite()
    for tc in testcases:
        test_suite.addTest(
            suiteMaker(
                tc,
                sortUsing=lambda a, b, case=tc: testSorter(case, a, b)
            )
        )

    return test_suite


def caseFactory(
        scope=globals().copy(),
        caseSorter=_sourceFinder,
        caseSuperCls=unittest.TestCase,
        caseMatches=re.compile("^Test_")):
    """
    get TestCase-y subclasses from frame "scope", filtering name and attribs
    scope        = iterable to use for a frame; preferably a hashable (dictionary).
    caseMatches  = regex to match function names against; blank matches every TestCase subclass
    caseSuperCls = superclass of test cases; unittest.TestCase by default
    caseSorter   = sort test cases using this function over sorting by line number
    """

    # note that 'name' is the string key of the object in the dictionary
    return sorted(
        [
            scope[name]
            for name in scope
            if re.match(caseMatches, name) and inspect.isclass(scope[name])
            and issubclass(
                scope[name],
                caseSuperCls
            )
        ],
        key=caseSorter
    )
