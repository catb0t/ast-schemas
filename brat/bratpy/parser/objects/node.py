import copy
from enum import Enum

from bratpy.schema_data import Key, is_any_instance_or_subclass, \
    linear_selection, linear_selection_by, SCHEMA_INFO
from .nolastid import NoLastID, _NoLastID


class NoFieldValue:
    pass


def filter_no_field_value(args):
    return filter(lambda x: x is not NoFieldValue, args)


class Node(Enum):
    '''
    since the `node`, `assignment_target`, `basic_object`, `object_expression`,
        and `expression` nodes are simply collections of other nodes, they
        themselves have no concrete definition and are not distinct objects,
        only their subobjects are
    '''
    SEPARATOR = 1
    COMMENT = 2
    LITERAL = 3
    VAR_BY_NAME = 4
    INDEX = 5
    MEMBER_ACCESS = 6
    VIRTUAL_ASSIGNMENT_TARGET = 7
    VIRTUAL_BASIC_OBJECT = 8
    FUNCTION = 9
    VALUE_OF = 10        # aliases
    ASSIGNMENT = 11
    APPLICATION = 12
    VIRTUAL_OBJECT_EXPRESSION = 13
    VIRTUAL_EXPRESSION = 14
    COMMA_OPERATOR = 15
    VIRTUAL_NODE = 16

    @staticmethod
    def display_name(node):
        en = Node.to_enum(node)
        return DISPLAY_NAMES.get(en, '(no display name for node)') + ' AST node'

    @staticmethod
    def node_is(node, base):
        base = Node.to_enum(base)
        if base is NoLastID or isinstance(base, _NoLastID):
            raise ValueError(base)
        if isinstance(node, dict):
            return Node.to_enum(node) == base
        if isinstance(node, str):
            return node == NODE_ENUMS_TO_IDS[base]
        if isinstance(node, Node):
            return node == base
        if node is NoLastID or isinstance(node, _NoLastID):
            return False
        if node is None:
            raise DeprecationWarning(
                'use of None in place of NoLastID (valve, pls fix)')
        raise ValueError(node)

    @staticmethod
    def to_enum(node):
        if isinstance(node, Node):
            return node
        if isinstance(node, str):
            return IDS_TO_NODE_ENUMS[node]
        if isinstance(node, dict):
            return Node.to_enum(node[Key.ID])
        raise ValueError(node)

    @staticmethod
    def to_id(node):
        if isinstance(node, Node):
            return NODE_ENUMS_TO_IDS[node]
        if isinstance(node, str):
            return node
        if isinstance(node, dict):
            return node[Key.ID]
        raise ValueError(node)

    @staticmethod
    def node_isinstance(node, base):
        node = Node.to_enum(node)
        base = Node.to_enum(base)
        if base not in NODE_ALL_SUBNODES:
            return False
        return node in NODE_ALL_SUBNODES[base]

    @staticmethod
    def node_issupernode(super_node, sub_node):
        super_node = Node.to_enum(super_node)
        sub_node = Node.to_enum(sub_node)
        if sub_node not in NODE_ALL_SUPERNODES:
            return False
        return super_node in NODE_ALL_SUPERNODES[sub_node]

    @staticmethod
    def nodes_all(nodes, base):
        return all(map(lambda n: Node.node_is(n, base), nodes))

    @staticmethod
    def nodes_any(nodes, base):
        return any(map(lambda n: Node.node_is(n, base), nodes))

    @staticmethod
    def nodes_none(node, bases):
        return not Node.nodes_any(node, bases)

    @staticmethod
    def nodes_all_instance(nodes, base):
        return all(map(lambda n: Node.node_isinstance(n, base), nodes))

    @staticmethod
    def nodes_all_separator(nodes):
        return all(map(lambda n: Node.node_is_separator(n), nodes))

    @staticmethod
    def nodes_all_not_separator(nodes):
        return all(map(lambda n: Node.node_is_not_separator(n), nodes))

    @staticmethod
    def node_is_separator(node):
        return Node.node_is(node, Node.SEPARATOR)

    @staticmethod
    def node_is_not_separator(node):
        return Node.node_isinstance(node, Node.VIRTUAL_NODE) \
            and not Node.node_is(node, Node.SEPARATOR)

    @staticmethod
    def create(node_id, props, line=None, col=None, debug=False):
        obj = {
            Key.ID: Node.to_id(node_id),
        }
        schema = NODE_FIELDS[Node.to_enum(node_id)]
        required_keys = schema['required'].keys()
        # print("props: ", props)

        if Key.ID in props:
            if not Node.node_is(props[Key.ID], node_id):
                raise ValueError(
                    f"props of different node ID than expected (probably a bug): {node_id} vs {props}"
                )
            del props[Key.ID]
        # selecting only the required keys from props should be 1 less than
        # the total required keys because we are omitting 'id'
        got_required_keys = (
            0 if not props
            else len(linear_selection(props, required_keys))
        )
        # print(props, got_required_keys, required_keys)
        if got_required_keys != len(required_keys) - 1:
            raise ValueError(
                f'create_node for {node_id} missing required keys: '
                f'{linear_selection_by(schema["required"], lambda a: a[0] not in props)}'  # noqa
            )

        if not props:
            return obj

        for kw, val in props.items():
            # print(f'prop key: {kw}')
            is_required = kw in schema['required']
            is_optional = kw in schema['optional']
            assured_selection = 'required' if is_required else 'optional'

            if not (is_required or is_optional):
                if not schema['additional']:
                    raise ValueError(''.join([
                        f"illegal additional property '{kw}'"
                        f": disallowed by the schema for node '{node_id}':",
                        f'\n\tis_required: {is_required}',
                        f'\n\tis_optional: {is_optional}',
                        f'\n\tadditonal:   {schema["additional"]}'
                    ]))

            elif not is_any_instance_or_subclass(
                val,
                schema[assured_selection][kw][Key.TYPE]
            ):
                raise TypeError(
                    f'value of type "{type(val)}" for key {repr(kw)} is not'
                    ' instance/subclass in types:\n\t'
                    f' {schema[assured_selection][kw]["type"]}'
                )

            # print('success!', kw)
            obj[kw] = val

        # if debug:
        #    obj.update({'_debug': {'_pos': [line, col]}})
        return obj

    def check_basic_array_subform_special_case(node):
        if Node.to_enum(node) == Node.LITERAL:
            return isinstance(node.get(Key.VALUE), list)
        return True

    @staticmethod
    def can_subform(node):
        if not isinstance(node, dict):
            raise ValueError(node)

        nid = Node.to_enum(node)
        kind = node.get(Key.KIND, '*')

        return nid in NODE_SUBFORM_PROPERTIES \
            and kind in NODE_SUBFORM_PROPERTIES[nid] \
            and (Node.check_basic_array_subform_special_case(node))
        # special case of non-annotated basic array

    @staticmethod
    def get_subform_properties(node):
        """ get the list of properties in node that contain its sub-forms """
        return NODE_SUBFORM_PROPERTIES.get(Node.to_enum(node))

    @staticmethod
    def subforms(node):
        """ return the sub-form properties in this node,
            after some pre-processing
        """
        node_prop_sets = Node.get_subform_properties(node)

        kind_key = node.get(Key.KIND)

        if kind_key is None \
                and Node.check_basic_array_subform_special_case(node):
            kind_key = '*'
        elif kind_key is None or node_prop_sets is None:
            raise TypeError(
                'NODE_SUBFORM_PROPERTIES is missing a '
                f'subkey: {kind_key} for {Node.to_enum(node)}: {node}'
            )

        subform_props = node_prop_sets.get(kind_key)

        subforms = dict()
        for p in subform_props:
            if '/' in p:
                path = p.split('/')
                props_curr = node
                forms_curr = subforms
                for q in path:
                    props_curr = props_curr[q]
                    forms_curr[q] = copy.deepcopy(props_curr[q])
            else:
                subforms[p] = node[p]

        return subforms


