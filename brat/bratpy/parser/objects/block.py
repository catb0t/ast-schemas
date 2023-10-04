from enum import Enum


class Block(Enum):
    OPEN  = 0
    CLOSE = 1

    @staticmethod
    def ch_is(ch, base):
        if not isinstance(base, Block):
            raise ValueError(base)
        return ch == BLOCK_CHARS[base]

    @staticmethod
    def to_ch(base):
        if not isinstance(base, Block):
            raise ValueError(base)
        return BLOCK_CHARS[base]

    @staticmethod
    def from_ch(ch):
        if not isinstance(ch, str):
            raise ValueError(ch)
        return CHARS_TO_BLOCKS[ch]


BLOCK_CHARS = {
    Block.OPEN: '{',
    Block.CLOSE: '}'
}

CHARS_TO_BLOCKS = {
    '{': Block.OPEN,
    '}': Block.CLOSE
}
