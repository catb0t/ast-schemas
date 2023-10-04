import ompy.parser as parser
from ompy.parser import DoNotSkip, NoLastID, Node, node_is, create_node
from ._evaluator_common import SkipEnd


def _evaluate_rec(form, up_bindings=None):
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
            new_form.append(node)

        elif node_is(node, Node.OPERATOR):
            if last_id == Node.OPERATOR:
                new_form.append(create_node(Node.SEPARATOR, 0))

            bound = up_bindings.get(node['value'])
            if bound is not None:
                # invoke the bound operation with the rest of the current form
                # as its inputs
                new_part, used = bound['builtin'](form[idx:], up_bindings)
                # print("new_part", idx, used, new_part)
                new_form.extend(new_part)
                if used == SkipEnd:
                    return new_form
                skip_to_idx = idx + used + 1
            else:
                new_form.append(node)

        elif node_is(node, Node.OPERAND):
            val = _evaluate_rec(node['value'])
            new_form.append(
                parser.create_node(Node.OPERAND, val)
            )

        last_id = node['id']
    return new_form
