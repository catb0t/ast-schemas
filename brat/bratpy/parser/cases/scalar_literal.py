from bratpy.util import Key
from ...schema_data import linear_selection_by
from ..node_readers import scalar_literal_value
from ..objects import Node, ScalarLiteral, DECIMAL_SEP
from ..errors import literal as literal_error

# from .._error import bad_literal
from .._parse_common import get_next_ch


def handle_regex_structure(regex):
    if not regex.get('flags'):
        return regex.get('value')

    return linear_selection_by({
        'pattern': regex['value'],
        'flags':   regex['flags']
    })


class scalar_literal():
    '''
        TODO: consistently handle these cases:
        .               (nothing method call on nothing)
        .''             (string literal method call on nothing)
        .f              (method call on nothing)
        .@//            (regex literal method call on nothing)
            -> member_access -> parse error: literal as method name

        5.   = 5.0      (5.0)
            -> literal

        5.a  = 5. a     (5.0; a)
            -> [literal, var_by_name] -> expression_separator

        5..a = 5.0.a    (invoke a on 5.0)
            -> literal -> member_access

        a.5  = a 0.5    (invoke a with 0.5)
            -> [var_by_name, literal] -> application

        a..5 = a. 0.5   (nothing method call on a; 0.5)
            -> var_by_name -> member_access -> parse error: literal as method name   # noqa

        a1.5 = a1. 0.5  (same, nothing method call on variable a1)
            -> (same)

        " ' @/ :        (strings/regex/symbol missing closes/name)
            -> literal -> parse error: missing literal value / close char
    '''
    @staticmethod
    def test(ch, **k):
        source = k['source']

        next_ch = get_next_ch(source)

        # if parser_state._debug():
        # print(f"next: {repr(next_ch)}")

        ''' the most sensible thing to do is just to return false
            but it might be more helpful to tell the parser
            where the right handler is (member_access)
            unfortunately there's no simple way to standardise the handler
            keys because that list is in this file's __init__ '''
        if ch == DECIMAL_SEP:
            ''' this if accounts for .', .@/, and .., which should be errors
                raised by member_access '''
            if (
                (not ScalarLiteral.ch_is(next_ch))
                or next_ch == DECIMAL_SEP
                or ScalarLiteral.ch_is_unfinished_literal(next_ch)
            ):
                return {Key.HANDLER: 'member_access'}

        return ScalarLiteral.ch_is(ch)

    @staticmethod
    def handle(ch, parser_state, _):
        if parser_state._debug():
            pass
            # print(f'DEBUG: scalar_literal.handle debug: {parser_state}')

        (info, skip_len, add_line, new_col) = scalar_literal_value(
            parser_state
        )

        gen_type: str = info[0]
        literal: dict = info[1]

        # going to handle the problems that occured
        if literal.get('_warning'):
            print('WARN:', literal['_warning'], repr(
                literal.get(Key.VALUE)), parser_state.line(), parser_state.col())
        if literal.get('_error'):
            print(f"{literal['_error']}, {info}, {parser_state.source()}, "
                  f"idx: {parser_state.idx()}, line: {parser_state.line()}, col: {parser_state.col()}\nview: {parser_state.source_view()}")
            literal_error.literal.find_scalar_error(
                info, parser_state.source(), parser_state.idx(),
                parser_state.line(), parser_state.col()
            )
            raise ValueError(literal)

        # print(literal)

        props = linear_selection_by(
            {
                Key.VALUE: handle_regex_structure(literal)
                if gen_type == 'regex' else literal.get(Key.VALUE),

                'quote_type': literal.get('quote_type'),
                'format_type': literal.get('format_type'),
                Key.KIND: literal.get(Key.KIND)
            },
            # 0 must be preserved, false, none, and empty string must not
            lambda a: a[1] or isinstance(a[1], (int, float))
        )

        return {
            Key.NODE_PROPS:  props,
            Key.NODE_ID:     Node.LITERAL,
            Key.SKIP_TO_IDX: parser_state.idx() + skip_len,
            Key.LINE:        parser_state.line() + add_line,
            Key.COL:         new_col
        }
