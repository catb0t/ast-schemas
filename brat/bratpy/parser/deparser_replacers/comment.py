from ..objects import Comment


def literalize_single_comment_line(note):
    return (
        note if isinstance(note, str)
        # TODO: repr non-string elements
        else ' '.join(str(note[i]) for i in note)
    )


def replace_comment(val):
    if 'multi' not in val:
        return ''.join((
            Comment.to_ch(Comment.OPEN),
            literalize_single_comment_line(val['note'])
            if 'note' in val else ''
        ))
    return ''.join((
        Comment.to_ch(Comment.OPEN),
        Comment.to_ch(Comment.MOD_MULTI),
        '\n'.join(
            (literalize_single_comment_line(line)
             for line in val['note']) if val.get('note') else ()
        ),
        (
            (Comment.to_ch(Comment.MOD_MULTI) + Comment.to_ch(Comment.CLOSE))
            if not val.get('extends_to_eof') else ''
        )
    ))
