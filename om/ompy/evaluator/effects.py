def basic_arity(arity):
    return ['x'] * arity


class Effect:
    input = None
    output = None

    def __init__(self, inputs, outputs):
        self.input = inputs
        self.output = outputs

    def net_effect(self):
        return len(self.output) - len(self.input)

    def input_arity(self):
        return len(self.input)

    def output_arity(self):
        return len(self.output)


class BasicEffect(Effect):
    def __init__(self, in_arity, out_arity):
        super().__init__(basic_arity(in_arity), basic_arity(out_arity))
