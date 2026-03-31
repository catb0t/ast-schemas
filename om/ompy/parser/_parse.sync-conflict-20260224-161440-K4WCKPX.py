import re

from ._parse_common import SEP_STR, NOT_OP, \
    DoNotSkip, NoLastID, check_skip, Form, _ch_is, _form_to_ch, Node, \
    _node_is, _create_node
from ._error import CantParse, ParseError
from ._normalize import _shrink_separator_span
# read forward in the source to get the name of the operator
# stops when it finds an unescaped separator or brace
operator_reader = re.compile(r'^(?:`[`\n\t {}]|[^`\n\t {}])+')
# find unescaped open braces
unesc_opens = re.compile(r'(?<![^`]`)' + _form_to_ch(Form.OPEN))
# find unescaped close braces
unesc_closes = re.compile(r'(?<![^`]`)' + _form_to_ch(Form.CLOSE))
# lexical escape for anything that follows it including space/tab/newline
ESCAPE = '`'


def _operator_name(optr_source):
    '''read the name of an operator from the source. returns a re.Match'''
    return operator_reader.match(optr_source)


def _count_found(use, source):
    '''the number of times the regex `use` matched `source`'''
    return len(re.findall(use, source))


def _unbalanced_braces(source):
    '''
        test whether a program has balanced unescaped open/close braces

        result is boolean
    '''
    return (_count_found(unesc_opens, source) !=
            _count_found(unesc_closes, source))


def _list_finditer(use, source):
    '''finditer(use, source) but not a generator'''
    return list(re.finditer(use, source))


def _create_context(source, idx):
    closes_after = _list_finditer(unesc_closes, source[idx:])
    opens_before = _list_finditer(unesc_opens,  source[:idx])

    # where the context should begin
    return (
        opens_before[
            -2 if len(opens_before) > 1 else 0
        ].span()[0],
        idx + closes_after[
            1 if len(closes_after) > 1 else 0
        ].span()[1]
    )


def _brace_match(fname, source):
    '''
        find unmatched braces in the source.

        matches from left-to-right. in `{ { }`, the first open brace will be
            found to match the close brace, so the second open brace will be
            considered stray and reported as an error.

        similarly, in `{ } }`, the first pair of braces will match, and the
            last brace will be considered stray.
    '''
    # should escape the next char / have we seen an open brace yet
    escape_next = seen_open = False
    depth = 0
    line = col = 1
    # total number of unescaped close braces for the entire source
    count_close = _count_found(unesc_closes, source)
    for idx, ch in enumerate(source):
        if escape_next:
            escape_next = False
            # print(f"escaped {repr(ch)} at {idx} ({line}:{col-1})")
            col += 1
            continue

        if ch == ESCAPE:
            escape_next = True
        elif ch == '\n':
            col = 1
            line += 1
            continue

        elif _ch_is(ch, Form.OPEN):
            # looking for STRAY OPENS
            seen_open = True
            depth += 1
            offset = 2
            # there are no close braces in this program
            if count_close == 0:
                raise ParseError(fname, CantParse.STRAY_OPEN, source,
                                 idx - offset, len(source), offset,
                                 idx, line, col)

            # we have gone deeper than we can return from
            if depth > count_close:
                begin, end = _create_context(source, idx)
                raise ParseError(fname, CantParse.STRAY_OPEN, source, begin,
                                 end, idx - begin, idx, line, col)

        elif _ch_is(ch, Form.CLOSE):
            # looking for STRAY CLOSES
            depth -= 1
            offset = 2
            if not seen_open:
                raise ParseError(fname, CantParse.STRAY_CLOSE, source, 0,
                                 idx + offset, 0, idx, line, col)
            if depth < 0:
                begin, end = _create_context(source, idx)
                raise ParseError(fname, CantParse.STRAY_CLOSE, source, begin,
                                 end, idx - begin, idx, line, col)
        col += 1
    return depth


def _parse_to_tree(source, fname, strip=False, skip_to_idx=DoNotSkip, depth=0, line=1, col=1):
    if depth == 0 and _unbalanced_braces(source):
        _brace_match(fname, source)
        return [{}]

    building = []
    escape_next = False
    last_id = NoLastID

    idx = 0
    for idx, ch in enumerate(source):
        # print(
        #     '>' * (depth + 1)
        #     + f"\tidx: {idx}\t({line}:{col})\tch: {repr(ch)} \t-> {skip_to_idx}"
        #     f"({repr(source[skip_to_idx]) if skip_to_idx < len(source) else ''})"
        # )
        # aka idx < skip_to_idx
        if skip_to_idx > idx:
            continue
        if skip_to_idx == idx:
            skip_to_idx = DoNotSkip
        if not escape_next and ch == ESCAPE:
            escape_next = True
            continue

        # passed the target or we are closing a form: return
        # aka idx > skip_to_idx
        if skip_to_idx < idx or (not escape_next and _ch_is(ch, Form.CLOSE)):
            return building, idx, line, col

        if not escape_next and ch in SEP_STR:
            if ch == '\n':
                line += 1
                col = 1
            else:
                col += 1
            # omit the separator in { A} {A } {A {B}} {{A} B} { {A} {B} }
            if strip:
                if idx in (0, len(source) - 1):
                    continue

                next_ch = source[idx + 1]

                if next_ch in SEP_STR:
                    sep_node, skip_to_idx = _shrink_separator_span(
                        True, source, idx, last_id
                    )

                    check_skip(skip_to_idx)

                    last_id = Node.SEPARATOR
                    building.extend(sep_node)
                    continue

                # NOTE: skip the separator if we are NOT between two operators
                # the only semantic separators in { A} {A } {A  A} {A {B}}
                # {{A} B} { {A} {B} } etc
                # are in {A  A}
                if not (_node_is(last_id, Node.OPERATOR)
                        and next_ch not in NOT_OP):
                    continue

            last_id = Node.SEPARATOR
            building.append(
                _create_node(Node.SEPARATOR, SEP_STR.index(ch))
            )

        elif not escape_next and _ch_is(ch, Form.OPEN):
            operand, skip_to_idx, line, col = _parse_to_tree(
                source,
                fname,
                strip=strip,
                skip_to_idx=idx + 1,
                depth=depth + 1,
                line=line,
                col=col
            )

            check_skip(skip_to_idx)

            building.append( _create_node(Node.OPERAND, operand) )
            last_id = Node.OPERAND
            skip_to_idx += 1
            col += 1

        elif ch not in NOT_OP:
            match = _operator_name(source[idx:])
            building.append( _create_node(Node.OPERATOR, match.group()) )
            last_id = Node.OPERATOR
            skip_to_idx = idx + match.span()[1]
            col += match.span()[1] + 1
            escape_next = False
        else:
            raise ValueError(ch, 'parser bug found!')

    return building, idx, line, col


def _parse(source, fname='input', strip=False):
    return [ *_parse_to_tree(source, fname, strip) ][0]


def _parse_file(fp, fname='input', strip=False):
    return _parse(fp.read().rstrip('\n\r'), fname, strip)
