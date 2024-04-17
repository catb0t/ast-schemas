from ompy.schema_data import Key
import ompy.parser as parser
from ompy.parser import DoNotSkip, NoLastID, Node, node_is, create_node, next_non_separator
from ._evaluator_common import SkipEnd


def _evaluate_rec(form, up_bindings):
    if up_bindings is None:
        up_bindings = {}
    new_form = []
    last_id = NoLastID
    skip_to_idx = DoNotSkip

    for idx, node in enumerate(form):
        # print('doing', node)

        if skip_to_idx > idx:
            continue
        if skip_to_idx == idx:
            skip_to_idx = DoNotSkip

        if skip_to_idx < idx:
            return new_form

        if node_is(node, Node.SEPARATOR):
            print(f'Separator node: {node}')
            new_form.append(node)

        elif node_is(node, Node.OPERATOR):
            print(f'Operator node: {node}')
            if last_id == Node.OPERATOR:
                new_form.append(create_node(Node.SEPARATOR, 0))

            bound = up_bindings.get(node[Key.VALUE])

            if bound is not None:
                want_operands = bound.effect.in_arity()
                next_idx, next_node = next_non_separator(form[idx:])
                if next_idx == -1:
                    pass


                elif form[idx + 1:idx + 1 + want_operands]:
                    pass

                print(f'bound operation: {bound}')
                # invoke the bound operation with the rest of the current form
                # as its inputs
                new_part, used=bound[Key.BUILTIN](
                    form[idx:], up_bindings
                )
                print("new_part  == ", new_part, idx, used)
                new_form.extend(new_part)
                if used == SkipEnd:
                    return new_form
                skip_to_idx=idx + used + 1
            else:
                new_form.append(node)

        elif node_is(node, Node.OPERAND):
            print(f'Operand node: {node}')
            val=_evaluate_rec(node[Key.VALUE], up_bindings)
            new_form.append(
                parser.create_node(Node.OPERAND, val)
            )

        last_id=node['id']
    return new_form
