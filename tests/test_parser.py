from writing_an_interpreter.ast import (BooleanExpression, CallExpression,
                                        Expression, ExpressionStatement,
                                        FunctionLiteral, Identifier,
                                        IfExpression, InfixExpression,
                                        IntegerLiteral, LetStatement,
                                        PrefixExpression, Program,
                                        ReturnStatement, StringLiteral)
from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.parser import ParseError, Parser
from writing_an_interpreter.tokens import Token, TokenType


def test_can_parse_let_statements():
    tests = [
        ("let x = 5;", "x", 5),
        ("let y = true;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ]
    for string, ident, value in tests:
        lexer = Lexer(string)
        parser = Parser(lexer)

        program = parser.parse_program()
        assert not parser.errors

        assert len(program.statements) == 1
        [statement] = program.statements
        assert isinstance(statement, LetStatement)

        assert is_let_statement_valid(statement, ident)
        assert is_literal_expression_valid(statement.value, value)


def is_let_statement_valid(statement: LetStatement, name: str):
    assert statement.token_literal() == "let"
    assert statement.name.value == name
    assert statement.name.token_literal() == name

    return True


def test_can_parse_invalid_let_statements():
    string = """
let x 5;
let = 10;
let 838383;
    """
    lexer = Lexer(string)
    parser = Parser(lexer)

    parser.parse_program()

    assert len(parser.errors) == 4

    first, second, third, fourth = parser.errors

    assert exceptions_equal(
        first, ParseError("expected next token to be =, got INT instead")
    )
    assert exceptions_equal(
        second, ParseError("expected next token to be IDENT, got = instead")
    )
    assert exceptions_equal(third, ParseError("no prefix parse function for = found"))
    assert exceptions_equal(
        fourth, ParseError("expected next token to be IDENT, got INT instead")
    )


def exceptions_equal(first, second):
    same_exception = first.__class__ == second.__class__
    same_content = first.args == second.args
    return same_exception and same_content


def test_can_parse_valid_return_statements():
    string = """
return 5;
return 10;
return 993322;
    """
    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()

    if parser.errors:
        raise ValueError(str(parser.errors))

    assert program is not None
    assert len(program) == 3

    first, second, third = program

    assert isinstance(first, ReturnStatement)
    assert first.token_literal() == "return"
    assert isinstance(second, ReturnStatement)
    assert second.token_literal() == "return"
    assert isinstance(third, ReturnStatement)
    assert third.token_literal() == "return"


def test_can_convert_ast_back_to_string():
    statement = LetStatement(
        token=Token(type=TokenType.LET, literal="let"),
        name=Identifier(
            token=Token(type=TokenType.IDENT, literal="myVar"), value="myVar"
        ),
        value=Identifier(
            token=Token(type=TokenType.IDENT, literal="anotherVar"),
            value="anotherVar",
        ),
    )
    program = Program(statements=[statement])

    assert str(program) == "let myVar = anotherVar;"


def test_can_parse_identifier_expression():
    string = "foobar;"

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    identifier = statement.expression
    assert isinstance(identifier, Identifier)

    assert identifier.value == "foobar"
    assert identifier.token_literal() == "foobar"


def test_can_parse_integer_expression():
    string = "5;"

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    integer_literal = statement.expression
    assert isinstance(integer_literal, IntegerLiteral)

    assert integer_literal.value == 5
    assert integer_literal.token_literal() == "5"


def test_can_parse_prefix_expressions():
    tests = [
        # string, operator, value
        ("!5;", "!", 5),
        ("-15;", "-", 15),
        ("!true;", "!", True),
        ("!false;", "!", False),
    ]

    for string, operator, value in tests:
        lexer = Lexer(string)
        parser = Parser(lexer)

        program = parser.parse_program()
        assert not parser.errors

        assert len(program) == 1

        [statement] = program.statements
        assert isinstance(statement, ExpressionStatement)

        prefix_expression = statement.expression
        assert isinstance(prefix_expression, PrefixExpression)

        assert prefix_expression.operator == operator
        assert is_literal_expression_valid(prefix_expression.right, value)


def test_can_parse_infix_expressions():
    tests = [
        # string, left, operator, right
        ("5 + 5;", 5, "+", 5),
        ("5 - 5;", 5, "-", 5),
        ("5 * 5;", 5, "*", 5),
        ("5 / 5;", 5, "/", 5),
        ("5 > 5;", 5, ">", 5),
        ("5 < 5;", 5, "<", 5),
        ("5 == 5;", 5, "==", 5),
        ("5 != 5;", 5, "!=", 5),
        ("true == true", True, "==", True),
        ("true != false", True, "!=", False),
        ("false == false", False, "==", False),
    ]

    for string, left, operator, right in tests:
        lexer = Lexer(string)
        parser = Parser(lexer)

        program = parser.parse_program()
        assert not parser.errors

        assert len(program) == 1

        [statement] = program.statements
        assert isinstance(statement, ExpressionStatement)

        infix_expression = statement.expression
        assert isinstance(infix_expression, InfixExpression)

        assert is_literal_expression_valid(infix_expression.left, left)
        assert infix_expression.operator == operator
        assert is_literal_expression_valid(infix_expression.right, right)


def test_operator_precedence_is_correct():
    tests = [
        # string, parsed
        ("-a * b", "((-a) * b)"),
        ("!-a", "(!(-a))"),
        ("a + b + c", "((a + b) + c)"),
        ("a + b - c", "((a + b) - c)"),
        ("a * b * c", "((a * b) * c)"),
        ("a * b / c", "((a * b) / c)"),
        ("a + b / c", "(a + (b / c))"),
        ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
        ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
        ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
        ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
        ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
        ("true", "true"),
        ("false", "false"),
        ("3 > 5 == false", "((3 > 5) == false)"),
        ("3 < 5 == true", "((3 < 5) == true)"),
        ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
        ("(5 + 5) * 2", "((5 + 5) * 2)"),
        ("2 / (5 + 5)", "(2 / (5 + 5))"),
        ("-(5 + 5)", "(-(5 + 5))"),
        ("!(true == true)", "(!(true == true))"),
        ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
        (
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ),
        ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"),
    ]

    for string, expected in tests:
        lexer = Lexer(string)
        parser = Parser(lexer)

        program = parser.parse_program()
        assert not parser.errors

        assert str(program) == expected


def test_can_parse_if_statement():
    string = "if (x < y) { x }"

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    if_expression = statement.expression
    assert isinstance(if_expression, IfExpression)

    assert is_infix_expression_valid(if_expression.condition, "x", "<", "y")

    assert len(if_expression.consequence.statements) == 1
    [consequence_expression] = if_expression.consequence.statements
    assert isinstance(consequence_expression, ExpressionStatement)
    assert is_identifier_valid(consequence_expression.expression, "x")

    assert if_expression.alternative is None


def test_can_parse_if_else_statement():
    string = "if (x < y) { x } else { y }"

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    if_expression = statement.expression
    assert isinstance(if_expression, IfExpression)

    assert is_infix_expression_valid(if_expression.condition, "x", "<", "y")

    assert len(if_expression.consequence.statements) == 1
    [consequence] = if_expression.consequence.statements
    assert isinstance(consequence, ExpressionStatement)
    assert is_identifier_valid(consequence.expression, "x")

    assert if_expression.alternative is not None
    assert len(if_expression.alternative.statements) == 1
    [alternative] = if_expression.alternative.statements
    assert isinstance(alternative, ExpressionStatement)
    assert is_identifier_valid(alternative.expression, "y")


def test_can_parse_function_literal():
    string = "fn(x, y) { x + y; }"

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    function = statement.expression
    assert isinstance(function, FunctionLiteral)

    assert len(function.parameters) == 2
    param_1, param_2 = function.parameters
    assert is_literal_expression_valid(param_1, "x")
    assert is_literal_expression_valid(param_2, "y")

    assert len(function.body.statements) == 1
    [body_statement] = function.body.statements
    assert is_infix_expression_valid(body_statement.expression, "x", "+", "y")


def test_can_parse_function_params():
    tests = [
        ("fn() {};", []),
        ("fn(x) {};", ["x"]),
        ("fn(x, y, z) {};", ["x", "y", "z"]),
    ]

    for string, want in tests:
        lexer = Lexer(string)
        parser = Parser(lexer)

        program = parser.parse_program()
        assert not parser.errors

        assert len(program) == 1

        [statement] = program.statements
        assert isinstance(statement, ExpressionStatement)

        function = statement.expression
        assert isinstance(function, FunctionLiteral)

        assert len(function.parameters) == len(want)

        for param, expected in zip(function.parameters, want):
            is_literal_expression_valid(param, expected)


def test_can_parse_call_expression():
    string = "add(1, 2 * 3, 4 + 5);"

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    call_expression = statement.expression
    assert isinstance(call_expression, CallExpression)

    assert is_identifier_valid(call_expression.function, "add")

    assert len(call_expression.arguments) == 3
    arg_1, arg_2, arg_3 = call_expression.arguments

    assert is_literal_expression_valid(arg_1, 1)
    assert is_infix_expression_valid(arg_2, 2, "*", 3)
    assert is_infix_expression_valid(arg_3, 4, "+", 5)


def test_can_parse_string_literal():
    string = '"hello world";'

    lexer = Lexer(string)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors

    assert len(program) == 1

    [statement] = program.statements
    assert isinstance(statement, ExpressionStatement)

    string_literal = statement.expression
    assert isinstance(string_literal, StringLiteral)

    assert string_literal.value == "hello world"


# -------helper functions-------
def is_identifier_valid(expression: Identifier, value: str):
    assert isinstance(expression, Identifier)
    assert expression.value == value
    assert expression.token_literal() == value
    return True


def is_literal_expression_valid(expression: Expression, expected):
    match expected:
        case str():
            return is_identifier_valid(expression, expected)
        case bool():
            return is_boolean_valid(expression, expected)
        case int():
            return is_integer_literal_valid(expression, int(expected))
        case _:
            return False


def is_integer_literal_valid(expression: Expression, value: int):
    assert isinstance(expression, IntegerLiteral), expression
    assert expression.value == value
    assert expression.token_literal() == str(value)
    return True


def is_infix_expression_valid(expression: InfixExpression, left, operator, right):
    assert isinstance(expression, InfixExpression)
    assert is_literal_expression_valid(expression.left, left)
    assert expression.operator == operator
    assert is_literal_expression_valid(expression.right, right)

    return True


def is_boolean_valid(expression: BooleanExpression, value):
    assert isinstance(expression, BooleanExpression)
    assert expression.value == value
    assert expression.token_literal() == str(value).lower()

    return True
