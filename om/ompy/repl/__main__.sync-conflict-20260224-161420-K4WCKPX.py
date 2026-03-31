import docopt

__doc__ = '''Om.

Usage:
    __main__.py (-h | --help)
    __main__.py (-v | --version)
    __main__.py parse    [-c] <source> [-fj <json>]
    __main__.py deparse  [-c] <source> [-fm <om>]
    __main__.py evaluate [-c] <source> [-fm <om>]

Options:
    -h --help         Show this screen
    -v --version      Version information
    -j --json <json>  Parse   Om   to file [default: ./saved.json]
    -m --om   <om>    Deparse JSON to file [default: ./saved.om]
    -f --force        Force-overwrite output file(s)

Om-py v0.1, by Olivia (Cat) Stevens (catb0t)
'''

from .parser import parser, deparser
from .evaluator import evaluator


def main():
    args = docopt.docopt(__doc__)
    cmd_code = False
    if args['-c']:
        cmd_code = True
    if args['parse']:
        parser(args['<source>'], cmd_code, args['--json'], args['--force'])
    elif args['deparse']:
        deparser(args['<source>'], cmd_code, args['--om'], args['--force'])
    elif args['evaluate']:
        evaluator(args['<source>'], cmd_code, args['--om'], args['--force'])


if __name__ == '__main__':
    main()
