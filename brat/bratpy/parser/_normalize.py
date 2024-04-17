import copy

from bratpy.schema_data import Key, linear_selection, linear_selection_by

from .objects import Node, CompoundLiteral, NoLastID

from ._parse_common import DoNotSkip

# set the priority for keeping a significant separator
SEP_PRIORITY = [
    # NEWLINE
    1,
    # SPACE
    0,
    # TAB
    2
]


def adjacent_literal_handler(building, roundtrip, curr_node, create_node):
    if roundtrip or len(building) == 0:
        return

    if building[-1].get(Key.KIND) == 'symbol':
        curr_value = curr_node.get(Key.VALUE)

        if isinstance(curr_value, float) or isinstance(curr_value, int):
            building.append(create_node(Node.SEPARATOR, {Key.VALUE: 0}))


def _shrink_separator_span(form, span_begin_idx, previous_node=NoLastID):
    '''
        shrink a run of separators down to zero or one (if it is significant)

        returns a tuple of ([optimal_partial_form], skip_to_idx), where
            skip_to_idx is the end of the processed run (i.e., where the
            calling loop should pick up from).

        NOTE: you must use building.extend( [optimal_partial_form] ); it is
            returned as a list because it may be empty (in the case of a
            compltetely omitted run)

        the resulting partial form has no runs of more than one significant
            separator, and has no separators that are not
            semantically significant.


        parameters:
            form:           the piece of source to shrink
            span_begin_idx: the index in `form` at which the span of separators
                                begins
            previous_node:  the last node processed by the calling loop (i.e,
                                either the string ID of the node or a Node
                                enum member)
                            default: NoLastID (singleton)


        the priority for preserving significant separators is:
            1. newline (id 1), 2. space (id 0), 3. tab (id 2)

        given a run of separators where one significant separator is needed:

        if it contains only tabs, one tab will appear as the sole separator.

        if it contains tabs and spaces, the tabs will be omitted, and
            one space will remain.

        if it contains newlines and spaces, the spaces will be omitted,
            preserving one newline.

        if it contains newlines, spaces, and tabs, only one newline will
            appear in the result.
    '''
    if previous_node is NoLastID:
        # the node preceding the span, if there was one ...
        previous_node = form[span_begin_idx - 1] \
            if span_begin_idx != 0 else NoLastID

        if Node.node_is_separator(previous_node):
            span_begin_idx -= 1

    # our interest
    form_rest = form[span_begin_idx:]
    # the baseline for the span_end
    span_end = span_begin_idx
    sep_values = set()
    # search forward for the end of the span
    for elt in form_rest:
        if Node.node_is_separator(elt):
            sep_values.add(elt[Key.VALUE])
            span_end += 1
        else:
            break

    # span is between operators
    # pick the separator to remain based on the priority
    for p in SEP_PRIORITY:
        if p in sep_values:
            return [Node.create(Node.SEPARATOR, {Key.VALUE: p})], span_end

    # i don't know what happened!
    raise ValueError('something is broken...',
                     SEP_PRIORITY, sep_values, form_rest)


def normalize_subforms(subforms):
    return {k: normalize_separators(v) for k, v in subforms.items()}


def merge_subform_properties(subforms, all_properties):
    missing = linear_selection_by(
        all_properties,
        lambda a: a[0] not in subforms
    )
    new_subforms = copy.deepcopy(subforms)
    new_subforms.update(linear_selection(all_properties, missing))

    return new_subforms


def remove_trailing_newline_chars():
    pass


def normalize_separators(form):
    if not isinstance(form, list):
        raise ValueError('want list, got ' + repr(type(form)))
    new_form = []
    last_node = NoLastID
    next_node = NoLastID
    skip_to_idx = DoNotSkip

    for i, e in enumerate(form):
        # i.e. i < skip_to_idx
        if skip_to_idx > i:
            # probably unnecessary
            # last_id = _node_from_id(e['id'])
            continue
        if skip_to_idx == i:
            skip_to_idx = DoNotSkip

        if i != 0:
            last_node = Node.to_enum(form[i - 1])
        if i != (len(form) - 1):
            next_node = Node.to_enum(form[i + 1])
        else:
            next_node = NoLastID

        # print(f"e: {e}")

        # print(f"========\nlastid\t{last_node}\ne \t{e}\nnext\t{next_node}")
        if Node.nodes_all_separator((e, next_node)):
            # this separator begins a span of more than one separator
            # print(f"e next all sep {e} {next_node}")
            new_part, skip_to_idx = _shrink_separator_span(
                form, i, last_node
            )
            new_form.extend(new_part)

        elif Node.node_is_separator(e) \
                and (last_node == NoLastID
                     or next_node == NoLastID):
            pass

        elif Node.node_is_separator(e):

            # (last_node == NoLastID or next_node == NoLastID) \
            if (Node.node_is_not_separator(last_node)
                    and Node.node_is_not_separator(next_node)):

                new_form.append(e)
                # early-omits { A} and {A }
                # this separator is between operators so it is significant
            # omit otherwise

        elif Node.can_subform(e):
            print(f"e can subform: {e}")
            new_form.append(Node.create(
                Node.to_enum(e),
                merge_subform_properties(
                    normalize_subforms(Node.subforms(e)),
                    e
                )
            ))

        elif Node.node_is_not_separator(e):
            new_form.append(e)

        else:
            raise ValueError(e)

    return new_form
