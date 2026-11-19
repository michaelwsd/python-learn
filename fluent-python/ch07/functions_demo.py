"""Chapter 7: functions as first-class objects.

Run:  uv run python ch07/functions_demo.py
"""

import random
from collections import namedtuple
from functools import partial, reduce
from operator import attrgetter, itemgetter, methodcaller, mul


def section(title):
    print(f"\n--- {title} ---")


section("A function is an object (Examples 7-1, 7-2)")


def factorial(n):
    """returns n!"""
    return 1 if n < 2 else n * factorial(n - 1)


print(factorial.__doc__, "|", type(factorial))
fact = factorial  # another name for the same function object
print(fact(5), "|", list(map(factorial, range(6))))  # passed as an argument

section("Higher-order functions (Examples 7-3 to 7-6)")
fruits = ["strawberry", "fig", "apple", "cherry", "raspberry", "banana"]
print(sorted(fruits, key=len))  # len is passed, not called


def reverse(word):
    return word[::-1]


print(sorted(fruits, key=reverse))  # rhyme order
print(list(map(factorial, filter(lambda n: n % 2, range(6)))))  # map + filter
print([factorial(n) for n in range(6) if n % 2])  # the same, clearer
print(reduce(lambda a, b: a + b, range(100)), sum(range(100)))
print(all([1, 2, 0]), any([0, 0, 3]), all([]), any([]))

section("Anonymous functions (Example 7-7)")
print(sorted(fruits, key=lambda word: word[::-1]))

section("Callables")
print([callable(obj) for obj in (abs, str, "Ni!", factorial, len)])


class BingoCage:
    def __init__(self, items):
        self._items = list(items)
        random.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError("pick from empty BingoCage")

    def __call__(self):  # bingo() is a shortcut for bingo.pick()
        return self.pick()


section("User-defined callable types (Example 7-8)")
random.seed(0)
bingo = BingoCage(range(3))
print(bingo.pick(), bingo(), callable(bingo))

section("Keyword-only and positional-only parameters (Examples 7-9, 7-10)")


def tag(name, /, *content, class_=None, **attrs):
    """Generate one or more HTML tags"""
    if class_ is not None:
        attrs["class"] = class_
    attr_str = "".join(f' {attr}="{value}"' for attr, value in sorted(attrs.items()))
    if content:
        return "\n".join(f"<{name}{attr_str}>{c}</{name}>" for c in content)
    return f"<{name}{attr_str} />"


print(tag("br"))
print(tag("p", "hello", "world", class_="sidebar"))
print(tag("img", src="sunset.jpg", title="Sunset"))
my_tag = {"src": "sunset.jpg", "class": "framed"}
print(tag("img", **my_tag))  # ** unpacks the dict into keyword arguments


def f(a, *, b):  # b is keyword-only and has no default: it's mandatory
    return a, b


print(f(1, b=2))
for call in (lambda: f(1, 2), lambda: tag(name="br"), lambda: divmod(a=10, b=3)):
    try:
        call()
    except TypeError as e:
        print("TypeError:", e)

section("The operator module (Examples 7-11 to 7-15)")
print(reduce(mul, range(1, 6)))  # factorial without a lambda
metro_data = [
    ("Tokyo", "JP", 36.933, (35.689722, 139.691667)),
    ("Delhi NCR", "IN", 21.935, (28.613889, 77.208889)),
    ("Mexico City", "MX", 20.142, (19.433333, -99.133333)),
]
for city in sorted(metro_data, key=itemgetter(1)):  # sort by country code
    print(city[:2])
print(list(map(itemgetter(1, 0), metro_data)))  # several fields → tuples
City = namedtuple("City", "name cc pop")
cities = [City(*row[:3]) for row in metro_data]
print([c.name for c in sorted(cities, key=attrgetter("pop"))])
upcase = methodcaller("upper")
hyphenate = methodcaller("replace", " ", "-")  # extra arguments are bound
print(upcase("the time"), hyphenate("the time has come"))

section("Freezing arguments with functools.partial (Examples 7-16, 7-18)")
triple = partial(mul, 3)
print(triple(7), list(map(triple, range(1, 5))))
picture = partial(tag, "img", class_="pic-frame")
print(picture(src="wumpus.jpeg"))
print(picture.func.__name__, picture.args, picture.keywords)
