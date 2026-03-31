from enum import Enum


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
