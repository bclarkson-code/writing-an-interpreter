from writing_an_interpreter.evaluator import monkey_eval
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.parser import Parser

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


def start():
    while True:
        print(PROMPT, end="")
        scanned = input()
        lexer = Lexer(scanned)
        parser = Parser(lexer)
        program = parser.parse_program()

        if parser.errors:
            print(MONKEY_FACE)
            print("Woops! We ran into some monkey business here!")
            print("    parser errors:")
            for error in parser.errors:
                print("        " + str(error))
            continue

        evaluated = monkey_eval(program)
        if evaluated is not None:
            print(evaluated.inspect())


if __name__ == "__main__":
    start()
