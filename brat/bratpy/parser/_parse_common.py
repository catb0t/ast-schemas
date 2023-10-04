import copy
from enum import Enum
import re

from jsonschema import Draft7Validator
from bratpy.schema_data import BRAT_SCHEMA
from .objects import NoLastID

# our separators
SEP_STR = ' \n\t'
# lexical escape for anything that follows it including space/tab/newline
ESCAPE = '\\'
EOL = '\n'


Draft7Validator.check_schema(BRAT_SCHEMA)
BratValidator = Draft7Validator(BRAT_SCHEMA)


def check_skip(val):
    if val is DoNotSkip or isinstance(val, _DoNotSkip):
        raise ValueError(
            'OOPS! real value for `skip_to_idx` required in this context'
            '\n\t(instead, it was a singleton NoLastID)\n\tparser bug found!'
        )
    return val


def get_next_ch(source, idx=0):
    if idx >= len(source) - 1:
        print("get_next_ch: no next ch (reached end of source)")
        return ''
    return source[idx + 1]


def count_matches(r, s):
    return sum(1 for _ in r.finditer(s))


class _DoNotSkip:
    def __init__(self):
        pass

    def __lt__(self, rhs):
        return False

    def __gt__(self, rhs):
        return False

    def __eq__(self, rhs):
        return self is rhs

    def __ge__(self, rhs):
        return self is rhs

    def __le__(self, rhs):
        return self is rhs

    def __repr__(self):
        return "(DoNotSkip)"


DoNotSkip = _DoNotSkip()


class Scope:
    name = None
    source_idx = None
    skip_to_idx = None
    line = None
    col = None
    last_id = None

    def __init__(
        self,
        name='(anonymous lexical scope)',
        source_idx=0,
        line=1,
        col=1,
        skip_to_idx=DoNotSkip,
        last_id=NoLastID
    ):
        self.name = name
        self.source_idx = source_idx
        self.line = line
        self.col = col
        self.skip_to_idx = skip_to_idx
        self.last_id = last_id

    def __repr__(self):
        return f"""Scope(
    name='{self.name}'
    source_idx={self.source_idx},
    line={self.line},
    col={self.col},
    skip_to_idx={self.skip_to_idx},
    last_id={self.last_id},
)"""

    def deepen(self, name):
        """copy into a deeper scope"""
        return Scope(
            name, self.source_idx, self.line,
            self.col, DoNotSkip, NoLastID
        )


class ParserState:
    _source = None
    _fname = None
    _scope_stack = None
    _depth = 0
    _roundtrip = None
    _is_debug = None

    def __init__(
        self,
        source,
        fname='<input>',
        outer_scope_name='(top level scope)',
        roundtrip=False,
        _debug=False,
    ):
        self._source = source
        self._fname = fname
        self._scope_stack = {}
        self._depth = 0
        self._roundtrip = roundtrip
        self._is_debug = _debug

        self._scope_stack[self._depth] = Scope(name=outer_scope_name)

    def __repr__(self):
        return f"""ParserState(
    source='{self.source()[:60]}{'...' if len(self.source()) > 60 else ''}',
    fname='{self.fname()}',
    depth={self.depth()},
    scope_stack={self.scope_stack()},
    roundtrip={self.roundtrip()},
    _debug={self._debug()},
)"""

    def push_scope(self, name):
        new_depth = self._depth + 1
        if self._scope_stack.get(new_depth) is not None:
            raise ValueError(
                f"requested scope depth {new_depth} already exists and isn't current: new scope '{name}' stack {self._scope_stack}"
            )

        self._scope_stack[new_depth] = (
            self._scope_stack[self._depth]
            .deepen(name)
        )

        self._depth = new_depth
        return new_depth

    def pop_scope(self):
        if self._depth == 0:
            raise ValueError('pop from empty Scope Stack!')
        old_scope = self._scope_stack.pop(self._depth)
        self._depth -= 1
        # copy skip_to_idx?
        self.set_idx(old_scope.source_idx)
        self.set_line(old_scope.line)
        self.set_col(old_scope.col)
        self.set_skip_to_idx(old_scope.skip_to_idx)
        return old_scope

    def current_scope(self):
        return self._scope_stack[self._depth]

    def copy(self):
        res = ParserState(
            source=self.source(), fname=self.fname(),
            roundtrip=self.roundtrip(), _debug=self._debug()
        )
        res._depth = self._depth
        res._scope_stack = copy.deepcopy(self.scope_stack())
        return res

    def source(self):
        return self._source

    def depth(self):
        return self._depth

    def fname(self):
        return self._fname

    def roundtrip(self):
        return self._roundtrip

    def scope_stack(self):
        return self._scope_stack

    def _debug(self):
        return self._is_debug

    def source_view(self):
        return self._source[self.idx():]

    def idx(self):
        return self.current_scope().source_idx

    def set_idx(self, idx):
        self.current_scope().source_idx = idx

    def inc_idx(self, add=1):
        self.current_scope().source_idx += add
        return self.current_scope().source_idx

    def line(self):
        return self.current_scope().line

    def set_line(self, line):
        self.current_scope().line = line

    def inc_line(self, add=1):
        self.current_scope().line += add
        return self.current_scope().line

    def col(self):
        return self.current_scope().col

    def set_col(self, col):
        self.current_scope().col = col

    def inc_col(self, add=1):
        self.current_scope().col += add
        return self.current_scope().col

    def skip_to_idx(self):
        return self.current_scope().skip_to_idx

    def set_skip_to_idx(self, skip_to_idx):
        self.current_scope().skip_to_idx = skip_to_idx

    def inc_skip_to_idx(self, add=1):
        self.current_scope().skip_to_idx += add
        return self.current_scope().skip_to_idx

    def last_id(self):
        return self.current_scope().last_id

    def set_last_id(self, last_id):
        self.current_scope().last_id = last_id
