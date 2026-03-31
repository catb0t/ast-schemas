#! /usr/bin/env python3
import json
import unittest
from pprint import pprint

from jsonschema import Draft7Validator
import ompy.parser as parser
from ompy.parser import ParseError
from ompy.test.util import read_segmented_om, all_eq, suiteFactory, \
    caseFactory

from ._test_common import STATIC_DIR, NORM_DIR, ILLFORMED_DIR, OM_SCHEMA_FILE

with open(OM_SCHEMA_FILE) as sfp:
    OM_SCHEMA = json.load(sfp)
Draft7Validator.check_schema(OM_SCHEMA)
OmValidator = Draft7Validator(OM_SCHEMA)


class Test_MyTests(unittest.TestCase):
    def test_static(self):
        print()
        for file in sorted(STATIC_DIR.glob('*.json')):
            with open(file.with_suffix('.om')) as fp:
                original_om = fp.read().rstrip('\r\n')
            with open(file) as fp:
                test_json = json.load(fp)

            computed_json = parser.parse(original_om)
            computed_om = parser.deparse(computed_json)

            self.assertTrue(OmValidator.is_valid(test_json),
                            'the test AST must follow the schema')
            self.assertTrue(OmValidator.is_valid(computed_json),
                            'the AST from parsing must follow the schema')
            json_same = computed_json == test_json
            self.assertEqual(computed_json, test_json,
                             'the parsed AST should be equal to the test AST')

            om_same = computed_om == original_om
            self.assertEqual(computed_om, original_om,
                             'the deparsed Om should match the test Om')
            ok = json_same and om_same
            print('-', file.stem)
            print('\t- JSON parses to valid instance: ok')
            print('\t- Om parses to valid instance: ok')
            print('\t- Om correctly parses to JSON:', ('ok' if json_same else 'nope'))
            print('\t- parsed JSON correctly deparses to Om:', ('ok' if om_same else 'nope'))
            print('\t' 'pass' if ok else 'fail')

    def test_normalized(self):
        print()
        for file in sorted(NORM_DIR.glob('*.json')):
            print(file)
            with open(file.with_suffix('.om')) as fp:
                fact_om = read_segmented_om(fp)
            with open(file) as fp:
                fact_json = json.load(fp)

            # print(om_src)
            ok = True

            filter_fact_json = parser.filter_separators(fact_json)
            reparse_strip_fact_json = parser.parse(parser.deparse(fact_json),
                                                   strip=True)

            all_eq(
                self,
                'test JSON should already be optimal (filtered/reparsed/stripped)',  # noqa
                [fact_json, filter_fact_json, reparse_strip_fact_json]
            )

            del filter_fact_json, reparse_strip_fact_json

            parsed_fact_om_big, parsed_fact_om_optimal = map(parser.parse, fact_om)  # noqa

            stripped_fact_om, stripped_fact_om_optimal = map(
                lambda x: parser.parse(x, strip=True),
                fact_om
            )

            filtered_stripped_fact_om = parser.filter_separators(stripped_fact_om)  # noqa
            filtered_fact_om_big = parser.filter_separators(parsed_fact_om_big)

            all_eq(
                self,
                'parse(strip=True) should match the test data/idempotent on optimal',  # noqa
                [parsed_fact_om_optimal, stripped_fact_om,
                 stripped_fact_om_optimal, filtered_stripped_fact_om, filtered_fact_om_big]  # noqa

            )

            deparsed_fact_json = parser.deparse(fact_json)
            # print(parser.deparse(parsed_fact_om_optimal))
            # print()
            # print(parser.deparse(parser.parse(deparsed_fact_json)))
            self.assertEqual(
                parsed_fact_om_optimal,
                parser.parse(deparsed_fact_json),
                'deparsing optimal JSON should result in no unecessary whitespace'  # noqa
            )

            reparsed_fact_json = parser.parse(deparsed_fact_json)
            self.assertEqual(
                fact_json,
                reparsed_fact_json,
                're-parsing the deparsed optimal JSON should be lossless'
            )

            for instance in (fact_json, parsed_fact_om_big, parsed_fact_om_optimal,  # noqa
                             reparsed_fact_json):
                instance_ok = OmValidator.is_valid(instance)
                self.assertTrue(instance_ok, 'all ASTs must follow the schema')
                ok = ok and instance_ok

            print('-', file.stem)
            print('\t- JSON parses to valid instance: ok')
            print('\t- Om parses to valid instance: ok')
            print('\t- Om correctly parses to JSON: ok')
            print('\t- parsed JSON correctly deparses to Om: ok')
            print('\t' 'pass' if ok else 'fail')

    def test_illformed(self):
        print()
        for file in sorted(ILLFORMED_DIR.glob('*.om')):
            print(file)
            with open(file.with_suffix('.om')) as fp:
                om_src, expected = read_segmented_om(fp)

            with self.assertRaises(ParseError) as cm:
                parser.parse(om_src)

            exc = cm.exception
            expect_vals = list(map(int, expected.split('\n')))
            self.assertEqual(
                [exc.reason.value, exc.line, exc.col],
                expect_vals
            )
            print('-', file.stem)
            print('\t- File has parse error: ok')
            print('\t- ParseError is thrown: ok')
            print('\t- Correct type of parse error: ok')
            print('\t- Line number is correct: ok')
            print('\t- Column number is correct: ok')
            print('\tpass')


if __name__ == '__main__':
    cases = suiteFactory( *caseFactory( scope=globals().copy() ) )
    runner = unittest.TextTestRunner(verbosity=4)
    runner.run(cases)
