#! /usr/bin/env python3
import itertools
from pprint import pprint
import ompy.parser as parser
import ompy.parser.test as test
from ompy.test.util import read_segmented_om
from timeit import timeit


with open(test.STATIC_DIR / 'rearrange.om') as fp:
    c = fp.read().rstrip('\n\r')

print(parser.parse(c))


'''
    test, reason = read_segmented_om(fp)

print(reason)
print(parser.parse(test))'''


'''def all_eq(*i):
    for comb in itertools.combinations(i, 2):
        if comb[0] != comb[1]:
            return False
    return True


with open(test.NORM_DIR / 'rearrange.om') as fp:
    big_text, optimal_text = read_segmented_om(fp)

fact_big = parser.parse(big_text)
fact_optimal = parser.parse(optimal_text)

#pprint(fact_optimal)

strip_optimal = parser.parse(optimal_text, strip=True)
filter_optimal = parser.filter_separators(fact_optimal)
print( all_eq(fact_optimal, strip_optimal, filter_optimal) )

strip_big = parser.parse(big_text, strip=True)
filter_big = parser.filter_separators(fact_big)

# print(parser.deparse(filter_big))
pprint(strip_big)
# print(filter_big == fact_optimal)
print( all_eq(strip_big, filter_big, fact_optimal) )
'''
