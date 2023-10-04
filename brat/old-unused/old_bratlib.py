import copy
import re


class T:
    pass


class F:
    pass


class N:
    pass


BOOL = (F, T)
TRIN = (F, T, N)
FALSES = (F, N)
SYMBOL_RE = re.compile(r'^\w+$')


PyFunction = (lambda: ()).__class__


def type_prime(obj):
    if isinstance(obj, str):
        return String if re.match(SYMBOL_RE, obj) is None \
            else Symbol
    if isinstance(obj, (int, float)):
        return Number

    return type(obj)


class Function:
    def __init__(self, uid, title='(anonymous)',
                 required=None, default=None, extra=False,
                 py_call=None, use_py_call=False, code=None,
                 allow_call_site_args=False,
                 comments=None, lua_like=False):
        self.uid = uid
        self.title = title
        self.required = required or []
        self.default = default or []
        self.extra = extra
        self.my = None
        self.use_py_call = py_call or use_py_call
        self.py_call = py_call or (lambda call_args: None)
        self.code = code or []
        self.allow_call_site_args = allow_call_site_args
        self.comments = comments or {}
        self.lua_like = lua_like  # en/disable strict argument-counting mode

        self.return_type_cache = set()

    def __repr__(self):
        return f"Function[{self.required}, {self.default}{(', *' + self.extra) if self.extra else ''}] -> \
({self.repr_return_type()})"

    def repr_return_type(self):
        return (' | '.join(map(str, self.return_type_cache))
                if self.return_type_cache else '?')

    def check_proto(self, pos_args, hash_args):
        """
          always good: correct number
            { a   | }(1)
            { a=1 | }( )
            { *a  | }( )
            { a   | }( "g": 3 )
          lua-like only: too many
            { a      | }(1, 2)
            { a, b=1 | }(1, 2, 3)
            { }(1)
          always bad: not enough
            { a, b | }(1)
        """
        input_len = len(pos_args) + bool(hash_args)
        required_len = len(self.required)
        default_len = len(self.default)

        if hash_args and required_len == 0:
            raise TypeError(
                f"hash arguments must be collected in the last formal \
(positional) argument, but {self.uid} {self.title} has no formal \
(non-default, non-extra) arguments\n\t(call: {hash_args})"
            )

        if input_len < required_len:
            raise TypeError(
                f"not enough positional arguments to function {self.uid} \
{self.title}: (call: {input_len}) < (declared: {required_len})\n\t\
(call: {pos_args}, {hash_args}) < (declared: {self.required})"
            )

        if (not (self.lua_like or self.extra)
                and (input_len > required_len + default_len)):
            raise TypeError(
                f"too many arguments (in strict mode) to function {self.uid} \
{self.title}: (call: {input_len}) > (declared: \
{required_len + default_len})\n\t(call: {pos_args}, \
{hash_args}) > (declared: {self.required} + {self.default})"
            )

    def invoke(self, *call_site_args, in_pos_args: list = None,
               in_hash_args: dict = None, in_scope: dict = None,
               out_node_results: list = None, **call_site_kwargs):
        from brat import nodes_values

        if in_pos_args is None:
            pos_args = []
        else: pos_args = in_pos_args
        if in_hash_args is None:
            hash_args = {}
        else: hash_args = in_hash_args
        if in_scope is None:
            scope = {}
        else: scope = in_scope

        self.check_proto(pos_args, hash_args)

        len_pos_args = len(pos_args)
        decl_names = self.required + self.default
        extra = []
        if self.extra and len_pos_args > len(decl_names):
            num_extra = len_pos_args - len(decl_names)  # - 1
            from_end = len_pos_args - num_extra
            extra = pos_args[from_end:]
            print("extra arguments are: (" + str(num_extra) + ")", extra)

        required_len = len(self.required)
        # hash args must go to the last formal parameter
        if hash_args:
            available = required_len - 1
        else:
            available = required_len

        positional_in = pos_args[:available]
        rest_in = pos_args[available:]
        combined_defaults = []
        index = 0
        for k, v in self.default:
            use_val = rest_in[index] if index < len(rest_in) else v
            combined_defaults.append([k, use_val])
            index += 1

        call_args = {
            'required': dict(zip(self.required, positional_in + [hash_args])),
            'default': dict(combined_defaults),
            'extra': {self.extra: extra}
        }

        sub_scope = copy.deepcopy(scope)
        sub_scope.update(call_args['required'])
        sub_scope.update(call_args['default'])
        sub_scope.update(call_args['extra'])
        if isinstance(self.my, BaseObject):
            sub_scope.update({'my': self.my})
        elif self.my is not None:
            raise TypeError('.my must be None or inherit from BaseObject: '
                            + repr(self.my) + '; ' + repr(self))

        if self.use_py_call:
            sub_scope = dict(map(
                lambda i: (i[0], deep_underlying(i[1])),
                sub_scope.items()
            ))
            if not self.allow_call_site_args:
                if call_site_args or call_site_kwargs:
                    raise TypeError(
                        "call site args are disallowed: "
                        + repr(call_site_args) + ' ' + repr(call_site_kwargs)
                    )
                return self.py_call(sub_scope)
            return self.py_call(sub_scope, *call_site_args, **call_site_kwargs)

        # this can be used to implement static scope in the future
        node_results, _sub_scope = nodes_values(self.code, sub_scope)
        if out_node_results is not None:
            out_node_results.extend(node_results)
        # last expression in a function is the return value of the function
        val = node_results[-1]
        self.return_type_cache.add( type_prime(val) )
        return val


