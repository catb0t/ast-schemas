#! /usr/bin/env python3
from pprint import pprint

import ompy.evaluator as ev
import ompy.parser as pa

print(
    pa.deparse(ev.evaluate(pa.parse(
        'quote {1 {2 3}'
    )))
)
