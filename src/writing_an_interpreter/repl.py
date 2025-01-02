import sys
from pathlib import Path

from writing_an_interpreter.environment import Environment
from writing_an_interpreter.evaluator import monkey_eval
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.objects import Object
from writing_an_interpreter.parser import ParseError, Parser

PROMPT = ">> "


MONKEY_FACE = r'''           __,__ 
  .--.  .-"     "-.  .--. 
 / .. \/  .-. .-.  \/ .. \ 
| |  '|  /   Y   \  |' | | 
| \   \  \ 0 | 0 / /   / | 
 \ '- ,\.-""" """-./, -' /
  ''-' /_   ^ ^   _\ '-'' 
      |  \._   _./  | 
      \   \ '~' /   / 
       '._ '-=-' _.' 
          '-----'
'''


def execute_string(text, environment) -> Object | None | list[Exception]:
    lexer = Lexer(text)
    parser = Parser(lexer)
    program = parser.parse_program()
    if parser.errors:
        print(MONKEY_FACE)
        print("Woops! We ran into some monkey business here!")
        print("    parser errors:")
        for error in parser.errors:
            print("        " + str(error))
        return parser.errors

    return monkey_eval(program, environment)


def load_standard_library(environment):
    # Try to get the PyInstaller bundle path first
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
        stdlib_path = base_path / "writing_an_interpreter" / "standard_library.🐵"
    else:
        # If not bundled, use the original Path approach
        stdlib_path = Path(__file__).parent / "standard_library.🐵"
    
    try:
        out = execute_string(stdlib_path.read_text(), environment)
        if isinstance(out, list):
            # failed to read standard library
            exit(1)
        return environment
    except FileNotFoundError as e:
        print(f"Failed to load standard library from {stdlib_path}: {e}")
        exit(1)


def start():
    environment = Environment()
    environment = load_standard_library(environment)

    while True:
        print(PROMPT, end="")
        scanned = input()
        evaluated = execute_string(scanned, environment)
        if isinstance(evaluated, list):
            continue
        elif evaluated is not None:
            print(evaluated.inspect())


if __name__ == "__main__":
    start()
