from typing import Iterable

from pydantic_core import PydanticCustomError

from . import Entity, FuzzType


def NameStr(source: Iterable, case_sensitive: bool = False):
    return FuzzType(lookup_function=NameLookup(source, case_sensitive))


def CasedNameStr(source: Iterable):
    return FuzzType(lookup_function=NameLookup(source, True))


class NameLookup:
    def __init__(self, source: Iterable, case_sensitive: bool):
        self.prepped: bool = False
        self.source: Iterable = source
        self.case_sensitive: bool = case_sensitive
        self.name_exact: dict[str, str] = {}
        self.name_lower: dict[str, str] = {}

    def __call__(self, key: str) -> str:
        if not self.prepped:
            self._prep_source()

        name = self.name_exact.get(key)
        if not self.case_sensitive and name is None:
            name = self.name_lower.get(key.lower())

        if name is None:
            msg = "Key ({key}) not found."
            raise PydanticCustomError("name_str_not_found", msg, dict(key=key))

        return name

    # private functions

    def _prep_source(self):
        if self.prepped:
            return

        self.prepped = True
        for item in self.source:
            entity = Entity.convert(item)
            self.name_exact[entity.name] = entity.name
            self.name_lower[entity.name.lower()] = entity.name

