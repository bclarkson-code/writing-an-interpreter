from abc import abstractmethod
from dataclasses import dataclass

from writing_an_interpreter.tokens import Token


class Node:
    @abstractmethod
    def token_literal(self) -> str:
        pass


class Statement(Node):
    @abstractmethod
    def statement_node(self):
        pass


class Expression(Node):
    @abstractmethod
    def expression_node(self):
        pass


@dataclass
class Identifier(Expression):
    token: Token
    value: str

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal


@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier
    value: Expression

    def token_literal(self):
        return self.token.literal

    def statement_node(self):
        return None


@dataclass
class Program:
    statements: list[Statement]

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""
