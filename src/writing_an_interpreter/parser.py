from writing_an_interpreter.ast import Program
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.tokens import Token, TokenType


class Parser:
    lexer: Lexer
    current: Token
    next: Token

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current = self.lexer.next_token()
        self.next = self.lexer.next_token()

    def next_token(self):
        self.current = self.next
        self.next = self.lexer.next_token()

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
            case _:
                return None

    def parse_let_statement(self):
        if 

