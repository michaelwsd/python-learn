"""Chapter 14 exercises: inheritance, for better or for worse.

Replace each `raise NotImplementedError` with your code (and fill in the base
classes where a comment asks), then run:

    uv run pytest ch14 -v

Check one exercise at a time with -k, e.g.  uv run pytest ch14 -v -k symbol
"""

from collections import UserDict  # noqa: F401  (you may need it)


# Exercise 1: super() in __init__
# ---------------------------------------------------------------------------
# Order stores symbol and qty. LimitOrder adds a price.
# Write LimitOrder.__init__ so that Order does its part of the setup.
# Don't copy Order's assignments, and don't name Order inside the method.
#   o = LimitOrder("aapl", 100, 190.5)
#   o.symbol, o.qty, o.price -> ("AAPL", 100, 190.5)
#   o.notional() -> 19050.0
class Order:
    def __init__(self, symbol, qty):
        self.symbol = symbol.upper()
        self.qty = qty


class LimitOrder(Order):
    def __init__(self, symbol, qty, price):
        raise NotImplementedError

    def notional(self):
        return self.qty * self.price


# Exercise 2: subclass the right base class
# ---------------------------------------------------------------------------
# PriceBook maps symbol -> price, and every price must be > 0.
# Raise ValueError for a price <= 0, however it is stored:
#   PriceBook(AAPL=-1)          -> ValueError  (constructor)
#   book["AAPL"] = 0            -> ValueError  ([] assignment)
#   book.update(MSFT=-5)        -> ValueError  (update)
# Override ONLY __setitem__. Choose the base class so that the constructor
# and update() go through your __setitem__ without overriding them.
class PriceBook(dict):  # <- is this the right base class?
    def __setitem__(self, key, value):
        raise NotImplementedError


# Exercise 3: cooperative multiple inheritance and the MRO
# ---------------------------------------------------------------------------
# Handler.handle returns ["Handler"]. Write AuthMixin.handle and
# LogMixin.handle so each returns its own name in front of whatever the NEXT
# class in the MRO returns:
#   AuthLogService().handle("msg") -> ["Auth", "Log", "Handler"]
#   LogAuthService().handle("msg") -> ["Log", "Auth", "Handler"]
# Then add the base classes of the two service classes so
# their MROs produce those results. The service classes need no methods.
class Handler:
    def handle(self, msg):
        return ["Handler"]


class AuthMixin:
    def handle(self, msg):
        raise NotImplementedError


class LogMixin:
    def handle(self, msg):
        raise NotImplementedError


class AuthLogService:  # <- add the base classes
    """Auth, then Log, then Handler"""


class LogAuthService:  # <- add the base classes
    """Log, then Auth, then Handler"""


# Exercise 4: write a mixin
# ---------------------------------------------------------------------------
# UpperKeyMixin makes string keys case-insensitive by uppercasing them before
# passing them on with super(). Non-string keys pass through unchanged
# (the _upper helper below does that part for you).
# It must handle: d[k] = v, d[k], k in d, d.get(k, default).
# Then define SymbolDict by combining the mixin with UserDict (body: just the
# docstring). Mind the order of the bases.
#   d = SymbolDict(aapl=190.5)
#   d["AAPL"], d["Aapl"], "aApL" in d, d.get("msft", 0) -> 190.5, 190.5, True, 0
def _upper(key):
    try:
        return key.upper()
    except AttributeError:
        return key


class UpperKeyMixin:
    def __setitem__(self, key, value):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError


class SymbolDict:  # <- add the base classes
    """Case-insensitive symbol -> value mapping"""


# Exercise 5: favor composition over inheritance
# ---------------------------------------------------------------------------
# This Stack inherits from list, so callers also get insert, sort, remove,
# [] assignment... all of which break the stack's last-in-first-out rule:
#
#     class Stack(list):
#         def push(self, item):
#             self.append(item)
#
# Rewrite it WITHOUT inheritance: Stack holds a list and delegates to it.
# It offers only: push(item), pop(), peek(), len(stack), and bool(stack).
# pop() and peek() on an empty stack raise IndexError("empty stack").
class Stack:
    def __init__(self):
        raise NotImplementedError

    def push(self, item):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def peek(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError
