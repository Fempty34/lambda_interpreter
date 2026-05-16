from models import *


def get_free_vars(term: Term) -> set[str]:
    match term:
        case Variable(name):
            return {name}
        case Application(left, right):
            return get_free_vars(left) | get_free_vars(right)
        case Abstraction(param, body):
            return get_free_vars(body) - {param}
        case MacroReference(name):
            return set()
        case _:
            raise ValueError(f"Unexpectable type of node: {type(term)}")


def expand_macroses(term: Term, macroses: dict[str, Term]) -> Term:
    match term:
        case Variable(name):
            return term
        case Application(left, right):
            return Application(
                expand_macroses(left, macroses), expand_macroses(right, macroses)
            )
        case Abstraction(param, body):
            return Abstraction(param, expand_macroses(body, macroses))
        case MacroReference(name):
            if name not in macroses:
                raise ValueError(f"Undefined marcro: {name}")

            return expand_macroses(macroses[name], macroses)
        case _:
            raise ValueError(f"Unexpectable type of node: {type(term)}")


def alpha_reduction(name: str, used_names: set[str]) -> str:
    counter = 1
    res = f"{name}{counter}"
    while res in used_names:
        counter += 1
        res = f"{name}{counter}"
    return res


def subtitude(term: Term, var: str, value: Term) -> Term:
    match term:
        case Variable(name):
            if name == var:
                return value
            return term
        case Application(left, right):
            return Application(
                subtitude(left, var, value), subtitude(right, var, value)
            )
        case Abstraction(param, body):
            if param == var:
                return term

            free_vars = get_free_vars(value)
            if param in free_vars and var in get_free_vars(body):
                used_names = get_free_vars(body) | free_vars | {var}

                new_param = alpha_reduction(param, used_names)
                new_body = subtitude(body, param, Variable(new_param))

                return Abstraction(
                    param=new_param, body=subtitude(new_body, var, value)
                )
            return Abstraction(param=param, body=subtitude(body, var, value))
        case MacroReference(name):
            raise RuntimeError(
                f"Noticed unexpectable marco: {name}, expand macroses before subtitude"
            )


def reduce_term(term: Term) -> Term | None:
    match term:
        case Variable(name):
            return None

        case Abstraction(param, body):
            new_body = reduce_term(body)
            if new_body is not None:
                return Abstraction(param, new_body)
            return None

        case Application(left, right):
            if isinstance(left, Abstraction):
                return subtitude(left.body, left.param, right)

            new_left = reduce_term(left)
            if new_left is not None:
                return Application(new_left, right)

            new_right = reduce_term(right)
            if new_right is not None:
                return Application(left, new_right)

            return None

        case MacroReference(name):
            return None
