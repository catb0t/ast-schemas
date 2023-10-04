import re
from bratpy.schema_data import Key

from .._parse_common import EOL

from ..objects import ScalarLiteral, SINGLE_INFO, DOUBLE_INFO
from .escapable_literal import escapable_literal_reader, \
    unescaped_delimiter_finder

single_quote = ScalarLiteral.to_ch(ScalarLiteral.STRING, SINGLE_INFO)
double_quote = ScalarLiteral.to_ch(ScalarLiteral.STRING, DOUBLE_INFO)

single_string_reader = escapable_literal_reader(single_quote)
double_string_reader = escapable_literal_reader(double_quote)

unescaped_single_quotes = unescaped_delimiter_finder(single_quote)
unescaped_double_quotes = unescaped_delimiter_finder(double_quote)

''' .5 and 5. are not valid LuaBrat syntax but we support them anyway... '''
number_reader = re.compile(
    r'(?:(\.\d+)|(\d+\.\d+)|(\d+\.)|(\d+))'
)

symbol_reader = re.compile(
    fr'{ScalarLiteral.to_ch(ScalarLiteral.SYMBOL)}(\w+\b)'
)

regex_reader = escapable_literal_reader(
    ScalarLiteral.REGEX_OPEN_RE,
    ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE)
)

LITERAL_RES = {
    single_string_reader: ('string', {'quote_type': SINGLE_INFO}),
    double_string_reader: ('string', {'quote_type': DOUBLE_INFO}),
    number_reader:        ('number', {}),
    symbol_reader:        ('symbol', {'kind': 'symbol'}),
    regex_reader:         ('regex', {'kind': 'regex', 'flags': ''})
}


def multiline_literal_position(obj, old_col):
    new_col = old_col
    add_line = obj.count(EOL)
    if add_line:
        new_col = len(obj) - obj.rindex(EOL)
    return add_line, new_col


def string_quoting_handler(string, roundtrip) -> dict:
    '''
        simple > complex > complicated

        'evaluator' can refer to the deparser or the runtime executing the AST

        if we are handed:
            a single quoted string with unescaped double quotes
                where the evaluator defaults to double quotes

        we must either:
            tell the evaluator to roundtrip with single quotes
                    + default JSON escaping
                -> space: 1 per dq + len(`,"quote_type":"s"`) (18)
                    per such literal
                -> comp:  1 extra string key per such literal

            pre-double-escape all double quotes in the string
                -> space: 3 per double quote
                -> comp:  separate string unescaping operation per such literal

                even for very short inputs like the single-quoted literal:
                    (Brat) '"""' (4 double quotes)
                where the other option is 2 bytes and an object key longer
                    (total 8 + 18 + 4 = 30)
                    this option saves 10 bytes per instance:
                    (JSON string) "'\\\"\\\"\\\"\\\"'"
                but we need to unescape the value after the JSON parser
                    does its unescaping, or else the user will not get their
                    string back!

                -> sorry but this sounds pretty stupid
    '''
    if string.get(Key.KIND) == 'symbol':
        print('Parser bug: must not give a symbol literal to '
              + string_quoting_handler.__name__)
        return string

    if not string.get('quote_type'):
        raise ValueError(
            'Parser bug: must not strip quote_type information from a string'
            ' literal beforing giving it to '
            + string_quoting_handler.__name__)

    # print(roundtrip)

    if roundtrip:
        return string

    # print(unescaped_double_quotes(string.get('value', '')))
    """
        "" are the deparser's default

        "", unescaped "":     (creates multiple strings)
        "", no unescaped "":  default always OK
        "", escaped "":       ...
        "", (un)escaped '':   ...

        '', unescaped '':     (creates multiple strings)
        '', no unescaped '':  default OK, must specify SINGLE_INFO for roundtrip
        '', escaped '':       ...
        '', escaped "":       ...
        '', unescaped "":     must specify SINGLE_INFO in all cases

        TODO BUG: naive '\" in string' test does not respect #{interpolation}
    """

    if not (
        string['quote_type'] == SINGLE_INFO
        and unescaped_double_quotes(string.get('value', ''))
    ):
        string['quote_type'] = ''

    # print(f'rt: {roundtrip}, {string}')
    return string


