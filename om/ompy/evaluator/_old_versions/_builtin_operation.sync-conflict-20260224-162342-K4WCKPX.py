def om_quote(elt, new_prog, _bindings):
    if len(new_prog) >= 1:
        return [{'id': 'operand', 'value': [new_prog[0]]}] + new_prog[1:]
    return new_prog + [elt]


def om_dequote(elt, new_prog, _bindings):
    if len(new_prog) >= 1:
        return (
            new_prog[0]['value']
            if isinstance(new_prog[0], dict)
            else new_prog[0]
            + new_prog[1:]
        )
    return new_prog + [elt]


def om_copy(elt, new_prog, _bindings):
    if len(new_prog) >= 1:
        return [new_prog[0], new_prog[0]] + new_prog[1:]
    return new_prog + [elt]


def om_define(elt, new_prog, bindings):
    from ._evaluator import _evaluate
    if len(new_prog) >= 2:
        # if these are not operands ...?
        let_block = new_prog[0]['value']
        in_block = new_prog[1]['value']
        print('in:', repr(in_block))
        # i have no idea what the reference implementation does for
        # define { {quoted} ... } ...
        assert let_block[0]['id'] == 'operator'
        binding = let_block[0]['value']
        # ditto for define { x y }
        assert let_block[1]['id'] == 'operand'
        bound_program = let_block[1]['value']
        new_bindings = bindings.copy()
        new_bindings[binding] = bound_program

        return [_evaluate(in_block, new_bindings)] + new_prog[2:]
    return new_prog + [elt]


def om_pullfront_characters(elt, new_prog, _bindings):
    if len(new_prog) >= 1:
        operand = new_prog[0]
        return (
            {'id': operand[0]['id'], 'value': [operand[0]['value'][0]]}
            + new_prog[1:]
        )
    return [elt] + new_prog


def make_py_builtin_operation(kv):
    return (kv[0], {
        'id': kv[1].__name__,
        'builtin': kv[1]
    })


operations = dict(map(
    make_py_builtin_operation,
    {
        'dequote': om_dequote,
        'quote': om_quote,
        'copy': om_copy,
        'define': om_define,
        '<-[characters]': om_pullfront_characters
    }.items()
))
