from src.lambda_calc.parser import parse
from src.lambda_calc.evaluator import expand_macroses, reduce_term


def evaluate_full(code: str, max_steps: int = 1000) -> str:
    program = parse(code)
    term = expand_macroses(program.target, program.macros)

    step = 0
    while step < max_steps:
        next = reduce_term(term)
        if next is None:
            return str(term)

        term = next
        step += 1

    return "TIMEOUT"


def test_identity():
    code = "(\\x.x) y"
    result = evaluate_full(code)
    assert result == "y"


def test_logic_not_true():
    code = """
    TRUE = \\x y.x
    FALSE = \\x y.y
    NOT = \\p.p FALSE TRUE
    
    NOT TRUE
    """
    result = evaluate_full(code)
    assert result == "(\\x.(\\y.y))"


def test_alpha_conversion():
    code = "(\\x y.x) y"
    result = evaluate_full(code)
    assert result == "(\\y1.y)"


def test_omega_combinator():
    code = "(\\x.x x) (\\x.x x)"
    result = evaluate_full(code, max_steps=50)
    assert result == "TIMEOUT"


def test_church_addition():
    code = """
    ZERO = \\f x.x
    SUCC = \\n f x.f (n f x)
    ADD = \\m n.m SUCC n
    
    ONE = SUCC ZERO
    
    ADD ONE ONE
    """
    result = evaluate_full(code)
    assert result == "(\\f.(\\x.(f (f x))))"
