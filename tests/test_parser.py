from writing_an_interpreter.ast import LetStatement
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.parser import Parser


def test_can_parse_let_statements():
    string = """
let x = 5;
let y = 10;
let foobar = 838383;
    """
    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()

    assert program is not None
    assert len(program) == 3

    assert is_let_statement_valid(program[0], "x")
    assert is_let_statement_valid(program[1], "y")
    assert is_let_statement_valid(program[2], "foobar")


def is_let_statement_valid(statement: LetStatement, name: str):
    assert statement.token_literal() == "let"
    assert statement.name.value == name
    assert statement.name.token_literal == name

    return True
