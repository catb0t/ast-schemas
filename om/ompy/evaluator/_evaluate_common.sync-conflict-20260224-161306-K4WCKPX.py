from ompy.parser import node_is, Node


class _SkipEnd:
    def __init__(self):
        pass

    def __eq__(self, rhs):
        return self is rhs


SkipEnd = _SkipEnd()


def find_next_node(form, node_like):
    for idx, elt in enumerate(form):
        if node_is(elt, node_like):
            return form[idx:], idx
    return None, -1


def filter_operands(form):
    result = []
    for node in form:
        if node_is(node, Node.OPERAND):
            result.append(node)
    return result
