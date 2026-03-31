from pprint import pprint

import ompy.parser as parser
from ompy.parser import (
    DoNotSkip,
    Node,
    NoLastID,
    create_node,
    next_non_separator,
    node_is,
)
from ompy.schema_data import Key

from ._builtin_operation import builtin_operation_shared_name, builtin_operations
from ._evaluate_common import SkipEnd


def _evaluate(form, up_bindings=None):
    """
     Evaluate a form with enclosing/global bindings in 'up_bindings'.

     According to sparist, application goes only to the right, no
         operands-evaluating-operators goes on. No, not even when it seems
         like leftward is the right way.

     An operator needs to be applied to at most its arity number of operands,
         and at least 0 operands. Applying an operator to fewer than its arity
         number of operands results in a partial application.

     If the form seems to suggest an operator should be applied to more operands
         than its arity, the rest of the form needs to be left alone, with only
         the first arity + 1 items collapsed/expanded into the number of
         resulting values.

    `copy` is one of the few builtin operations that returns more than 1 value;
         most builtins return exactly 1 value.
    """

    if up_bindings is None:
        up_bindings = builtin_operations.copy()

    # we are going to build a new form
    new_form = []
    # stores the id of the previous node
    last_id = NoLastID
    # where we are skipping to next
    skip_to_idx = DoNotSkip

    for idx, node in enumerate(form):
        print(f"_evaluate idx {idx}: ", node)

        if skip_to_idx > idx:
            continue
        if skip_to_idx == idx:
            skip_to_idx = DoNotSkip

        if skip_to_idx < idx:
            return new_form

        if node_is(node, Node.SEPARATOR):
            print(f"Separator node: {node}")
            new_form.append(node)

        elif node_is(node, Node.OPERATOR):
            print(f"Operator node: {node}")
            if last_id == Node.OPERATOR:
                new_form.append(create_node(Node.SEPARATOR, 0))

            bound = up_bindings.get(node[Key.VALUE])

            if bound is not None:
                in_arity = bound.effect.input_arity()
                fixed_len = in_arity.fixed()
                is_variadic = in_arity.is_variadic()
                # next_idx, next_node = next_non_separator(form[idx:])
                # if next_idx == -1:
                #     pass
                # elif form[idx + 1 : idx + 1 + fixed_len]:
                #     pass

                cleaned_form = parser.filter_separators(form[idx:])

                print(f"\nCall bound operation: {bound}")
                print("With the form:")
                # invoke the bound operation with the rest of the current form
                # as its inputs
                if is_variadic:
                    pprint(cleaned_form[idx:])
                    new_part, used = bound(cleaned_form[idx:], up_bindings)
                else:
                    pprint(cleaned_form[idx : idx + 1 + fixed_len])
                    new_part, used = bound(
                        cleaned_form[idx : idx + 1 + fixed_len],
                        up_bindings
                    )
                print("new_part == ", new_part, idx, used)
                new_form.extend(new_part)
                if used == SkipEnd:
                    return new_form
                skip_to_idx = idx + used + 1
            else:
                new_form.append(node)

        elif node_is(node, Node.OPERAND):
            print(f"Operand node: {node}")
            val = _evaluate(node[Key.VALUE], up_bindings)
            new_form.append(parser.create_node(Node.OPERAND, val))

        last_id = node["id"]
    return new_form


builtin_operation_shared_name(_evaluate)
