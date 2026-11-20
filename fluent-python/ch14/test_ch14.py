import inspect
from collections import UserDict

import pytest
from exercises_ch14 import (
    AuthLogService,
    AuthMixin,
    Handler,
    LimitOrder,
    LogAuthService,
    LogMixin,
    Order,
    PriceBook,
    Stack,
    SymbolDict,
    UpperKeyMixin,
)


def body(func):
    """Source of a function without its def line, for checking what it uses."""
    return inspect.getsource(func).split(":", 1)[1]


# Exercise 1 ---------------------------------------------------------------
def test_limit_order():
    o = LimitOrder("aapl", 100, 190.5)
    assert (o.symbol, o.qty, o.price) == ("AAPL", 100, 190.5)
    assert o.notional() == 19050.0
    assert isinstance(o, Order)


def test_limit_order_uses_super():
    src = body(LimitOrder.__init__)
    assert "super().__init__(" in src
    assert "Order" not in src, "don't hardcode the base class: use super()"
    assert "self.symbol" not in src and "self.qty" not in src, "let Order set those"


# Exercise 2 ---------------------------------------------------------------
def test_price_book_accepts_positive_prices():
    book = PriceBook(AAPL=190.5)
    book["MSFT"] = 410.0
    book.update(NVDA=120.0)
    assert dict(book) == {"AAPL": 190.5, "MSFT": 410.0, "NVDA": 120.0}


@pytest.mark.parametrize(
    "store",
    [
        lambda: PriceBook(AAPL=-1),
        lambda: PriceBook().__setitem__("AAPL", 0),
        lambda: PriceBook().update(MSFT=-5),
        lambda: PriceBook([("X", -2)]),
    ],
    ids=["constructor", "setitem", "update", "constructor-pairs"],
)
def test_price_book_rejects_bad_prices(store):
    with pytest.raises(ValueError):
        store()


def test_price_book_overrides_only_setitem():
    assert "__setitem__" in vars(PriceBook)
    extra = {"__init__", "update", "setdefault"} & set(vars(PriceBook))
    assert not extra, (
        f"override only __setitem__, not {extra}: pick a better base class"
    )


# Exercise 3 ---------------------------------------------------------------
def test_services():
    assert AuthLogService().handle("msg") == ["Auth", "Log", "Handler"]
    assert LogAuthService().handle("msg") == ["Log", "Auth", "Handler"]


def test_services_use_the_mro():
    assert AuthLogService.__mro__[1:4] == (AuthMixin, LogMixin, Handler)
    assert LogAuthService.__mro__[1:4] == (LogMixin, AuthMixin, Handler)
    for mixin in (AuthMixin, LogMixin):
        assert Handler not in mixin.__mro__, "a mixin shouldn't inherit from Handler"
        assert "super().handle(" in body(mixin.handle)
    for service in (AuthLogService, LogAuthService):
        assert "handle" not in vars(service), "the service classes need no methods"


# Exercise 4 ---------------------------------------------------------------
def test_symbol_dict():
    d = SymbolDict(aapl=190.5)
    d["Msft"] = 410.0
    assert list(d.keys()) == ["AAPL", "MSFT"]
    assert d["AAPL"] == d["Aapl"] == 190.5
    assert "aApL" in d and "nvda" not in d
    assert d.get("msft") == 410.0
    assert d.get("nvda", 0) == 0


def test_symbol_dict_non_string_keys():
    d = SymbolDict()
    d[1] = "one"
    assert d[1] == "one" and 1 in d and d.get(1) == "one"


def test_symbol_dict_is_a_mixin_plus_user_dict():
    assert SymbolDict.__mro__[1:3] == (UpperKeyMixin, UserDict)
    assert UpperKeyMixin.__bases__ == (object,), "a mixin stands alone: no base class"
    methods = [name for name, value in vars(SymbolDict).items() if callable(value)]
    assert not methods, f"SymbolDict needs no methods of its own, found {methods}"


# Exercise 5 ---------------------------------------------------------------
def test_stack():
    s = Stack()
    assert len(s) == 0 and not s
    s.push(1)
    s.push(2)
    assert len(s) == 2 and s
    assert s.peek() == 2
    assert s.pop() == 2
    assert s.pop() == 1
    assert not s


def test_stack_empty():
    for method in (Stack().pop, Stack().peek):
        with pytest.raises(IndexError, match="empty stack"):
            method()


def test_stack_uses_composition():
    assert Stack.__bases__ == (object,), "don't inherit: hold a list instead"
    s = Stack()
    for name in ("append", "insert", "sort", "remove", "__setitem__", "__getitem__"):
        assert not hasattr(s, name), f"Stack should not offer {name}"
