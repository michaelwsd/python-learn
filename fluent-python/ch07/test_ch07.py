import functools
import inspect

import pytest
from exercises_ch07 import (
    CallCounter,
    apply_twice,
    clamp,
    compose,
    connect,
    make_multiplier,
    product,
    rhyme_sort,
    sort_by,
)


def body(func):
    """Source of a function without its def line, for checking what it uses."""
    return inspect.getsource(func).split(":", 1)[1]


# Exercise 1 ---------------------------------------------------------------
def test_apply_twice():
    assert apply_twice(lambda n: n + 3, 10) == 16
    assert apply_twice(str.upper, "hi") == "HI"


def test_compose():
    inc_then_double = compose(lambda n: n * 2, lambda n: n + 1)
    assert callable(inc_then_double)
    assert inc_then_double(5) == 12
    assert compose(len, str.strip)("  abc  ") == 3


# Exercise 2 ---------------------------------------------------------------
def test_rhyme_sort():
    assert rhyme_sort(["apple", "fig", "banana"]) == ["banana", "apple", "fig"]
    words = ["strawberry", "fig", "apple", "cherry", "raspberry", "banana"]
    assert rhyme_sort(words) == [
        "banana",
        "apple",
        "fig",
        "raspberry",
        "strawberry",
        "cherry",
    ]


# Exercise 3 ---------------------------------------------------------------
def test_product():
    assert product([1, 2, 3, 4]) == 24
    assert product([7]) == 7
    assert product([]) == 1


def test_product_uses_operator_mul():
    assert "mul" in body(product) and "lambda" not in body(product)


# Exercise 4 ---------------------------------------------------------------
def test_call_counter():
    sq = CallCounter(lambda n: n * n)
    assert callable(sq)
    assert sq.calls == 0
    assert sq(3) == 9
    assert sq(4) == 16
    assert sq.calls == 2


def test_call_counter_passes_all_arguments():
    joined = CallCounter(lambda *a, sep="-": sep.join(a))
    assert joined("a", "b", sep="+") == "a+b"


# Exercise 5 ---------------------------------------------------------------
def test_connect():
    assert connect("db", timeout=5) == {
        "host": "db",
        "port": 5432,
        "timeout": 5,
        "retries": 3,
    }
    assert connect("db", 6000, timeout=1, retries=0)["port"] == 6000


def test_connect_keyword_only():
    assert connect("db", timeout=5)["timeout"] == 5  # the valid call works
    with pytest.raises(TypeError):
        connect("db", 5432, 5)
    with pytest.raises(TypeError):
        connect("db")


# Exercise 6 ---------------------------------------------------------------
def test_clamp():
    assert clamp(15, 0, 10) == 10
    assert clamp(-3, 0, 10) == 0
    assert clamp(4, 0, 10) == 4


def test_clamp_positional_only():
    assert clamp(4, 0, 10) == 4  # the valid call works
    with pytest.raises(TypeError):
        clamp(value=4, low=0, high=10)


# Exercise 7 ---------------------------------------------------------------
TRADES = [("MSFT", "BUY", 30), ("AAPL", "SELL", 10), ("AAPL", "BUY", 20)]


def test_sort_by():
    assert sort_by(TRADES, 0) == [
        ("AAPL", "SELL", 10),
        ("AAPL", "BUY", 20),
        ("MSFT", "BUY", 30),
    ]
    assert sort_by(TRADES, 1, 2) == [
        ("AAPL", "BUY", 20),
        ("MSFT", "BUY", 30),
        ("AAPL", "SELL", 10),
    ]
    assert sort_by(TRADES, 2)[0] == ("AAPL", "SELL", 10)


def test_sort_by_uses_itemgetter():
    assert "itemgetter" in body(sort_by) and "lambda" not in body(sort_by)


# Exercise 8 ---------------------------------------------------------------
def test_make_multiplier():
    triple = make_multiplier(3)
    assert isinstance(triple, functools.partial)
    assert triple(7) == 21
    assert list(map(make_multiplier(2), [1, 2, 3])) == [2, 4, 6]
