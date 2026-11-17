"""Example 1-2: a 2D vector that works with +, *, abs(), bool() and repr().

Run:  uv run python ch01/vector2d.py
"""

import math


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):  # used by the console, repr(), and inside containers
        return f"Vector({self.x!r}, {self.y!r})"  # !r: repr of each field

    def __abs__(self):  # abs(v) -> magnitude
        return math.hypot(self.x, self.y)

    def __bool__(self):  # bool(v), `if v:` -> False only for Vector(0, 0)
        return bool(abs(self))

    def __add__(self, other):  # v1 + v2 -> a NEW vector; operands unchanged
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):  # v * 3 (but not 3 * v: that needs __rmul__)
        return Vector(self.x * scalar, self.y * scalar)


if __name__ == "__main__":
    v1, v2 = Vector(2, 4), Vector(2, 1)
    print("v1 + v2         ", v1 + v2)  # __add__
    v = Vector(3, 4)
    print("abs(v)          ", abs(v))  # __abs__
    print("v * 3           ", v * 3)  # __mul__
    print("abs(v * 3)      ", abs(v * 3))
    print("bool(Vector())  ", bool(Vector()))  # __bool__
    print("[v1, v2]        ", [v1, v2])  # containers show items with __repr__
