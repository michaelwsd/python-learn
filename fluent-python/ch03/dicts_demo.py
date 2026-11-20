"""Chapter 3, part 1: dictionaries and mappings.

Run:  uv run python ch03/dicts_demo.py
"""

import collections
from collections import ChainMap, Counter, UserDict, defaultdict
from types import MappingProxyType


def section(title):
    print(f"\n--- {title} ---")


section("dict comprehensions (Example 3-1)")
dial_codes = [(880, "Bangladesh"), (55, "Brazil"), (86, "China"), (91, "India")]
country_dial = {country: code for code, country in dial_codes}
print(country_dial)
print(
    {
        code: country.upper()
        for country, code in sorted(country_dial.items())
        if code < 70
    }
)

section("Unpacking and merging mappings")


def dump(**kwargs):
    return kwargs


print(dump(**{"x": 1}, y=2, **{"z": 3}))  # ** in a call
print(
    {"a": 0, **{"x": 1}, "y": 2, **{"z": 3, "x": 4}}
)  # ** in a literal: later keys win
d1 = {"a": 1, "b": 3}
d2 = {"a": 2, "b": 4, "c": 6}
print("d1 | d2 =", d1 | d2)  # new dict; right side wins
d1 |= d2  # update d1 in place
print("d1 after |= :", d1)

section("Pattern matching with mappings (Example 3-2)")


def get_creators(record):
    match record:
        case {"type": "book", "api": 2, "authors": [*names]}:
            return names
        case {"type": "book", "api": 1, "author": name}:
            return [name]
        case {"type": "book"}:
            raise ValueError(f"Invalid 'book' record: {record!r}")
        case {"type": "movie", "director": name}:
            return [name]
        case _:
            raise ValueError(f"Invalid record: {record!r}")


b1 = dict(api=1, author="Douglas Hofstadter", type="book", title="Godel, Escher, Bach")
print(get_creators(b1))  # extra keys (title) are fine: partial match
match {"type": "book", "title": "X", "year": 2001}:
    case {"type": "book", **details}:  # **rest captures the other keys
        print("details:", details)

section("What is hashable")
tt = (1, 2, (30, 40))
print("hash(tt) works:", hash(tt) == hash((1, 2, (30, 40))))
for obj in [(1, 2, [30, 40]), [1, 2], {1: 2}]:
    try:
        hash(obj)
    except TypeError as e:
        print(f"hash({obj!r}): {e}")
print("frozenset is hashable:", hash(frozenset([30, 40])) == hash(frozenset([40, 30])))

section("setdefault: insert-or-get in one lookup (Example 3-5)")
text = "the quick fox the lazy dog the end"
index = {}
for position, word in enumerate(text.split()):
    index.setdefault(word, []).append(position)  # one lookup instead of get + set
print(index)

section("defaultdict: missing keys get a default (Example 3-6)")
index = defaultdict(list)  # list is the default_factory, called with no arguments
for position, word in enumerate(text.split()):
    index[word].append(position)
print(dict(index))
print(
    "index.get('cat'):", index.get("cat"), "| 'cat' in index:", "cat" in index
)  # only [] triggers it

section("__missing__ (Example 3-7, simplified)")


class StrKeyDict0(dict):
    def __missing__(self, key):  # called by dict.__getitem__ when a key is absent
        if isinstance(key, str):
            raise KeyError(key)  # avoid infinite recursion
        return self[str(key)]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys() or str(key) in self.keys()


d = StrKeyDict0([("2", "two"), ("4", "four")])
print(d[2], d["4"], d.get(1, "N/A"), 4 in d, 1 in d)

section("Variations of dict")
ct = Counter("abracadabra")
print(ct, ct.most_common(2))
ct.update("aaaaazzz")
print(ct.most_common(3))
defaults = {"timeout": 30, "retries": 3}
env = {"timeout": 5}
cli = {"retries": 10}
config = ChainMap(cli, env, defaults)  # searches cli, then env, then defaults
print(config["timeout"], config["retries"])
od = collections.OrderedDict(a=1, b=2, c=3)
od.move_to_end("a")
print(od, od.popitem(last=False))

section("Subclass UserDict, not dict (Example 3-9)")


class StrKeyDict(UserDict):  # stores items in self.data, a real dict
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data

    def __setitem__(self, key, item):
        self.data[str(key)] = item  # every write converts the key


d = StrKeyDict([(2, "two")])
d[4] = "four"
d.update({6: "six"})  # update() goes through __setitem__ too
print(d.data, d[2], 6 in d)

section("Immutable mappings: MappingProxyType (Example 3-10)")
d = {1: "A"}
d_proxy = MappingProxyType(d)
print(d_proxy[1])
try:
    d_proxy[2] = "x"
except TypeError as e:
    print("TypeError:", e)
d[2] = "B"  # the proxy is a live, read-only view of d
print(d_proxy)

section("Dictionary views (Example 3-11)")
d = dict(a=10, b=20, c=30)
values = d.values()
print(values, len(values), list(reversed(values)))
d["z"] = 99
print("view updated live:", values)
