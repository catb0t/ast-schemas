from bratpy.util import Key

from ...schema_data import linear_selection_by
from ..node_readers import comment_value
from ..objects import Comment, Node

from .._parse_common import get_next_ch


class comment():
    @staticmethod
    def test(ch, **_):
        return Comment.ch_is(ch, Comment.OPEN)

    @staticmethod
    def handle(ch, parser_state, create_node):
        if parser_state._debug():
            print(f'DEBUG: comment.handle: {parser_state}')

        multi = Comment.ch_is(
            get_next_ch(parser_state.source(), parser_state.idx()),
            Comment.MOD_MULTI
        )

        (comment_lines, is_eof,
         skip_len, add_line, new_col) = comment_value(
            parser_state,
            multi
        )

        if parser_state._debug():
            print(
                f"skip_len: {skip_len} add_line: {add_line} new_col: {new_col} multi: {multi}\n{parser_state}"
            )

        props = linear_selection_by(
            {
                'multi': multi,
                'note': comment_lines,
                'extends_to_eof': is_eof
            },
            lambda a: a[1] if not isinstance(a[1], list) else any(a[1])
        )

        return {
            Key.NODE_PROPS:  props,
            Key.NODE_ID:     Node.COMMENT,
            Key.SKIP_TO_IDX: parser_state.idx() + skip_len,
            Key.LINE:        parser_state.line() + (add_line if multi else 0),
            Key.COL:         new_col
        }
