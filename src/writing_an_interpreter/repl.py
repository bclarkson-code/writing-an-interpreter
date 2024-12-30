from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.tokens import TokenType

PROMPT = ">> "


def start():
    while True:
        print(PROMPT, end="")
        scanned = input()
        lexer = Lexer(scanned)

        next_token = lexer.next_token()

        while next_token.type != TokenType.EOF:
            print(next_token)
            next_token = lexer.next_token()


if __name__ == "__main__":
    start()
