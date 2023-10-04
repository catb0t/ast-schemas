# def operator_name(source):
#     '''read the name of an operator from the source. returns a re.Match'''
#     return operator_reader.match(source)

from .escapable_literal import escapable_literal_reader

from .comment import comment_value
from .scalar_literal import scalar_literal_value
from .compound_literal import compound_literal_value, \
    compound_literal_shared_name

__all__ = [
    'escapable_literal_reader',
    'comment_value',
    'scalar_literal_value',
    'compound_literal_value',
    'compound_literal_shared_name'
]
