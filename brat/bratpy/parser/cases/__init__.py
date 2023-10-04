from .comment import comment
from .scalar_literal import scalar_literal
from .compound_literal import compound_literal

""" what is False supposed to mean? """
PARSER_CASES = {
    'comment': [False, comment],
    'scalar_literal': [False, scalar_literal],
    'compound_literal': [False, compound_literal]
}
