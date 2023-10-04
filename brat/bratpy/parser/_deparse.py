import json
from io import StringIO

from bratpy.schema_data import Key, is_any_instance_or_subclass

from ._parse_common import SEP_STR
from .objects import Comment, ScalarLiteral, \
    Block, Node

from .deparser_replacers import replace_comment, replace_literal, \
    literal_shared_name


def replace_separator(val):
    value = val['value']
    if value > 2:
        raise ValueError("invalid separator: " + repr(val))

    return SEP_STR[value]


def replace_function(val):
    return Block.to_ch(Block.OPEN) + _deparse_to_string(val).getvalue() \
        + Block.to_ch(Block.CLOSE)


def replace_var_by_name(val):
    pass


def replace_member_access(val):
    pass


def replace_value_of(val):
    pass


def replace_assignment(val):
    pass


def replace_application(val):
    pass


def replace_index(val):
    pass


def replace_comma_operator(val):
    pass


def _deparse_to_string(elts, _inject_space=False):
    building = StringIO()

    for idx, e in enumerate(elts):
        # if not isinstance(e, dict):
        #    raise ValueError(e)
        # TODO: look at prev/next nodes to tell where mandatory whitespace
        # should be inserted
        after_space = False
        # print(f'space: {after_space}')
        if idx != len(elts) - 1 and (
            Node.nodes_all_not_separator((e, elts[idx + 1]))
        ):
            after_space = _inject_space

        # if is_any_instance_or_subclass(e, (str, int, float)):
        #    building.write(str(e))
        # elif is_any_instance_or_subclass(e, (list, dict)):
        #    building, write(replace_deep_iterable(e))

        deparsed = {
            Node.SEPARATOR: replace_separator,
            Node.COMMENT: replace_comment,
            Node.LITERAL: replace_literal,
            Node.VAR_BY_NAME: replace_var_by_name,
            Node.MEMBER_ACCESS: replace_member_access,
            Node.FUNCTION: replace_function,
            Node.VALUE_OF: replace_value_of,
            Node.ASSIGNMENT: replace_assignment,
            Node.APPLICATION: replace_application,
            Node.INDEX: replace_index,
            Node.COMMA_OPERATOR: replace_comma_operator,
        }.get(Node.to_enum(e))(e)

        building.write(deparsed)

        if after_space:
            building.write(' ')

    return building


def _deparse(elts: list[dict]):
    if (isinstance(elts, tuple)
        and len(elts) == 3
        and isinstance(elts[1], int)
        and isinstance(elts[2], int)
        and elts[1] >= 1
            and elts[2] >= 1):
        raise ValueError(
            "test-mode parse() return tuple wrongly given directly to"
            " deparse(list[dict]) (tuple indices 1 and 2 are line and col)"
            f"\n\terror value is {elts}")

    return _deparse_to_string(elts).getvalue()


def _deparse_file(fp):
    return _deparse(json.load(fp))


literal_shared_name(_deparse)
