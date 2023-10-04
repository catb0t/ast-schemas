import unittest

from bratpy.schema_data import Key, recursive_all
from bratpy.parser.objects import Node


class Test_CompoundLiteral(unittest.TestCase):
    def test_recursive_all(self):
        obj = {
            'id': 'literal',
            'value': [{
                'id': 'literal',
                'value': [{
                    'id': 'literal',
                    'value': [{
                        'id': 'literal',
                        'value': 5
                    }]
                }]
            }]
        }
        rec_key = Key.VALUE

        def rec_key_func(v):
            return isinstance(v, list)

        def cond(_, val):
            return isinstance(val, dict) \
                and Node.node_is(val.get(Key.ID), Node.LITERAL)

        self.assertTrue(
            recursive_all(obj, rec_key, rec_key_func, cond)
        )

        obj1 = {
            'id': 'literal',
            'value': [{
                'id': 'literal',
                'value': [{
                    'id': 'separator',
                    'value': [{
                        'id': 'separator',
                        'value': 0
                    }, {
                        'id': 'literal',
                        'value': 5
                    }]
                }]
            }]
        }

        self.assertFalse(
            recursive_all(obj1, rec_key, rec_key_func, cond)
        )
