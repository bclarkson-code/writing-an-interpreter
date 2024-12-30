from enum import IntEnum, auto
from typing import Callable

from writing_an_interpreter.ast import (
    Boolean,
    Expression,
    ExpressionStatement,
    Identifier,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
)
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.tokens import Token, TokenType


class ParseError(Exception):
    """
    Raised when parsing fails
    """


class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()  # ==
    LESSGREATER = auto()  # > or <
    SUM = auto()  # +
    PRODUCT = auto()  # *
    PREFIX = auto()  # -X or !X
    CALL = auto()  # myFunction(X)


precedences = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
}


class Parser:
    lexer: Lexer
    current: Token
    next: Token
    errors: list[Exception]
    prefix_parse_functions: dict[TokenType, Callable]
    infix_parse_functions: dict[TokenType, Callable]

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current = self.lexer.next_token()
        self.next = self.lexer.next_token()

        self.errors = []

        self.prefix_parse_functions = {}
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_integer_literal)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.TRUE, self.parse_boolean)
        self.register_prefix(TokenType.FALSE, self.parse_boolean)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)

        self.infix_parse_functions = {}
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)

    def next_token(self):
        self.current = self.next
        self.next = self.lexer.next_token()

    def current_token_is(self, token_type: TokenType):
        return self.current.type == token_type

    def peek_token_is(self, token_type: TokenType):
        return self.next.type == token_type

    def expect_peek(self, token_type: TokenType):
        if self.peek_token_is(token_type):
            self.next_token()
            return True
        else:
            self.errors.append(
                ParseError(
                    f"expected next token to be {token_type}, got {self.next.type} instead"
                )
            )
            return False

    def parse_program(self):
        statements = []

        while self.current.type != TokenType.EOF:
            if statement := self.parse_statement():
                statements.append(statement)
            self.next_token()
        return Program(statements=statements)

    def parse_statement(self):
        match self.current.type:
            case TokenType.LET:
                return self.parse_let_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self):
        token = self.current
        if not self.expect_peek(TokenType.IDENT):
            return None

        identifier = Identifier(token=self.current, value=self.current.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        # keep going until we hit a semicolon
        while not self.current_token_is(TokenType.SEMICOLON):
            self.next_token()

        return LetStatement(token=token, name=identifier, value=None)

    def parse_return_statement(self):
        token = self.current

        self.next_token()

        while not self.current_token_is(TokenType.SEMICOLON):
            self.next_token()
        return ReturnStatement(token=token, return_value=None)

    def register_prefix(self, token_type: TokenType, parse_function: Callable):
        self.prefix_parse_functions[token_type] = parse_function

    def register_infix(self, token_type: TokenType, parse_function: Callable):
        self.infix_parse_functions[token_type] = parse_function

    def parse_expression_statement(self):
        token = self.current

        expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return ExpressionStatement(token=token, expression=expression)

    def parse_expression(self, precedence: Precedence) -> Expression | None:
        prefix = self.prefix_parse_functions.get(self.current.type, None)
        if prefix is None:
            self.errors.append(
                ParseError(f"no prefix parse function for {self.current.type} found")
            )
            return None

        left = prefix()

        while (
            not self.peek_token_is(TokenType.SEMICOLON)
            and precedence < self.peek_precedence()
        ):
            infix = self.infix_parse_functions.get(self.next.type)
            if infix is None:
                return left
            self.next_token()
            left = infix(left)

        return left

    def parse_identifier(self) -> Identifier:
        return Identifier(token=self.current, value=self.current.literal)

    def parse_integer_literal(self) -> IntegerLiteral | None:
        try:
            value = int(self.current.literal)
        except ValueError:
            error = ParseError(f"Could not parse {self.current.literal} as integer")
            self.errors.append(error)
            return None

        return IntegerLiteral(token=self.current, value=value)

    def parse_prefix_expression(self) -> PrefixExpression:
        token = self.current
        operator = self.current.literal
        self.next_token()
        right = self.parse_expression(Precedence.PREFIX)

        return PrefixExpression(token=token, operator=operator, right=right)

    def peek_precedence(self) -> Precedence:
        return precedences.get(self.next.type, Precedence.LOWEST)

    def current_precedence(self) -> Precedence:
        return precedences.get(self.current.type, Precedence.LOWEST)

    def parse_infix_expression(self, left: Expression) -> InfixExpression:
        token = self.current
        operator = self.current.literal
        precedence = self.current_precedence()

        self.next_token()
        right = self.parse_expression(precedence)

        return InfixExpression(token=token, left=left, operator=operator, right=right)

    def parse_boolean(self) -> Boolean:
        return Boolean(token=self.current, value=self.current_token_is(TokenType.TRUE))

    def parse_grouped_expression(self) -> Expression | None:
        self.next_token()

        expression = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return expression
