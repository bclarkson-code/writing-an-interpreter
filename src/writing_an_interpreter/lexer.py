from writing_an_interpreter.token import Token, TokenType, keywords


class Lexer:
    inputs: str
    position: int = 0
    read_position: int = 0
    current: str = ""

    def __init__(self, inputs: str):
        self.inputs = inputs
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.inputs):
            self.current = ""
        else:
            self.current = self.inputs[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def next_token(self):
        self.skip_whitespace()
        match self.current:
            case "=":
                token = Token(TokenType.ASSIGN, self.current)
            case "+":
                token = Token(TokenType.PLUS, self.current)
            case ",":
                token = Token(TokenType.COMMA, self.current)
            case ";":
                token = Token(TokenType.SEMICOLON, self.current)
            case "(":
                token = Token(TokenType.LPAREN, self.current)
            case ")":
                token = Token(TokenType.RPAREN, self.current)
            case "{":
                token = Token(TokenType.LBRACE, self.current)
            case "}":
                token = Token(TokenType.RBRACE, self.current)
            case "":
                token = Token(TokenType.EOF, "")
            case _:
                if self.is_letter(self.current):
                    literal = self.read_identifier()
                    return Token(keywords.get(literal, TokenType.IDENT), literal)
                elif self.is_number(self.current):
                    literal = self.read_number()
                    return Token(keywords.get(literal, TokenType.INT), literal)
                else:
                    token = Token(TokenType.ILLEGAL, self.current)

        self.read_char()
        return token

    def is_letter(self, char: str):
        if not isinstance(char, str) or len(char) > 1:
            raise ValueError(f"Expected string of length 1. Found: {char}")

        is_lowercase = ord("a") <= ord(char) <= ord("z")
        is_uppercase = ord("A") <= ord(char) <= ord("A")
        is_underscore = char == "_"

        return is_lowercase | is_uppercase | is_underscore

    def is_number(self, char: str):
        if not isinstance(char, str) or len(char) > 1:
            raise ValueError(f"Expected string of length 1. Found: {char}")

        return ord("0") <= ord(char) <= ord("9")

    def read_identifier(self):
        start = self.position
        while self.is_letter(self.current):
            self.read_char()

        return self.inputs[start : self.position]

    def read_number(self):
        start = self.position
        while self.is_number(self.current):
            self.read_char()

        return self.inputs[start : self.read_position]

    def skip_whitespace(self):
        while self.current in {" ", "\n", "\t", "\r"}:
            self.read_char()
