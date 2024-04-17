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
from ompy.parser import Node, node_is, node_is_any, create_node
from ompy.schema_data import Key
from ._evaluator_common import SkipEnd, find_next_node
from ._do_evaluate import _evaluate_rec
from .effects import BasicEffect


OPERATION_NAME = re.compile(r'^om_(.+)$')


class Operation:
    func = None
    effect = None

    def __init__(self, func, effect):
        self.func = func
        self.effect = effect

    def __call__(self, args, _bindings=None):
        in_arity_error = self.effect.input_arity() - len(args)
        if in_arity_error != 0:
            adj = "under" if in_arity_error > 0 else "over"
            print(
                f"Partial application {adj}flow:\n\tarity = "
                + f"{self.effect.input_arity()}\n\t  got = {len(args)}: {args}"
            )

        output, used_nodes = self.func(args, _bindings)

        out_arity_error = self.effect.input_arity() - len(output)
        if out_arity_error != 0:
            adj = "under" if out_arity_error > 0 else "over"
            print(
                "Result value arity {adj}flow:\n\tarity = "
                + f"{self.effect.output_arity()}\n\t  got = {len(output)}: {output}"
            )

        return output, used_nodes

    def __name__(self):
        return self.func.__name__


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
    print('try_eval trying to do ', form)
    ok, next_ops, used = _next_operands(form, required)
    print(ok, next_ops, used)
    if ok:
        return (true_func(next_ops), used)
    if false_func is None:
        return (_evaluate_rec(form, {}), SkipEnd)
    return (false_func(), 0)


def _om_quote(form, _bindings):
    return _try_eval(form, 1, lambda p: _create_operand(p[0]))


om_quote = Operation(_om_quote, BasicEffect(1, 1))


def _om_dequote(form, _bindings):
    print(f"\nom_dequote {repr(parser.deparse(form))}")
    current_operator = form[0]
    form_rest = form[1:]
    operand, idx = next_node(form_rest, Node.OPERAND)
    print('current_operator\n\t', end='')
    pprint(current_operator)
    print('rest\n\t', end='')
    pprint(form_rest)
    print(f'next operand at {idx}\n\t', end='')
    pprint(operand)
    if operand is not None:
        return operand[0][Key.VALUE], idx + 1
    return form, 0


om_dequote = Operation(_om_dequote, BasicEffect(1, 1))


def _om_copy(form, _bindings):
    if not form or not node_is(form[0], Node.OPERAND):
        raise ValueError(form)
    return create_node(Node.OPERAND, [form[0], form[0]])


om_copy = Operation(_om_copy, BasicEffect(1, 2))


def _om_define(form, bindings):
    pass


om_define = Operation(_om_define, BasicEffect(2, 1))


def _om_pullfront_characters(form, _bindings):
    pass


om_pullfront_characters = Operation(
    _om_pullfront_characters, BasicEffect(1, 1))


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
