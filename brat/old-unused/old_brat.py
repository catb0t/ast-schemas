#! /usr/bin/env python3
import copy
import pprint
import re

import bratlib


RE_FLAGS = {
    "s": re.DOTALL,
    "i": re.IGNORECASE,
    "x": re.VERBOSE,
    "u": re.UNICODE,
    "m": re.MULTILINE
}


def make_value_raiser(key='?'):
    def _inner():
        raise ValueError(key)
    return _inner


def make_impl_raiser(key='?'):
    def _inner():
        raise NotImplementedError(key)
    return _inner


def dict_is_true(d, k):
    return isinstance(d, (dict, list)) and k in d and d[k]


def py_type_to_brat_type(obj):
    return {
        list:                    "_array",
        dict:                    "_hash",
        bratlib.String:          "_string",
        bratlib.Symbol:          "_symbol",
        bratlib.Number:          "_number",
        re.Pattern:              "_regex",
        bratlib.PyFunction:      "_function",
        bratlib.Function:        "_function",
        bratlib.ValueOfFunction: "_value_of",
    }[bratlib.type_prime(obj)]


def py_obj_to_brat_obj(obj):
    return {
        "_number": lambda: bratlib.Number(obj),
        "_string": lambda: bratlib.String(obj),
        "_symbol": lambda: bratlib.Symbol(obj),
        "_regex":  lambda: realise_regex(obj),
    }.get(py_type_to_brat_type(obj), make_value_raiser(obj))


def _kv_to_brat(k, v):
    return (
        py_obj_to_brat_obj(i)() if is_scalar(i) else deep_to_brat(i)
        for i in (k, v)
    )


def is_assoc(seq):
    return (isinstance(seq, list)
            and all(map(lambda x: isinstance(x, list) and len(x) == 2, seq)))


def deep_to_brat(coll):
    if isinstance(coll, dict):
        return dict(map(
            lambda di: (*_kv_to_brat(*di), ),
            coll.items()
        ))
    # an associative array (assoc)
    if is_assoc(coll):
        return list(map(
            lambda si: [*_kv_to_brat(*si)],
            coll
        ))
    if isinstance(coll, list):
        return list(map(
            lambda v: py_obj_to_brat_obj(v)()
            if is_scalar(v) else deep_to_brat(v),
            coll
        ))
    raise NotImplementedError(coll)


def realise_regex(rx):
    import functools
    if isinstance(rx, str):
        return re.compile(rx)

    flags = functools.reduce(
        lambda l, r: l | r,
        map(
            lambda c: RE_FLAGS.get(c, 0),
            "".join(rx["_flags"])
        )
    )
    return re.compile(rx["_pattern"], flags=flags)


def realise_hash(node, scope):
    items = node.items()
    new = dict()
    scope_copy = copy.deepcopy(scope)
    for k, v in items:
        val, new_scope = node_value(v, scope_copy)
        scope_copy = new_scope
        new[py_obj_to_brat_obj(k)()] = val
    return new, scope_copy


def is_scalar(obj):
    return not isinstance(obj, (dict, list, tuple))


def bare_var_name(obj: object):
    if dict_is_true(obj, "_var_by_name"):
        return obj["_name"]
    if isinstance(obj, str):
        return obj
    raise TypeError('nonsense `bare_var_name` of: ' + repr(obj))
    # return None


def indices_node_values(indices_node, scope):
    values = []
    new_scope = scope
    for i in indices_node:
        index, new_scope = node_value(i, new_scope)
        values.append(index)
    return values, new_scope


def apply_property_list(target: object, app: list):
    if len(app) > 1:
        if app[0][0] not in ("getattr", "index"):
            raise ValueError(target, app)
        if is_scalar(app[0][1]):
            if isinstance(target, bratlib.ListWrapper):
                return apply_property_list(
                    bratlib.ListWrapper(list(
                        map(lambda t: t[app[0][1]], target.value)))
                    if app[0][0] == "index"

                    else bratlib.ListWrapper(list(
                        map(lambda t: getattr(t, app[0][1]), target.value)))
                    if app[0][0] == "getattr"

                    else None,
                    app[1:]
                )
            return apply_property_list(
                target[app[0][1]]
                if app[0][0] == "index"
                else getattr(target, app[0][1])
                if app[0][0] == "getattr"
                else None,
                app[1:]
            )
        if isinstance(target, bratlib.ListWrapper):
            raise TypeError("???: " + repr(target))
            # return apply_property_list(
            #     ListWrapper([target.value[i] for i in app[0][1]])
            #     if app[0][0] == "index"
            #     else ListWrapper([getattr(target.value, i) for i in app[0]
            # [1]])
            #     if app[0][0] == "getattr"
            #     else None,
            #     app[1:]
            # )
        return apply_property_list(
            bratlib.ListWrapper([target[i] for i in app[0][1]])
            if app[0][0] == "index"
            else bratlib.ListWrapper([getattr(target, i) for i in app[0][1]])
            if app[0][0] == "getattr"
            else None,
            app[1:]
        )

    def _inner(source):
        if app[0][0] == "setattr":
            if is_scalar(app[0][1]):
                return setattr(target, app[0][1], source)

            return bratlib.ListWrapper(list(map(
                lambda i: setattr(target, i, source),
                app[0][1]
            )))
        if app[0][0] == "setindex":
            if is_scalar(app[0][1]):
                target[app[0][1]] = source
                return source

            def _assigner(i):
                target[ i._underlying ] = source
                return source
            return bratlib.ListWrapper(list(map( _assigner, app[0][1] )))
        raise ValueError(target, app)
    return _inner


