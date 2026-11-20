"""Chapter 8: mistakes that only a type checker catches.

This file runs without type errors at runtime up to the first bad call, but every
line marked ERROR is reported by mypy before the code ever runs:

    uv run mypy ch08/mypy_demo.py
    uv run mypy --strict ch08/mypy_demo.py   # also flags the unannotated function
"""

from collections.abc import Callable, Sequence
from typing import Any, Protocol, TypeVar


class Bird:
    pass


class Duck(Bird):
    def quack(self) -> None:
        print("Quack!")


def alert_bird(birdie: Bird) -> None:
    birdie.quack()  # ERROR: "Bird" has no attribute "quack" (nominal typing)


alert_bird(Duck())  # fine: a Duck is a Bird
woody = Bird()


def alert_duck(birdie: Duck) -> None:
    birdie.quack()


alert_duck(woody)  # ERROR: a Bird is not a Duck


def double_seq(x: Sequence[int]) -> Any:
    return x * 2  # ERROR: Sequence declares no __mul__ (types = supported operations)


def double_obj(x: object) -> object:
    return x * 2  # ERROR: object supports almost nothing; Any would allow everything


def hex2rgb(color=str) -> tuple[int, int, int]:  # ERROR in --strict: `=` instead of `:`
    return (0, 0, 0)


def show_count(count: int, word: str) -> str:
    return f"{count} {word}s"


show_count(3, "mouse", "mice")  # ERROR: too many arguments
show_count("3", "bird")  # ERROR: "3" is a str, not an int


def update(probe: Callable[[], float], display: Callable[[float], None]) -> None:
    display(probe())


def probe_ok() -> int:
    return 42


def display_wrong(temperature: int) -> None:
    print(hex(temperature))


update(
    probe_ok, display_wrong
)  # ERROR: display may receive a float, hex() needs an int


class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...


LT = TypeVar("LT", bound=SupportsLessThan)


def top(series: list[LT], length: int) -> list[LT]:  # noqa: UP047
    return sorted(series, reverse=True)[:length]


top([object(), object()], 1)  # ERROR: object has no __lt__
