import unittest

from bratpy.parser.objects.node import Node

from bratpy.util import Key


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
            ({Key.ID: Node.COMMENT}, '*', False),
            (Node.LITERAL, '*', False),
            (Node.LITERAL, 'array', False),
            (Node.LITERAL, 'assoc', True),
            (Node.LITERAL, 'deep_exprkey', True),
            (Node.LITERAL, 'deep_array', True),
            (Node.MEMBER_ACCESS, '*', True),
            (Node.ASSIGNMENT, '*', True),
            (Node.FUNCTION, '*', True),
        ):
            (self.assertTrue if val[2] else self.assertFalse)(
                Node.can_subform(
                    {
                        Key.ID: Node.to_id(val[0]),
                        Key.KIND: val[1],
                        Key.VALUE: []
                    }
                ),
                f"failed with {val}"
            )