def node_refers(node, scope: dict) -> lambda: (object, list, dict):
    if dict_is_true(node, "_var_by_name"):
        return lambda: ([["setindex", node["_name"]]], scope, scope)

    if dict_is_true(node, "_member_access"):
        access_field = bare_var_name(node["_member"])

        if (isinstance(node["_target"], str)
                or dict_is_true(node["_target"], "_var_by_name")):
            access_target = bare_var_name(node["_target"])

            # access_target is the string name of a scoped_variable
            def _inner():
                return [
                    [ "index", access_target ],
                    [ "setattr", access_field ]
                ], scope, scope
        else:
            access_target, new_scope = node_value(node["_target"], scope)

            # access_target is a value to which the member access is applied
            def _inner():
                return [
                    [ "setattr", access_field ]
                ], access_target, new_scope

        return _inner

    if dict_is_true(node, "_index"):
        indices, new_scope = indices_node_values(node["_indices"], scope)

        if (isinstance(node["_target"], str)
                or dict_is_true(node["_target"], "_var_by_name")):
            index_target = bare_var_name(node["_target"])

            # index_target is the string name of a scoped variable
            def _inner():
                return [
                    [ "index", index_target ],
                    [ "setindex", indices ]
                ], scope, scope
        else:
            index_target, new_scope = node_value(node["_target"], scope)

            # index_target is a value to index
            def _inner():
                return [
                    [ "setindex", indices ]
                ], index_target, new_scope
        return _inner

    raise AttributeError(node)


# TODO: fix comments
def val_comment(node, scope):
    text = make_value_raiser("comment")
    if dict_is_true(node, "_note"):
        note = node["_note"]
        if dict_is_true(node, "_multi"):
            text = ""
            for part in note:
                if isinstance(part, list):
                    text += ' '.join(map(
                        lambda s: s if isinstance(s, str) else repr(s),
                        part
                    )) + "\n"
                elif is_scalar(part):
                    text += str(part) + "\n"
                else:
                    # unreachable due to schema
                    raise AttributeError(node, " requires _multi: true")
        else:
            text = note

        print("\t##  " + text + "\n")
    else:
        text = str(node)
        print("\t#n" + text + "\n")
    # TODO: make comment represenation configurable
    return lambda: (bratlib.EmptyExpression, scope)


def val_literal(node, scope):
    value = node["_value"]

    # _deep_hash and _deep_array
    if ("_kind" in node and node["_kind"].startswith("_deep_")
            and "_exprkey" not in node["_kind"]):
        literal = lambda: (deep_to_brat(value), scope)
    else:
        literal = {
            "_number": lambda: (bratlib.Number(value), scope),
            "_string": lambda: (bratlib.String(value), scope),
            "_symbol": lambda: (bratlib.Symbol(value), scope),
            "_regex":  lambda: (realise_regex(value), scope),
            "_array":  lambda: nodes_values(value, scope),
            "_assoc":  lambda: nodes_values(value, scope),
            "_hash":   lambda: realise_hash(value, scope),
            # repr will be called 2x every time this literal is instantiated
            "_exprkey":
                make_impl_raiser('expression-computed key (`_exprkey`) \
[thrown from do_literal.else.value]; node: '),  # + repr(node)),
            "_deep_exprkey": make_impl_raiser(
                'deep expression-computed key (`_deep_exprkey`) \
[thrown from do_literal.else.value]; node: ')  # + repr(node))
        }[node.get("_kind", py_type_to_brat_type(value))]

    print("\tLITERAL: ", end='')
    pprint.pprint(literal()[0])
    return literal


def val_var_by_name(node, scope):
    # TODO: special 'my'
    return lambda: (scope[node["_name"]], scope)


