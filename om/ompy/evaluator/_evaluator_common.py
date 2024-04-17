from ompy.parser import node_is


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
