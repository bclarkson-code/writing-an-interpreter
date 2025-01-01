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
    ARRAY = "ARRAY"
    HASH = "HASH"


class Object:
    type: ObjectType

    @abstractmethod
    def inspect(self) -> str:
        pass


@dataclass(frozen=True)
class Integer(Object):
    value: int
    type: ObjectType = ObjectType.INTEGER

    def hash(self):
        return HashKey(type=self.type, value=self.value)

    def inspect(self):
        return str(self.value)


@dataclass(frozen=True)
class Boolean(Object):
    value: bool
    type: ObjectType = ObjectType.BOOLEAN

    def inspect(self):
        return str(self.value)

    def hash(self):
        return HashKey(type=self.type, value=1 if self.value else 0)


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


@dataclass(frozen=True)
class String(Object):
    value: str
    type: ObjectType = ObjectType.STRING

    def inspect(self):
        return self.value

    def hash(self):
        return HashKey(value=hash(self.value), type=ObjectType.STRING)


@dataclass
class Builtin(Object):
    function: Callable
    type: ObjectType = ObjectType.BUILTIN

    def inspect(self):
        return "builtin function"


@dataclass
class Array(Object):
    elements: list[Object]
    type: ObjectType = ObjectType.ARRAY

    def inspect(self):
        elements = ", ".join(e.inspect() for e in self.elements)
        return f"[{elements}]"


@dataclass(frozen=True)
class HashKey:
    value: int
    type: ObjectType = ObjectType.ARRAY


@dataclass
class HashPair:
    key: Object
    value: Object


@dataclass
class Hash(Object):
    pairs: dict[HashKey, HashPair]
    type: ObjectType = ObjectType.HASH

    def inspect(self):
        pairs = []
        for pair in self.pairs.values():
            key = pair.key.inspect()
            val = pair.value.inspect()
            pairs.append(f"{key}: {val}")
        pairs = ", ".join(pairs)
        return f"{{{pairs}}}"


def is_hashable(obj: Object):
    try:
        hash(obj)
        return True
    except TypeError:
        return False
