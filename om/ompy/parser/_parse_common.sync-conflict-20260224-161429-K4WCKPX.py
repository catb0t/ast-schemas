from enum import Enum

# our separators. please no changey order
SEP_STR = ' \n\t'


class _DoNotSkip:
    def __init__(self):
        pass

    def __lt__(self, rhs):
        return False

    def __gt__(self, rhs):
        return False

    def __eq__(self, rhs):
        return self is rhs


DoNotSkip = _DoNotSkip()


def check_skip(val):
    if val is DoNotSkip or isinstance(val, _DoNotSkip):
        raise ValueError(
            'OOPS! real value for `skip_to_idx` required in this context'
            '\n\t(instead, it was a singleton NaN)\n\tparser bug found!'
        )
    return val


class _NoLastID:
    def __init__(self):
        pass

    def __eq__(self, rhs):
        return self is rhs


NoLastID = _NoLastID


class Form(Enum):
    OPEN  = 0
    CLOSE = 1


FORM_CHARS = {
    Form.OPEN: '{',
    Form.CLOSE: '}'
}

CHARS_TO_FORMS = {
    '{': Form.OPEN,
    '}': Form.CLOSE
}


def _ch_is(ch, base):
    if not isinstance(base, Form):
        raise ValueError(base)
    return ch == FORM_CHARS[base]


def _form_to_ch(base):
    if not isinstance(base, Form):
        raise ValueError(base)
    return FORM_CHARS[base]


def _form_from_ch(ch):
    if not isinstance(ch, str):
        raise ValueError(ch)
    return CHARS_TO_FORMS[ch]


# characters that are not an operator alone
NOT_OP = (_form_to_ch(Form.OPEN), _form_to_ch(Form.CLOSE), *SEP_STR)


class Node(Enum):
    SEPARATOR = 0
    OPERATOR  = 1
    OPERAND  = 2


NODE_IDS = {
    Node.SEPARATOR: 'separator',
    Node.OPERATOR: 'operator',
    Node.OPERAND: 'operand'
}

IDS_TO_NODES = {
    'separator': Node.SEPARATOR,
    'operator': Node.OPERATOR,
    'operand': Node.OPERAND
}


def _node_is(node, base):
    if not isinstance(base, Node) or \
            base is NoLastID or isinstance(base, _NoLastID):
        raise ValueError(base)
    if isinstance(node, dict):
        return node['id'] == NODE_IDS[base]
    if isinstance(node, str):
        return node == NODE_IDS[base]
    if isinstance(node, Node):
        return node == base
    if node is NoLastID or isinstance(node, _NoLastID):
        return False
    if node is None:
        raise DeprecationWarning(
            'use of None in place of NoLastID (valve, pls fix)')
    raise ValueError(node)


def _nodes_are(nodes, base):
    return all(map(lambda n: _node_is(n, base), nodes))


def _node_is_any(node, bases):
    return any(map(lambda b: _node_is(node, b), bases))


def _node_to_id(base):
    if not isinstance(base, Node):
        raise ValueError(base)
    return NODE_IDS[base]


def _node_from_id(nid):
    if not isinstance(nid, str):
        raise ValueError(nid)
    return IDS_TO_NODES[nid]


def _create_node(nid, value):
    return {'id': NODE_IDS[nid], 'value': value}
