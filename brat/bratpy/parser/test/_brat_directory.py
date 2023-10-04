import json

from bratpy.util import read_segmented_brat_dir

from bratpy import parser

from ._test_common import BratValidator, show_schema_errors_and_assert, \
    DEBUG


def test_brat_dir(self, _dir_name, d):
    print()
    for file_stem, program in read_segmented_brat_dir(d).items():

        is_strict = {'parse:strict': True,
                     'parse:normal': False}.get(program['mode'])
        if is_strict is None:
            raise ValueError(
                f"Bad parse mode '{program['mode']}' (expected 'parse:strict' or 'parse:normal')")

        print(f'\n- {_dir_name}.{file_stem} in {program["mode"]} mode')

        parse_input = program['parse_input']
        want_deparse_output = program['deparse_output']

        parsed_input = parser.parse(parse_input, roundtrip=is_strict)
        print(f" input: {repr(parse_input)}")

        deparsed_result = parser.deparse(parsed_input)

        print(f"actual: {repr(deparsed_result)}")
        print(f"expect: {repr(want_deparse_output)}")

        self.assertEqual(want_deparse_output, deparsed_result)
