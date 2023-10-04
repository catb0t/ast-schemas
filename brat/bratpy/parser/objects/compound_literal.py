import copy
from bratpy.schema_data import Key, recursive_all
from enum import Enum
from .node import Node


class CompoundLiteral(Enum):
    '''
        hashes:
            [a:1]
            a is a bareword.
            to use a bareword-eligible variable name's value as a key, use:
            [(a):1]

            "Node.property" cannot be the name of a bareword, so the following
                are equivalent:
            [Node.property:4]
            [(Node.property):4]

            [(some.expression? 3, 34): 'some key', blah: val]
                the expression key must appear in parens unless it is a
                simple var


        hashes and symbols:
        there must be no ambiguity when parsing hashes containing
            symbol :syntax.

        the following are not amgbiguous with respect to eachother:
            [1::a] ("1" => Symbol('a'))
            [1:a]  ("1" => NameVar('a'))

        the ambiguity arises when parsing [1:a], because this could be:
            [1, Symbol('a')] or
            [1 => NameVar('a')]
        but because square brackets are used for both, and
            whitespace and commas are optional, it is impossible to
            know for sure.

        in my opinion, the best thing to do in this case without creating
            bad edge cases and rule exceptions is to parse as follows
            [1:a] ("1" => NameVar('a'))
        a warning should be displayed. any use of commas or whitespace around
            the values will disambiguate this expression,
            [1: a]
            [1 :a]
            [1,:a]
            [1:, a] (syntax error, mixing hash and array syntax in a literal)
        and a double colon can still be used to force a
            symbol hash value
            [1::a]

        as a consequence of barewords in hashes, numeric keys are stringified.
            this also has a benefit for inexact float keys.

        sorry, but Python's behaviour:
            {1:2} != {'1':2}
        is really, really bad in the context of barewords as above,

        of course, Python does not have barewords in dict keys, but since
            Brat does, it would be logical for Brat not to consider
            these different (which it does):
            [1:2] != ['1':2]

        the following are equivalent:
            [1:a]
            [(1):a]
            ['1':a]
            [('1'):a]
    '''
    BASIC_ARRAY = 1
    BASIC_HASH = 2
    BASIC_ASSOC = 3
    BASIC_EXPRKEY = 4
    DEEP_ARRAY = 5
    DEEP_HASH = 6
    DEEP_ASSOC = 7
    DEEP_EXPRKEY = 8
    OPEN = 9
    CLOSE = 10

    @staticmethod
    def display_name(ref):
        return DISPLAY_NAMES.get(ref, 'compound') + ' literal object'

    @staticmethod
    def ch_is(ch):
        return ch in {COMPOUND_OPEN, COMPOUND_CLOSE}

    @staticmethod
    def ch_is_open(ch):
        return ch == COMPOUND_OPEN

    @staticmethod
    def ch_is_close(ch):
        return ch == COMPOUND_CLOSE

    @staticmethod
    def to_ch(val):
        return COMPOUND_CHARS_DICT[val]

    def ch_open():
        return CompoundLiteral.to_ch(CompoundLiteral.OPEN)

    def ch_close():
        return CompoundLiteral.to_ch(CompoundLiteral.CLOSE)

    def deepen(val):
        if isinstance(val, list):
            return list(map(CompoundLiteral.deepen, val))
        elif isinstance(val, dict):
            return CompoundLiteral.deepen(val[Key.VALUE])
        else:
            return val

    def make_deep(initial_kind, basic_literal):
        if not len(basic_literal):
            return initial_kind, basic_literal

        rec_key = Key.VALUE

        def rec_key_func(v):
            return isinstance(v, list)

        def cond(_, val):
            return isinstance(val, dict) \
                and Node.node_is(val.get(Key.ID), Node.LITERAL)

        if recursive_all(basic_literal, rec_key, rec_key_func, cond):
            literal = copy.deepcopy(basic_literal)
            literal = CompoundLiteral.deepen(literal)
            return MAKE_DEEP_KIND_CONV.get(initial_kind), literal

        return initial_kind, basic_literal


MAKE_DEEP_KIND_CONV = {
    None: 'deep_array',
    'hash': 'deep_hash',

    # 'exprkey': 'deep_exprkey',
    # 'assoc': 'deep_assoc'
}


COMPOUND_OPEN = '['
COMPOUND_CLOSE = ']'

COMPOUND_CHARS_DICT = {
    CompoundLiteral.OPEN: COMPOUND_OPEN,
    CompoundLiteral.CLOSE: COMPOUND_CLOSE


}

CHARS_TO_COMPOUNDS = {
    COMPOUND_OPEN: CompoundLiteral.OPEN,
    COMPOUND_CLOSE: CompoundLiteral.CLOSE
}


DISPLAY_NAMES = {
    CompoundLiteral.BASIC_ARRAY:   'array',
    CompoundLiteral.BASIC_HASH:    'hash',
    CompoundLiteral.BASIC_ASSOC:   'associative array',
    CompoundLiteral.BASIC_EXPRKEY: 'expression-keyed hash',

    CompoundLiteral.DEEP_ARRAY:   'array (containing only literals)',
    CompoundLiteral.DEEP_HASH:    'hash (containing only literals)',
    CompoundLiteral.DEEP_ASSOC:   'associative array (containing only literals)',
    CompoundLiteral.DEEP_EXPRKEY: 'expression-keyed hash (containing only literals)'
}