NODE_SUBFORM_PROPERTIES = {
    Node.LITERAL: {
        'deep_array': {'value'},
        'deep_assoc': {'value'},
        'deep_exprkey': {'key', 'value'},
        'deep_hash': {'value'},
        '*': {'value'},
        'assoc': {'value'},
        'hash': {'value'},
        'exprkey': {'key', 'value'},
    },

    Node.MEMBER_ACCESS: {'*': {'target'}},
    Node.FUNCTION: {'*': {'does', 'args/default'}},
    Node.VALUE_OF: {'*': {'target'}},
    Node.ASSIGNMENT: {'*': {'target', 'source'}},
    Node.APPLICATION: {'*': {'target', 'positional_args', 'hash_args'}},
    Node.INDEX: {'*': {'target', 'indices'}},
    Node.COMMA_OPERATOR: {'*': {'expressions'}}
}

NODE_ENUMS_TO_IDS = {
    Node.SEPARATOR:             'separator',
    Node.COMMENT:               'comment',
    Node.LITERAL:               'literal',
    Node.VAR_BY_NAME:           'var_by_name',
    Node.MEMBER_ACCESS:         'member_access',
    Node.FUNCTION:              'function',
    Node.VALUE_OF:              'value_of',
    Node.ASSIGNMENT:            'assignment',
    Node.APPLICATION:           'application',
    Node.INDEX:                 'index',
    Node.COMMA_OPERATOR:        'comma_operator'
}

IDS_TO_NODE_ENUMS = {
    'separator':                Node.SEPARATOR,
    'comment':                  Node.COMMENT,
    'literal':                  Node.LITERAL,
    'var_by_name':              Node.VAR_BY_NAME,
    'member_access':            Node.MEMBER_ACCESS,
    'function':                 Node.FUNCTION,
    'value_of':                 Node.VALUE_OF,
    'assignment':               Node.ASSIGNMENT,
    'application':              Node.APPLICATION,
    'index':                    Node.INDEX,
    'comma_operator':           Node.COMMA_OPERATOR
}