def double_match_error(literal, is_a, parser_state):
    raise ValueError(
        f"""BUG: {literal[0]} and {is_a[0]} both match input
\tstarting with {repr(parser_state.source_view()[:10])}...
\t(please report!)"""
    )


def scalar_literal_value(parser_state):
    '''
        .' , .@/ , and .. are already rejected by cases.scalar_literal.test
            and handed to member_access

        #{interpolation} is TODO

        regex syntax validation is handled by re.compile, etc
        the translation layer is responsible for regex flag translation
    '''
    # TODO: "#{interpolation}"
    match = None
    literal = ()

    if False:
        print(
            f"testing {parser_state.idx()}"
            f" {repr(parser_state.source_view())}..."
        )
    """ we have to test all the literals; there is no precedence
        but crashes with more than 1 match
    """
    for r, is_a in LITERAL_RES.items():
        m = r.match(parser_state.source_view())
        # print(f"""is a? {is_a} from regex {repr(r)} |  match: {m}""")
        # checks if literal was assigned to in the last iteration
        if parser_state._debug() and m and literal:
            double_match_error(literal, is_a, parser_state)

        elif m:
            match = m
            literal = is_a

    # print(id(literal[1]))

    if match is None:
        return (((), {'_error': 'no-match'}), 0, 0, 0)

    # so fking dumb, i don't want a reference almost never ever
    literal = [literal[0], literal[1].copy()]

    skip_len = match.span()[1]
    # print(f'skip_len {skip_len}')
    # by default, new column is just the single-line literal length
    add_line, new_col = 0, parser_state.col() + skip_len

    ''' re.match always has 2 capturing groups
        second capture (i.e match.group(2)) will be 'pattern' '''
    if literal[0] == 'regex':
        literal[1]['flags'] = (
            ScalarLiteral.normalize_regex_flags(match.group(1))
        )
        literal[1]['value'] = value = match.group(2)
        # print(literal)

    elif literal[0] == 'number':
        value = match.group(0)
    # symbol and string don't want the leading : ' "
    else:
        value = match.group(1)

    ''' symbols and numbers may not contain \\n
        strings and regexes can'''
    if literal[0] not in ('symbol', 'number'):

        ''' if you're not going to split the string anyway (like comment_value)
            then we shouldn't use len(.split) '''
        add_line, new_col = multiline_literal_position(
            match.group(0), new_col
        )

        if literal[0] == 'string':
            #   print(f"`{value}`, {new_col}")
            if value:
                literal[1]['value'] = value

            should_be_symbol = symbol_reader.fullmatch(':' + value)
            if should_be_symbol is not None and should_be_symbol.group(1):
                literal[1]['_warning'] = 'string-should-be-symbol'
                literal[1]['kind'] = 'symbol'
                literal[1]['quote_type'] = ''
                literal = ('symbol', literal[1])
            else:
                literal[1] = string_quoting_handler(
                    literal[1], parser_state.roundtrip()
                )

    else:  # symbol or number
        ''' in Lua, all numbers are double-precision, so this behaviour clones
            LuaBrat.
            the distinction between [i]nt, [l]eft decimal, [m]iddle decimal,
            and [r]ight decimal is purely for roundtrip / strict mode.
        '''
        if literal[0] == 'number':
            # print(f"VALUE: {value} roundtrips {roundtrip}")
            if parser_state.roundtrip():
                try:
                    sep_idx = value.index('.')
                except ValueError:
                    sep_idx = None
                # print('SEP', sep)
                ''' left, right, middle, int
                     .5     5.     5.0    5

                    LuaBrat only supports middle and int
                '''
                literal[1]['format_type'] = (
                    'l' if sep_idx == 0
                    else 'r' if sep_idx == len(value) - 1
                    else 'i' if sep_idx is None
                    else 'm'  # len(value) - 1 > idx > 0
                )
                value = float(value)
            else:
                fval = float(value)
                if int(fval) == fval:
                    value = int(fval)
                else:
                    value = fval

        literal[1]['value'] = value

    return (literal, skip_len, add_line, new_col)
