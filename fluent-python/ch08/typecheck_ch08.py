"""Calls that mypy checks against your hints. Don't edit this file.

test_ch08.py runs:  mypy --strict exercises_ch08.py typecheck_ch08.py

- assert_type(expr, T): mypy fails unless your hints make expr exactly type T.
- `# type: ignore[code]`: this call MUST be a type error. If your hints let it
  through, mypy reports the ignore comment as unused, and the test fails.
These functions are never called; they exist only to be type checked.
"""

from types import MappingProxyType
from typing import Any, assert_type

from exercises_ch08 import (
    best_symbol,
    first,
    largest,
    make_url,
    midpoint,
    parse_side,
    show_count,
    word_lengths,
)


def check_ex1() -> None:
    assert_type(show_count(2, "bird"), str)
    assert_type(show_count(2, "mouse", "mice"), str)
    show_count(2, "mouse", None)
    show_count("2", "bird")  # type: ignore[arg-type]


def check_ex2() -> None:
    assert_type(word_lengths(["a", "bb"]), dict[str, int])
    word_lengths(w for w in ("a", "bb"))  # a generator: not a list
    word_lengths(("a", "bb"))  # a tuple: not a list


def check_ex3() -> None:
    assert_type(midpoint((0.0, 0.0), (2.0, 4.0)), tuple[float, float])
    midpoint((0, 0), (2, 4))  # int is accepted where float is expected
    midpoint((0.0, 0.0, 0.0), (2.0, 4.0))  # type: ignore[arg-type]


def check_ex4() -> None:
    assert_type(first([1, 2, 3]), int)
    assert_type(first("abc"), str)
    assert_type(first((1.5, 2.5)), float)


class Price:
    def __init__(self, value: float) -> None:
        self.value = value

    def __lt__(self, other: Any) -> bool:
        return bool(self.value < other.value)


def check_ex5() -> None:
    assert_type(largest([3, 9, 2]), int)
    assert_type(largest(["pear", "apple"]), str)
    assert_type(largest([Price(1), Price(2)]), Price)  # only __lt__, no inheritance
    largest([object(), object()])  # type: ignore[type-var]


def by_name(a: str, b: str) -> bool:
    return a < b


def check_ex6() -> None:
    prices = MappingProxyType({"AAPL": 190.0, "MSFT": 410.0})  # a Mapping, not a dict
    assert_type(best_symbol(prices, lambda a, b: a < b), str)
    best_symbol(prices, by_name)  # type: ignore[arg-type]


def check_ex7() -> None:
    assert_type(make_url("https://x.com", "api", page="2"), str)
    make_url("https://x.com", 1)  # type: ignore[arg-type]
    make_url("https://x.com", page=2)  # type: ignore[arg-type]


def check_ex8() -> None:
    assert_type(parse_side("buy"), str)
