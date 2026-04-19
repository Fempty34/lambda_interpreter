from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


class Term(ABC):

    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass(frozen=True, slots=True)
class Variable(Term):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class Abstraction(Term):
    param: str
    body: Term

    def __str__(self) -> str:
        return f"(\\{self.param}.{self.body})"


@dataclass(frozen=True, slots=True)
class Application(Term):
    left: Term
    right: Term

    def __str__(self) -> str:
        return f"({self.left} {self.right})"


@dataclass(frozen=True, slots=True)
class MacroReference(Term):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class Program:
    macros: Dict[str, Term]
    target: Term

    def __str__(self) -> str:
        macros_str = "\n".join(f"{name} = {term}" for name, term in self.macros.items())
        return f"{macros_str}\n\n{self.target}".strip()
