from typing import List

ROW_VARIADIC = '...'


class Arity:
    _fixed = 0
    _is_variadic = False

    def fixed(self):
        return self._fixed

    def is_variadic(self):
        return self._is_variadic

    def is_empty(self):
        return self._fixed == 0 and not self._is_variadic

    def __init__(self, fixed: int, is_variadic: bool):
        self._fixed = fixed
        self._is_variadic = is_variadic

    def __repr__(self):
        if self._is_variadic:
            if not self._fixed:
                return "N-ary"
            return f"N+{self._fixed}-ary"
        else:
            if not self._fixed:
                return "nullary"
            return f"{self._fixed}-ary"


def basic_arity(effect_side) -> Arity:
    var = False
    if effect_side.count(ROW_VARIADIC) > 1:
        raise ValueError(f"an effect can only contain one row variadic marker ('...'): f{effect_side}")  # noqa
    if ROW_VARIADIC in effect_side:
        if not (
            effect_side[0] == ROW_VARIADIC
            or effect_side[-1] == ROW_VARIADIC
        ):
            raise ValueError(f"the row variadic marker ('...') must appear at the beginning or end of the effect: {effect_side}")  # noqa
        var = True

    return Arity(
        len(list(filter(lambda x: x != ROW_VARIADIC, effect_side))),
        var
    )


class Effect:
    in_effect = None
    in_arity = None

    out_effect = None
    out_arity = None

    def __init__(self, in_effect, in_arity, out_effect, out_arity):
        self.in_effect = in_effect
        self.in_arity = in_arity
        if in_arity.is_variadic():
            self.in_effect.remove(ROW_VARIADIC)

        self.out_effect = out_effect
        self.out_arity = out_arity
        if out_arity.is_variadic():
            self.out_effect.remove(ROW_VARIADIC)

    def input_arity(self):
        return self.in_arity

    def output_arity(self):
        return self.out_arity

    def __repr__(self):
        left = ''
        right = ''
        lvars = self.in_effect
        lvars += [ROW_VARIADIC] if self.in_arity.is_variadic() else []

        left = ' '.join(lvars)
        if left:
            left = ' ' + left

        rvars = self.out_effect
        rvars += [ROW_VARIADIC] if self.out_arity.is_variadic() else []

        right = ' '.join(rvars)
        if right:
            right = right + ' '
        return f"({left} -- {right})"


class BasicEffect(Effect):
    def __init__(self, in_effect: List, out_effect: List):
        super().__init__(
            in_effect, basic_arity(in_effect),
            out_effect, basic_arity(out_effect)
        )