'''Node.VIRTUAL_NODE is assumed to be the ultimate supernode for all nodes'''
NODE_DIRECT_SUPERNODES = dict(map(lambda i: (i[0], i[1] + [Node.VIRTUAL_NODE]), {
    Node.SEPARATOR: [],
    Node.COMMENT:  [],

    Node.LITERAL: [Node.VIRTUAL_BASIC_OBJECT],
    Node.VIRTUAL_ASSIGNMENT_TARGET: [Node.VIRTUAL_BASIC_OBJECT],

    Node.VAR_BY_NAME: [Node.VIRTUAL_ASSIGNMENT_TARGET],
    Node.MEMBER_ACCESS: [Node.VIRTUAL_ASSIGNMENT_TARGET],
    Node.INDEX: [Node.VIRTUAL_ASSIGNMENT_TARGET, Node.VIRTUAL_OBJECT_EXPRESSION],

    Node.VIRTUAL_BASIC_OBJECT: [Node.VIRTUAL_OBJECT_EXPRESSION],
    Node.APPLICATION: [Node.VIRTUAL_OBJECT_EXPRESSION],
    Node.ASSIGNMENT: [Node.VIRTUAL_OBJECT_EXPRESSION],

    Node.FUNCTION: [Node.VIRTUAL_EXPRESSION],
    Node.VALUE_OF: [Node.VIRTUAL_EXPRESSION],
    Node.VIRTUAL_OBJECT_EXPRESSION: [Node.VIRTUAL_EXPRESSION],

    Node.VIRTUAL_EXPRESSION: [],
    Node.COMMA_OPERATOR: [],
}.items()))


def rec_supernodes(supernodes, stop_rec):
    if stop_rec:
        return [], True
    all_supers = []

    for node in supernodes:
        if node not in all_supers:
            all_supers.append(node)
        if node == Node.VIRTUAL_NODE:
            stop_rec = True
            continue
        else:
            node_supers, stop_rec = rec_supernodes(
                NODE_DIRECT_SUPERNODES[node], stop_rec)
            all_supers.extend(node_supers)

    return all_supers, stop_rec


def make_supernodes():
    result = dict()
    for k, v in NODE_DIRECT_SUPERNODES.items():
        sn, _ = rec_supernodes(v, False)
        if k in result:
            result[k].extend(sn)
        else:
            result[k] = sn
    return result


NODE_ALL_SUPERNODES = make_supernodes()

# pprint(NODE_ALL_SUPERNODES)


def make_all_subnodes():
    building = dict()
    for k, v in NODE_ALL_SUPERNODES.items():
        for supernode in v:
            if supernode in building:
                building[supernode].append(k)
            else:
                building[supernode] = [k]
    return building


NODE_ALL_SUBNODES = make_all_subnodes()
# pprint(NODE_ALL_SUBNODES)

DISPLAY_NAMES = {
    Node.SEPARATOR:             "separator (whitespace)",
    Node.COMMENT:               "comment",
    Node.LITERAL:               "literal (non-function)",
    Node.VAR_BY_NAME:           "bare variable name",
    Node.MEMBER_ACCESS:         "member access ",
    Node.FUNCTION:              "function literal",
    Node.VALUE_OF:              "value-of operator",        # aliases
    Node.ASSIGNMENT:            "assignment operator",
    Node.APPLICATION:           "application",
    Node.INDEX:                 "index expression",
    Node.COMMA_OPERATOR:        "comma operator"
}

'''TODO: VIRTUAL NODES'''
NODE_FIELDS = dict()


_type_lookup = {"boolean": bool, "number": float, "string": str, "array": list,
                "object": dict}

for k, v in SCHEMA_INFO.items():
    required, properties = set(v['required']), v['properties']
    # live testing lol
    assert (k == properties[str(Key.ID)].get('const', False)) or k in properties[str(Key.ID)].get('enum', ()), \
        repr(k) + ': someone probably changed the schema.json without updating parser.objects.node (LOL)'
    for _, prop in properties.items():
        if Key.TYPE in prop:
            if isinstance(prop[str(Key.TYPE)], str):
                prop[str(Key.TYPE)] = [_type_lookup[prop[str(Key.TYPE)]]]
            elif isinstance(prop[str(Key.TYPE)], list):
                prop[str(Key.TYPE)] = list(
                    map(lambda t: _type_lookup[t], prop[str(Key.TYPE)]))

    # you could also write
    # properties = dict(map(
    #     lambda v: {
    #         'type': _type_lookup[ v['type'] ],
    #         **linear_selection(v, set('type') ^ set(v.keys()))
    #     },
    #     _properties.items()
    # ))
    # and i would if it wasn't SO dumb.

    properties_keys = set(properties.keys())
    optional_properties = required ^ properties_keys
    NODE_FIELDS[IDS_TO_NODE_ENUMS[k]] = {
        'doc': v['$comment'],
        'required': linear_selection(properties, required),
        'optional': linear_selection(properties, optional_properties),
        'additional': v.get('additionalProperties', True)
    }
