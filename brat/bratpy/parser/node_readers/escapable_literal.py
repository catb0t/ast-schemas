import re
from .._parse_common import ESCAPE


def escapable_literal_reader(
    opener,
    closer=None,
    escaper=ESCAPE,
    unclosed=False,
    single_line=False
):
    if closer is None:
        closer = opener
    if unclosed == 'allow':
        closer = f'(?:[^{closer}]|{closer}|)'
    elif unclosed:
        closer = f'(?:[^{closer}]|)'
    escaper = re.escape(escaper)
    return re.compile(
        f'{opener}((?:(?!{closer}|{escaper}).)*?(?:{escaper}.(?:(?!{closer}|{escaper}).)*)*?){closer}',  # noqa
        flags=re.DOTALL if not single_line else 0
    )


def backslashreplace(s):
    return s.encode('latin-1', 'backslashreplace').decode('unicode_escape')


def unescaped_delimiter_finder(delim, escaper=ESCAPE):
    escaper = re.escape(escaper)
    test = re.compile(
        f'(?<!{escaper}){delim}'
    )

    def func(s):
        # print(f's: `{s}`')
        t = test.findall(backslashreplace(s))
        # print(f't: {t}')
        return t

    return func
