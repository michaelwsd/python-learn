"""Chapter 2 exercises: an array of sequences.

Replace each `raise NotImplementedError` with your code, then run:

    uv run pytest ch02 -v

Check one exercise at a time with -k, e.g.  uv run pytest ch02 -v -k skus
"""

from collections import deque


# Exercise 1: list comprehensions and generator expressions
# ---------------------------------------------------------------------------
# skus(["black", "white"], ["S", "M"]) -> ["black-S", "black-M", "white-S", "white-M"]
# Use ONE list comprehension with two `for` clauses.
def skus(colors, sizes):
    return [f'{color}-{size}' for color in colors for size in sizes]


# total_length(["ab", "cde"]) -> 5
# Use a generator expression (no list built in memory). It must also work
# when `words` is a one-pass iterator, like a generator.
def total_length(words):
    return sum(len(word) for word in words)


# Exercise 2: unpacking with *
# ---------------------------------------------------------------------------
# split_ends("hello")     -> ("h", ["e", "l", "l"], "o")
# split_ends((1, 2))      -> (1, [], 2)
# split_ends(range(5))    -> (0, [1, 2, 3], 4)
# One unpacking assignment, no indexing or slicing.
def split_ends(seq):
    first, *middle, last = seq 
    return first, middle, last


# Exercise 3: pattern matching on sequences
# ---------------------------------------------------------------------------
# Use one `match` statement. Patterns are tried top to bottom, so order matters.
#   ["go", direction]       -> "go north"          (for direction "north")
#   ["go"]                  -> "go where?"
#   ["pick", "up", item]    -> "picked up lamp"
#   ["drop"]                -> "drop what?"
#   ["drop", *items]        -> "dropped 2 items"   (any number >= 1)
#   ["move", x, y] where x and y are both ints -> "moved to (3, 4)"
#                              hint: the pattern int(x) matches only ints
#   anything else, including the plain string "go north" -> "unknown command"
def run(command):
    match command:
        case ["go", direction]:
            return "go north"
        case ["go"]:
            return "go where?"
        case ["pick", "up", item]:
            return f"picked up {item}"
        case ["drop"]:
            return "drop what?"
        case ["drop", *items]:
            return f"dropped {len(items)} items"
        case ["move", int(x), int(y)]:
            return f"moved to ({x}, {y})"
        case _:
            return "unknown command"


# Exercise 4: named slices for fixed-width data
# ---------------------------------------------------------------------------
# Each line has fixed-width columns:
#   symbol: characters 0-5, side: 6-11, quantity: 12-17, price: 18 to the end
#   "AAPL  BUY   100   189.50" -> ("AAPL", "BUY", 100, 189.5)
# Define module-level slice objects (SYMBOL = slice(...), ...) and use them,
# then strip spaces and convert quantity to int and price to float.
TRADE_LINES = [
    "AAPL  BUY   100   189.50",
    "MSFT  SELL  25    411.20",
    "NVDA  BUY   7     118.03",
]

SYMBOL = slice(0, 5)
SIDE = slice(6, 11)
QTY = slice(12, 17)
PRICE = slice(18, None)

def parse_trade(line):
    return (line[SYMBOL].strip(), line[SIDE].strip(), int(line[QTY]), float(line[PRICE]))


# Exercise 5: building a grid without the * trap
# ---------------------------------------------------------------------------
# make_grid(2, 3) -> [["_", "_", "_"], ["_", "_", "_"]]
# Changing one cell must change ONLY that cell.
def make_grid(rows, cols, fill="_"):
    return [[fill] * cols for _ in range(rows)]


# Exercise 6: sorted with a key
# ---------------------------------------------------------------------------
# top_n(words, n) -> the n longest words; ties broken alphabetically.
# top_n(["kiwi", "fig", "banana", "apple", "date"], 3) -> ["banana", "apple", "date"]
# Must NOT change the caller's list.
def top_n(words, n):
    return sorted(words, key=lambda x: (-len(x), x))[:n]


# Exercise 7: when a list is not the answer
# ---------------------------------------------------------------------------
# tail(lines, n) -> a list of the last n lines, like `tail -n` on a log.
# `lines` may be a huge generator, so don't build a full list of it:
# keep only n lines in memory at any time (hint: deque has a maxlen).
def tail(lines, n):
    from collections import deque 
    return list(deque(lines, maxlen=n))