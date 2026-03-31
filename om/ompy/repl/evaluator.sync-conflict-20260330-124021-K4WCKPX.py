from pathlib import Path
import pprint

from ompy.evaluator import evaluate
import ompy.parser as parser


def _parevde(prog: str) -> str:
    return parser.deparse(evaluate(parser.parse(prog)))


def _parevde_file(fp):
    return _parevde(fp.read().rstrip('\n\r'))


def evaluator(sourcef, cmd_code, targetf, force):
    if cmd_code:
        print(_parevde(sourcef))
    elif sourcef == '-':
        print(
            'each line of input will be parsed -> evaluated -> deparsed',
            end=''
        )
        if targetf:
            if not force and Path(targetf).exists():
                raise FileExistsError(targetf)
            print(', and written to', targetf)
            with open(targetf, 'w') as fp:
                try:
                    while True:
                        res = _parevde(input('Om > '))
                        pprint.pprint(res)
                        print('   >>', targetf)
                        print('   < ', res)
                        fp.write(res)
                except (EOFError, KeyboardInterrupt):
                    print('\nbye!')
        else:
            print()
            while True:
                print('   <', _parevde(input('Om > ')))
    else:
        source = None
        with open(sourcef, 'r') as fp:
            source = _parevde_file(fp)
        if source is None:
            return
        if targetf:
            with open(targetf, 'w') as fp:
                fp.write(source)
        else:
            pprint.pprint(source)
