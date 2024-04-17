from ..objects import CompoundLiteral

_shared_parse = None


def compound_literal_shared_name(*args):
    global _shared_parse
    _shared_parse, *_ = args


def compound_literal_value(parser_state):
    if False and parser_state._debug():
        pass
        print(f"DEBUG: compound_literal_value debug: {parser_state}")

    contents = _shared_parse(
        parser_state=parser_state,
        break_on_test=lambda ch, source, idx, last_id:
            CompoundLiteral.ch_is_close(ch)
    )

    # print(contents, parser_state)

    return None, contents
