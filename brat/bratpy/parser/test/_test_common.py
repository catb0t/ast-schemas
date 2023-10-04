import json
from pathlib import Path

from jsonschema import Draft7Validator

from bratpy.parser import BratValidator
from bratpy.schema_data import BRAT_SCHEMA_FILE, BRAT_SCHEMA

DEBUG = True

FILE_LOC = Path(__file__).resolve().parent
TESTS_DIR = FILE_LOC / 'test_data'
OBJECTS = 'objects'
COMPLEX = 'complex'
NORM = 'normalizer'
INVALID = 'invalid'
PROGRAMS = 'programs'
OBJECTS_DIR = TESTS_DIR / OBJECTS
COMPLEX_DIR = TESTS_DIR / COMPLEX
NORM_DIR = TESTS_DIR / NORM
INVALID_DIR = TESTS_DIR / INVALID
PROGRAMS_DIR = TESTS_DIR / PROGRAMS
# BRAT_SCHEMA_FILE = FILE_LOC / '..' / '..' / '..' / 'brat.schema.json'
TEST_SCHEMA_FILE = FILE_LOC / 'parser_test.schema.json'


with open(TEST_SCHEMA_FILE) as tfp:
    TEST_SCHEMA = json.load(tfp)


Draft7Validator.check_schema(TEST_SCHEMA)
TestFileValidator = Draft7Validator(TEST_SCHEMA)


def show_schema_errors_and_assert(self, v, i, assert_message):
    if not v.is_valid(i):
        print("\t\t\t- Schema errors follow...\n")
    for e in v.iter_errors(i):
        print(e)

    self.assertTrue(v.is_valid(i), assert_message)
