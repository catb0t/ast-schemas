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
from pprint import pprint

import ompy.parser as parser
from ompy.parser import Node, create_node, node_is, node_is_any
from ompy.schema_data import Key

from ._evaluate_common import SkipEnd, find_next_node
from ._operation import Operation
from .effects import BasicEffect

_shared_evaluate = None


def builtin_operation_shared_name(*args):
    global _shared_parse
    _shared_evaluate, *_ = args



def _create_operand(val):
    return [create_node(Node.OPERAND, [val])]


def _next_operands(elts, required):
    ops = []
    used = 0
    for e in elts:
        print(e)
        if node_is(e, Node.OPERAND):
            ops.append(e)
        if len(ops) == required:
            return True, ops, used
        used += 1
    return False, ops, used


def _try_eval(form, required, true_func, false_func=None):
    from ._evaluate import _evaluate
    print('try_eval trying to do ', form)
    ok, next_ops, used = _next_operands(form, required)
    print(ok, next_ops, used)
    if ok:
        return (true_func(next_ops), used)
    if false_func is None:
        return (_evaluate(form, {}), SkipEnd)
    return (false_func(), 0)


def _om_quote(form, _bindings):
    return _try_eval(form, 1, lambda p: _create_operand(p[0]))


om_quote = Operation(_om_quote, BasicEffect(1, 1), 'om_quote')


def old_om_dequote(_operator, operands, _bindings):
    print(f"\nom_dequote {repr(parser.deparse(operands))}")

    if not operands:
        return [_operator], 0
    operand = operands[0]

    print(f'current_operator\n\t{_operator}')
    print(f'rest\n\t{operands[1:]}')
    print(f'operand at {idx}\n\t{operand}')

    if operand is not None:
        return operand[0][Key.VALUE], idx + 1
    return form, 0

def _om_dequote(_operator, operands, _bindings) -> list[Node], int:
    target = operands[0]
    dequoted = target[Key.VALUE][0]




om_dequote = Operation(_om_dequote, BasicEffect(1, 1), 'om_dequote')


def _om_copy(form, _bindings):
    if not form or not node_is(form[0], Node.OPERAND):
        raise ValueError(form)
    return create_node(Node.OPERAND, [form[0], form[0]])


om_copy = Operation(_om_copy, BasicEffect(1, 2), 'om_copy')


def _om_define(form, bindings):
    pass


om_define = Operation(_om_define, BasicEffect(2, 1), 'om_define')


def _om_pullfront_characters(form, _bindings):
    pass


om_pullfront_characters = Operation(
    _om_pullfront_characters, BasicEffect(1, 1), 'om_pullfront_characters')


builtin_operations = {
    'dequote': om_dequote,
    'quote': om_quote,
    'copy': om_copy,
    'define': om_define,
    '<-[characters]': om_pullfront_characters
}
