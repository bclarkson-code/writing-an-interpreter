from enum import IntEnum, auto
from typing import Callable

from writing_an_interpreter.ast import (
    BlockStatement,
    BooleanExpression,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    Identifier,
    IfExpression,
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
    TokenType.LPAREN: Precedence.CALL,
}


class Parser:
    lexer: Lexer
    token: Token
    next: Token
    errors: list[Exception]
    prefix_parse_functions: dict[TokenType, Callable]
    infix_parse_functions: dict[TokenType, Callable]

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()
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
        self.register_prefix(TokenType.IF, self.parse_if_expression)
        self.register_prefix(TokenType.FUNCTION, self.parse_function_literal)

        self.infix_parse_functions = {}
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)
        self.register_infix(TokenType.LPAREN, self.parse_call_expression)

    def next_token(self):
        self.token = self.next
        self.next = self.lexer.next_token()

    def current_token_is(self, token_type: TokenType):
        return self.token.type == token_type

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

        while self.token.type != TokenType.EOF:
            if statement := self.parse_statement():
                statements.append(statement)
            self.next_token()
        return Program(statements=statements)

    def parse_statement(self):
        match self.token.type:
            case TokenType.LET:
                return self.parse_let_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self):
        token = self.token
        if not self.expect_peek(TokenType.IDENT):
            return None

        identifier = Identifier(token=self.token, value=self.token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return LetStatement(token=token, name=identifier, value=value)

    def parse_return_statement(self):
        token = self.token

        self.next_token()

        return_value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return ReturnStatement(token=token, return_value=return_value)

    def register_prefix(self, token_type: TokenType, parse_function: Callable):
        self.prefix_parse_functions[token_type] = parse_function

    def register_infix(self, token_type: TokenType, parse_function: Callable):
        self.infix_parse_functions[token_type] = parse_function

    def parse_expression_statement(self):
        token = self.token

        expression = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return ExpressionStatement(token=token, expression=expression)

    def parse_expression(self, precedence: Precedence) -> Expression | None:
        prefix = self.prefix_parse_functions.get(self.token.type, None)
        if prefix is None:
            self.errors.append(
                ParseError(f"no prefix parse function for {self.token.type} found")
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
        return Identifier(token=self.token, value=self.token.literal)

    def parse_integer_literal(self) -> IntegerLiteral | None:
        try:
            value = int(self.token.literal)
        except ValueError:
            error = ParseError(f"Could not parse {self.token.literal} as integer")
            self.errors.append(error)
            return None

        return IntegerLiteral(token=self.token, value=value)

    def parse_prefix_expression(self) -> PrefixExpression:
        token = self.token
        operator = self.token.literal
        self.next_token()
        right = self.parse_expression(Precedence.PREFIX)

        return PrefixExpression(token=token, operator=operator, right=right)

    def peek_precedence(self) -> Precedence:
        return precedences.get(self.next.type, Precedence.LOWEST)

    def current_precedence(self) -> Precedence:
        return precedences.get(self.token.type, Precedence.LOWEST)

    def parse_infix_expression(self, left: Expression) -> InfixExpression:
        token = self.token
        operator = self.token.literal
        precedence = self.current_precedence()

        self.next_token()
        right = self.parse_expression(precedence)

        return InfixExpression(token=token, left=left, operator=operator, right=right)

    def parse_boolean(self) -> BooleanExpression:
        return BooleanExpression(
            token=self.token, value=self.current_token_is(TokenType.TRUE)
        )

    def parse_grouped_expression(self) -> Expression | None:
        self.next_token()

        expression = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return expression

    def parse_if_expression(self) -> Expression | None:
        token = self.token

        if not self.expect_peek(TokenType.LPAREN):
            return None
        self.next_token()

        condition = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        consequence = self.parse_block_statement()

        if self.next.type == TokenType.ELSE:
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None

            alternative = self.parse_block_statement()
        else:
            alternative = None

        return IfExpression(
            token=token,
            condition=condition,
            consequence=consequence,
            alternative=alternative,
        )

    def parse_block_statement(self):
        token = self.token
        statements = []

        self.next_token()
        while self.token.type not in [TokenType.RBRACE, TokenType.EOF]:
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            self.next_token()
        return BlockStatement(token=token, statements=statements)

    def parse_function_literal(self):
        token = self.token

        if not self.expect_peek(TokenType.LPAREN):
            return None

        parameters = self.parse_function_parameters()
        if not self.expect_peek(TokenType.LBRACE):
            return None

        body = self.parse_block_statement()

        return FunctionLiteral(token=token, parameters=parameters, body=body)

    def parse_function_parameters(self) -> list[Identifier] | None:
        identifiers = []
        if self.peek_token_is(TokenType.RPAREN):
            self.next_token()
            return identifiers
        self.next_token()

        identifiers.append(Identifier(token=self.token, value=self.token.literal))

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            identifiers.append(Identifier(token=self.token, value=self.token.literal))

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return identifiers

    def parse_call_expression(self, function: FunctionLiteral | Identifier):
        token = self.token
        arguments = self.parse_call_arguments()
        return CallExpression(token=token, function=function, arguments=arguments)

    def parse_call_arguments(self):
        arguments = []

        if self.peek_token_is(TokenType.RPAREN):
            self.next_token()
            return arguments

        self.next_token()
        arguments.append(self.parse_expression(Precedence.LOWEST))

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            arguments.append(self.parse_expression(Precedence.LOWEST))

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return arguments
