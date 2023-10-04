#! /usr/bin/env python3

import unittest

from bratpy.util import suiteFactory, caseFactory

from bratpy.schema_data import recursive_all

from ._test_common import OBJECTS, OBJECTS_DIR, NORM, NORM_DIR, INVALID, \
    INVALID_DIR, COMPLEX, COMPLEX_DIR, PROGRAMS, PROGRAMS_DIR, \
    BRAT_SCHEMA_FILE, TEST_SCHEMA_FILE, \
    DEBUG

from ._node import Test_Node
from ._compound_literal import Test_CompoundLiteral
from ._parser_state import Test_ParserState

from ._normalizer import test_normalizer
from ._json_directory import test_json_dir
from ._brat_directory import test_brat_dir

'''   NOTE!!!   DEBUG is declared in _test_common.py '''


class Test_directories(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    # @unittest.skip("no")
    def test_objects(self):
        test_json_dir(self, OBJECTS, OBJECTS_DIR)

    @unittest.skip("no")
    def test_complex(self):
        test_json_dir(self, COMPLEX, COMPLEX_DIR)

    @unittest.skip("no")
    def test_programs(self):
        test_brat_dir(self, PROGRAMS, PROGRAMS_DIR)


if __name__ == '__main__':
    cases = suiteFactory(*caseFactory(scope=globals().copy()))
    runner = unittest.TextTestRunner(verbosity=4)
    runner.run(cases)
