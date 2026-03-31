from .effects import BasicEffect
from ._evaluate_common import filter_operands


class Operation:
    func = None
    effect = None
    py_id = None

    def __init__(self, func, effect, py_id):
        self.func = func
        self.effect = effect
        self.py_id = py_id

    def __call__(self, args, _bindings=None):
        operands = filter_operands(args[1:])
        in_arity_error = self.effect.input_arity() - len(operands)
        if in_arity_error != 0:
            adj = "under" if in_arity_error > 0 else "over"
            print(
                f"Partial application {adj}flow:\n\tarity = "
                + f"{self.effect.input_arity()}\n\t  got = {len(args)}: {args}"
            )

        output, used_nodes = self.func(args[0], operands, _bindings)

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
