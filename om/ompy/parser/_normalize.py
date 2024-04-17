from ._parse_common import SEP_STR, NOT_OP, \
    DoNotSkip, NoLastID, Node, _node_is, _nodes_are, _node_from_id, \
    _node_is_any, _create_node

# set the priority for keeping a significant separator
SEP_PRIORITY = list(map(SEP_STR.index, '\n \t'))
assert list(SEP_PRIORITY)
assert list(SEP_PRIORITY)


def getfunc(text_mode):
    def _src_test(ch): return ch in SEP_STR
    def _obj_test(elt): return _node_is(elt, Node.SEPARATOR)

    _src_kind = SEP_STR.index
    def _obj_kind(elt): return elt['value']

    def _src_next(ch): return Node.OPERAND if ch in NOT_OP else Node.OPERATOR
    def _obj_next(elt): return elt['id']

    def invalid_where(*x):
        raise ValueError(x)

    lookup = [{
        'test': _obj_test,
        'kind': _obj_kind,
        'next': _obj_next,
    }, {
        'test': _src_test,
        'kind': _src_kind,
        'next': _src_next,
    }][text_mode]

    return lambda where: lookup.get(where, lambda: invalid_where(where))


def _shrink_separator_span(
    text_mode,
    form,
    span_begin_idx,
    previous_node=NoLastID
):
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
            text_mode:      whether this is being invoked from a text parser or
                                an AST node traverser
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
    if not text_mode and previous_node is NoLastID:
        # the node preceding the span, if there was one ...
        previous_node = form[span_begin_idx - 1] if span_begin_idx != 0 else ''
    # our interest
    form_rest = form[span_begin_idx:]
    # the baseline for the span_end
    span_end = span_begin_idx
    sep_kinds = set()
    # the type of the node following the span
    following_node = ''
    # mode-specific functions
    funcs = getfunc(text_mode)
    # search forward for the end of the span
    for elt in form_rest:
        if funcs('test')(elt):
            sep_kinds.add(funcs('kind')(elt))
            span_end += 1
        else:
            following_node = funcs('next')(elt)
            break

    # NOTE: the condition is negated, we are NOT between 2 operators
    if not _nodes_are((previous_node, following_node), Node.OPERATOR):
        # this span is not even significant, just delete it
        return [], span_end

    # span is between operators
    # pick the separator to remain based on the priority
    for p in SEP_PRIORITY:
        if p in sep_kinds:
            return [_create_node(Node.SEPARATOR, p)], span_end

    # i don't know what happened!
    raise ValueError('something is broken...', SEP_PRIORITY, sep_kinds)


def filter_separators(form):
    if not isinstance(form, list):
        raise ValueError('want list, got ' + repr(type(form)))
    new_form = []
    last_id = NoLastID
    skip_to_idx = DoNotSkip
    for i, e in enumerate(form):
        # i.e. i < skip_to_idx
        if skip_to_idx > i:
            # probably unnecessary
            # last_id = _node_from_id(e['id'])
            continue
        if skip_to_idx == i:
            skip_to_idx = DoNotSkip

        if _node_is(e, Node.SEPARATOR):
            # partially redundant: prevents OOB on next_node
            # early-omits { A} and {A }
            if i in (0, len(form) - 1):
                continue

            next_node = form[i + 1]
            # this separator is between operators so it is significant
            if _nodes_are((last_id, next_node), Node.OPERATOR):
                new_form.append(e)

            # this separator begins a span of more than one separator
            elif _node_is(next_node, Node.SEPARATOR):
                new_part, skip_to_idx = _shrink_separator_span(
                    False, form, i, last_id
                )
                new_form.extend(new_part)
            # omit otherwise

        elif _node_is(e, Node.OPERATOR):
            new_form.append(e)

        elif _node_is(e, Node.OPERAND):
            new_form.append(
                _create_node(Node.OPERAND, filter_separators(e['value']))
            )

        last_id = _node_from_id(e['id'])

    return new_form


def normalize_separators(form):
    new_form = []
    for node in form:
        if _node_is(node, Node.SEPARATOR):
            new_form.append(
                _create_node(Node.SEPARATOR, 1)
            )
        elif _node_is(node, Node.OPERAND):
            new_form.append(
                _create_node(
                    Node.OPERAND,
                    normalize_separators(node['value'])
                )
            )
        elif _node_is(node, Node.OPERATOR):
            new_form.append(node)
    return new_form


def next_non_separator(form):
    for idx, node in enumerate(form):
        if _node_is_any(node, set(Node.OPERAND, Node.OPERATOR)):
            return idx, node
    return -1, None
