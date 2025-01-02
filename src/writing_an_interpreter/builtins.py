from copy import deepcopy
from pathlib import Path

from writing_an_interpreter.evaluator import new_error
from writing_an_interpreter.objects import (
    Array,
    Boolean,
    Builtin,
    Hash,
    Integer,
    Null,
    ObjectType,
    String,
    is_hashable,
)

TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()


def run_len(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )
    [arg] = args
    match arg:
        case String():
            return Integer(value=len(arg.value))
        case Array():
            return Integer(value=len(arg.elements))
        case Hash():
            return Integer(value=len(arg.pairs))
        case _:
            return new_error("argument to 'len' not supported, got {arg}", arg=arg.type)


def run_first(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [arg] = args

    match arg.type:
        case ObjectType.ARRAY:
            if len(arg.elements) > 0:
                return arg.elements[0]
            return NULL
        case ObjectType.STRING:
            if len(arg.value) > 0:
                return String(arg.value[0])
            return NULL
        case _:
            return new_error(
                "argument to 'first' must be ARRAY or STRING, got {arg}", arg=arg.type
            )


def run_last(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [arg] = args
    match arg.type:
        case ObjectType.ARRAY:
            if len(arg.elements) > 0:
                return arg.elements[-1]
            return NULL
        case ObjectType.STRING:
            if len(arg.value) > 0:
                return String(arg.value[-1])
            return NULL
        case _:
            return new_error(
                "argument to 'last' must be ARRAY or STRING, got {arg}", arg=arg.type
            )


def run_rest(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [arg] = args
    match arg.type:
        case ObjectType.ARRAY:
            if len(arg.elements) > 1:
                return Array(arg.elements[1:])
            return NULL
        case ObjectType.STRING:
            if len(arg.value) > 1:
                return String(arg.value[1:])
            return NULL
        case _:
            return new_error(
                "argument to 'rest' must be ARRAY or STRING, got {arg}", arg=arg.type
            )


def run_push(*args):
    if len(args) != 2:
        return new_error(
            "wrong number of arguments. got={argslen}, want=2", argslen=len(args)
        )

    [arr, val] = args
    if arr.type != ObjectType.ARRAY:
        return new_error("argument to 'push' must be ARRAY, got {arg}", arg=arr.type)

    elements = deepcopy(arr.elements)
    elements.append(val)
    return Array(elements=elements)


def run_sort(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [arr] = args
    if arr.type != ObjectType.ARRAY:
        return new_error("argument to 'sort' must be ARRAY, got {arg}", arg=arr.type)

    if len(arr.elements) == 0:
        return Array([])

    types = {val.type for val in arr.elements}

    if len(types) > 1:
        types = [val.type for val in arr.elements]
        types = ", ".join(types)
        types = f"[{types}]"
        return new_error(
            "argument to 'sort' must be ARRAY with a single type, got {types}",
            types=types,
        )
    type_ = types.pop()
    match type_:
        case ObjectType.INTEGER:
            elements = deepcopy(arr.elements)
            values = [e.value for e in elements]
            values = sorted(values)
            elements = [Integer(val) for val in values]
            return Array(elements=elements)
        case ObjectType.STRING:
            elements = deepcopy(arr.elements)
            values = [e.value for e in elements]
            values = sorted(values)
            elements = [String(val) for val in values]
            return Array(elements=elements)
        case ObjectType.BOOLEAN:
            elements = deepcopy(arr.elements)
            values = [e.value for e in elements]
            values = sorted(values)
            elements = [Boolean(val) for val in values]
            return Array(elements=elements)
        case _:
            return new_error(
                "sorting ARRAYs containing {type_} is not supported", type_=type_
            )


def run_puts(*args):
    for arg in args:
        print(arg.inspect())
    return NULL


def run_contains(*args):
    if len(args) != 2:
        return new_error(
            "wrong number of arguments. got={argslen}, want=2", argslen=len(args)
        )

    [hash_, val] = args
    if hash_.type != ObjectType.HASH:
        return new_error(
            "argument to 'contains' must be HASH, got {arg}", arg=hash_.type
        )

    if not is_hashable(val):
        return new_error("unusable as hash key: {index_type}", index_type=val.type)

    if val.hash() in hash_.pairs:
        return Boolean(True)
    else:
        return Boolean(False)


def run_keys(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [hash_] = args
    if hash_.type != ObjectType.HASH:
        return new_error("argument to 'keys' must be HASH, got {arg}", arg=hash_.type)

    elements = [pair.key for pair in hash_.pairs.values()]
    return Array(elements=elements)


def run_values(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [hash_] = args
    if hash_.type != ObjectType.HASH:
        return new_error("argument to 'values' must be HASH, got {arg}", arg=hash_.type)

    elements = [pair.value for pair in hash_.pairs.values()]
    return Array(elements=elements)


def run_read_file(*args):
    if len(args) != 1:
        return new_error(
            "wrong number of arguments. got={argslen}, want=1", argslen=len(args)
        )

    [path] = args
    if path.type != ObjectType.STRING:
        return new_error(
            "argument to 'read_file' must be STRING, got {arg}", arg=path.type
        )

    try:
        content = Path(path.value).read_text()
    except FileNotFoundError:
        return new_error("file {path} does not exist", path=path.value)
    except PermissionError:
        return new_error("permission denied to read file {path}", path=path.value)
    except UnicodeDecodeError:
        return new_error("file contains invalid characters for the specified encoding")
    except OSError as e:
        return new_error(f"OS error occurred: {e}")

    return String(content)


builtins = {
    "len": Builtin(run_len),
    "first": Builtin(run_first),
    "last": Builtin(run_last),
    "rest": Builtin(run_rest),
    "push": Builtin(run_push),
    "sort": Builtin(run_sort),
    "puts": Builtin(run_puts),
    "contains": Builtin(run_contains),
    "keys": Builtin(run_keys),
    "values": Builtin(run_values),
    "read_file": Builtin(run_read_file),
}
