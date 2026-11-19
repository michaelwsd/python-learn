"""Chapter 6: object references, mutability, and recycling.

Run:  uv run python ch06/references_demo.py
"""

import copy
import weakref


def section(title):
    print(f"\n--- {title} ---")


section("Variables are labels, not boxes (Example 6-1)")
a = [1, 2, 3]
b = a  # b is a second label on the SAME list, not a copy
a.append(4)
print("b:", b)


class Gizmo:
    def __init__(self):
        print(f"Gizmo id: {id(self)}")


section("The right-hand side runs first (Example 6-2)")
x = Gizmo()
try:
    y = Gizmo() * 10  # a Gizmo is created, then * fails, so y is never bound
except TypeError as e:
    print("TypeError:", e)
print("'y' in globals():", "y" in globals())

section("Identity, equality, aliases (Examples 6-3, 6-4)")
charles = {"name": "Charles L. Dodgson", "born": 1832}
lewis = charles  # alias
alex = {"name": "Charles L. Dodgson", "born": 1832}  # equal value, different object
print("lewis is charles:", lewis is charles, "| id equal:", id(lewis) == id(charles))
print("alex == charles:", alex == charles, "| alex is charles:", alex is charles)
END_OF_DATA = object()  # a sentinel: compare with `is`
print("x is None:", x is None, "| END_OF_DATA is END_OF_DATA:", END_OF_DATA is END_OF_DATA)

section("Relative immutability of tuples (Example 6-5)")
t1 = (1, 2, [30, 40])
t2 = (1, 2, [30, 40])
print("t1 == t2:", t1 == t2)
t1[-1].append(99)  # the tuple holds the same list; the list itself changed
print("t1:", t1, "| t1 == t2:", t1 == t2)

section("Copies are shallow by default (Example 6-6)")
l1 = [3, [66, 55, 44], (7, 8, 9)]
l2 = list(l1)  # new outer list, SAME inner objects
l1.append(100)
l1[1].remove(55)  # inner list is shared: l2 sees this
print("l1:", l1)
print("l2:", l2)
l2[1] += [33, 22]  # list += mutates in place: l1 sees this
l2[2] += (10, 11)  # tuple += builds a new tuple: only l2 changes
print("l1:", l1)
print("l2:", l2)


class Bus:
    def __init__(self, passengers=None):
        self.passengers = [] if passengers is None else list(passengers)

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        self.passengers.remove(name)


section("copy vs deepcopy (Example 6-9)")
bus1 = Bus(["Alice", "Bill", "Claire", "David"])
bus2 = copy.copy(bus1)  # shallow: shares the passengers list
bus3 = copy.deepcopy(bus1)  # deep: its own passengers list
bus1.drop("Bill")
print("bus2:", bus2.passengers)
print("bus3:", bus3.passengers)
a = [10, 20]
b = [a, 30]
a.append(b)  # a cycle: a contains b, b contains a
c = copy.deepcopy(a)  # deepcopy handles cycles
print("deepcopy of a cycle:", c)

section("Function parameters are references (Example 6-11)")


def f(a, b):
    a += b  # list: mutates the caller's object; int/tuple: rebinds locally
    return a


for x_, y_ in [(1, 2), ([1, 2], [3, 4]), ((10, 20), (30, 40))]:
    f(x_, y_)
    print("after f:", x_)


class HauntedBus:
    def __init__(self, passengers=[]):  # BAD: one list, created once, shared
        self.passengers = passengers

    def pick(self, name):
        self.passengers.append(name)


section("Mutable default argument trap (Example 6-13)")
bus_a = HauntedBus()
bus_a.pick("Carrie")
bus_b = HauntedBus()  # gets the SAME default list
print("bus_b.passengers:", bus_b.passengers)
print("default list:", HauntedBus.__init__.__defaults__)


class TwilightBus:
    def __init__(self, passengers=None):
        self.passengers = [] if passengers is None else passengers  # BAD: alias

    def drop(self, name):
        self.passengers.remove(name)


section("Mutating an argument by aliasing it (Example 6-14)")
basketball_team = ["Sue", "Tina", "Maya", "Diana", "Pat"]
bus = TwilightBus(basketball_team)
bus.drop("Tina")
print("team after a passenger left the bus:", basketball_team)

section("del deletes names, not objects (Example 6-16)")
s1 = {1, 2, 3}
s2 = s1
ender = weakref.finalize(s1, lambda: print("...object destroyed"))
del s1  # only the name s1 is gone; s2 still refers to the set
print("alive after del s1:", ender.alive)
s2 = "spam"  # last reference gone: the set is destroyed now
print("alive after rebinding s2:", ender.alive)

section("Tricks with immutables (Examples 6-17, 6-18)")
t = (1, 2, 3)
print("tuple(t) is t:", tuple(t) is t, "| t[:] is t:", t[:] is t)
s = "ABC"
print("s[:] is s:", s[:] is s)
n1, n2 = 256, 256
print("small ints are cached:", n1 is n2, "| but never rely on it: compare with ==")
