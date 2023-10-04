"""
    an operation has a well-defined number of required input operands
    less than which it is a partial application
    for operations ( -- ... ), the number is 0 (i,e, they always return zero
    or more values with no inputs )
    such operations are rare (non-existent?) in the ref impl stdlib
    the number of inputs required for totality may vary with the input data,
    but is constant for each possible input to an operation
    remember, operations only deal with operands -- any operators must be
    evaluated to find the value and whether it's partial
    an operator always evaluates to itself if it is free
"""

import re
OPERATION_NAME = re.compile(r'^om_(.+)$')
from ompy.parser import Node, node_is, node_is_any, create_node
from ._do_evaluate import _evaluate_rec
from ._evaluator_common import SkipEnd
from pprint import pprint


def _create_operand(val):
    return [create_node(Node.OPERAND, [val])]


def _next_operands(elts, required):
    ops = []
    used = 0
    for e in elts:
        if node_is(e, Node.OPERAND):
            ops.append(e)
        if len(ops) == required:
            return True, ops, used
        used += 1
    return False, ops, used


def _try_eval(form, required, true_func, false_func=None):
    # print('trying to do ', form)
    ok, next_ops, used = _next_operands(form, required)
    if ok:
        return (true_func(next_ops), used)
    if false_func is None:
        return (_evaluate_rec(form), SkipEnd)
    return (false_func(), 0)


def om_quote(form, _bindings):
    return _try_eval(form, 1, lambda p: _create_operand(p[0]))


def om_dequote(form, _bindings):
    return _try_eval(form, 1, lambda p: p[0]['value'])


def om_copy(form, _bindings):
    if not form or not node_is(form[0], Node.OPERAND):
        raise ValueError(form)
    return create_node(Node.OPERAND, [form[0], form[0]])


def om_define(form, bindings):
    pass


def om_pullfront_characters(form, _bindings):
    pass


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
