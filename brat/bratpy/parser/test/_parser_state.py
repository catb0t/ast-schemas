import unittest

from bratpy.parser import ParserState


class Test_ParserState(unittest.TestCase):
    def test_state_change(self):
        s = ParserState('#')
        s.set_idx(2)
        self.assertEqual(s.idx(), 2)
        s.inc_idx()
        self.assertEqual(s.idx(), 3)
