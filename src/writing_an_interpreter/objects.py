from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from writing_an_interpreter.ast import BlockStatement, Identifier
from writing_an_interpreter.environment import Environment


class ObjectType(str, Enum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    RETURN_VALUE = "RETURN_VALUE"
    ERROR = "ERROR"
    FUNCTION = "FUNCTION"
    STRING = "STRING"
    BUILTIN = "BUILTIN"


class Object:
    type: ObjectType

    @abstractmethod
    def inspect(self) -> str:
        pass


@dataclass
class Integer(Object):
    value: int
    type: ObjectType = ObjectType.INTEGER

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                f"expected value: {value} to have type int. Found: {type(value)}"
            )
        self.value = value

    def inspect(self):
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool
    type: ObjectType = ObjectType.BOOLEAN

    def inspect(self):
        return str(self.value)


@dataclass
class Null(Object):
    type: ObjectType = ObjectType.NULL

    def inspect(self):
        return "null"


@dataclass
class ReturnValue(Object):
    value: Object
    type: ObjectType = ObjectType.RETURN_VALUE

    def inspect(self):
        return self.value.inspect()


@dataclass
class Error(Object):
    message: Object
    type: ObjectType = ObjectType.RETURN_VALUE

    def inspect(self):
        return f"ERROR: {self.message}"


@dataclass
class Function(Object):
    parameters: list[Identifier]
    body: BlockStatement
    environment: Environment
    type: ObjectType = ObjectType.FUNCTION

    def inspect(self):
        args = ", ".join(str(p) for p in self.parameters)
        body = self.body

        return f"fn({args}){{\n{body}\n}}"


@dataclass
class String(Object):
    value: str
    type: ObjectType = ObjectType.STRING

    def inspect(self):
        return self.value


@dataclass
class Builtin(Object):
    function: Callable
    type: ObjectType = ObjectType.BUILTIN

    def inspect(self):
        return "builtin function"
