import re
from ..objects import Comment
from .._parse_common import EOL
from .escapable_literal import escapable_literal_reader

# read forward in the source to get the name of the operator
# stops when it finds an unescaped separator or brace
# operator_reader = re.compile(r'^(?:`[`\n\t {}]|[^`\n\t {}])+')
single_comment_reader = re.compile(
    rf'^{Comment.to_ch(Comment.OPEN)}([^\n]*)(\n?)'
)

multi_comment_reader = escapable_literal_reader(Comment.MULTI_OPEN_RE,
                                                Comment.MULTI_CLOSE_RE)


def comment_value(parser_state, multi):
    '''
        read a comment value from the source. not in the RI, just
        for fun as a proof of concept. returns a tuple:
            (note, extends_to_eof, skip_ahead_by, add_line, new_col)

        the unused arg is roundtrip, which we don't need, since this is
            basically like a string
    '''
    if not multi:
        comment = single_comment_reader.match(parser_state.source_view())
        is_eof = not comment.group(2)
        skip_len = comment.span()[1]
        if False and parser_state._debug:
            print(
                f"comment debug:\n\tmatch: {repr(comment)}, {is_eof}, {skip_len}")

        comment_note = comment.group(1).rstrip()
        new_col = parser_state.col() + skip_len

        add_line = 0

        if not is_eof:
            if skip_len > 1:
                skip_len -= 1

        return (
            comment_note, is_eof, skip_len,
            add_line, 1 if not is_eof else new_col
        )

    # the length of the multiline comment syntax #* at the beginning and end
    multi_comment_syntax_len = 2
    # whether this comment extends to eof
    is_eof = False
    comment = multi_comment_reader.match(parser_state.source_view())
    # if the regex doesn't match, this is a comment which extends to the end
    #   of the source
    if comment is None:
        is_eof = True
        comment = parser_state.source_view()[2:]
        comment_len = len(comment) + multi_comment_syntax_len
    # otherwise all is straightforward
    else:
        comment_len = comment.span()[1]
        comment = comment.group(1)

    comment_lines = comment.split('\n')

    # this min call is probably not necessary but it makes me feel good :)

    # add_line is how many source lines the comment occupies
    #   (how many to add to the parser position)
    add_line = min(comment.count(EOL), len(comment_lines))
    # print(add_line, comment_lines)

    # we are going to adjust the parser's column position to the column where
    #   the comment ended
    # columns are 1-based
    new_col = 1
    if add_line:
        # if the comment spans multiple lines, take the length of the last line
        #   and only add 2 cols if it ended with *#, or add 0 cols if it's EOF
        new_col += len(comment_lines[-1]) + (multi_comment_syntax_len
                                             if not is_eof else 0)
    else:
        # if the comment only spans 1 line, take the length of its only line
        #   and add just 2 cols for one opening #* if EOF, or 4 for both #* *#
        #   if it isn't EOF
        new_col = parser_state.col() + len(comment_lines[0]) \
            + multi_comment_syntax_len \
            + (multi_comment_syntax_len if not is_eof else 1)

        # print(f'new_col: {new_col}')

    return comment_lines, is_eof, comment_len, add_line, new_col
