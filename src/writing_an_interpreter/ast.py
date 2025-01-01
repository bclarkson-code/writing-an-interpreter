from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from writing_an_interpreter.tokens import Token


class Node:
    @abstractmethod
    def token_literal(self) -> str:
        pass

    def __repr__(self):
        return self.__str__()


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

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier
    value: Expression

    def token_literal(self):
        return self.token.literal

    def statement_node(self):
        return None

    def __str__(self):
        literal = self.token_literal()
        name = str(self.name)

        return f"{literal} {name} = {self.value};"

    def __repr__(self):
        return self.__str__()


@dataclass
class ReturnStatement(Statement):
    token: Token
    return_value: Expression

    def statement_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        literal = self.token_literal()
        return_value = str(self.return_value)

        return f"{literal} {return_value};"

    def __repr__(self):
        return self.__str__()


@dataclass
class ExpressionStatement(Statement):
    token: Token
    expression: Expression

    def statement_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        if self.expression is None:
            return ""
        return str(self.expression)

    def __repr__(self):
        return self.__str__()


@dataclass
class IntegerLiteral(Expression):
    token: Token
    value: int

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return str(self.token.literal)

    def __repr__(self):
        return self.__str__()


@dataclass
class PrefixExpression(Expression):
    token: Token
    operator: str
    right: Expression

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"({self.operator}{self.right})"

    def __repr__(self):
        return self.__str__()


@dataclass
class InfixExpression(Expression):
    token: Token
    left: Expression
    operator: str
    right: Expression

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

    def __repr__(self):
        return self.__str__()


@dataclass
class BooleanExpression(Expression):
    token: Token
    value: bool

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return self.token.literal

    def __repr__(self):
        return self.__str__()


@dataclass
class BlockStatement(Expression):
    token: Token
    statements: list[Statement]

    def statement_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "".join(str(s) for s in self.statements)


@dataclass
class IfExpression(Expression):
    token: Token
    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement | None = None

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"if{self.condition}{self.consequence}{self.alternative}"


@dataclass
class FunctionLiteral(Expression):
    token: Token
    parameters: list[Identifier]
    body: BlockStatement

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        params = ", ".join(str(p) for p in self.parameters)
        return f"{self.token_literal()}({params}){self.body}"


@dataclass
class CallExpression(Expression):
    token: Token
    function: FunctionLiteral | Identifier
    arguments: list[Expression]

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        args = ", ".join(str(a) for a in self.arguments)
        return f"{str(self.function)}({args})"


@dataclass
class StringLiteral(Expression):
    token: Token
    value: str

    def expression_node(self):
        return None

    def token_literal(self):
        return self.token.literal

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.token.literal


@dataclass
class Program(Sequence):
    statements: list[Statement]

    def __init__(self, statements: list | None = None):
        if statements is None:
            self.statements = []
        else:
            self.statements = statements

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        return ""

    def __len__(self):
        return len(self.statements)

    def __getitem__(self, key):
        return self.statements.__getitem__(key)

    def __str__(self):
        statements = [str(s) for s in self.statements]
        return "".join(statements)

    def __repr__(self):
        return self.__str__()
