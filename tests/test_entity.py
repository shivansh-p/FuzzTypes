from fuzztype import Entity, AliasStr


def test_entity_conv():
    def c(item):
        return Entity.convert(item).model_dump(exclude_defaults=True)

    assert c("A") == dict(name="A")
    assert c(("A", "B")) == dict(name="A", aliases=["B"])
    assert c(("A", ["B"])) == dict(name="A", aliases=["B"])
    assert c(("A", ["B", "C"])) == dict(name="A", aliases=["B", "C"])


def test_meta():
    entity = Entity(name="a", meta=dict(b=1, c=None), priority=10)
    assert entity.name == "a"
    assert entity.b == 1
    assert entity.c is None
    assert entity.priority == 10
    assert entity.model_dump() == {
        "name": "a",
        "label": None,
        "aliases": [],
        "meta": {"b": 1, "c": None},
        "priority": 10,
    }


def test_meta_edge_cases():
    entity = Entity(name="a")

    try:
        assert entity.unknown
        assert False, "Did not throw AttributeError exception."

    except AttributeError:
        pass

    entity.unknown = 123
    assert entity.unknown == 123

    assert entity.label is None
    entity.label = "LABEL"
    assert entity.label == "LABEL"


def test_csv_load(EmojiSource):
    Emoji = AliasStr(EmojiSource)
    assert Emoji["happy"].name == "happy"
    assert Emoji["🎉"].name == "celebrate"


def test_jsonl_load(MixedSource):
    assert MixedSource[0].name == "Dog"
    assert MixedSource[:2][-1].name == "Cat"

    AnimalStr = AliasStr(MixedSource["animal"])
    assert AnimalStr["dog"] == MixedSource[0]
    assert AnimalStr["Bird of prey"].name == "Eagle"

    FruitStr = AliasStr(
        MixedSource["fruit"],
        case_sensitive=True,
        notfound_mode="none",
    )
    assert FruitStr["apple"] is None
    assert FruitStr["Pome"].name == "Apple"


def test_tsv_load(MythSource):
    Myth = AliasStr(MythSource)
    assert Myth["Pallas"].name == "Athena"
    assert Myth["Jupiter"].name == "Zeus"
