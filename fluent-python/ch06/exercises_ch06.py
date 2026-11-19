"""Chapter 6 exercises: object references, mutability, and recycling.

Replace each `raise NotImplementedError` with your code, then run:

    uv run pytest ch06 -v

Check one exercise at a time with -k, e.g.  uv run pytest ch06 -v -k classify
"""

import copy


# Exercise 1: identity vs equality
# ---------------------------------------------------------------------------
# classify(a, b) -> "same object" if a and b are the same object,
#                   "equal" if they are different objects with equal values,
#                   "different" otherwise.
def classify(a, b):
    if a is b:
        return "same object"
    elif a == b:
        return "equal"
    else:
        return "different"


# count_distinct(items) -> how many DIFFERENT OBJECTS are in items (not values).
#   x = [1]; y = [1]
#   count_distinct([x, x, y]) -> 2   (x and y are equal, but two objects)
# Hint: id() gives each live object a unique number.
def count_distinct(items):
    return len(set(id(item) for item in items))


# Exercise 2: shallow copies share inner objects
# ---------------------------------------------------------------------------
# clone_grid(grid) -> a copy of a list of lists where changing a cell in the
# copy never changes the original. Don't use the copy module.
#   g = [[1, 2], [3, 4]];  c = clone_grid(g);  c[0][0] = 99  ->  g unchanged
def clone_grid(grid):
    return [g[:] for g in grid]


# Exercise 3: deep copies
# ---------------------------------------------------------------------------
# snapshot(config) -> a fully independent copy of a nested structure
# (dicts of lists of dicts, any depth). Later changes to the original, at any
# level, must not show up in the snapshot.
def snapshot(config):
    return copy.deepcopy(config)


# Exercise 4: the mutable default argument trap
# ---------------------------------------------------------------------------
# append_to(item, target=...) -> target with item appended. When no target is
# given, start from a NEW empty list every call:
#   append_to(1) -> [1];  append_to(2) -> [2]   (not [1, 2])
#   lst = ["a"];  append_to("b", lst) -> ["a", "b"] and lst is changed
# Fix the signature too: a mutable default is the bug.
def append_to(item, target=None):
    if not target:
        return [item]
    target.append(item)
    return target


# Exercise 5: defensive copies of arguments
# ---------------------------------------------------------------------------
# A Playlist keeps its own list of songs. Like the book's fixed Bus:
#   - Playlist() starts empty; two empty playlists don't share a list
#   - Playlist(songs) accepts ANY iterable (list, tuple, generator, ...)
#   - add() and remove() must never change the caller's original object
class Playlist:
    def __init__(self, songs=None):
        self.songs = [] if not songs else list(songs)

    def add(self, song):
        self.songs.append(song)

    def remove(self, song):
        self.songs.remove(song)


# Exercise 6: functions receive references
# ---------------------------------------------------------------------------
# doubled(nums) -> a NEW list with every number doubled; nums is unchanged.
def doubled(nums):
    return list(map(lambda x: 2 * x, nums[:]))


# double_in_place(nums) -> double every number IN the given list and return
# None (the convention for functions that change their argument, like
# list.sort). The caller's list object must be the one that changes.
def double_in_place(nums):
    for i in range(len(nums)): nums[i] *= 2
    return None


# Exercise 7: a sentinel compared with `is`
# ---------------------------------------------------------------------------
# get_setting(settings, key, default=...) ->
#   settings[key] if the key exists (even if its value is None)
#   default if the key is missing and a default was passed (even default=None)
#   raise KeyError(key) if the key is missing and NO default was passed
# None can't mark "no default given", because None is a valid default.
# Create a module-level sentinel with object() and test it with `is`.
_MISSING = object()       # a brand-new, unique object, equal to nothing else

def get_setting(settings, key, default=_MISSING):
    if key in settings:
        return settings[key]          # key exists: return its value, even if None
    if default is _MISSING:           # was the default left out?
        raise KeyError(key)
    return default                    # a default was given (possibly None)
