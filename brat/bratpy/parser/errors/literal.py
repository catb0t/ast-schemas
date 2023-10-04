import re
from enum import Enum

from ..objects import ScalarLiteral, SINGLE_INFO, DOUBLE_INFO
from ..node_readers import escapable_literal_reader


class literal():

    class reasons(Enum):
        # ' " : @/
        UNCLOSED_SCALAR_LITERAL = 0
        # [
        UNCLOSED_COMPOUND_LITERAL = 1
        # ]
        UNOPENED_COMPOUND_LITERAL = 2
        # "#{false"
        UNCLOSED_STRING_INTERPOLATION = 3

        # @garbage//, @l/str pattern/
        BAD_REGEX_FLAGS = 4
        # @/\/, @/[\]/, @/(/, @/(\)/, @/)/
        BAD_REGEX_PATTERN = 5
        # [:], [-], [;] etc for syntax + operators inside compounds
        BAD_COMPOUND_LITERAL = 6
        # the interpolation had a parser error. the details of the error follow
        # "#{'}" -> BAD_INTERPOLATION, cause: UNCLOSED_SCALAR_LITERAL
        BAD_INTERPOLATION = 7

    def __init__(self, reason, fname, source, idx, pos1, cause):
        self.reason = reason
        self.fname = fname
        self.source = source
        self.idx = idx
        self.pos1 = pos1
        self.cause = cause

    def title(self):
        pass

    @classmethod
    def find_scalar_error(cls, info, source, idx, line, col, _debug=False):
        match = None
        literal_info = ()

        for kind, tests in INVALID_SCALAR_RES.items():
            print(f'error.literals looking at {kind}')
            for test_tuple in tests:
                print(test_tuple)
                regex, is_a = test_tuple
                m = regex.match(source)
                if _debug and m and literal_info:
                    assert False, (
                        f'{literal_info[0]} and {is_a[0]} both match'
                        f' input starting with {repr(source[:10])} (please report)'
                    )
                elif m:
                    match = m
                    literal_info = is_a

        print(literal_info)
        if match is None:
            raise ValueError('no match?')

        literal_info = [literal_info[0], literal_info[1].copy()]

        __import__('sys').exit()

    @classmethod
    def find_compound_error(cls, info, source, idx, line, col):
        pass


INCOMPLETE_LITERAL_DISPLAY = (
    'Stray {target_char_name}',
    'no matching {matching_char_name} `{matching_char}`'
)

DISPLAYS = {
    literal.reasons.UNCLOSED_SCALAR_LITERAL:        INCOMPLETE_LITERAL_DISPLAY,
    literal.reasons.UNCLOSED_COMPOUND_LITERAL:      INCOMPLETE_LITERAL_DISPLAY,
    literal.reasons.UNOPENED_COMPOUND_LITERAL:      INCOMPLETE_LITERAL_DISPLAY,
    literal.reasons.UNCLOSED_STRING_INTERPOLATION:  ('Unterminated string interpolation', 'no matching close brace `}`'),

    literal.reasons.BAD_REGEX_FLAGS:        ('Bad RegEx flags: {regex_error_cut}', 'flag{flags_plural} `{bad_flags}` {regex_error_full}'),
    literal.reasons.BAD_REGEX_PATTERN:      ('Bad RegEx pattern: {regex_error_cut}', '... `{pattern_context}` ...: {regex_error_full}'),
    literal.reasons.BAD_COMPOUND_LITERAL:   ('Ill-formed compound literal', '{target_char_name} `{target_char}` cannot appear here'),
    # Bad Interpolation is always a parent of another parser error
    literal.reasons.BAD_INTERPOLATION:      ('In string interpolation', 'syntax error in string interpolation'),
}

single_quote = ScalarLiteral.to_ch(ScalarLiteral.STRING, SINGLE_INFO)
double_quote = ScalarLiteral.to_ch(ScalarLiteral.STRING, DOUBLE_INFO)

unclosed_single_string = escapable_literal_reader(
    single_quote, unclosed=True)
unclosed_double_string = escapable_literal_reader(
    double_quote, unclosed=True)

nameless_symbol = re.compile(
    fr'{ScalarLiteral.to_ch(ScalarLiteral.SYMBOL)}(?!\w+\b)'
)

unclosed_regex = escapable_literal_reader(
    ScalarLiteral.REGEX_OPEN_RE,
    ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE),
    unclosed=True
)

bad_regex_flags = escapable_literal_reader(
    ScalarLiteral.REGEX_INVALID_OPEN_RE,
    ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE),
    unclosed='allow'
)
bad_regex_pattern = re.compile('bad_regex')

# TODO
# invalid_interpolation = re.compile('$$$__BAD_INTERPOLATION_TODO')

# there are no invalid ways to write a number that are handled by
# a literal handler -- they cause errors in member_access, etc

# bad_regex_flags, bad_regex_pattern, and unclosed_regex must NOT
# all be exclusive regexes, or else an unclosed regex with bad flags
# will not match either bad_regex_flags nor unclosed_regex
INVALID_SCALAR_RES = {
    'string': (
        (unclosed_single_string, literal.reasons.UNCLOSED_SCALAR_LITERAL),
        (unclosed_double_string, literal.reasons.UNCLOSED_SCALAR_LITERAL),
        # TODO: (invalid_interpolation, literal.reasons.UNCLOSED_STRING_INTERPOLATION)
    ),
    'symbol': (
        (nameless_symbol, literal.reasons.UNCLOSED_SCALAR_LITERAL),
    ),
    'regex': (
        (bad_regex_flags, literal.reasons.BAD_REGEX_FLAGS),
        (unclosed_regex, literal.reasons.UNCLOSED_SCALAR_LITERAL),
        (bad_regex_pattern, literal.reasons.BAD_REGEX_PATTERN),
        # TODO: (invalid_interpolation, literal.reasons.UNCLOSED_STRING_INTERPOLATION)
    )
}
