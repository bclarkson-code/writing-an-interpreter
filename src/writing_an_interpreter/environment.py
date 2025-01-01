from collections.abc import MutableMapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from writing_an_interpreter.objects import Object


class Environment(MutableMapping):
    store: dict[str, "Object"]
    outer: "Environment | None"

    def __init__(
        self,
        store: dict[str, "Object"] | None = None,
        outer: "Environment | None" = None,
    ):
        if store is None:
            self.store = {}
        else:
            self.store = store
        self.outer = outer

    def __getitem__(self, key: str):
        if key in self.store:
            return self.store[key]

        if self.outer is None:
            raise KeyError(key)

        return self.outer[key]

    def __setitem__(self, key: str, val: "Object"):
        self.store[key] = val

    def __delitem__(self, key: str):
        return self.store.__delitem__(key)

    def __iter__(self):
        return self.store.__iter__()

    def __len__(self):
        return self.store.__len__()
