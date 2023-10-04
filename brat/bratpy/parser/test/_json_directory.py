import json
from bratpy import parser


from bratpy.util import apply_variance_to_normal_objects

from ._test_common import TestFileValidator, BratValidator, \
    show_schema_errors_and_assert, \
    DEBUG


def run_json_assertions(
    self,
    name,
    trial,
    case,
    correct_output,
    is_strict_dp,
    normal_deparse_result=None,
    strict_deparse_result=None
):

    mode_string = 'Strict' if is_strict_dp else 'Normal'

    parsed_json, line, col = parser.parse(
        trial, roundtrip=is_strict_dp, _test=True, _debug=DEBUG
    )
    deparsed_brat = parser.deparse(parsed_json)

    show_schema_errors_and_assert(self, BratValidator, correct_output,
                                  'the correct output AST must follow the schema')

    print('\t\t\t- expected JSON parses to valid instance: ok')
    print('Parser said:', parsed_json)

    show_schema_errors_and_assert(self, BratValidator, parsed_json,
                                  f'actual AST from {mode_string} parsing must follow the schema')

    print('\t\t\t- actual Brat parses to valid schema instance: ok')

    # print(f'normal_deparse: {normal_deparse}')
    # print(f'computed_json: {computed_json}')
    json_same = correct_output == parsed_json
    print(f'\t\t\t- actual Brat correctly {mode_string} parses to JSON:',
          ('ok' if json_same else 'nope'))
    self.assertEqual(correct_output, parsed_json,
                     f'{name}\n\tactual {mode_string} parsed AST must be equal to the test AST\n\tin trial {repr(trial)}')
    source_position_ok = case['pos'] == [line, col]
    print(f'\t\t\t- {mode_string} parser keeps track of source position:',
          ('ok' if source_position_ok else 'nope'))
    self.assertEqual(case['pos'], [line, col],
                     f'{name}\n\tactual {mode_string} parser must keep track of the source position\n\tin trial {repr(trial)}')

    varied_parsed_json = None
    ''' to test source-level roundtripping (including whitespace) '''
    if is_strict_dp:

        strict_trial = strict_deparse_result \
            if strict_deparse_result is not None else trial

        print(
            '\t\t\tSTRICT deparser said:',
            f'{repr(deparsed_brat)}\n`{deparsed_brat}`'
        )

    else:
        ''' Normal mode just needs semantic equivalence'''

        print(
            f'\t\t\tNORMAL deparser said: {repr(deparsed_brat)}\n`{deparsed_brat}`')
        reparsed_brat_result, line, col = parser.parse(
            deparsed_brat, roundtrip=is_strict_dp, _test=True, _debug=DEBUG
        )
        varied_parsed_json = apply_variance_to_normal_objects(
            parsed_json, case.get('deparser_normal_variance')
        )

    if varied_parsed_json:
        brat_same = reparsed_brat_result == varied_parsed_json \
            or deparsed_brat == normal_deparse_result
        print(f'\t\t\t- actual {mode_string} parsed JSON correctly deparses to Brat:',
              ('ok' if brat_same else 'nope'))

        if reparsed_brat_result != varied_parsed_json and normal_deparse_result is not None:
            self.assertEqual(
                deparsed_brat, normal_deparse_result,
                f'{name}\n\tactual {mode_string} deparsed Brat must match the test Brat'
            )
        else:
            self.assertEqual(
                reparsed_brat_result, varied_parsed_json,
                f'{name}\n\tactual {mode_string} deparsed-parsed Brat must match the varianced test Brat'
            )
    else:
        brat_same = deparsed_brat == strict_trial
        print(f'\t\t\t- actual {mode_string} parsed JSON correctly deparses to Brat:',
              ('ok' if brat_same else 'nope')
              )
        self.assertEqual(strict_trial, deparsed_brat,
                         f'{name}\n\tactual {mode_string} deparsed Brat must match the test Brat')

    return json_same and brat_same


def test_json_dir(self, _dir_name, d):
    print()
    for file in sorted(d.glob('*.json')):
        with open(file) as fp:
            test_json = json.load(fp)

        print(f'\n- {_dir_name}.{file.stem}')
        show_schema_errors_and_assert(self, TestFileValidator, test_json,
                                      f'the test file {file} must follow the schema')

        for idx, case in enumerate(test_json):
            name = case['name']

            trial = case['trial']

            normal_parse = case['normal_parse']

            strict_parse = case.get('strict_parse', None)
            strict_deparse = case.get('strict_deparse_to', None)
            normal_deparse = case.get('normal_deparse_to', None)
            print(
                f"\n\t- {_dir_name}.{file.stem}  {idx+1}:  {name}"
                + ('\n\t\t-> must roundtrip!' if strict_parse is not None else '')
                + '\n'
            )
            print(f'\t- Trial: {repr(trial)}\n`{trial}`')
            if case.get('skip'):
                print('\t\t  Skipped!')
                continue

            print('\t\t- Normal parse mode')
            normal_parse_ok = run_json_assertions(
                self, name, trial, case,
                normal_parse, False,
                normal_deparse_result=normal_deparse
            )
            print('\t\t\b-> Normal mode ' "pass" if normal_parse_ok else "fail")

            if strict_parse:
                print('\t\t- Strict parse mode')
                strict_parse_ok = run_json_assertions(
                    self, name, trial, case,
                    normal_parse if strict_parse is True else strict_parse,
                    True,
                    normal_deparse_result=normal_deparse,
                    strict_deparse_result=strict_deparse
                )
                print('\t\t\b-> Strict mode ' "pass" if strict_parse_ok else "fail")

                print(
                    '\t\b-> ALL MODES ' 'pass' if normal_parse_ok and strict_parse_ok else 'fail')
            else:
                print('\t\b-> Normal-only ' 'pass' if normal_parse_ok else 'fail')
