"""
"""
from pathlib import Path
import json
import copy


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
    BUILTIN = 'builtin'


Key = _CommonKey

FILE_LOC = Path(__file__).resolve().parent
OM_SCHEMA_FILE = FILE_LOC / '..' / 'om.schema.json'

with open(OM_SCHEMA_FILE) as sfp:
    _om_schema_mut = json.load(sfp)

OM_SCHEMA = copy.deepcopy(_om_schema_mut)
