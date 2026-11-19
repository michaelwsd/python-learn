"""Chapter 3, part 2: sets, and how hash tables shape dicts and sets.

Run:  uv run python ch03/sets_demo.py
"""

import timeit


def section(title):
    print(f"\n--- {title} ---")


section("Sets remove duplicates")
items = ["spam", "spam", "eggs", "spam", "bacon", "eggs"]
print(set(items))  # order not guaranteed
print(list(dict.fromkeys(items)))  # dedupe AND keep first-seen order

section("Set literals, frozenset, set comprehensions")
s = {1, 2, 3}  # literal; note: {} is an empty DICT, use set() for an empty set
print(type({}), type(set()))
fs = frozenset([1, 2, 3])  # immutable and hashable: can be a dict key or set item
print({fs: "ok"})
print({chr(i) for i in range(32, 48)})  # set comprehension

section("Set operations")
a = {"AAPL", "MSFT", "NVDA"}
b = {"MSFT", "TSLA", "NVDA", "AMZN"}
print("a & b  intersection:", sorted(a & b))
print("a | b  union:       ", sorted(a | b))
print("a - b  difference:  ", sorted(a - b))
print("a ^ b  symmetric:   ", sorted(a ^ b))
print("{'MSFT'} <= a subset:", {"MSFT"} <= a, "| isdisjoint:", a.isdisjoint({"IBM"}))

section("Membership: set vs list (Example 3-14 idea)")
haystack_list = list(range(1_000_000))
haystack_set = set(haystack_list)
t_list = timeit.timeit(lambda: 999_999 in haystack_list, number=100)
t_set = timeit.timeit(lambda: 999_999 in haystack_set, number=100)
print(f"100 lookups: list {t_list:.3f}s, set {t_set:.6f}s")

section("Set operations on dict views")
d1 = dict(a=1, b=2, c=3, d=4)
d2 = dict(b=20, d=40, e=50)
print("d1.keys() & d2.keys():", d1.keys() & d2.keys())  # keys views act like sets
print("d1.keys() - {'a'}:   ", d1.keys() - {"a"})
required = {"symbol", "qty", "price"}
order = {"symbol": "AAPL", "qty": 100}
print("missing fields:", required - order.keys())
