import json

from bratpy import parser
from bratpy.parser import ParseError
from ._test_common import TestFileValidator, INVALID_DIR, \
    DEBUG


def test_invalid(self):
    print()
    for file in sorted(INVALID_DIR.glob('*.json')):
        print(file)
        with open(file.with_suffix('.json')) as fp:
            test_json = json.load(fp)

        print('-', file.stem)
        self.assertTrue(TestFileValidator.is_valid(test_json),
                        f'the test file {file} must follow the schema')

        for case in test_json:

            trial = case['trial']
            expect_vals = case['normal_deparse']

            with self.assertRaises(ParseError) as cm:
                parser.parse(trial, _debug=DEBUG)

            exc = cm.exception
            self.assertEqual(
                [exc.node_type.value, exc.reason.value, exc.pos1, exc.pos2],
                expect_vals
            )
            print('-', file.stem)
            print('\t- Test has parse error: ok')
            print('\t- ParseError is thrown: ok')
            print('\t- Correct type of parse error: ok')
            print('\t- Line number is correct: ok')
            print('\t- Column number is correct: ok')
            print('\tpass')
