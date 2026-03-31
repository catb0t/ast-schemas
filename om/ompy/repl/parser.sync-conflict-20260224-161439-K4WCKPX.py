#! /usr/bin/env python3
import json
from pathlib import Path
import pprint

from ompy.parser import parse, parse_file, deparse, deparse_file


def parser(sourcef, cmd_code, targetf, force):
    if cmd_code:
        print(parse(sourcef))
    elif sourcef == '-':
        if targetf:
            if not force and Path(targetf).exists():
                raise FileExistsError(targetf)
            print(
                'each line of input will be parsed, quoted, and written to',
                targetf
            )
            with open(targetf, 'w') as fp:
                fp.write('[\n\t')
                try:
                    did_write = False
                    while True:
                        res = parse(input('> '))
                        pprint.pprint(res)
                        print('\t  >>', targetf)
                        if did_write:
                            fp.write(',\n\t')
                        json.dump({'id': 'operand', 'value': res}, fp)
                        did_write = True
                except (EOFError, KeyboardInterrupt):
                    print('\nbye!')
                finally:
                    fp.write('\n]\n')
        else:
            while True:
                print('<', parse(input('> ')))
    else:
        with open(sourcef, 'r') as fp:
            source = parse_file(fp)
        if targetf:
            with open(targetf, 'w') as fp:
                json.dump(source, fp)
        else:
            pprint.pprint(source)


def deparser(sourcef, targetf, force):
    if sourcef == '-':
        if targetf:
            if not force and Path(targetf).exists():
                raise FileExistsError(targetf)
            print(
                'each line of input will be deparsed, quoted, and written to',
                targetf
            )
            with open(targetf, 'w') as fp:
                try:
                    while True:
                        res = deparse(json.loads(input('> ')))
                        pprint.pprint(res)
                        print('\t  >>', targetf)
                        fp.write('{' + res + '}')
                except (EOFError, KeyboardInterrupt):
                    print('\nbye!')
        else:
            while True:
                print('<', deparse(json.loads(input('> '))))
    else:
        with open(sourcef, 'r') as fp:
            source = deparse_file(fp)
        if targetf:
            with open(targetf, 'w') as fp:
                fp.write(source)
        else:
            pprint.pprint(source)
