from bratpy.util import Key
from ..objects import ScalarLiteral, CompoundLiteral

DEFAULT_QUOTE_TYPE = 'd'

_deparse = None


def literal_shared_name(*args):
    global _deparse
    _deparse, *_ = args


def replace_compound_literal(val):
    return ''.join((
        CompoundLiteral.to_ch(CompoundLiteral.OPEN),
        _deparse(val.get(Key.VALUE)),
        CompoundLiteral.to_ch(CompoundLiteral.CLOSE)
    ))


def roundtrip_number(value, format_type=None):
    if format_type == 'm' or format_type is None:
        return str(value)

    elif format_type == 'i':
        return str(int(value))

    value = str(value)
    try:
        sep_idx = value.index('.')
    except ValueError:
        sep_idx = None

    if format_type == 'r':
        if sep_idx is None:
            return value + '.'

        return value[:sep_idx + 1]

    elif format_type == 'l':
        if sep_idx is None:
            return '.' + value

        return value[sep_idx:]

    raise ValueError('garbage format_type: ' + format_type)


def replace_literal(val):
    if val.get('kind') == 'regex':
        return (''.join((
            ScalarLiteral.to_ch(ScalarLiteral.REGEX_OPEN),
            val['value'].get('flags'),
            ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE),
            val['value'].get('pattern'),
            ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE)
        )) if isinstance(val.get('value'), dict) else ''.join((
            ScalarLiteral.to_ch(ScalarLiteral.REGEX_OPEN),
            ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE),
            val.get('value', ''),
            ScalarLiteral.to_ch(ScalarLiteral.REGEX_CLOSE)
        )))

    if val.get('kind') == 'symbol':
        return ScalarLiteral.to_ch(ScalarLiteral.SYMBOL) + val['value']

    if isinstance(val.get('value'), (float, int)):
        return roundtrip_number(val['value'], val.get('format_type'))

    if isinstance(val.get(Key.VALUE), list) \
            or isinstance(val.get(Key.VALUE), dict):
        return replace_compound_literal(val)

    # print(val)
    quote = ScalarLiteral.to_ch(
        ScalarLiteral.STRING,
        info=val.get('quote_type', DEFAULT_QUOTE_TYPE)
    )
    return quote + val.get(Key.VALUE, '') + quote
