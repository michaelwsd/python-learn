"""Chapter 2, part 1: listcomps, genexps, tuples, unpacking, match.

Run:  uv run python ch02/sequences_demo.py
"""

import array


def section(title):
    print(f"\n--- {title} ---")


section("Listcomps vs map/filter (Example 2-2)")
symbols = "$¢£¥€¤"
beyond_ascii = [ord(s) for s in symbols if ord(s) > 127]
same_thing = list(filter(lambda c: c > 127, map(ord, symbols)))
print(beyond_ascii, beyond_ascii == same_thing)  # listcomp reads better

section("Cartesian product (Example 2-4)")
colors = ["black", "white"]
sizes = ["S", "M", "L"]
tshirts = [
    (color, size) for color in colors for size in sizes
]  # nested loops, same order
print(tshirts)

section("Generator expressions (Example 2-5, 2-6)")
print(tuple(ord(s) for s in symbols))  # sole argument: no extra parentheses needed
print(array.array("I", (ord(s) for s in symbols)))
for tshirt in (f"{c} {s}" for c in colors for s in sizes):  # never builds a list
    print(tshirt)

section("Tuples as records (Example 2-7)")
lax_coordinates = (33.9425, -118.408056)
city, year, pop, chg, area = ("Tokyo", 2003, 32_450, 0.66, 8014)  # position = meaning
traveler_ids = [("USA", "31195855"), ("BRA", "CE342567"), ("ESP", "XDA205856")]
for country, _ in sorted(traveler_ids):  # _ = "I don't need this field"
    print(country)

section("Relative immutability")
a = (10, "alpha", [1, 2])
b = (10, "alpha", [1, 2])
print("a == b:", a == b)
b[-1].append(99)  # the tuple can't change which objects it holds,
print("after append:", b, "a == b:", a == b)  # but a mutable item inside can change
try:
    hash(b)
except TypeError as e:
    print("hash(b):", e)  # only tuples of hashable items are hashable

section("Unpacking")
latitude, longitude = lax_coordinates
a, b = 1, 2
a, b = b, a  # swap without a temp variable
print("swapped:", a, b)
print("divmod(*(20, 8)):", divmod(*(20, 8)))  # * spreads an iterable into arguments
first, second, *rest = range(5)
print(first, second, rest)  # rest is always a list
*head, last = range(5)
print(head, last)
print([*range(3), 3, *"ab"])  # * inside a list literal

section("Nested unpacking (Example 2-8)")
metro_areas = [
    ("Tokyo", "JP", 36.933, (35.689722, 139.691667)),
    ("Delhi NCR", "IN", 21.935, (28.613889, 77.208889)),
    ("Sao Paulo", "BR", 19.649, (-23.547778, -46.635833)),
]
for name, _, _, (lat, lon) in metro_areas:  # shape of the target = shape of the data
    if lon <= 0:
        print(f"{name:15} | {lat:9.4f} | {lon:9.4f}")

section("Pattern matching on sequences (Example 2-9)")
for record in metro_areas:
    match record:
        case [name, _, _, (lat, lon)] if lon <= 0:  # destructure + guard
            print(f"west of Greenwich: {name}")
        case [name, *_]:
            print(f"elsewhere: {name}")

for command in (["go", "north"], ["drop", "key", "map"], "go north"):
    match command:
        case ["go", direction]:
            print("going", direction)
        case ["drop", *items]:
            print("dropping", items)
        case _:  # a str is NOT matched as a sequence in `match`
            print("no match for", repr(command))
