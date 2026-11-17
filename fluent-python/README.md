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

**Skipped chapters you'll see mentioned:**
- Ch 5 (data classes) is used in Ch 8's examples.
- Ch 9 (decorators): the basics are covered in `docs/imc-notes.pdf`.
- Ch 13 (protocols and ABCs) overlaps with Ch 8 and 14.

**Effort:** about 15-20 hours in total. Ch 2 and Ch 8 are the longest. A mixed checkpoint across all chapters comes at the end.

## Progress

- [ ] Ch 1: The Python Data Model (set up: `ch01/`)
- [ ] Ch 2: An Array of Sequences
- [ ] Ch 3: Dictionaries and Sets
- [ ] Ch 6: Object References, Mutability, and Recycling
- [ ] Ch 7: Functions as First-Class Objects
- [ ] Ch 8: Type Hints in Functions
- [ ] Ch 14: Inheritance: For Better or for Worse
- [ ] Final checkpoint
