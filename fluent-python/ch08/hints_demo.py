"""Chapter 8: type hints in functions.

Run:  uv run python ch08/hints_demo.py
Then: uv run mypy ch08/mypy_demo.py   (to see what a type checker catches)
"""

from collections import Counter
from collections.abc import Callable, Hashable, Iterable, Iterator, Sequence
from random import shuffle
from typing import Any, NoReturn, Protocol, TypeVar


def section(title: str) -> None:
    print(f"\n--- {title} ---")


section("Gradual typing: hints are not checked at runtime (Example 8-3)")


def show_count(count: int, singular: str, plural: str | None = None) -> str:
    if count == 1:
        return f"1 {singular}"
    count_str = str(count) if count else "no"
    if not plural:
        plural = singular + "s"
    return f"{count_str} {plural}"


print(show_count(99, "bird"), "|", show_count(1, "bird"), "|", show_count(3, "mouse", "mice"))
print("hints are just stored:", show_count.__annotations__)
print("no runtime check:", show_count("lots", "bird"))  # type: ignore[arg-type]  # mypy rejects, Python runs it


section("Duck typing vs nominal typing (Examples 8-4 to 8-7)")


class Bird:
    pass


class Duck(Bird):
    def quack(self) -> None:
        print("Quack!")


def alert(birdie):  # no hints: mypy skips this function
    birdie.quack()


def alert_duck(birdie: Duck) -> None:
    birdie.quack()


alert(Duck())
alert_duck(Duck())
try:
    alert(Bird())  # duck typing: fails only when .quack() is attempted
except AttributeError as e:
    print("AttributeError:", e)


section("Optional / Union (str | None)")


def parse_token(token: str) -> str | float:
    try:
        return float(token)
    except ValueError:
        return token


print(parse_token("1.5"), parse_token("x"))

section("Generic collections, tuples (Examples 8-8, 8-13)")


def tokenize(text: str) -> list[str]:
    return text.upper().split()


def columnize(sequence: Sequence[str], num_columns: int = 0) -> list[tuple[str, ...]]:
    if num_columns == 0:
        num_columns = round(len(sequence) ** 0.5)
    num_rows, reminder = divmod(len(sequence), num_columns)
    num_rows += bool(reminder)
    return [tuple(sequence[i::num_rows]) for i in range(num_rows)]


print(tokenize("mad skilled noob"))
print(columnize(["drake", "fawn", "heron", "ibex", "koala", "lynx", "tahr", "xerus", "yak", "zapus"]))

section("Iterable parameter, type alias (Example 8-15)")
FromTo = tuple[str, str]


def zip_replace(text: str, changes: Iterable[FromTo]) -> str:
    for from_, to in changes:
        text = text.replace(from_, to)
    return text


l33t = [("a", "4"), ("e", "3"), ("i", "1"), ("o", "0")]
print(zip_replace("mad skilled noob powned leet", l33t))
print(zip_replace("leet", (pair for pair in l33t)))  # a generator is Iterable too


def name_words(names: Iterable[str]) -> Iterator[str]:  # returns a generator
    for name in names:
        yield from name.upper().split()


print(list(name_words(["digit eight", "plus sign"])))

section("TypeVar: the return type follows the input (Example 8-16)")
T = TypeVar("T")


def sample(population: Sequence[T], size: int) -> list[T]:  # noqa: UP047  book style
    if size < 1:
        raise ValueError("size must be >= 1")
    result = list(population)
    shuffle(result)
    return result[:size]


print(sample([10, 20, 30], 2), sample("abc", 2))  # list[int], then list[str]


# Python 3.12+ syntax: declare the type parameter in [] instead of with TypeVar
def sample_312[U](population: Sequence[U], size: int) -> list[U]:
    return sample(population, size)


print(sample_312((1.5, 2.5), 1))  # list[float]

section("Bounded TypeVar (Example 8-18)")
HashableT = TypeVar("HashableT", bound=Hashable)


def mode(data: Iterable[HashableT]) -> HashableT:  # noqa: UP047
    pairs = Counter(data).most_common(1)
    if len(pairs) == 0:
        raise ValueError("no mode for empty data")
    return pairs[0][0]


print(mode([1, 1, 2, 3, 3, 3, 3, 4]), mode(["red", "blue", "red"]))

section("Protocol: static duck typing (Examples 8-20, 8-21)")


class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...


LT = TypeVar("LT", bound=SupportsLessThan)


def top(series: Iterable[LT], length: int) -> list[LT]:  # noqa: UP047
    return sorted(series, reverse=True)[:length]


print(top([4, 1, 5, 2, 6, 7, 3], 3), top(["mango", "pear", "apple", "kiwi"], 2))

section("Callable (Example 8-24)")


def update(probe: Callable[[], float], display: Callable[[float], None]) -> None:
    display(probe())


def probe_ok() -> int:  # returning int where float is expected: fine
    return 42


def display_ok(temperature: complex) -> None:  # accepts more than float: fine
    print("temperature:", temperature)


update(probe_ok, display_ok)

section("Variadic parameters and NoReturn")


def tag(name: str, /, *content: str, class_: str | None = None, **attrs: str) -> str:
    # inside: content is tuple[str, ...], attrs is dict[str, str]
    if class_ is not None:
        attrs["class"] = class_
    attr_str = "".join(f' {k}="{v}"' for k, v in sorted(attrs.items()))
    return f"<{name}{attr_str}>{''.join(content)}</{name}>"


print(tag("p", "hello", class_="intro", id="a1"))


def fail(msg: str) -> NoReturn:  # never returns: always raises
    raise ValueError(msg)


try:
    fail("boom")
except ValueError as e:
    print("ValueError:", e)
