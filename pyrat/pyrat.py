#! /usr/bin/env python3

try:
    import ujson as json
except ImportError:
    import json  # type: ignore mypy bug
import re
import fileinput

from pathlib import Path
from typing import (Callable, Union, Dict, List,
                    TypeVar, cast)


# import fastjsonschema
import jsonschema

JSONPrimitive = Union[str, int, bool, None]
JSONType = Union[JSONPrimitive, 'JSONList', 'JSONDict']


# work around mypy#731: no recursive structural types yet
class JSONList(List[JSONType]): pass
class JSONDict(Dict[str, JSONType]): pass  # noqa


FJSValidator = Callable[[JSONDict], JSONDict]
T = TypeVar('T')
IdentityCallable = Callable[[T], T]


identity: Callable[[T], T] = lambda x: x


class Constants:

    class Re:
        COMMENTS = re.compile(
            r'#.*?$|//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        TRAILING_OBJECT_COMMAS = re.compile(
            r'(,)\s*}(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
        TRAILING_ARRAY_COMMAS = re.compile(
            r'(,)\s*\](?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')


# https://gist.github.com/liftoff/ee7b81659673eca23cd9fc0d8b8e68b7
def remove_comments(json_like: str) -> str:
    """
    Removes C-style comments from *json_like* and returns the result.
    Example::

        >>> test_json = '''\
        {
            "foo": "bar", // This is a single-line comment
            "baz": "blah" /* Multi-line
            Comment */
        }'''
        >>> remove_comments('{"foo":"bar","baz":"blah",}')
        '{\n    "foo":"bar",\n    "baz":"blah"\n}'
    """
    replacer: (  # type: ignore
        Callable[[re.Match], str]
    ) = (lambda match:
         "" if match.group(0)[0] in ('/', '#')  # type: ignore \
         else match.group(0))

    return Constants.Re.COMMENTS.sub(replacer, json_like)


def remove_trailing_commas(json_like: str) -> str:
    """
    Removes trailing commas from *json_like* and returns the result.
    Example::

        >>> remove_trailing_commas('{"foo":"bar","baz":["blah",],}')
        '{"foo":"bar","baz":["blah"]}'
    """
    # Now fix arrays/lists [] and return the result
    return Constants.Re.TRAILING_ARRAY_COMMAS.sub(
        "]",
        # Fix objects {} first
        Constants.Re.TRAILING_OBJECT_COMMAS.sub("}", json_like)
    )


def transform_json (s: str, join_by: str = "", do_strip: bool = True) -> str:
    strip: IdentityCallable[str]  = lambda line: line.lstrip().strip()
    extant: Callable[[str], bool] = lambda line: len(line) != 0
    x = join_by.join(filter(
        extant,
        map(
            cast(IdentityCallable[str], strip if do_strip else identity),
            remove_trailing_commas( remove_comments(s) ).split("\n")
        )
    ) )
    print(x)
    return x


def transform_json_dbg () -> Callable[[str], str]:
    return lambda s: transform_json(s, join_by = "\n", do_strip = False)


def realize_json (f: Path) -> JSONDict:
    with open(f, "r") as fp:
        return cast(JSONDict, json.loads( transform_json_dbg()( fp.read(), ) ))


def py_of (x: JSONDict) -> None:
    pass


def main () -> None:
    schema = realize_json(  Path(__file__).resolve().parent / "pyrat.schema.json" )
    # validator = fastjsonschema.compile(  )

    src: JSONDict = json.loads(
        transform_json_dbg()( "\n".join(fileinput.input()) )
    )
    print(jsonschema.validate(schema, src))


if __name__ == '__main__':
    main()
