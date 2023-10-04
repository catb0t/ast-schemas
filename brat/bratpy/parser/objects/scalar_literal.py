from enum import Enum

from ...schema_data import linear_selection_by

class ScalarLiteral(Enum):
    '''
        contains the literal type enum values (number, string etc).

        to prevent ambiguity, regexes only start with @/, not /, otherwise
            operator precedence is the only thing preventing 1 /some_regex/ 2
            from parsing as 1 DIVIDE some_regex DIVIDE 2 instead, etc
            which i have always thought is a very bad feature of languages
            where / is both open_regex and divide (js, perl, ruby, luabrat etc)

        using R/ from Factor is tempting, but that could be a variable /
            method as as it starts with a letter

        you can still have an infix method named '@' and use 1 @ @/some_regex/2
            (i.e. 1.@(@/some_regex/), 2) but it's never ambiguous because
            there's always 2 definite characters to start the regex.
    '''

    NUMBER = 0
    STRING = 1
    SYMBOL = 2
    REGEX_OPEN = 3
    REGEX_CLOSE = 4

    @staticmethod
    def display_name(ref):
        return DISPLAY_NAMES.get(ref, '(no display name) scalar') + ' literal object'

    @staticmethod
    def ch_is(ch: str):
        return ch in NUMBER_CHARS or ch == SYMBOL_CHAR or ch in STRING_CHARS \
            or ch == REGEX_CHAR

    @staticmethod
    def ch_is_numeric(ch: str):
        return ch.isdigit() or ch == DECIMAL_SEP

    @classmethod
    def ch_is_unfinished_literal(cls, ch: str):
        'the only literals representable in just one character are numbers'
        return (
            cls.ch_is(ch) and not ch.isdigit()
        )

    @classmethod
    def to_ch(cls, ref, info=None):
        '''
            for string deparsing, `info` should be either `d` or `s` to
                indicate the quote style of the original string literal
        '''
        if not isinstance(ref, ScalarLiteral):
            raise ValueError(ref)

        if info is None and ref in (
            cls.REGEX_OPEN, cls.REGEX_CLOSE, cls.SYMBOL
        ):
            # i know it SOUNDS ridiculous, but try to get the ref in the regex
            #   lookup, and if that fails, get the symbol : instead
            # because SYMBOL_CHARS is not in CHARS_TO_REGEXES
            return CHARS_TO_REGEXES.get(ref, SYMBOL_CHAR)

        if ref == cls.STRING:
            # defaulting to double quotes so that apostrophes are likely to
            #   deparse correctly; the deparser must error when a quote type
            #   is required but not stored
            if info is None:
                info = 'd'
            return STRING_CHARS[STRING_INFO.index(info)]

        # no boilerplate for literal numbers
        return ''

    @staticmethod
    def normalize_regex_flags(flags):
        # print(f"Regex flags: {repr(flags)}")
        norm = ''.join(linear_selection_by(
            dict.fromkeys(flags),
            lambda a: a[0] in REGEX_FLAG_CHARS
        ).keys())
        # print(f"Norm: {repr(norm)}")
        return norm


DIGIT_CHARS  = '0123456789'
DECIMAL_SEP  = '.'
NUMBER_CHARS = DIGIT_CHARS + DECIMAL_SEP
STRING_CHARS = '\'"'
SYMBOL_CHAR  = ':'
REGEX_CHAR   = '@'

REGEX_FLAG_CHARS = 'aAiIlLmMsSxX'

SINGLE_INFO = 's'
DOUBLE_INFO = 'd'
STRING_INFO = SINGLE_INFO + DOUBLE_INFO
NUMBER_INFO = 'lirm'

REGEX_CHARS_DICT = {
    REGEX_CHAR: ScalarLiteral.REGEX_OPEN,
    '/': ScalarLiteral.REGEX_CLOSE
}

CHARS_TO_REGEXES = {
    ScalarLiteral.REGEX_OPEN: REGEX_CHAR,
    ScalarLiteral.REGEX_CLOSE: '/'
}

# @<flags>/ starts a regex
ScalarLiteral.REGEX_OPEN_RE = (
    ScalarLiteral.to_ch(ScalarLiteral.REGEX_OPEN)
    + '([' + REGEX_FLAG_CHARS + r'\s]*)'
    + ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE)
)

# / closes a regex
ScalarLiteral.REGEX_CLOSE_RE = (
    r'[^\\' + ScalarLiteral.to_ch(ScalarLiteral.REGEX_OPEN) + ']'
    + ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE)
)

ScalarLiteral.REGEX_INVALID_OPEN_RE = (
    ScalarLiteral.to_ch(ScalarLiteral.REGEX_OPEN)
    + '([^' + REGEX_FLAG_CHARS + r'\s]*)'
    + ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE)
)

DISPLAY_NAMES = {
    ScalarLiteral.NUMBER:      'number',
    ScalarLiteral.STRING:      'string',
    ScalarLiteral.SYMBOL:      'symbol',
    ScalarLiteral.REGEX_OPEN:  'RegEx',
    ScalarLiteral.REGEX_CLOSE: 'RegEx'
}
