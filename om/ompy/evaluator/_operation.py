from .effects import BasicEffect
from ._evaluate_common import only_operands


def arity_error(args, arity, prep, variadic=False):
    var = 'row variadic' if variadic else ''
    print(
        f"Partial application {prep}flow:\n\t{var}arity = "
        + f"{arity}\n\t  got = {len(args)}: {args}"
    )

class Operation:
    func = None
    effect = None
    py_name = None

    def __init__(self, func, effect, py_name):
        self.func = func
        self.effect = effect
        self.py_name = py_name

    def __call__(self, args, _bindings=None):
        operands = only_operands(args[1:])

        in_arity = self.effect.input_arity()

        if in_arity.is_variadic():
            if len(operands) < in_arity.fixed():
                arity_error(operands, in_arity, "under", variadic=True)
        else:
            in_arity_error = in_arity.fixed() - len(operands)
            prep = "under" if in_arity_error > 0 else "over"
            arity_error(operands, in_arity, prep)

        output, used_nodes = self.func(args[0], operands, _bindings)

        out_arity = self.effect.output_arity()

        if out_arity.is_variadic():
            if len(output) < out_arity.fixed():
                arity_error(operands, out_arity, "under", variadic=True)
        else:
            out_arity_error = out_arity.fixed() - len(output)
            prep = "under" if out_arity_error > 0 else "over"
            arity_error(output, out_arity, prep)

        return output, used_nodes

    def __name__(self):
        return self.func.__name__

    def __repr__(self):
        return f"{self.py_name} {self.effect}"
