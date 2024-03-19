import json
from enum import Enum
from typing import Optional, List, Iterable, Type

from pydantic import TypeAdapter

from fuzztypes import EntitySource, NamedEntity, OnDisk, flags, utils


class LanguageScope(Enum):
    INDIVIDUAL = "I"
    MACROLANGUAGE = "M"
    SPECIAL = "S"


class LanguageType(Enum):
    ANCIENT = "A"
    CONSTRUCTED = "C"
    EXTINCT = "E"
    HISTORICAL = "H"
    LIVING = "L"
    SPECIAL = "S"


class LanguageNamedEntity(NamedEntity):
    """Resolves to language full name."""

    alpha_2: Optional[str] = None
    alpha_3: str
    scope: Optional[LanguageScope] = None
    type: Optional[LanguageType] = None
    common_name: Optional[str] = None
    inverted_name: Optional[str] = None
    bibliographic: Optional[str] = None

    @property
    def code(self):
        return self.alpha_2 or self.alpha_3


class LanguageModelNamedEntity(LanguageNamedEntity):
    """Resolves to self as a full child object."""

    def resolve(self):
        return self


class LanguageCodeNameEntity(LanguageNamedEntity):
    """Resolves to code name."""

    def resolve(self):
        return self.code


remote = (
    "https://salsa.debian.org/iso-codes-team/iso-codes/-/raw/main/data"
    "/iso_639-3.json"
)
local = utils.get_file(remote)


def load_languages(cls: Type[LanguageNamedEntity] = LanguageNamedEntity):
    def do_load() -> Iterable[NamedEntity]:
        data = json.load(open(local))["639-3"]
        alias_fields = {
            "alpha_2",
            "alpha_3",
            "common_name",
            "inverted_name",
            "bibliographic",
        }
        entities = []
        for item in data:
            item["value"] = item.pop("name")
            aliases = [v for k, v in item.items() if k in alias_fields]
            item["aliases"] = aliases
            entities.append(item)
        return TypeAdapter(List[cls]).validate_python(data)

    return do_load


LanguageName = OnDisk(
    "Language",
    EntitySource(load_languages(LanguageNamedEntity)),
    entity_type=LanguageNamedEntity,
    search_flag=flags.AliasSearch,
    tiebreaker_mode="lesser",
)

LanguageCode = OnDisk(
    "Language",
    EntitySource(load_languages(LanguageCodeNameEntity)),
    entity_type=LanguageCodeNameEntity,
    search_flag=flags.AliasSearch,
    tiebreaker_mode="lesser",
)

Language = OnDisk(
    "Language",
    EntitySource(load_languages(LanguageModelNamedEntity)),
    entity_type=LanguageModelNamedEntity,
    input_type=LanguageModelNamedEntity,
    search_flag=flags.AliasSearch,
    tiebreaker_mode="lesser",
)
