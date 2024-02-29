from typing import Callable, Union

from . import FuzzType, NamedEntity, MatchList, const


def FunctionStr(
    source: Callable[[str], Union[str, MatchList]],
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    def do_lookup(key: str) -> MatchList:
        response = source(key)
        match_list = MatchList()
        if isinstance(response, str):
            entity = NamedEntity(name=response)
            match_list.set(key=key, entity=entity)
        return match_list

    return FuzzType(
        do_lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
