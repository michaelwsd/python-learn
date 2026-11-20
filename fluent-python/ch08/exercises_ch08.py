"""Chapter 8 exercises: type hints in functions.

Each exercise has two parts: make the function WORK, and give it type hints that
pass `mypy --strict`. typecheck_ch08.py holds calls that mypy checks against your
hints (read it to see exactly what is expected). Then run:

    uv run pytest ch08 -v

Check one exercise at a time with -k, e.g.  uv run pytest ch08 -v -k first
See the raw mypy output with:  cd ch08 && uv run mypy --strict exercises_ch08.py typecheck_ch08.py

Write the hints yourself: add imports from typing / collections.abc as needed.
"""


# Exercise 1: Optional parameter (Example 8-3)
# ---------------------------------------------------------------------------
# show_count(count, singular, plural=None) -> "1 bird", "no birds", "3 mice"
# plural may be a str or None; when it is None, use singular + "s".
def show_count(count: int, singular: str, plural: str | None = None) -> str:
    if not plural:
        plural = singular + "s"

    if count == 0:
        return "no " + plural
    elif count == 1:
        return f"1 {singular}"
    else:
        return f"{count} {plural}"


# Exercise 2: be liberal in what you accept, conservative in what you return
# ---------------------------------------------------------------------------
# word_lengths(words) -> {word: len(word)}
#   word_lengths(["ab", "c"]) -> {"ab": 2, "c": 1}
# It must accept ANY iterable of str (list, tuple, generator), and its return
# type must be a concrete dict type.
def word_lengths(words):
    raise NotImplementedError


# Exercise 3: tuples as records, type alias
# ---------------------------------------------------------------------------
# midpoint(a, b) -> the point halfway between two (x, y) points
#   midpoint((0.0, 0.0), (2.0, 4.0)) -> (1.0, 2.0)
# Define a type alias Point for a 2-float tuple and use it for all three hints.
def midpoint(a, b):
    raise NotImplementedError


# Exercise 4: TypeVar
# ---------------------------------------------------------------------------
# first(items) -> the first item of a sequence; raise ValueError if it is empty
# The return type must follow the input: a list of int gives an int,
# a str gives a str. Hint: Sequence[T].
def first(items):
    raise NotImplementedError


# Exercise 5: Protocol + bounded TypeVar (Examples 8-20, 8-21)
# ---------------------------------------------------------------------------
# largest(items) -> the largest item of a non-empty iterable (use max)
#   largest([3, 9, 2]) -> 9;  largest(["pear", "apple"]) -> "pear"
# It must accept any type that supports <, including a class that only
# defines __lt__, and return that same type. objects without < must be
# rejected by mypy. Define a SupportsLessThan Protocol and a TypeVar bound to it.
def largest(items):
    raise NotImplementedError


# Exercise 6: Callable and Mapping
# ---------------------------------------------------------------------------
# best_symbol(prices, better) -> the symbol with the best price
#   prices maps symbol -> price, e.g. {"AAPL": 190.0, "NVDA": 120.0}
#   better(a, b) returns True if price a is better than price b
#   best_symbol(prices, lambda a, b: a < b) -> "NVDA"  (cheapest)
# Raise ValueError if prices is empty. prices is only read, never changed,
# so accept any read-only mapping, not just dict.
def best_symbol(prices, better):
    raise NotImplementedError


# Exercise 7: annotating positional-only and variadic parameters
# ---------------------------------------------------------------------------
# make_url(base, /, *path, **query) -> base, then each path part joined by "/",
# then "?k=v&k2=v2" if there is any query
#   make_url("https://x.com", "api", "v1") -> "https://x.com/api/v1"
#   make_url("https://x.com", "q", page="2") -> "https://x.com/q?page=2"
# All path parts and query values must be str.
def make_url():
    raise NotImplementedError


# Exercise 8: NoReturn
# ---------------------------------------------------------------------------
# fail(msg) -> always raises ValueError(msg); it never returns
# parse_side(side) -> "BUY" or "SELL" (ignore case and surrounding spaces);
#   anything else: call fail(f"unknown side: {side}")
# With the right return hint on fail, mypy knows parse_side can't fall off
# the end without returning a str.
def fail(msg):
    raise NotImplementedError


def parse_side(side):
    raise NotImplementedError
