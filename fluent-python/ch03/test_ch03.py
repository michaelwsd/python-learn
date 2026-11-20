import pytest
from exercises_ch03 import (
    StrKeyDict,
    compare,
    dedupe,
    describe,
    group_by_symbol,
    invert,
    is_hashable,
    merge_config,
    missing_fields,
    read_only,
    top_words,
)


# Exercise 1 ---------------------------------------------------------------
def test_invert():
    assert invert({"AAPL": "Apple", "MSFT": "Microsoft"}) == {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
    }
    assert invert({}) == {}


def test_merge_config_new_dict_overrides_win():
    defaults = {"timeout": 30, "retries": 3}
    overrides = {"timeout": 5, "debug": True}
    assert merge_config(defaults, overrides) == {
        "timeout": 5,
        "retries": 3,
        "debug": True,
    }
    assert defaults == {"timeout": 30, "retries": 3}
    assert overrides == {"timeout": 5, "debug": True}


# Exercise 2 ---------------------------------------------------------------
def test_describe_trade():
    assert describe({"type": "trade", "symbol": "AAPL", "qty": 100}) == "trade 100 AAPL"
    assert (
        describe({"type": "trade", "symbol": "AAPL", "qty": 100, "venue": "X"})
        == "trade 100 AAPL"
    )
    assert (
        describe({"type": "trade", "symbol": "AAPL", "qty": "100"}) == "unknown event"
    )


def test_describe_error_counts_extra_fields():
    assert describe({"type": "error", "code": 503}) == "error 503 (0 extra fields)"
    event = {"type": "error", "code": 503, "msg": "busy", "retry": 2}
    assert describe(event) == "error 503 (2 extra fields)"


def test_describe_other():
    assert describe({"type": "heartbeat"}) == "heartbeat"
    assert describe({"type": "quote"}) == "unknown event"
    assert describe(["type", "trade"]) == "unknown event"


# Exercise 3 ---------------------------------------------------------------
def test_group_by_symbol():
    trades = [("AAPL", 100), ("MSFT", 25), ("AAPL", 50)]
    result = group_by_symbol(trades)
    assert result == {"AAPL": [100, 50], "MSFT": [25]}
    assert type(result) is dict
    assert group_by_symbol([]) == {}


# Exercise 4 ---------------------------------------------------------------
def test_top_words():
    assert top_words("the cat and The dog and THE end", 2) == [("the", 3), ("and", 2)]
    assert top_words("a b a", 1) == [("a", 2)]


# Exercise 5 ---------------------------------------------------------------
def test_strkeydict_stores_str_keys():
    d = StrKeyDict([(2, "two")])
    d[5] = "five"
    d.update({6: "six"})
    assert d.data == {"2": "two", "5": "five", "6": "six"}


def test_strkeydict_lookup():
    d = StrKeyDict([("2", "two"), ("4", "four")])
    assert d[2] == d["2"] == "two"
    assert 4 in d and "4" in d and 1 not in d
    assert d.get(4) == "four"
    assert d.get(1, "N/A") == "N/A"
    with pytest.raises(KeyError):
        d[1]


# Exercise 6 ---------------------------------------------------------------
def test_is_hashable():
    assert is_hashable((1, 2)) and is_hashable("x") and is_hashable(frozenset([1]))
    assert not is_hashable((1, [2]))
    assert not is_hashable([])
    assert not is_hashable({})


def test_dedupe_keeps_first_seen_order():
    assert dedupe(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]
    assert dedupe([]) == []


# Exercise 7 ---------------------------------------------------------------
def test_compare():
    a = {"AAPL", "MSFT", "NVDA"}
    b = {"MSFT", "TSLA", "NVDA"}
    assert compare(a, b) == {
        "both": {"MSFT", "NVDA"},
        "only_a": {"AAPL"},
        "only_b": {"TSLA"},
        "either": {"AAPL", "MSFT", "NVDA", "TSLA"},
    }


def test_missing_fields():
    required = {"symbol", "qty", "price"}
    assert missing_fields({"symbol": "AAPL", "qty": 1}, required) == {"price"}
    assert (
        missing_fields({"symbol": "A", "qty": 1, "price": 2.0, "x": 0}, required)
        == set()
    )


# Exercise 8 ---------------------------------------------------------------
def test_read_only():
    d = {"a": 1}
    view = read_only(d)
    assert view["a"] == 1
    with pytest.raises(TypeError):
        view["b"] = 2
    d["b"] = 2
    assert view["b"] == 2  # live view of d
