# Fluent Python (2nd edition): study roadmap

Chapters 1, 2, 3, 6, 7, 8 and 14, about 250 pages. Page numbers are the book's; PDF pages in brackets.

## How each chapter works

1. **Setup:** a plain explanation of the key ideas, plus the book's main examples as runnable demos in `chNN/`.
2. **Read** the chapter alongside it.
3. **Exercises:** fill in `chNN/exercises_chNN.py` until `uv run pytest chNN` passes.
4. **Review and quiz:** code review, then a short quiz in your own words.

```bash
cd fluent-python
uv run python ch01/frenchdeck.py   # run a demo
uv run pytest ch01 -v              # check your exercises
```

## Roadmap

| # | Chapter | Pages | Key ideas | Exercises practise |
|---|---|---|---|---|
| 1 | The Python Data Model | 3-20 (PDF 33-50) | Special methods, `__repr__` vs `__str__`, truthiness, the Collection API, why `len()` is a function | Making classes work with `len`, `[]`, `in`, operators, `repr` |
| 2 | An Array of Sequences | 21-76 (PDF 51-106) | Container vs flat, mutable vs immutable sequences; listcomps and genexps; tuples as records; unpacking (`*rest`); `match` on sequences; slicing; `+=` traps; `sort` vs `sorted`; `array`, `deque`, `memoryview` | Comprehensions, unpacking, slicing, picking the right container |
| 3 | Dictionaries and Sets | 77-116 (PDF 107-146) | Dict comprehensions, merging with `\|`, `match` on mappings, hashability, `setdefault`, `defaultdict`, `__missing__`, `Counter`, `ChainMap`, read-only mappings, dict views, set operations, why lookups are fast | Grouping and counting, a custom mapping with `__missing__`, set algebra |
| 6 | Object References, Mutability, and Recycling | 201-230 (PDF 231-260) | Variables are labels; `is` vs `==`; shallow vs deep copy; call by sharing; the mutable default argument trap | Spotting and fixing aliasing and copy bugs |
| 7 | Functions as First-Class Objects | 231-252 (PDF 261-282) | Higher-order functions, `lambda`, the 9 kinds of callables, `__call__`, keyword-only and positional-only parameters, `operator`, `functools.partial` | Callables, `key=` functions, parameter rules |
| 8 | Type Hints in Functions | 253-302 (PDF 283-332) | Gradual typing, mypy, duck vs nominal typing, `Any`, `Optional`/`Union`, generics, `TypeVar`, `Protocol`, `Callable`, `NoReturn` | Adding hints and passing `mypy --strict` |
| 14 | Inheritance: For Better or for Worse | 487-518 (PDF 517-548) | `super()`, subclassing built-ins (use `UserDict`), multiple inheritance and MRO, mixins, composition over inheritance | Cooperative `super()`, a mixin, refactoring to composition |

**Order:** 1 → 2 → 3 cover the core data structures. 6 → 7 explain how names and objects behave before treating functions as objects. 8 adds type hints on top. 14 comes last because it builds on everything before it.

**Skipped chapter you'll see mentioned:** Ch 9 (decorators). The basics are covered in `docs/imc-notes.pdf`.

**Effort:** about 15-20 hours in total. Ch 2 and Ch 8 are the longest. A mixed checkpoint across all chapters comes at the end.

## Extension (if time)

Same four-step format, after the core chapters above.

| # | Chapter | Pages | Key ideas | Exercises practise |
|---|---|---|---|---|
| 5 | Data Class Builders | 163-200 (PDF 193-230) | `namedtuple` vs `typing.NamedTuple` vs `@dataclass`; `field()` and mutable defaults; `__post_init__`; `frozen=True`; `ClassVar` and `InitVar`; data classes as a code smell; `match` on class instances | Turning hand-written classes into data classes, validation in `__post_init__` |
| 13 | Interfaces, Protocols, and ABCs | 431-486 (PDF 461-516) | The four kinds of typing (duck, goose, static, static duck); monkey patching; the stdlib ABCs; writing and subclassing an ABC; virtual subclasses with `register`; `typing.Protocol` and `@runtime_checkable` | Writing an ABC, a `Protocol` that mypy checks, choosing between them |
| 17 | Iterators, Generators, and Classic Coroutines | 593-656 (PDF 623-686) | Iterable vs iterator; how `iter()` works; generator functions and lazy evaluation; generator expressions; `itertools`; `yield from`; `Iterator`/`Generator` hints; classic coroutines (skim) | A custom iterator, rewriting it as a generator, lazy pipelines over a log file |
| 18 | with, match, and else Blocks | 657-694 (PDF 687-724) | Context managers (`__enter__`/`__exit__`, exceptions in `__exit__`); `contextlib` (`@contextmanager`, `suppress`, `ExitStack`); `match` in depth; `else` on `for`, `while` and `try` | A timer context manager both ways, cleanup with `ExitStack`, `for`/`else` searches |

**Order:** 5 first, since it builds on Ch 8's type hints. 13 then joins Ch 8's `Protocol` with Ch 14's ABCs. 17 comes before 18 because `@contextmanager` is built on generators.

**If time is short:** do 17 and 18 first (make 18's `@contextmanager` part optional). Generators and context managers come up constantly in reliability code: streaming logs, and cleaning up connections and locks.

**Effort:** about 12-15 hours more. Ch 17 is the longest; the classic coroutines section can be skimmed, because modern code uses `async`/`await` instead.