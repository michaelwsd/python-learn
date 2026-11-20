"""Chapter 7 exercises: functions as first-class objects.

Replace each `raise NotImplementedError` with your code, then run:

    uv run pytest ch07 -v

Check one exercise at a time with -k, e.g.  uv run pytest ch07 -v -k compose
"""

from functools import partial, reduce
from operator import itemgetter, mul


# Exercise 1: functions are objects you can pass and return
# ---------------------------------------------------------------------------
# apply_twice(f, x) -> f(f(x))
#   apply_twice(lambda n: n + 3, 10) -> 16
def apply_twice(f, x):
    return f(f(x))


# compose(f, g) -> a NEW function h such that h(x) == f(g(x))
#   inc_then_double = compose(lambda n: n * 2, lambda n: n + 1)
#   inc_then_double(5) -> 12
def compose(f, g):
    def h(x):
        return f(g(x))
    return h

# Exercise 2: key functions
# ---------------------------------------------------------------------------
# rhyme_sort(words) -> words sorted by their REVERSED spelling (Example 7-4),
# so words with the same ending end up next to each other.
#   rhyme_sort(["apple", "fig", "banana"]) -> ["banana", "apple", "fig"]
# One line: sorted() with a lambda as the key.
def rhyme_sort(words):
    return sorted(words, key=lambda x: x[::-1])


# Exercise 3: reduce with the operator module
# ---------------------------------------------------------------------------
# product(nums) -> the product of all numbers; product([]) -> 1
# Use reduce and operator.mul (no lambda). Hint: reduce takes an initial value.
def product(nums):
    return reduce(mul, nums, 1)


# Exercise 4: a user-defined callable
# ---------------------------------------------------------------------------
# CallCounter wraps a function: calling the instance calls the function,
# and .calls counts how many times it has been called.
#   sq = CallCounter(lambda n: n * n)
#   sq(3) -> 9;  sq(4) -> 16;  sq.calls -> 2;  callable(sq) -> True
class CallCounter:
    def __init__(self, func):
        self.func = func 
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


# Exercise 5: keyword-only parameters
# ---------------------------------------------------------------------------
# connect(host, port=5432, *, timeout, retries=3) -> a dict of the four values
#   connect("db", timeout=5) -> {"host": "db", "port": 5432, "timeout": 5, "retries": 3}
# timeout and retries can ONLY be passed by keyword, and timeout is required.
#   connect("db", 5432, 5)   -> TypeError
#   connect("db")            -> TypeError
# Write the signature yourself.
def connect(host, port=5432, *, timeout, retries=3):
    return {
        "host": host,
        "port": port,
        "timeout": timeout,
        "retries": retries
    }


# Exercise 6: positional-only parameters
# ---------------------------------------------------------------------------
# clamp(value, low, high) -> value limited to the range [low, high]
#   clamp(15, 0, 10) -> 10;  clamp(-3, 0, 10) -> 0;  clamp(4, 0, 10) -> 4
# All three must be positional-only: clamp(value=4, low=0, high=10) -> TypeError
# Write the signature yourself.
def clamp(value, low, high, /):
    return max(low, min(value, high))


# Exercise 7: itemgetter for sorting records
# ---------------------------------------------------------------------------
# sort_by(records, *fields) -> records sorted by the given fields, in order
#   trades = [("MSFT", "BUY", 30), ("AAPL", "SELL", 10), ("AAPL", "BUY", 20)]
#   sort_by(trades, 0)    -> sorted by symbol (ties keep their order)
#   sort_by(trades, 0, 2) -> sorted by symbol, then quantity
# Use operator.itemgetter as the key (no lambda).
def sort_by(records, *fields):
    return sorted(records, key=itemgetter(*fields))


# Exercise 8: freezing arguments with partial
# ---------------------------------------------------------------------------
# make_multiplier(n) -> a functools.partial object that multiplies by n
#   triple = make_multiplier(3);  triple(7) -> 21
# Use partial and operator.mul.
def make_multiplier(n):
    return partial(mul, n)
