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
        term = None

        for arg in args:
            if isinstance(arg, tuple):
                macroses[arg[0]] = arg[1]
            elif isinstance(arg, Term):
                term = arg

        return Program(macros=macroses, target=term)

    def macros_def(self, macros_name, term):
        return (str(macros_name), term)

    def vars(self, *tokens):
        return "".join(str(t) for t in tokens)

    def abstraction(self, vars, body):
        term = body
        for var in reversed(vars):
            term = Abstraction(param=var, body=term)
        return term

    def application(*atoms):
        return reduce(Application, atoms)

    def variable(self, token):
        chars = str(token)
        if len(chars) > 1:
            atoms = [Variable(c) for c in token]
            return reduce(Application, atoms)
        return Variable(str(token))

    def macro(self, token):
        return MacroReference(str(token))


def parse(code: str) -> Program:
    parser = Lark(
        LAMBDA_GRAMMAR, start="start", parser="lalr", transformer=ASTTransformer()
    )
    return parser.parse(code)


# TODO remove sample
if __name__ == "__main__":
    code = """
    TRUE = \\x y.x
    FALSE = \\x y.y
    NOT = \\p.p FALSE TRUE
    
    NOT TRUE
    """
    program = parse(code)
    print(program)
    print(repr(program.target))

    debug_parser = Lark(LAMBDA_GRAMMAR, start="start", parser="lalr")
    tree = debug_parser.parse(r"\xy.x y")
    larktree.pydot__tree_to_png(tree, "term.png")
    print(tree.pretty())
