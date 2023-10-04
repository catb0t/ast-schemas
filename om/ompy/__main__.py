import ompy.parser as parser
import ompy.evaluator as ev


def _parevde(prog: str) -> str:
    return parser.deparse( ev.evaluate( parser.parse( prog ) ) )


def _parevde_file(fp):
    return _parevde(fp.read().rstrip('\n\r'))
