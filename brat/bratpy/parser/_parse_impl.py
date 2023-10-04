from bratpy.util import Key

from ._parse_common import EOL, SEP_STR, \
    DoNotSkip, ParserState

from ._normalize import normalize_separators, adjacent_literal_handler

from .objects import NoLastID, Block, Node
from .cases import PARSER_CASES

from .node_readers import compound_literal_shared_name

DEBUG = False


def result_none_check(result, case_obj, ch, idx, fname, depth, line, col):
    if result is None \
            or result.get(Key.NODE_PROPS) is None \
            or result.get(Key.NODE_ID) is None:
        raise ValueError(
            f'case_obj.handle returned None: {case_obj}\n\t{result} \n\tch:{ch} '
            f'idx:{idx} at "{fname}" depth {depth} line {line} col {col}')


def _tree_parse_debug(local_idx, ch, parser_state, source_view):
    print(
        '>' * (parser_state.depth() + 1)

        + f"\tlocal: {local_idx} idx: {parser_state.idx()}\t"

        + f"({parser_state.line()}:{parser_state.col()})\tch: {repr(ch)} "

        + f"\tskip_to -> {parser_state.skip_to_idx()} "

        + (repr(source_view[parser_state.skip_to_idx()])
           if parser_state.skip_to_idx() < len(source_view)
           else '(or past end of source view)')
    )


def _do_parse_to_tree(parser_state: ParserState, break_on_test=None):
    building = []

    source_view = parser_state.source_view()

    for local_idx, ch in enumerate(source_view):
        create_node = (lambda nid, props=None:
                       Node.create(nid, props, parser_state.line(),
                                   parser_state.col(), parser_state._debug()))

        _tree_parse_debug(local_idx, ch, parser_state, source_view)

        if parser_state.idx() < parser_state.skip_to_idx():
            parser_state.inc_idx()
            continue
        if parser_state.skip_to_idx() == parser_state.idx():
            parser_state.set_skip_to_idx(DoNotSkip)

        # passed the target or we are closing a form: return
        # aka idx > skip_to_idx
        if parser_state.idx() > parser_state.skip_to_idx() \
                or Block.ch_is(ch, Block.CLOSE):
            break

        # print("COL top", col)
        if ch in SEP_STR:
            print(
                f"SEP_STR: {repr(ch)} {parser_state.line()}:{parser_state.col()}"
            )

            building.append(create_node(Node.SEPARATOR, {
                Key.VALUE: SEP_STR.index(ch)
            }))

            if ch == EOL:
                parser_state.inc_line()
                parser_state.set_col(1)
            else:
                parser_state.inc_col()

            parser_state.inc_idx()
        else:
            # print("COL in ", col)
            if break_on_test is not None and break_on_test(
                ch, source=source_view, idx=parser_state.idx(),
                last_id=parser_state.last_id()
            ):
                break

            redirected_handler = None
            for _key, case in PARSER_CASES.items():
                # from the last iteration
                if redirected_handler:
                    handler = redirected_handler[0]
                    _key, case = handler, PARSER_CASES[handler]
                    # very important!!!
                    redirected_handler = None
                # bool is unused
                _, case_obj = case

                ch_test = case_obj.test(
                    ch, source=source_view, last_id=parser_state.last_id()
                )
                # we are being redirected to a different handler
                if isinstance(ch_test, dict):
                    redirected_handler = (ch_test[Key.HANDLER], _key)
                    continue

                if ch_test:
                    result = case_obj.handle(ch, parser_state, create_node)

                    result_none_check(
                        result, case_obj, ch, parser_state.idx(), parser_state.fname(),
                        parser_state.depth(), parser_state.line(), parser_state.col()
                    )

                    """ handle :symbol5.0 -> :symbol50 when in normal mode etc """
                    adjacent_literal_handler(
                        building, parser_state.roundtrip(),
                        result[Key.NODE_PROPS], create_node
                    )

                    building.append(create_node(
                        result[Key.NODE_ID],
                        result[Key.NODE_PROPS]
                    ))
                    parser_state.set_last_id(result[Key.NODE_ID])
                    parser_state.set_skip_to_idx(result[Key.SKIP_TO_IDX])
                    parser_state.set_line(result[Key.LINE])
                    parser_state.set_col(result[Key.COL])

                    parser_state.inc_idx()

                elif redirected_handler:
                    assert ch_test, \
                        'Bullshit redirection to parser handler ' \
                        f"'{handler}' " \
                        f"(instructed by cases.{redirected_handler[1]}.test) "\
                        'was incorrect! parser bug found!'

    # end for
    print("bld", building)

    return building, parser_state.idx(), parser_state


def _parse(
    source='',
    fname='<input>',
    roundtrip=False,
    parser_state: ParserState = None,
    _test=False,
    _debug=False,
    break_on_test=None
):
    if parser_state is not None:
        state = parser_state
        roundtrip = parser_state.roundtrip()
    else:
        state = ParserState(
            source, fname,
            roundtrip=roundtrip, _debug=_debug
        )

    node, _, new_state = _do_parse_to_tree(
        state, break_on_test=break_on_test
    )

    if not roundtrip:
        node = normalize_separators(node)
    if not _test:
        return node

    return node, new_state.line(), new_state.col()


def _parse_file(fp, fname, roundtrip=False, _debug=False):
    return _parse(
        source=fp.read().rstrip('\n\r'), fname=fname,
        roundtrip=roundtrip, _debug=_debug
    )


compound_literal_shared_name(_parse)
