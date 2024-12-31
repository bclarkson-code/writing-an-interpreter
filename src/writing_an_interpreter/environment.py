from collections.abc import MutableMapping
from dataclasses import dataclass

from writing_an_interpreter.objects import Object


@dataclass
class Environment(MutableMapping):
    store: dict[str, Object]

    def __getitem__(self, *args, **kwargs):
        return self.store.__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.store.__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.store.__delitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.store.__iter__(*args, **kwargs)

    def __lent__(self):
        return self.store.__len__()
