#!/usr/bin/env python3

import unittest
from pathlib import Path

from ompy.evaluator import evaluate
from ompy.parser import parse, parse_file, deparse
from ompy.test.util import read_segmented_om, suiteFactory, caseFactory


FILE_LOC = Path(__file__).resolve().parent
TESTS_DIR = FILE_LOC / 'programs'
FULL_DIR = TESTS_DIR / 'full'
OPERATORS_DIR = TESTS_DIR / 'operators'


class Test_MyTests(unittest.TestCase):

    def test_operators(self):
        print()
        for d in sorted(OPERATORS_DIR.iterdir()):
            if d.name not in ('quote', 'dequote'):
                continue
            print('-', d.stem)
            for file in sorted(d.glob('*.om')):
                oks = ('basic', 'partial')
                if not any(map(lambda x: x in file.stem, oks)):
                    continue

                with open(file) as fp:
                    test_src, expect_src = read_segmented_om(fp)
                print('  -', file.stem)
                print('    -> test  ', repr(test_src))
                print('    -> expect', repr(expect_src))

                test, expect = parse(test_src), parse(expect_src)

                result = evaluate(test)
                print(f"expect: {expect}")
                print(f"actual: {result}")
                self.assertEqual(expect, result,
                                 'result of evaluation should match the test')

                print('\t- Om evaluates correctly')
                deparse_result, deparse_expect = (deparse(result),
                                                  deparse(expect))

                self.assertEqual(deparse_expect, deparse_result,
                                 'the expected and result should deparse the same')
                print('\t- evaluation deparses correctly')

                self.assertEqual(expect_src, deparse_result,
                                 'the deparser result should match the expect text')

                print('\t- evaluation deparses as expected')
                print('\tpass')


if __name__ == '__main__':
    cases = suiteFactory(*caseFactory(scope=globals().copy()))
    runner = unittest.TextTestRunner(verbosity=4)
    runner.run(cases)
