from writing_an_interpreter.ast import (
    BlockStatement,
    BooleanExpression,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    Identifier,
    IfExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    Node,
    PrefixExpression,
    Program,
    ReturnStatement,
    StringLiteral,
)
from writing_an_interpreter.environment import Environment
from writing_an_interpreter.objects import (
    Boolean,
    Builtin,
    Error,
    Function,
    Integer,
    Null,
    Object,
    ObjectType,
    ReturnValue,
    String,
)

TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()


def monkey_eval(node: Node, environment: Environment) -> Object:
    match node:
        case Program():
            return eval_program(node, environment)
        case BlockStatement():
            return eval_block_statement(node, environment)
        case ExpressionStatement():
            return monkey_eval(node.expression, environment)
        case IntegerLiteral():
            return Integer(value=node.value)
        case BooleanExpression():
            return native_bool_to_bool_object(node.value)
        case PrefixExpression():
            right = monkey_eval(node.right, environment)
            if is_error(right):
                return right

            return eval_prefix_expression(node.operator, right)
        case InfixExpression():
            left = monkey_eval(node.left, environment)
            if is_error(left):
                return left

            right = monkey_eval(node.right, environment)
            if is_error(right):
                return right

            return eval_infix_expression(node.operator, left, right)
        case IfExpression():
            return eval_if_expression(node, environment)
        case ReturnStatement():
            val = monkey_eval(node.return_value, environment)
            return val if is_error(val) else ReturnValue(val)

        case LetStatement():
            val = monkey_eval(node.value, environment)
            if is_error(val):
                return val
            environment[node.name.value] = val
        case Identifier():
            return eval_identifier(node, environment)
        case FunctionLiteral():
            params = node.parameters
            body = node.body
            return Function(parameters=params, body=body, environment=environment)
        case CallExpression():
            function = monkey_eval(node.function, environment)
            if is_error(function):
                return function

            args = eval_expressions(node.arguments, environment)
            if len(args) == 1 and is_error(args[0]):
                return args[0]
            return apply_function(function, args)

        case StringLiteral():
            return String(value=node.value)

        case _:
            return None


def eval_program(program: Program, environment: Environment):
    result = None

    for statement in program.statements:
        result = monkey_eval(statement, environment)

        match result:
            case ReturnValue():
                return result.value
            case Error():
                return result

    return result


def eval_block_statement(block: BlockStatement, environment: Environment):
    result = None

    for statement in block.statements:
        result = monkey_eval(statement, environment)

        if result is not None and result.type in [
            ObjectType.RETURN_VALUE,
            ObjectType.ERROR,
        ]:
            return result

    return result


def native_bool_to_bool_object(inputs: bool) -> Boolean:
    if inputs:
        return TRUE
    return FALSE


def eval_prefix_expression(operator: str, right: Object) -> Object:
    match operator:
        case "!":
            return eval_bang_operator_expression(right)
        case "-":
            return eval_minus_prefix_operator_expression(right)
        case _:
            return new_error(
                "unknown operator: {operator}{type}", operator=operator, type=right.type
            )


def eval_bang_operator_expression(right: Object) -> Object:
    if isinstance(right, Null):
        return TRUE
    elif isinstance(right, Boolean):
        if right.value:
            return FALSE
        return TRUE
    return FALSE


def eval_minus_prefix_operator_expression(right: Object) -> Object:
    if not right.type == ObjectType.INTEGER:
        return new_error("unknown operator: -{type}", type=right.type)

    return Integer(value=-right.value)


def eval_infix_expression(operator: str, left: Object, right: Object) -> Object:
    if left.type != right.type:
        return new_error(
            "type mismatch: {left_type} {operator} {right_type}",
            left_type=left.type,
            operator=operator,
            right_type=right.type,
        )
    elif left.type == ObjectType.INTEGER and right.type == ObjectType.INTEGER:
        return eval_integer_infix_expression(operator, left, right)
    elif left.type == ObjectType.STRING and right.type == ObjectType.STRING:
        return eval_string_infix_expression(operator, left, right)
    elif operator == "==":
        return native_bool_to_bool_object(left == right)
    elif operator == "!=":
        return native_bool_to_bool_object(left != right)

    return new_error(
        "unknown operator: {left_type} {operator} {right_type}",
        left_type=left.type,
        operator=operator,
        right_type=right.type,
    )


def eval_integer_infix_expression(
    operator: str, left: Integer, right: Integer
) -> Integer:
    match operator:
        case "+":
            return Integer(left.value + right.value)
        case "-":
            return Integer(left.value - right.value)
        case "*":
            return Integer(left.value * right.value)
        case "/":
            return Integer(left.value // right.value)
        case "<":
            return native_bool_to_bool_object(left.value < right.value)
        case ">":
            return native_bool_to_bool_object(left.value > right.value)
        case "==":
            return native_bool_to_bool_object(left.value == right.value)
        case "!=":
            return native_bool_to_bool_object(left.value != right.value)
        case _:
            return new_error(
                "unknown operator:{left_type} {operator} {right_type}",
                left_type=left.type,
                operator=operator,
                right_type=right.type,
            )


def eval_string_infix_expression(operator: str, left: String, right: String) -> String:
    if operator != "+":
        return new_error(
            "unknown operator: {left_type} {operator} {right_type}",
            left_type=left.type,
            operator=operator,
            right_type=right.type,
        )
    return String(left.value + right.value)


def eval_if_expression(expression: IfExpression, environment: Environment) -> Object:
    condition = monkey_eval(expression.condition, environment)
    if is_error(condition):
        return condition

    if is_truthy(condition):
        return monkey_eval(expression.consequence, environment)
    elif expression.alternative is not None:
        return monkey_eval(expression.alternative, environment)
    return NULL


def eval_identifier(identifier: Identifier, environment: Environment) -> Object:
    if identifier.value in environment:
        return environment[identifier.value]
    if identifier.value in builtins:
        return builtins[identifier.value]
    return new_error(f"identifier not found: {identifier.value}")


def eval_expressions(
    expressions: list[Expression], environment: Environment
) -> list[Object]:
    result = []
    for expression in expressions:
        evaluated = monkey_eval(expression, environment)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def apply_function(function: Function, args: list[Object]):
    match function:
        case Function():
            extended_environment = extend_function_environment(function, args)
            evaluated = monkey_eval(function.body, extended_environment)
            return unwrap_return_value(evaluated)
        case Builtin():
            return function.function(*args)
        case _:
            return new_error("not a function: {type}", type=function.type)


def extend_function_environment(function: Function, args: list[Object]):
    environment = Environment(outer=function.environment)

    for idx, param in enumerate(function.parameters):
        environment[param.value] = args[idx]

    return environment


def unwrap_return_value(obj: Object):
    if isinstance(obj, ReturnValue):
        return obj.value
    return obj


def is_truthy(obj: Object) -> bool:
    if isinstance(obj, Null):
        return False
    elif isinstance(obj, Boolean):
        return obj.value
    return True


def new_error(format_string: str, **kwargs) -> Error:
    return Error(message=format_string.format(**kwargs))


def is_error(obj: Object) -> bool:
    if obj is None:
        return False

    return obj.type == ObjectType.ERROR


# ------builtins--------
def run_len(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )
    [arg] = args
    match arg:
        case String():
            return Integer(value=len(arg.value))
        case _:
            return new_error("argument to 'len' not supported, got {arg}", arg=arg.type)


builtins = {"len": Builtin(run_len)}
