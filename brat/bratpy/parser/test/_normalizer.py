import json
import bratpy.parser as parser

from bratpy.util import read_segmented_brat, all_eq

from ._test_common import BratValidator, NORM_DIR, \
    DEBUG


def test_normalizer(self):
    print()
    for file in sorted(NORM_DIR.glob('*.json')):
        print(file)
        with open(file.with_suffix('.brat')) as fp:
            fact_brat = read_segmented_brat(fp)
        with open(file) as fp:
            fact_json = json.load(fp)

        # print(brat_src)
        ok = True

        filter_fact_json = parser.filter_separators(fact_json)
        reparse_strip_fact_json = parser.parse(parser.deparse(fact_json),
                                               strip=True, _debug=DEBUG)

        all_eq(
            self,
            'test JSON should already be optimal (filtered/reparsed/stripped)',  # noqa
            [fact_json, filter_fact_json, reparse_strip_fact_json]
        )

        del filter_fact_json, reparse_strip_fact_json

        parsed_fact_om_big, parsed_fact_om_optimal = map(parser.parse, fact_brat)  # noqa

        stripped_fact_brat, stripped_fact_om_optimal = map(
            lambda x: parser.parse(x, strip=True, _debug=DEBUG),
            fact_brat
        )

        filtered_stripped_fact_brat = parser.filter_separators(stripped_fact_brat)  # noqa
        filtered_fact_om_big = parser.filter_separators(parsed_fact_om_big)

        all_eq(
            self,
            'parse(strip=True) should match the test data/idempotent on optimal',  # noqa
            [parsed_fact_om_optimal, stripped_fact_brat,
             stripped_fact_om_optimal, filtered_stripped_fact_brat, filtered_fact_om_big]  # noqa

        )

        deparsed_fact_json = parser.deparse(fact_json)
        # print(parser.deparse(parsed_fact_om_optimal))
        # print()
        # print(parser.deparse(parser.parse(deparsed_fact_json)))
        self.assertEqual(
            parsed_fact_om_optimal,
            parser.parse(deparsed_fact_json, _debug=DEBUG),
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
            instance_ok = BratValidator.is_valid(instance)
            self.assertTrue(instance_ok, 'all ASTs must follow the schema')
            ok = ok and instance_ok

        print('-', file.stem)
        print('\t- JSON parses to valid instance: ok')
        print('\t- Brat parses to valid instance: ok')
        print('\t- Brat correctly parses to JSON: ok')
        print('\t- parsed JSON correctly deparses to Brat: ok')
        print('\t' 'pass' if ok else 'fail')
