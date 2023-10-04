from enum import Enum


class CantParse(Enum):
    STRAY_CLOSE = 0
    STRAY_OPEN = 1


MESSAGES = {
    CantParse.STRAY_CLOSE: ('close', 'open'),
    CantParse.STRAY_OPEN: ('open', 'close')
}


'''
    ....ParseError:
    Syntax Error

    When parsing compound literal object:
        [1 [2 3]
           |
           ^ HERE

    Stray open brace    at line 1, column 5     marked by 'HERE'
        -> <input>:1:5
        -> no matching close brace `]`

    ===

    ....ParseError:
    Syntax Error

    When parsing compound literal object:
        "#{ [ }"
         *  |
            ^ HERE

    Stray open brace            at line 1, column 5     marked by 'HERE'
    In string interpolation     at line 1, column 2     marked by *
        -> <input>:1:5
           no matching close brace `]`
        -> <input>:1:2
           syntax error in string interpolation


    WRITTEN AS:
    Syntax Error

    When parsing {problem.node_display_name}:
        {context_snippet}
        {ptr_intro}{first_ptr}{ptr_between}{maybe_second_ptr}
        {align_here_ptr_whitespace}{here_ptr} {HERE_MARKER}

    {problem.title}{align_title_1_1}at line {problem.pos1.line}, column {problem.pos1.col}{align_marker_1_2}marked by '{HERE_MARKER}'
    {parent.title}{align_title_2_1}at line {parent.pos1.line}, column {parent.pos1.col}{align_marker_2_2}marked by {STAR_MARKER}
        -> {problem.fname}:{line}:{col}
           {problem.detail}
        -> {parent.fname}:{line}:{col}
           {parent.detail}

    Run brat_help(syntax:{problem.node_id}) for help with this error.
'''


class ParseError(Exception):

    def __init__(self, problem, parent=None):
        self.problem = problem
        self.parent = parent
        self.parent_has_own_cause = hasattr(parent, 'cause')
        super().__init__()

    def __str__(self):
        '''kind, unkind = MESSAGES[self.problem]
        spaces = ' ' * (
            19 + self.offset + sum(self.source.count(s) for s in ("\n", "\t")))
        ''.format(
            kind=kind,
            unkind=unkind,
            fname=self.fname,
            bridge=spaces + '|',
            ptr=spaces + '^ HERE',
            line=self.line,
            col=self.col,
            form=repr(self.source[self.begin:self.end])
        )'''
        ptr_intro = ' ' * 3
        first_ptr = '*'
        ptr_between = ' ' * 12
        maybe_second_ptr = '|'
        align_here_ptr_space = ptr_intro + ptr_between + 2
        align_here_ptr_whitespace = ' ' * align_here_ptr_space
        here_ptr = '^'

        align_title_1_1 = align_marker_1_2 = align_title_2_1 = align_marker_2_2 = 4
        HERE_MARKER = 'HERE'
        STAR_MARKER = '*'
        error_message = f'''
Syntax Error

When parsing {self.problem.node.display_name}:
    {self.problem.context}
    {ptr_intro}{first_ptr}{ptr_between}{maybe_second_ptr}
    {align_here_ptr_whitespace}{here_ptr} {HERE_MARKER}

{self.problem.title}{align_title_1_1}at line {self.problem.pos1.line}, column {self.problem.pos1.col}{align_marker_1_2}marked by '{HERE_MARKER}'
{self.parent.title}{align_title_2_1}at line {self.parent.pos1.line}, column {self.parent.pos1.col}{align_marker_2_2}marked by {STAR_MARKER}
    -> {self.problem.fname}:{self.problem.pos1.line}:{self.problem.pos1.col}
       {self.problem.detail}
    -> {self.parent.fname}:{self.parent.pos1.line}:{self.parent.pos1.col}
       {self.parent.detail}

Run brat_help('syntax:{self.problem.node_id}') for help with this error.
'''
        return error_message
