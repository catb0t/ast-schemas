import json
import re
import copy
from pathlib import Path


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
