from writing_an_interpreter.environment import Environment
from writing_an_interpreter.evaluator import monkey_eval
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.objects import (
    Boolean,
    Error,
    Function,
    Integer,
    Null,
    Object,
    String,
)
from writing_an_interpreter.parser import Parser


def test_can_eval_integer_expression():
    tests = [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ]

    for string, want in tests:
        got = run_eval(string)
        assert is_integer_object_valid(got, want)


def test_can_eval_boolean_expression():
    tests = [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ]

    for string, want in tests:
        got = run_eval(string)
        assert is_boolean_object_valid(got, want)


def test_can_eval_bang_operator():
    tests = [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ]

    for string, want in tests:
        got = run_eval(string)
        assert is_boolean_object_valid(got, want)


def test_if_else_expression():
    tests = [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ]
    for string, want in tests:
        got = run_eval(string)
        if want is None:
            assert is_null_object_valid(got)
        else:
            assert is_integer_object_valid(got, want)


def test_return_statements():
    tests = [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        (
            """
if (10 > 1) { 
    if (10 > 1) { 
        return 10; 
    } 
    return 1;
} """,
            10,
        ),
    ]
    for string, want in tests:
        got = run_eval(string)
        assert is_integer_object_valid(got, want)


def test_error_handling():
    tests = [
        ("5 + true;", "type mismatch: INTEGER + BOOLEAN"),
        ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"),
        ("-true", "unknown operator: -BOOLEAN"),
        ("true + false;", "unknown operator: BOOLEAN + BOOLEAN"),
        ("5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN"),
        ("if (10 > 1) { true + false; }", "unknown operator: BOOLEAN + BOOLEAN"),
        (
            "if (10 > 1) { if (10 > 1) { return true + false; } return 1; } ",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        ("foobar", "identifier not found: foobar"),
        ('"Hello" - "World"', "unknown operator: STRING - STRING"),
    ]
    for string, want in tests:
        got = run_eval(string)
        assert isinstance(got, Error)
        assert got.message == want


def test_can_eval_let_statements():
    tests = [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ]

    for string, want in tests:
        got = run_eval(string)
        assert is_integer_object_valid(got, want)


def test_can_build_function_object():
    string = "fn(x) { x + 2; };"

    got = run_eval(string)
    assert isinstance(got, Function)
    assert str(got.parameters) == "[x]"
    assert str(got.body) == "(x + 2)"


def test_can_eval_function_application_statements():
    tests = [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ]

    for string, want in tests:
        got = run_eval(string)
        assert is_integer_object_valid(got, want)


def test_can_build_string_literal():
    string = '"Hello world!"'

    got = run_eval(string)
    assert isinstance(got, String)
    assert str(got.value) == "Hello world!"


def test_can_concat_string():
    string = '"Hello" + " " + "world!"'

    got = run_eval(string)
    assert isinstance(got, String)
    assert str(got.value) == "Hello world!"


def test_can_eval_builtin_functions():
    tests = [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to 'len' not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
    ]

    for string, want in tests:
        got = run_eval(string)
        match want:
            case int():
                assert is_integer_object_valid(got, want)
            case str():
                assert isinstance(got, Error)
                assert got.message == want


# --------helper functions---------
def run_eval(string: str) -> Object:
    environment = Environment()
    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    return monkey_eval(program, environment)


def is_integer_object_valid(got: Integer, want: int):
    assert isinstance(got, Integer)
    assert got.value == want
    return True


def is_boolean_object_valid(got: Boolean, want: int):
    assert isinstance(got, Boolean)
    assert got.value == want
    return True


def is_null_object_valid(got: Null):
    assert isinstance(got, Null)
    return True
