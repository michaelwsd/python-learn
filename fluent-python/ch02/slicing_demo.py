"""Chapter 2, part 2: slicing, + and *, the += puzzler, sorting, other containers.

Run:  uv run python ch02/slicing_demo.py
"""

from collections import deque


def section(title):
    print(f"\n--- {title} ---")


section("Slicing: [start:stop:step], stop is excluded")
l = [10, 20, 30, 40, 50, 60]
print(l[:2], l[2:])  # split at 2: no overlap, no gap
print(l[::2], l[::-1])  # every other item, reversed
s = "bicycle"
print(s[::3], s[::-2])

section("Slice objects: name your slices (Example 2-13)")
invoice = """
1909  Pimoroni PiBrella                      $17.50    3    $52.50
1489  6mm Tactile Switch x20                  $4.95    2     $9.90
"""
SKU = slice(0, 6)
DESCRIPTION = slice(6, 40)
UNIT_PRICE = slice(40, 52)
for line in invoice.split("\n")[1:-1]:
    print(line[UNIT_PRICE].strip(), "|", line[DESCRIPTION].strip())

section("Assigning to slices (mutable sequences only)")
l = list(range(10))
l[2:5] = [20, 30]  # replace 3 items with 2: the list shrinks
print(l)
del l[5:7]
print(l)
l[3::2] = [11, 22]
print(l)

section("+ and * build NEW sequences")
print([1, 2] + [3], "ab" * 3)

section("Lists of lists: the * trap (Examples 2-14, 2-15)")
good = [["_"] * 3 for _ in range(3)]  # 3 separate row lists
bad = [["_"] * 3] * 3  # 3 references to the SAME row
good[1][2] = "X"
bad[1][2] = "O"
print("good:", good)
print("bad: ", bad)  # every row changed

section("Augmented assignment: += on mutable vs immutable")
l = [1, 2]
t = (1, 2)
print("before:", id(l), id(t))
l += [3]  # list: __iadd__ changes it in place, same object
t += (3,)  # tuple: no __iadd__, so t = t + (3,), a NEW object
print("after: ", id(l), id(t), "(list id same, tuple id changed)")

section("The += puzzler (Example 2-16)")
t = (1, 2, [30, 40])
try:
    t[2] += [50, 60]
except TypeError as e:
    print("TypeError:", e)
print("but t is now:", t)  # the list was extended BEFORE the assignment failed

section("list.sort vs sorted")
fruits = ["grape", "raspberry", "apple", "banana"]
print(sorted(fruits), sorted(fruits, key=len, reverse=True))
print("original untouched:", fruits)
print("fruits.sort() returns:", fruits.sort())  # in-place methods return None
print("now sorted in place:", fruits)

section("When a list is not the answer: deque (Example 2-23)")
dq = deque(range(10), maxlen=10)
dq.rotate(3)
print(dq)
dq.appendleft(-1)  # full: drops an item from the OTHER end
print(dq)
last_three = deque(maxlen=3)
for line in ["a", "b", "c", "d", "e"]:
    last_three.append(line)  # keeps only the newest 3: a tail -n 3
print(list(last_three))
