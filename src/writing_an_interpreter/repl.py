from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.parser import Parser

PROMPT = ">> "


def start():
    while True:
        print(PROMPT, end="")
        scanned = input()
        lexer = Lexer(scanned)
        parser = Parser(lexer)
        program = parser.parse_program()

        if parser.errors:
            for error in parser.errors:
                print(error)
            continue

        print(program)


if __name__ == "__main__":
    start()
