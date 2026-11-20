"""Chapter 14: inheritance, for better or for worse.

Run:  uv run python ch14/inheritance_demo.py
"""

import collections
from collections import OrderedDict, UserDict
from http.server import ThreadingHTTPServer


def section(title):
    print(f"\n--- {title} ---")


def print_mro(cls):
    print(", ".join(c.__name__ for c in cls.__mro__))


section("super(): call the overridden method of the superclass")


class LastUpdatedOrderedDict(OrderedDict):
    """Store items in the order they were last updated"""

    def __setitem__(self, key, value):
        super().__setitem__(key, value)  # let OrderedDict store it
        self.move_to_end(key)  # then do the extra work


d = LastUpdatedOrderedDict(a=1, b=2)
d["a"] = 10  # updating 'a' moves it to the end
print(list(d.items()))


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


class NamedPoint(Point):
    def __init__(self, x, y, name):
        super().__init__(x, y)  # Python does NOT call this for you
        self.name = name


p = NamedPoint(1, 2, "origin-ish")
print(p.x, p.y, p.name)

section("Subclassing built-ins is tricky (Examples 14-1 to 14-3)")


class DoppelDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)


dd = DoppelDict(one=1)  # dict.__init__ ignores our __setitem__
dd["two"] = 2  # [] uses it
dd.update(three=3)  # dict.update ignores it
print("dict subclass:    ", dd)


class DoppelDict2(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)


dd2 = DoppelDict2(one=1)
dd2["two"] = 2
dd2.update(three=3)
print("UserDict subclass:", dd2)


class AnswerDict(dict):
    def __getitem__(self, key):
        return 42


ad = AnswerDict(a="foo")
plain = {}
plain.update(ad)  # dict.update ignores AnswerDict.__getitem__
print(ad["a"], plain["a"])


class AnswerDict2(UserDict):
    def __getitem__(self, key):
        return 42


plain2 = {}
plain2.update(AnswerDict2(a="foo"))
print(plain2["a"])

section("Multiple inheritance and the MRO (Examples 14-4, 14-5)")


class Root:
    def ping(self):
        print(f"{self}.ping() in Root")

    def pong(self):
        print(f"{self}.pong() in Root")

    def __repr__(self):
        return f"<instance of {type(self).__name__}>"


class A(Root):
    def ping(self):
        print(f"{self}.ping() in A")
        super().ping()

    def pong(self):
        print(f"{self}.pong() in A")
        super().pong()


class B(Root):
    def ping(self):
        print(f"{self}.ping() in B")
        super().ping()

    def pong(self):  # does NOT call super(): the chain stops here
        print(f"{self}.pong() in B")


class Leaf(A, B):
    def ping(self):
        print(f"{self}.ping() in Leaf")
        super().ping()


print_mro(Leaf)
leaf1 = Leaf()
leaf1.ping()  # Leaf, A, B, Root: every ping calls super()
leaf1.pong()  # A, B: B.pong doesn't call super(), so Root.pong never runs

section("super() follows the MRO of the INSTANCE (Example 14-6)")


class U:
    def ping(self):
        print(f"{self}.ping() in U")
        super().ping()  # U's own base is object, which has no ping...


class LeafUA(U, A):
    def ping(self):
        print(f"{self}.ping() in LeafUA")
        super().ping()


try:
    U().ping()
except AttributeError as e:
    print("U().ping():", e)
print_mro(LeafUA)
LeafUA().ping()  # ...but in a LeafUA, the class after U is A

section("Mixin classes (Examples 14-8, 14-9)")


def _upper(key):
    try:
        return key.upper()
    except AttributeError:
        return key


class UpperCaseMixin:
    def __setitem__(self, key, item):
        super().__setitem__(_upper(key), item)

    def __getitem__(self, key):
        return super().__getitem__(_upper(key))

    def get(self, key, default=None):
        return super().get(_upper(key), default)

    def __contains__(self, key):
        return super().__contains__(_upper(key))


class UpperDict(UpperCaseMixin, collections.UserDict):  # mixin goes FIRST
    """Case-insensitive dict"""


class UpperCounter(UpperCaseMixin, collections.Counter):
    """Specialized 'Counter' that uppercases string keys"""


ud = UpperDict([("a", "letter A"), (2, "digit two")])
ud["b"] = "letter B"
print(list(ud.keys()), "b" in ud, ud["a"], ud.get("B"))
print(UpperCounter("BaNanA").most_common())
print_mro(UpperDict)

section("Real world: ThreadingHTTPServer is a mixin plus a base class")
print_mro(ThreadingHTTPServer)

section("Composition instead of inheritance")


class StackByInheritance(list):  # a Stack IS-A list: inherits 40+ list methods
    def push(self, item):
        self.append(item)


class Stack:  # a Stack HAS-A list: exposes only what it means
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)  # delegate to the list

    def pop(self):
        return self._items.pop()

    def __len__(self):
        return len(self._items)


bad = StackByInheritance()
bad.push(1)
bad.insert(0, 99)  # allowed: breaks the stack's rules
print("inherited:", bad)
good = Stack()
good.push(1)
print("composed: ", len(good), hasattr(good, "insert"))
