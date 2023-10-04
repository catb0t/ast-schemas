from ._do_evaluate import _evaluate_rec
from ._builtin_operation import operations


def _evaluate(form):
    return _evaluate_rec(form, up_bindings=operations)