def val_member_access(node, scope):
    target, new_scope = node_value(node["_target"], scope)
    member_name = bare_var_name(node["_member"])
    member_renamed = bratlib.RENAMES.get(member_name, member_name)

    if hasattr(target, member_name):
        return lambda: (getattr(target, member_name), new_scope)

    if hasattr(target, member_renamed):
        return lambda: (getattr(target, member_renamed), new_scope)

    if not hasattr(target, 'underlying'):
        raise AttributeError(target, member_name)

    if hasattr(target._underlying, member_name):
        return lambda: (getattr(target._underlying, member_name), new_scope)

    if hasattr(target._underlying, member_renamed):
        return lambda: (getattr(target._underlying, member_renamed), new_scope)

    raise AttributeError(target, member_name)


def val_function(node, scope):
    block = lambda does, arg_list: bratlib.Function(
        uid=id(does),
        required=arg_list.get("_required"),
        default=arg_list.get("_default"),
        extra=arg_list.get("_extra", False),
        code=does
    )

    return lambda: (
        block( node.get("_does", []), node.get("_args", {}) ),
        scope
    )


def val_value_of(node, scope):
    target, new_scope = node_value(node["_target"], scope)

    return lambda: (bratlib.ValueOfFunction(target), new_scope)


def val_assignment(node, scope):
    source, new_scope = node_value(node["_source"], scope)
    # print(node["_target"])
    refers_promise = node_refers(node["_target"], new_scope)

    ops, apply_ops_to, new_scope = refers_promise()
    assigner_promise = apply_property_list(apply_ops_to, ops)

    # assigner_promise(source)
    print("\tASSIGN TO:", node["_target"], source, apply_ops_to, ops)
    return lambda: (assigner_promise(source), new_scope)


def val_index(node, scope):
    target, new_scope = node_value(node["_target"], scope)
    indices, new_scope = indices_node_values(node["_indices"], new_scope)

    if len(indices) == 1:
        return lambda: (target[indices[0]._underlying], new_scope)

    return lambda: ([target[index._underlying] for index in indices], new_scope)


def val_application(node, scope):
    pos_args = []
    new_scope = scope
    if dict_is_true(node, "_positional_args"):
        for sub_node in node["_positional_args"]:
            arg, new_scope = node_value(sub_node, new_scope)
            pos_args.append(arg)

    if dict_is_true(node, "_hash_args"):
        hash_args, new_scope = node_value(node["_hash_args"], new_scope)
    else:
        hash_args = {}

    target, new_scope = node_value(node["_target"], new_scope)
    to_invoke = None
    if isinstance(target, bratlib.Function):
        to_invoke = target
    elif isinstance(target, bratlib.ValueOfFunction):
        to_invoke = target.func
    # elif dict_is_true(target, "_var_by_name"):
    #     to_invoke = new_scope[ target["_name"] ]
    # elif dict_is_true(target, "_function"):
    #     to_invoke = target
    elif dict_is_true(target, "_value_of") \
            or dict_is_true(target, "_dont_do_that"):
        to_invoke, new_scope = node_value(target, new_scope)
        to_invoke = to_invoke.func
    elif callable(target):
        print("callable", target)
        to_invoke = bratlib.Function(
            uid=target.__name__,
            title=repr(target),
            extra='args',
            py_call=lambda scope: target(*scope['args'])
        )
    else:
        raise NotImplementedError(target, new_scope)

    return lambda: (
        to_invoke.invoke(in_pos_args=pos_args, in_hash_args=hash_args,
                         in_scope=new_scope),
        new_scope
    )


def dispatch_node(kind: str, node: object, scope: dict):
    return {
        "_comment": val_comment,
        "_literal": val_literal,
        "_var_by_name": val_var_by_name,
        "_member_access": val_member_access,
        "_function": val_function,
        "_value_of": val_value_of,
        "_dont_do_that": val_value_of,
        "_assignment": val_assignment,
        "_application": val_application,
        "_index": val_index
    }[kind](node, scope)


def node_value(node: object, scope: dict) -> (object, dict):
    for kind in ( "_comment", "_literal", "_var_by_name",
                  "_member_access", "_function", "_value_of", "_dont_do_that",
                  "_assignment", "_application", "_index" ):
        if kind in node and node[kind]:
            raw_res = dispatch_node(kind, node, scope)
            # TODO: don't call the promise here
            if isinstance(raw_res, tuple):
                res, scope = raw_res
            else:
                res, scope = raw_res()
            if isinstance(res, bratlib.String):
                print(res._underlying)
            print(f"{repr(res)} <- {node}\n=====================\n")
            # input()
            return res, scope
    raise AttributeError(node)


def nodes_values(nodes: list, scope_update: dict = None) -> (list, dict):
    scope = dict()
    if scope_update is not None:
        scope.update(scope_update)
    scope['object'] = bratlib.BaseObject(dict())
    vals = []
    count = 0
    for node in nodes:
        print("\tScope: " + str(scope))
        print("\tNode #" + str(count) + " == " + str(node))
        res, scope = node_value(node, scope)
        if not isinstance(res, bratlib.EmptyExpression):
            vals.append(res)
        count += 1
    return vals, scope
