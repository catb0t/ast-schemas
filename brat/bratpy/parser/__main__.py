import sys

from ._parse import _parse
from ._deparse import _deparse

res, line, col = _parse(source=sys.argv[1], roundtrip=False, _test=True,
                        _debug=True)
print(f"\nResult:\t\t{res}\nFinal pos:\t{line}:{col}")
print()
print(_deparse(res))
