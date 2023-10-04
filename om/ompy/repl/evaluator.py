from pathlib import Path
import pprint

from ompy.evaluator import evaluate  # , parevde_file


def evaluator(sourcef, targetf, force):
    if sourcef == '-':
        print(
            'each line of input will be parsed -> evaluated -> deparsed',
            end=''
        )
        if targetf:
            if not force and Path(targetf).exists():
                raise FileExistsError(targetf)
            print( ', and written to', targetf )
            with open(targetf, 'w') as fp:
                try:
                    while True:
                        res = evaluate( input('> ') )
                        pprint.pprint(res)
                        print('\t  >>', targetf)
                        fp.write('{' + res + '}')
                except (EOFError, KeyboardInterrupt):
                    print('\nbye!')
        else:
            print()
            while True:
                print('<', evaluate( input('> ')) )
    else:
        with open(sourcef, 'r') as fp:
            source = evaluate(fp.read())
        if targetf:
            with open(targetf, 'w') as fp:
                fp.write(source)
        else:
            pprint.pprint(source)
