import docopt

__doc__ = '''Om.

Usage:
    __main__.py (-h | --help)
    __main__.py (-v | --version)
    __main__.py parse    <source> [-fj <json>]
    __main__.py deparse  <source> [-fm <om>]
    __main__.py evaluate <source> [-fm <om>]

Options:
    -h --help         Show this screen
    -v --version      Version information
    -j --json <json>  Parse   Om   to file [default: ./saved.json]
    -m --om   <om>    Deparse JSON to file [default: ./saved.om]
    -f --force        Force-overwrite output file(s)
'''

from .parser import parser, deparser
from .evaluator import evaluator


def main():
    args = docopt.docopt(__doc__)
    if args['parse']:
        parser(args['<source>'], args['--json'], args['--force'])
    elif args['deparse']:
        deparser(args['<source>'], args['--om'], args['--force'])
    elif args['evaluate']:
        evaluator(args['<source>'], args['--om'], args['--force'])


if __name__ == '__main__':
    main()