def builtin(name, calls, **kwargs) -> Function:
    return Function(
        uid=name, title='(builtin object.' + name + ')',
        py_call=calls, **kwargs)


class ValueOfFunction:
    def __init__(self, func):
        self.func = func


class EmptyExpression:
    def __init__(self):
        raise TypeError('EmptyExpression must not be instantiated')


class ListWrapper:
    def __init__(self, l):
        self.value = l

    def __repr__(self):
        return f"ListWrapper({self.value})"


def create_methods(self, methods):
    self.my = self
    for k, v in methods.items():
        new_v = copy.deepcopy(v)
        new_v.my = self
        setattr(self, k, new_v)


class BaseObject:

    def __init__(self, underlying):
        self._underlying = underlying
        # super().__setattr__('_underlying', underlying)
        create_methods(self, OBJECT)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            self_underlying = object.__getattribute__(self, '_underlying')
            return type(self_underlying) \
                .__getattribute__(self_underlying, name)

    # def __setattr__(self, name, value_pair):
    #     if value_pair:
    #         raise NotImplementedError(self, name, value)
    #     return super().__setattr__(self, name, value)

    def equals(self):
        pass

    def not_equals(self):
        pass

    def __repr__(self):
        return 'BaseObject(' + repr(self._underlying) + ')'

    def __str__(self):
        return str(self._underlying)


class Number(BaseObject):
    def __init__(self, underlying):
        self._underlying = underlying
        # super().__setattr__('_underlying', underlying)
        create_methods(self, NUMBER)
        super().__init__(underlying)

    def __repr__(self):
        return 'Number(' + repr(self._underlying) + ')'

    def __str__(self):
        return str(self._underlying)


class String(BaseObject):
    def __init__(self, underlying):
        self._underlying = underlying
        # super().__setattr__('_underlying', underlying)
        create_methods(self, STRING)
        super().__init__(underlying)

    def __repr__(self):
        return 'String(' + repr(self._underlying) + ')'

    def __str__(self):
        return self._underlying


class Symbol(String):
    def __init__(self, underlying):
        self._underlying = underlying
        # super().__setattr__('_underlying', underlying)
        create_methods(self, SYMBOL)
        super().__init__(underlying)

    def __repr__(self):
        return 'Symbol(' + repr(self._underlying) + ')'

    def __str__(self):
        return self._underlying


def make_type_raiser(info):
    def _inner():
        raise TypeError(info)
    return _inner


def is_brat_callable(obj):
    return isinstance(obj, Function)


RENAMES = {
    '+': '__add__',
    '-': '__sub__',
    '*': '__mul__',
    '/': '__div__',
}

REPLACEMENTS = {
    '_': '__under__',
    '?': '__question__',
    '!': '__exclamation__',
}.items()


def sanitize_name(name: str) -> str:
    if name in RENAMES:
        return RENAMES[name]
    temp_name = name
    for k, v in REPLACEMENTS:
        temp_name = temp_name.replace(k, v)
    return temp_name


def is_true(b):
    if is_brat_callable(b):
        b = b.invoke()
    return BOOL[b not in FALSES]


def is_false(b):
    if is_brat_callable(b):
        b = b.invoke()
    return BOOL[b in FALSES]


def is_null(b):
    if is_brat_callable(b):
        b = b.invoke()
    return BOOL[b is N]


p = lambda scope: print('-->\t', *map(str, scope['args'])) or T


true = lambda _: T
false = lambda _: F
null = lambda _: N


def trin_question(mode, scope):
    args = scope['args']

    test_func = {T: is_true, F: is_false, N: is_null}[mode]

    def _trin_question(condition, true_branch, false_branch=None):
        if is_brat_callable(condition):
            condition = condition.invoke()

        if test_func(condition):
            if is_brat_callable(true_branch):
                return true_branch.invoke(in_pos_args=[condition])
            return true_branch
        if false_branch is None:
            return F
        if is_brat_callable(false_branch):
            return false_branch.invoke(in_pos_args=[condition])
        return false_branch

    return {
        0: lambda: test_func(scope['my']),
        1: lambda: test_func(args[0]),
        2: lambda: _trin_question(*args),
        3: lambda: _trin_question(*args)
    }.get(
        len(args),
        make_type_raiser(
            {
                T: 'true',
                F: 'false',
                N: 'null'
            }[mode]
            + "? wanted 0-3 positional arguments, got " + str(len(args))
            + '(' + repr(args) + ')'
        )
    )


def _equals_equals(scope):
    try:
        return scope['my'].equals(scope['your'])
    except AttributeError:
        return scope['my'] == scope['your']


def _not_equals(scope):
    try:
        return scope['my'].not_equals(scope['your'])
    except AttributeError:
        return scope['my'] != scope['your']


_OBJECT_FUNCS = [
    builtin( 'p', p, extra='args' ),
    builtin( 'true', true ),
    builtin( 'false', false ),
    builtin( 'null', null ),
    builtin( 'true?', lambda s: trin_question(T, s), extra='args' ),
    builtin( 'false?', lambda s: trin_question(F, s), extra='args' ),
    builtin( 'null?', lambda s: trin_question(N, s), extra='args' ),
    builtin( 'my', lambda s: s['my'] ),  # this is wrong
    builtin( '==', _equals_equals, required=['your'] ),
    builtin( '!=', _not_equals, required=['your'] ),
]

OBJECT = dict(map(lambda f: [f.uid, f], _OBJECT_FUNCS))
NUMBER = {}
STRING = {}
SYMBOL = {}
