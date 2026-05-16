from functools import reduce
from lark import Lark, Transformer, v_args
from lark import tree as larktree
from models import (
    Term,
    Variable,
    Abstraction,
    Application,
    MacroReference,
    Program,
)

LAMBDA_GRAMMAR = r"""
start: _NL* (macro_def _NL+)* term _NL*

macro_def: MACRO_NAME "=" term

?term: "\\" vars "." term  -> abstraction
     | application

?application: atom+             -> application

?atom: VAR_CHARS                -> variable
     | MACRO_NAME               -> macro
     | "(" _NL* term _NL* ")"   

vars: VAR_CHARS+

VAR_CHARS: /[a-z]+/
MACRO_NAME: /[A-Z0-9_]+/

%import common.WS_INLINE
%import common.NEWLINE -> _NL
%ignore WS_INLINE
"""


@v_args(inline=True)
class ASTTransformer(Transformer):
    def start(self, *args):
        macroses = {}
        target_term = None

        for arg in args:
            if isinstance(arg, tuple):
                macroses[arg[0]] = arg[1]
            elif isinstance(arg, Term):
                target_term = arg

        return Program(macros=macroses, target=target_term)

    def macro_def(self, macro_name, term):
        return (str(macro_name), term)

    def vars(self, *tokens):
        return "".join(str(t) for t in tokens)

    def abstraction(self, vars_str, body):
        term = body
        for var in reversed(vars_str):
            term = Abstraction(param=var, body=term)
        return term

    def application(self, *atoms):
        return reduce(Application, atoms)

    def variable(self, token):
        chars = str(token)
        if len(chars) > 1:
            atoms = [Variable(c) for c in chars]
            return reduce(Application, atoms)
        return Variable(chars)

    def macro(self, token):
        return MacroReference(str(token))


def parse(code: str) -> Program:
    parser = Lark(
        LAMBDA_GRAMMAR, start="start", parser="lalr", transformer=ASTTransformer()
    )
    return parser.parse(code)
