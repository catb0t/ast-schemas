from io import StringIO

from ._parse_common import SEP_STR, \
    Form, _form_to_ch, Node, _node_to_id


def replace_separator(val):
    return SEP_STR[val]


def replace_operator(val):
    return val


def replace_operand(val):
    return _form_to_ch(Form.OPEN) + _deparse_to_string(val).getvalue() \
        + _form_to_ch(Form.CLOSE)


def _deparse_to_string(elts):
    building = StringIO()
    for e in elts:
        if not isinstance(e, dict):
            raise ValueError(e)
        building.write(
            {
                _node_to_id(Node.SEPARATOR): replace_separator,
                _node_to_id(Node.OPERATOR): replace_operator,
                _node_to_id(Node.OPERAND): replace_operand,
            }.get(e['id'])(e['value'])
        )
    return building


def _deparse(elts):
    return _deparse_to_string(elts).getvalue()


def _deparse_file(fp):
    import json
    return _deparse(json.load(fp))
