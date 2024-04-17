def deepen(val):
    print("deepen", val)
    if isinstance(val, list):
        return [*list(map(CompoundLiteral.deepen, val))]
    elif isinstance(val, dict) and Node.node_is(val, Node.LITERAL):
        return [*CompoundLiteral.deepen(val[Key.VALUE])]
    elif isinstance(val, dict):
        return []
    else:
        return [val]


def make_deep(initial_kind, basic_literal):
    if not len(basic_literal):
        return initial_kind, basic_literal

    rec_key = Key.VALUE

    def rec_key_func(v):
        return isinstance(v, list)

    def cond(_, val):
        return isinstance(val, dict) \
            and Node.node_is(val, Node.LITERAL)

    if recursive_all(basic_literal, rec_key, rec_key_func, cond):
        literal = copy.deepcopy(basic_literal)
        literal = CompoundLiteral.deepen(literal)
        return MAKE_DEEP_KIND_CONV.get(initial_kind), literal

    return initial_kind, basic_literal


def replace_deep_iterable(val):
    value = val.get(Key.VALUE)
    if isinstance(value, list):
        return " ".join(map(str, value))
    elif isinstance(value, dict) and Node.node_is(value, Node.LITERAL):
        return " ".join(f"{k}: {v}" for k, v in value.items())
    else:
        raise ValueError(value)
