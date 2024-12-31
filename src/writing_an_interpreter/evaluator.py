from writing_an_interpreter.ast import (BlockStatement, BooleanExpression,
                                        ExpressionStatement, IfExpression,
                                        InfixExpression, IntegerLiteral,
                                        LetStatement, Node, PrefixExpression,
                                        Program, ReturnStatement, Statement)
from writing_an_interpreter.objects import (Boolean, Error, Integer, Null,
                                            Object, ObjectType, ReturnValue)

TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()


def monkey_eval(node: Node) -> Object:
    match node:
        case Program():
            return eval_program(node)
        case BlockStatement():
            return eval_block_statement(node)
        case ExpressionStatement():
            return monkey_eval(node.expression)
        case IntegerLiteral():
            return Integer(value=node.value)
        case BooleanExpression():
            return native_bool_to_bool_object(node.value)
        case PrefixExpression():
            right = monkey_eval(node.right)
            if is_error(right):
                return right

            return eval_prefix_expression(node.operator, right)
        case InfixExpression():
            left = monkey_eval(node.left)
            if is_error(left):
                return left

            right = monkey_eval(node.right)
            if is_error(right):
                return right

            return eval_infix_expression(node.operator, left, right)
        case IfExpression():
            return eval_if_expression(node)
        case ReturnStatement():
            val = monkey_eval(node.return_value)
            return val if is_error(val) else ReturnValue(val)

        case LetStatement():
            val = monkey_eval(node.value)
            return val if is_error(val) else ?

        case _:
            return None


def eval_program(program: Program):
    result = None

    for statement in program.statements:
        result = monkey_eval(statement)

        match result:
            case ReturnValue():
                return result.value
            case Error():
                return result

    return result


def eval_block_statement(block: BlockStatement):
    result = None

    for statement in block.statements:
        result = monkey_eval(statement)

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


def eval_if_expression(expression: IfExpression) -> Object:
    condition = monkey_eval(expression.condition)
    if is_error(condition):
        return condition

    if is_truthy(condition):
        return monkey_eval(expression.consequence)
    elif expression.alternative is not None:
        return monkey_eval(expression.alternative)
    return NULL


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
