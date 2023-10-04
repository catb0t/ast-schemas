import re
from enum import Enum

from .objects import Block
from ._parse_common import ESCAPE, EOL


class CantParse(Enum):
    STRAY_CLOSE = 0
    STRAY_OPEN = 1


MESSAGES = {
    CantParse.STRAY_CLOSE: ('close', 'open'),
    CantParse.STRAY_OPEN: ('open', 'close')
}

ERROR_FORMAT = "\n\nWhen parsing form {form}\n{bridge}\n{ptr}\nStray {kind} brace at line {line}, column {col}\n\t-> <{fname}>:{line}:{col}\n\t-> no matching {unkind} brace (did you mean to ` escape it?)"


class ParseError(Exception):

    def __init__(self, fname, reason, source, begin, end, offset, idx, line, col):
        self.fname = fname
        self.reason = reason
        self.source = source
        self.begin = begin
        self.end = end
        self.idx = idx
        self.offset = offset
        self.line = line
        self.col = col

    def __str__(self):
        kind, unkind = MESSAGES[self.reason]
        spaces = ' ' * (
            19 + self.offset + sum(self.source.count(s) for s in ("\n", "\t")))
        return ERROR_FORMAT.format(
            kind=kind,
            unkind=unkind,
            fname=self.fname,
            bridge=spaces + '|',
            ptr=spaces + '^ HERE',
            line=self.line,
            col=self.col,
            form=repr(self.source[self.begin:self.end])
        )


# find unescaped open braces
unesc_opens = re.compile(r'(?<![^`]`)' + Block.to_ch(Block.OPEN))
# find unescaped close braces
unesc_closes = re.compile(r'(?<![^`]`)' + Block.to_ch(Block.CLOSE))


def _count_found(use, source):
    '''the number of times the regex `use` matched `source`'''
    return len(re.findall(use, source))


def unbalanced_braces(source):
    '''
        test whether a program has balanced unescaped open/close braces

        result is true if the program is broken
    '''
    return (_count_found(unesc_opens, source)
            != _count_found(unesc_closes, source))


def _list_finditer(use, source):
    '''finditer(use, source) but not a generator'''
    return list(re.finditer(use, source))


def _create_context(source, idx):
    '''create the context for parser error messages'''
    closes_after = _list_finditer(unesc_closes, source[idx:])
    opens_before = _list_finditer(unesc_opens,  source[:idx])

    # where the context should begin
    return (
        opens_before[
            -2 if len(opens_before) > 1 else 0
        ].span()[0],
        idx + closes_after[
            1 if len(closes_after) > 1 else 0
        ].span()[1]
    )


def brace_match(fname, source, line, col):
    '''
        find unmatched braces in the source.

        matches from left-to-right. in `{ { }`, the first open brace will be
            found to match the close brace, so the second open brace will be
            considered stray and reported as an error.

        similarly, in `{ } }`, the first pair of braces will match, and the
            last brace will be considered stray.
    '''
    # should escape the next char / have we seen an open brace yet
    escape_next = seen_open = False
    depth = 0
    # total number of unescaped close braces for the entire source
    count_close = _count_found(unesc_closes, source)
    for idx, ch in enumerate(source):
        if escape_next:
            escape_next = False
            # print(f"escaped {repr(ch)} at {idx} ({line}:{col-1})")
            col += 1
            continue

        if ch == ESCAPE:
            escape_next = True
        elif ch == EOL:
            col = 1
            line += 1
            continue

        elif Block.ch_is(ch, Block.OPEN):
            # looking for STRAY OPENS
            seen_open = True
            depth += 1
            offset = 2
            # there are no close braces in this program
            if count_close == 0:
                raise ParseError(fname, CantParse.STRAY_OPEN, source,
                                 idx - offset, len(source), offset,
                                 idx, line, col)

            # we have gone deeper than we can return from
            if depth > count_close:
                begin, end = _create_context(source, idx)
                raise ParseError(fname, CantParse.STRAY_OPEN, source, begin,
                                 end, idx - begin, idx, line, col)

        elif Block.ch_is(ch, Block.CLOSE):
            # looking for STRAY CLOSES
            depth -= 1
            offset = 2
            if not seen_open:
                raise ParseError(fname, CantParse.STRAY_CLOSE, source, 0,
                                 idx + offset, 0, idx, line, col)
            if depth < 0:
                begin, end = _create_context(source, idx)
                raise ParseError(fname, CantParse.STRAY_CLOSE, source, begin,
                                 end, idx - begin, idx, line, col)
        col += 1
    return depth


def bad_literal(reason, source, idx, line, col):
    raise ValueError("ERROR IS TODO")
