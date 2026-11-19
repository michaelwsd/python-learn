"""Chapter 3 exercises: dictionaries and sets.

Replace each `raise NotImplementedError` with your code, then run:

    uv run pytest ch03 -v

Check one exercise at a time with -k, e.g.  uv run pytest ch03 -v -k invert
"""

from collections import Counter, UserDict, defaultdict
from types import MappingProxyType


# Exercise 1: dict comprehensions and merging with |
# ---------------------------------------------------------------------------
# invert({"AAPL": "Apple", "MSFT": "Microsoft"}) -> {"Apple": "AAPL", "Microsoft": "MSFT"}
# Use one dict comprehension.
def invert(d):
    return {val: key for key, val in d.items()}


# merge_config(defaults, overrides) -> a NEW dict: defaults, with overrides winning.
# Use the | operator. Neither argument may be changed.
def merge_config(defaults, overrides):
    return defaults | overrides


# Exercise 2: pattern matching with mappings
# ---------------------------------------------------------------------------
# One `match` statement. Mapping patterns match even when the dict has EXTRA keys.
#   {"type": "trade", "symbol": s, "qty": q} where q is an int -> "trade 100 AAPL"
#   {"type": "error", "code": c, ...any other keys...}         -> "error 503 (2 extra fields)"
#        (count every key except "type" and "code"; hint: **rest)
#   {"type": "heartbeat"}                                       -> "heartbeat"
#   anything else                                               -> "unknown event"
def describe(event):
    match event:
        case {"type": "trade", "symbol": s, "qty": int(q)}:
            return f"trade 100 {s}"
        case {"type": "error", "code": c, **rest}:
            return f"error {c} ({len(rest)} extra fields)"
        case {"type": "heartbeat"}:
            return "heartbeat"
        case _:
            return "unknown event"


# Exercise 3: grouping without checking "is the key there yet?"
# ---------------------------------------------------------------------------
# group_by_symbol([("AAPL", 100), ("MSFT", 25), ("AAPL", 50)])
#   -> {"AAPL": [100, 50], "MSFT": [25]}
# Don't write `if key not in d`. Use setdefault or defaultdict.
# Return a plain dict (convert a defaultdict with dict(...)).
def group_by_symbol(trades):
    d = defaultdict(list)
    for symbol, price in trades:
        d[symbol].append(price)

    return dict(d)


# Exercise 4: counting with Counter
# ---------------------------------------------------------------------------
# top_words("the cat and The dog and THE end", 2) -> [("the", 3), ("and", 2)]
# Case-insensitive; split on whitespace.
def top_words(text, n):
    count = Counter(text.lower().split())
    return count.most_common(n)


# Exercise 5: a custom mapping with __missing__ (subclass UserDict)
# ---------------------------------------------------------------------------
# A dict whose keys are always stored as strings, like Example 3-9:
#   d = StrKeyDict([(2, "two")])   -> d.data == {"2": "two"}
#   d[2] == d["2"] == "two";  2 in d;  d[5] = "x" stores key "5"
#   d[1] -> KeyError;  d.get(1, "N/A") -> "N/A"
# Implement __missing__, __contains__ and __setitem__. UserDict keeps the
# real dict in self.data.
class StrKeyDict(UserDict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data

    def __setitem__(self, key, item):
        self.data[str(key)] = item 


# Exercise 6: hashability and de-duplication
# ---------------------------------------------------------------------------
# is_hashable((1, 2)) -> True;  is_hashable((1, [2])) -> False;  is_hashable([]) -> False
def is_hashable(obj):
    try:
        hash(obj)
    except TypeError:
        return False 
    return True 


# dedupe(["b", "a", "b", "c", "a"]) -> ["b", "a", "c"]   (first-seen order kept)
# One line, no loop: dict keys are unique AND keep insertion order.
def dedupe(items):
    return list(dict.fromkeys(items))


# Exercise 7: set operations and dict views
# ---------------------------------------------------------------------------
# compare(a, b) -> {"both": ..., "only_a": ..., "only_b": ..., "either": ...}
# Each value is a set. Use &, -, | (no loops).
def compare(a, b):
    return {
        "both": a & b,
        "only_a": a - b,
        "only_b": b - a,
        "either": a | b
    }


# missing_fields({"symbol": "AAPL", "qty": 1}, {"symbol", "qty", "price"}) -> {"price"}
# Use a set operation directly on the dict's keys view.
def missing_fields(record, required):
    return required - record.keys()


# Exercise 8: a read-only view
# ---------------------------------------------------------------------------
# read_only(d) -> a mapping that can be read but not written, and that shows
# later changes made to d. Hint: types.MappingProxyType.
def read_only(d):
    from types import MappingProxyType
    return MappingProxyType(d)
