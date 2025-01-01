from writing_an_interpreter.lexer import Lexer
from writing_an_interpreter.tokens import Token, TokenType


def test_can_lex_single_delimiters_and_operators():
    input = "=+(){},;"
    want = [
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.PLUS, "+"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.EOF, ""),
    ]

    lexer = Lexer(input)

    for token in want:
        assert lexer.next_token() == token


def test_can_create_variables():
    string = """let five = 5;
let ten = 10;"""


def test_can_create_function():
    string = """let add = fn(x, y) { x + y; };"""


def test_can_call_function():
    string = """let result = add(five, ten);"""


def test_can_lex_simple_snippet():
    string = """let five = 5; 
let ten = 10;

let add = fn(x, y) {
    x + y;
};

let result = add(five, ten);"""
    want = [
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "five"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.INT, "5"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "ten"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.INT, "10"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "add"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.FUNCTION, "fn"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.IDENT, "x"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENT, "y"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.IDENT, "x"),
        Token(TokenType.PLUS, "+"),
        Token(TokenType.IDENT, "y"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "result"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.IDENT, "add"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.IDENT, "five"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENT, "ten"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.EOF, ""),
    ]

    lexer = Lexer(string)

    for token in want:
        assert lexer.next_token() == token


def test_can_lex_with_extended_token_set():
    string = """let five = 5;
let ten = 10;

let add = fn(x, y) {
    x + y;
};

let result = add(five, ten);
!-/*5;
5 < 10 > 5;

if (5 < 10) {
    return true;
} else {
    return false;
}

10 == 10;
10 != 9;
"foobar"
"foo bar"
[1, 2];
{"foo": "bar"}
"""
    want = [
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "five"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.INT, "5"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "ten"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.INT, "10"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "add"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.FUNCTION, "fn"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.IDENT, "x"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENT, "y"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.IDENT, "x"),
        Token(TokenType.PLUS, "+"),
        Token(TokenType.IDENT, "y"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LET, "let"),
        Token(TokenType.IDENT, "result"),
        Token(TokenType.ASSIGN, "="),
        Token(TokenType.IDENT, "add"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.IDENT, "five"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.IDENT, "ten"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.BANG, "!"),
        Token(TokenType.MINUS, "-"),
        Token(TokenType.SLASH, "/"),
        Token(TokenType.ASTERISK, "*"),
        Token(TokenType.INT, "5"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.INT, "5"),
        Token(TokenType.LT, "<"),
        Token(TokenType.INT, "10"),
        Token(TokenType.GT, ">"),
        Token(TokenType.INT, "5"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.IF, "if"),
        Token(TokenType.LPAREN, "("),
        Token(TokenType.INT, "5"),
        Token(TokenType.LT, "<"),
        Token(TokenType.INT, "10"),
        Token(TokenType.RPAREN, ")"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RETURN, "return"),
        Token(TokenType.TRUE, "true"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.ELSE, "else"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.RETURN, "return"),
        Token(TokenType.FALSE, "false"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.INT, "10"),
        Token(TokenType.EQ, "=="),
        Token(TokenType.INT, "10"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.INT, "10"),
        Token(TokenType.NOT_EQ, "!="),
        Token(TokenType.INT, "9"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.STRING, "foobar"),
        Token(TokenType.STRING, "foo bar"),
        Token(TokenType.LBRACKET, "["),
        Token(TokenType.INT, "1"),
        Token(TokenType.COMMA, ","),
        Token(TokenType.INT, "2"),
        Token(TokenType.RBRACKET, "]"),
        Token(TokenType.SEMICOLON, ";"),
        Token(TokenType.LBRACE, "{"),
        Token(TokenType.STRING, "foo"),
        Token(TokenType.COLON, ":"),
        Token(TokenType.STRING, "bar"),
        Token(TokenType.RBRACE, "}"),
        Token(TokenType.EOF, ""),
    ]

    lexer = Lexer(string)

    for token in want:
        assert lexer.next_token() == token
