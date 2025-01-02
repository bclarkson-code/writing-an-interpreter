from pathlib import Path

from writing_an_interpreter.environment import Environment
from writing_an_interpreter.evaluator import monkey_eval
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.objects import (
    Array,
    Boolean,
    Error,
    Function,
    Hash,
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
        ('{"name": "Monkey"}[fn(x) { x }];', "unusable as hash key: FUNCTION"),
    ]
    for string, want in tests:
        got = run_eval(string)
        assert isinstance(got, Error)
        assert got.message == want


def test_can_eval_let_statements():
    tests = [
        ("let a = 5; a;", 5),
        ('let string = "a"; string;', "a"),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ]

    for string, want in tests:
        got = run_eval(string)
        match want:
            case int():
                assert is_integer_object_valid(got, want)
            case str():
                assert is_string_object_valid(got, want)


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
        ("len({1:1, 2:2})", 2),
        ("len(1)", "argument to 'len' not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
        ("len([1,2,3])", 3),
        ("first([1,2,3])", 1),
        ("first([], [1])", "wrong number of arguments. got=2, want=1"),
        ("first(1)", "argument to 'first' must be ARRAY, got INTEGER"),
        ("last([1,2,3])", 3),
        ("last([], [1])", "wrong number of arguments. got=2, want=1"),
        ("last(1)", "argument to 'last' must be ARRAY, got INTEGER"),
        ("rest([1,2,3])", Array([Integer(2), Integer(3)])),
        ("rest([], [1])", "wrong number of arguments. got=2, want=1"),
        ("rest(1)", "argument to 'rest' must be ARRAY, got INTEGER"),
        ("push([], 1)", Array([Integer(1)])),
        ("push([1,2], 3)", Array([Integer(1), Integer(2), Integer(3)])),
        ("push([])", "wrong number of arguments. got=1, want=2"),
        ("push(1, 1)", "argument to 'push' must be ARRAY, got INTEGER"),
        ("contains({}, 1)", Boolean(False)),
        ("contains({1: 1}, 1)", Boolean(True)),
        ("contains({})", "wrong number of arguments. got=1, want=2"),
        ("contains(1, 1)", "argument to 'contains' must be HASH, got INTEGER"),
        ("keys({})", Array([])),
        ("keys({1:1, 2:2})", Array([Integer(1), Integer(2)])),
        ("keys()", "wrong number of arguments. got=0, want=1"),
        ("keys(1)", "argument to 'keys' must be HASH, got INTEGER"),
        ("values({})", Array([])),
        ("values({1:1, 2:2})", Array([Integer(1), Integer(2)])),
        ("values()", "wrong number of arguments. got=0, want=1"),
        ("values(1)", "argument to 'values' must be HASH, got INTEGER"),
        (
            'read_file("example_script.🐵")',
            Path("example_script.🐵").read_text(),
        ),
        ("read_file()", "wrong number of arguments. got=0, want=1"),
        ('read_file("test", "test")', "wrong number of arguments. got=2, want=1"),
        ('read_file("does_not_exist.🐵")', "file does_not_exist.🐵 does not exist"),
        ("read_file(1)", "argument to 'read_file' must be STRING, got INTEGER"),
        ('read_file("")', "OS error occurred: [Errno 21] Is a directory: '.'"),
        ("sort([])", Array([])),
        ("sort([1,2,3])", Array([Integer(1), Integer(2), Integer(3)])),
        ("sort([3,1,2])", Array([Integer(1), Integer(2), Integer(3)])),
        ("sort()", "wrong number of arguments. got=0, want=1"),
        ("sort([], [])", "wrong number of arguments. got=2, want=1"),
        ("sort(1)", "argument to 'sort' must be ARRAY, got INTEGER"),
        ("sort([true])", "argument to 'sort' must be ARRAY of INTEGER got [BOOLEAN]"),
    ]

    for string, want in tests:
        got = run_eval(string)
        match want:
            case int():
                assert is_integer_object_valid(got, want)
            case str():
                match got:
                    case Error():
                        assert got.message == want
                    case String():
                        assert got.value == want
                    case _:
                        raise TypeError(f"Unexpected type: {type(got)}")


def test_can_build_array_literal():
    string = "[1, 2 * 2, 3 + 3]"

    got = run_eval(string)
    assert isinstance(got, Array)
    assert len(got.elements) == 3

    first, second, third = got.elements

    assert is_integer_object_valid(first, 1)
    assert is_integer_object_valid(second, 4)
    assert is_integer_object_valid(third, 6)


def test_can_build_empty_array_literal():
    string = "[];"

    got = run_eval(string)
    assert isinstance(got, Array)
    assert len(got.elements) == 0


def test_can_eval_array_index_expressions():
    tests = [
        ("[1, 2, 3][0]", 1),
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3][2]", 3),
        ("let i = 0; [1][i];", 1),
        ("[1, 2, 3][1 + 1];", 3),
        ("let myArray = [1, 2, 3]; myArray[2];", 3),
        ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
        ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
        ("[1, 2, 3][3]", None),
        ("[1, 2, 3][-1]", None),
    ]

    for string, want in tests:
        got = run_eval(string)
        if isinstance(want, int):
            assert is_integer_object_valid(got, want)
        else:
            assert is_null_object_valid(got)


def test_can_eval_string_index_expressions():
    tests = [
        # ('"abc"[0]', "a"),
        # ('"abc"[1]', "b"),
        # ('"abc"[2]', "c"),
        # ('let i = 0; "a"[i];', "a"),
        # ('"abc"[1 + 1];', "c"),
        ('let myString = "abc"; myString[2];', "c"),
        ('let myString = "abc"; myString[0] + myString[2] + myString[1];', "acb"),
        ('"abc"[3]', None),
        ('"abc"[-1]', None),
    ]

    for string, want in tests:
        breakpoint()
        got = run_eval(string)
        if isinstance(want, str):
            breakpoint()
            assert is_string_object_valid(got, want)
        else:
            assert is_null_object_valid(got)


def test_can_eval_hash_literals():
    string = """let two = "two"; 
{ 
    "one": 10 - 9, 
    two: 1 + 1, 
    "thr" + "ee": 6 / 2, 
    4: 4, 
    true: 5, 
    false: 6 
}
    """
    got = run_eval(string)
    assert isinstance(got, Hash)
    assert len(got.pairs) == 6

    want = {
        String("one").hash(): 1,
        String("two").hash(): 2,
        String("three").hash(): 3,
        Integer(4).hash(): 4,
        Boolean(True).hash(): 5,
        Boolean(False).hash(): 6,
    }

    for (got_key, got_val), (want_key, want_val) in zip(
        got.pairs.items(), want.items()
    ):
        assert got_key == want_key
        assert got_val.value.value == want_val


def test_can_eval_hash_indexes():
    tests = [
        ('{"foo": 5}["foo"]', 5),
        ('{"foo": 5}["bar"]', None),
        ('let key = "foo"; {"foo": 5}[key]', 5),
        ('{}["foo"]', None),
        ("{5: 5}[5]", 5),
        ("{true: 5}[true]", 5),
        ("{false: 5}[false]", 5),
    ]

    for string, want in tests:
        got = run_eval(string)
        if isinstance(want, int):
            assert is_integer_object_valid(got, want)
        else:
            assert is_null_object_valid(got)


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


def is_string_object_valid(got: String, want: str):
    assert isinstance(got, String)
    assert got.value == want
    return True


def is_boolean_object_valid(got: Boolean, want: int):
    assert isinstance(got, Boolean)
    assert got.value == want
    return True


def is_null_object_valid(got: Null):
    assert isinstance(got, Null)
    return True
