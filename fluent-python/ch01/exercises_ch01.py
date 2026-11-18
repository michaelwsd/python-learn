"""Chapter 1 exercises: the Python Data Model.

Replace each `raise NotImplementedError` with your code, then run:

    uv run pytest ch01 -v

Rule for all exercises: implement special methods; don't call them directly
(write len(x), not x.__len__()).
"""

import math


# Exercise 1: a sequence for free
# ---------------------------------------------------------------------------
# Make Playlist behave like a read-only sequence by implementing ONLY
# __len__ and __getitem__ (like FrenchDeck). Don't add __iter__,
# __contains__ or __reversed__: the tests check that iteration, `in`,
# slicing and reversed() all work anyway.
class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, position):
        return self._songs[position]


# Exercise 2: more operators for Vector
# ---------------------------------------------------------------------------
# This is the chapter's Vector. Add:
#   v1 == v2  -> True when x and y are equal          (__eq__)
#   v1 - v2   -> a new Vector                         (__sub__)
#   -v        -> a new Vector pointing the other way  (__neg__)
#   3 * v     -> same result as v * 3                 (__rmul__)
# Hint for __rmul__: for `3 * v`, Python first tries int's __mul__, which
# doesn't know Vector and gives up, then calls v.__rmul__(3).
class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x!r}, {self.y!r})"

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __rmul__(self, scalar):
        return Vector(scalar * self.x, scalar * self.y)


# Exercise 3: __repr__ vs __str__
# ---------------------------------------------------------------------------
#   repr(Temperature(21.5)) -> 'Temperature(21.5)'   (for developers: unambiguous)
#   str(Temperature(21.5))  -> '21.5°C'              (for end users: friendly)
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f'Temperature({self.celsius})'

    def __str__(self):
        return f'{self.celsius}°C'


# Exercise 4: truthiness without __bool__
# ---------------------------------------------------------------------------
# An Inbox should be falsy when empty and truthy otherwise, so that
# `if inbox:` reads naturally. Implement only __len__ (no __bool__).
class Inbox:
    def __init__(self, messages=()):
        self._messages = list(messages)

    def __len__(self):
        return len(self._messages)
