from .parse_common import SEP_STR


def transform_separator(elt, bindings):
    return SEP_STR[ elt['value'] ]


def transform_operator(elt, bindings):
    return bindings.get(
        elt['value'],
        {'meta': {'replaced_from': elt['value']}, **elt}
    )


def transform_operand(elt, bindings):
    return transform1(elt['value'], up_bindings=bindings)


def transform_builtin_operation(elt, bindings):
    return elt['value'](bindings)


def transform1(prog, up_bindings=None):
    local_bindings = dict()
    if up_bindings is not None:
        local_bindings.update(up_bindings)
    new_ast = []
    for elt in reversed(prog):
        new_ast.insert(
            0,
            {
                'separator': transform_separator,
                'operator': transform_operator,
                'operand': transform_operand,
                'builtin_operation': transform_builtin_operation
            }.get(elt['id'])(elt, local_bindings)
        )

    return new_ast


def evaluate(prog):
    from .builtin_operations import operations
    return transform1(prog, operations)
