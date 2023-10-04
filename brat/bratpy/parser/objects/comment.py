import re
from enum import Enum


class Comment(Enum):
    OPEN = 0
    CLOSE = 1
    MOD_MULTI = 2

    @staticmethod
    def display_name(ref):
        return ('multi-line ' if ref == Comment.MOD_MULTI else '') + 'comment'

    @staticmethod
    def ch_is(ch, ref):
        if not isinstance(ref, Comment):
            raise ValueError(ref)
        return ch == COMMENT_CHARS[ref]

    @staticmethod
    def to_ch(ref):
        if not isinstance(ref, Comment):
            raise ValueError(ref)
        return COMMENT_CHARS[ref]

    @staticmethod
    def from_ch(ch):
        if not isinstance(ch, str):
            raise ValueError(ch)
        return CHARS_TO_COMMENTS[ch]


COMMENT_CHARS = {
    Comment.OPEN: "#",
    Comment.CLOSE: "#",
    Comment.MOD_MULTI: "*"
}

CHARS_TO_COMMENTS = {
    "#": Comment.OPEN,
    "*": Comment.MOD_MULTI
}


Comment.MULTI_OPEN_RE = (
    Comment.to_ch(Comment.OPEN)
    + '\\' + Comment.to_ch(Comment.MOD_MULTI)
)

Comment.MULTI_CLOSE_RE = (
    '\\' + Comment.to_ch(Comment.MOD_MULTI)
    + Comment.to_ch(Comment.CLOSE)
)
