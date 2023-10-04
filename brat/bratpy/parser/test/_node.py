import unittest

from bratpy.schema_data import Key

from bratpy.parser.objects.node import Node


class Test_Node(unittest.TestCase):
    def test_node_isinstance(self):
        node_a = Node.COMMENT
        node_b = Node.VIRTUAL_NODE

        self.assertTrue(Node.node_isinstance(node_a, node_b))

        node_a = Node.COMMENT
        node_b = Node.VIRTUAL_OBJECT_EXPRESSION

        self.assertFalse(Node.node_isinstance(node_a, node_b))

        node_a = Node.SEPARATOR
        node_b = Node.LITERAL

        self.assertFalse(Node.node_isinstance(node_a, node_b))

        node_a = Node.FUNCTION
        node_b = Node.VALUE_OF

        self.assertFalse(Node.node_isinstance(node_b, node_a))

    def test_node_issupernode(self):
        node_a = Node.COMMENT
        node_b = Node.VIRTUAL_NODE

        self.assertTrue(Node.node_issupernode(node_b, node_a))

        node_a = Node.COMMENT
        node_b = Node.VIRTUAL_OBJECT_EXPRESSION

        self.assertFalse(Node.node_issupernode(node_b, node_a))

        node_a = Node.SEPARATOR
        node_b = Node.LITERAL

        self.assertFalse(Node.node_issupernode(node_b, node_a))

        node_a = Node.FUNCTION
        node_b = Node.VALUE_OF

        self.assertFalse(Node.node_issupernode(node_b, node_a))

    def test_node_can_subform(self):
        for val in (
            ({Key.ID: Node.SEPARATOR}, False),
            ({Key.ID: Node.COMMENT}, False),
            ({Key.ID: Node.LITERAL, Key.VALUE: []}, True),
            ({Key.ID: Node.LITERAL, Key.VALUE: [], Key.KIND: 'deep_array'},
                True),
            ({Key.ID: Node.LITERAL, Key.VALUE: [], Key.KIND: 'assoc'}, True),
            ({Key.ID: Node.LITERAL, Key.VALUE: [], Key.KIND: 'deep_exprkey'},
                True),
            ({Key.ID: Node.MEMBER_ACCESS}, True),
            ({Key.ID: Node.ASSIGNMENT}, True),
            ({Key.ID: Node.FUNCTION}, True),
        ):
            (self.assertTrue if val[1] else self.assertFalse)(
                Node.can_subform(val[0]),
                f"failed with {val}"
            )
