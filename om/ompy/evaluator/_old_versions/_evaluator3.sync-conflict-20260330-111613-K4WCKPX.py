def see_reversed(l):
    return list(reversed(l))


def transform_operator(elt, new_prog, bindings):
    print('operator:', elt)
    if elt['value'] in bindings:
        op = bindings[elt['value']]
        if op.get('builtin', False):
            return op['builtin'](elt, new_prog, bindings)
        raise NotImplementedError
        # return reversed(transform1(reversed(prog), up_bindings=bindings))

    return new_prog + [elt]


def transform_operand(elt, bindings):
    return see_reversed(transform1(see_reversed(elt['value']),
                                   up_bindings=bindings))


def transform1(prog, up_bindings=None):
    # don't give a reference to sub-scopes
    local_bindings = dict()
    if up_bindings is not None:
        local_bindings.update(up_bindings)
    new_prog = []
    print()
    print('doing prog:', prog)
    for elt in prog:
        print(f"\telt: {elt}\n\tcurrent prog: {new_prog}\n")
        if elt['id'] == 'operator':
            new_prog = transform_operator(elt, new_prog, local_bindings)
        elif elt['id'] == 'separator':
            new_prog.append(elt)
        else:
            new_prog.append({
                'id': 'operand',
                'value': transform_operand(elt, local_bindings)
            })
    print('returning prog:', new_prog)
    return new_prog


def _evaluate(prog, up_bindings=None):
    from ._builtin_operation import operations
    from ompy.parser import filter_separators

    bindings = dict()
    bindings.update(operations)
    if up_bindings is not None:
        bindings.update(up_bindings)

    return see_reversed( transform1(
        see_reversed( filter_separators(prog) ), operations
    ))


def _parevde(prog: str) -> str:
    import ompy.parser as parser
    return parser.deparse( _evaluate( parser.parse( prog ) ) )


def _parevde_file(fp):
    return _parevde(fp.read().rstrip('\n\r'))
