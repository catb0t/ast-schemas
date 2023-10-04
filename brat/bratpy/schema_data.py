import json
import re
import copy
from pathlib import Path


class _CommonKey():
    ID = 'id'
    KIND = 'kind'
    VALUE = 'value'
    TYPE = 'type'
    NODE_PROPS = 'node_props'
    NODE_ID = 'node_id'
    SKIP_TO_IDX = 'skip_to_idx'
    LINE = 'line'
    COL = 'col'
    HANDLER = 'handler'


Key = _CommonKey


def linear_selection_by(d, func=lambda a: a[1]):
    """ select items from d for which the func returns true
        the default func selects items with truthy values
    """
    return dict(filter(func, d.items()))


def linear_selection(d, select):
    """ select items from d whose keys exist in select """
    return linear_selection_by(d, lambda a: a[0] in select)


def linear_selection_where(d, select, func):
    """ select items from d whose keys exist in select
        and for which func returns true
    """
    return linear_selection_by(d, lambda a: a[0] in select and func(a))


def _rec_all(obj, rec_key, rec_key_func, cond_func, _state):
    if not isinstance(obj, dict) or not rec_key_func(obj.get(rec_key)):
        return _state

    else:
        val = obj.get(rec_key)

        if isinstance(val, list):
            return all(map(
                lambda elt: _rec_all(
                    elt, rec_key,
                    rec_key_func, cond_func, all(
                        map(lambda v: cond_func(obj, v), val))
                ),
                val
            ))

        elif cond_func(obj, val):
            print("scalar")
            return _rec_all(
                obj.get(rec_key), rec_key,
                rec_key_func, cond_func, _state
            )

        else:
            return False


def recursive_all(obj, rec_key, rec_key_func, cond_func):
    return _rec_all(obj, rec_key, rec_key_func, cond_func, True)


def is_any_instance_or_subclass(val, types):
    return (
        map(lambda t: isinstance(val, t), types)
        or map(lambda t: issubclass(val, t), types)
    )


FILE_LOC = Path(__file__).resolve().parent
BRAT_SCHEMA_FILE = FILE_LOC / '..' / 'brat.schema.json'

with open(BRAT_SCHEMA_FILE) as sfp:
    _brat_schema_mut = json.load(sfp)

BRAT_SCHEMA = copy.deepcopy(_brat_schema_mut)

top_definitions = _brat_schema_mut['definitions']

all_ast_objects = set(top_definitions.keys())

concrete_ri = re.compile('^(VIRTUAL|EXTENSION):')

concrete_ast_objects = set(map(lambda p: p[0], filter(
    lambda d: not concrete_ri.match(d[1]['$comment']),
    top_definitions.items()
)))

abstract_ast_objects = concrete_ast_objects ^ all_ast_objects

'''TODO: VIRTUAL NODES'''
SCHEMA_INFO = {}
KEEP = ('$comment', 'required', 'properties', 'additionalProperties')

for k in concrete_ast_objects:
    SCHEMA_INFO[k] = linear_selection(top_definitions[k], KEEP)
