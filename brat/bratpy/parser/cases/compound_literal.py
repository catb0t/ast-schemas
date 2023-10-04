from bratpy.schema_data import Key
from ..objects import CompoundLiteral, Node
from ..node_readers import compound_literal_value


class compound_literal():
    @staticmethod
    def test(ch, **_):

        return CompoundLiteral.ch_is_open(ch)

    @staticmethod
    def handle(ch, parser_state, create_node):

        parser_state.inc_idx(len(CompoundLiteral.ch_open()))
        parser_state.inc_col(len(CompoundLiteral.ch_open()))
        parser_state.push_scope('(compound literal value at file '
                                f'"{parser_state.fname()}" '
                                f'{parser_state.line()}:{parser_state.col()})')

        # print("CompoundLiteral handler", parser_state)

        initial_kind, basic_literal = compound_literal_value(parser_state)
        # print(f"literal_info: {literal_value}")

        parser_state.pop_scope()
        # print("CompoundLiteral handler pop scope ", )
        # print("CompoundLiteral handler after pop ", parser_state)

        parser_state.inc_idx(len(CompoundLiteral.ch_close()))
        parser_state.inc_col(len(CompoundLiteral.ch_close()))

        kind, literal_value = CompoundLiteral.make_deep(
            initial_kind, basic_literal
        )

        literal = {
            Key.VALUE: literal_value
        }

        print(literal)

        if isinstance(literal, dict) and kind:
            literal.update({Key.KIND: kind})

        return {
            Key.NODE_PROPS:   literal,
            Key.NODE_ID:      Node.LITERAL,
            Key.SKIP_TO_IDX:  parser_state.idx(),
            Key.LINE:         parser_state.line(),
            Key.COL:          parser_state.col()
        }
