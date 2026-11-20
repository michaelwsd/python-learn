import inspect
import subprocess
import sys
from pathlib import Path
from typing import NoReturn, get_type_hints

import exercises_ch08
import pytest
import typecheck_ch08
from exercises_ch08 import (
    best_symbol,
    fail,
    first,
    largest,
    make_url,
    midpoint,
    parse_side,
    show_count,
    word_lengths,
)

HERE = Path(__file__).parent


@pytest.fixture(scope="module")
def mypy_errors():
    """Run mypy --strict once; return its error lines as (file, line, message)."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--no-error-summary",
            "exercises_ch08.py",
            "typecheck_ch08.py",
        ],
        cwd=HERE,
        capture_output=True,
        text=True,
        check=False,
    )
    errors = []
    for line in result.stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) == 4 and parts[2].strip() == "error":
            errors.append((parts[0], int(parts[1]), line))
    return errors


def errors_in(mypy_errors, *objs):
    """mypy errors whose line falls inside the source of the given functions/classes."""
    found = []
    for obj in objs:
        lines, start = inspect.getsourcelines(obj)
        file = Path(inspect.getsourcefile(obj)).name
        found += [
            msg
            for f, n, msg in mypy_errors
            if f == file and start <= n < start + len(lines)
        ]
    return found


def assert_typed(mypy_errors, *objs):
    errors = errors_in(mypy_errors, *objs)
    assert not errors, "mypy --strict errors:\n" + "\n".join(errors)


# Exercise 1 ---------------------------------------------------------------
def test_show_count():
    assert show_count(1, "bird") == "1 bird"
    assert show_count(0, "bird") == "no birds"
    assert show_count(3, "mouse", "mice") == "3 mice"


def test_show_count_hints(mypy_errors):
    assert_typed(mypy_errors, show_count, typecheck_ch08.check_ex1)
    assert get_type_hints(show_count)["plural"] == str | None


# Exercise 2 ---------------------------------------------------------------
def test_word_lengths():
    assert word_lengths(["ab", "c"]) == {"ab": 2, "c": 1}
    assert word_lengths(w for w in ["xyz"]) == {"xyz": 3}


def test_word_lengths_hints(mypy_errors):
    assert_typed(mypy_errors, word_lengths, typecheck_ch08.check_ex2)


# Exercise 3 ---------------------------------------------------------------
def test_midpoint():
    assert midpoint((0.0, 0.0), (2.0, 4.0)) == (1.0, 2.0)


def test_midpoint_hints(mypy_errors):
    assert_typed(mypy_errors, midpoint, typecheck_ch08.check_ex3)


# Exercise 4 ---------------------------------------------------------------
def test_first():
    assert first([7, 8]) == 7
    assert first("xy") == "x"
    with pytest.raises(ValueError):
        first([])


def test_first_hints(mypy_errors):
    assert_typed(mypy_errors, first, typecheck_ch08.check_ex4)


# Exercise 5 ---------------------------------------------------------------
def test_largest():
    assert largest([3, 9, 2]) == 9
    assert largest(["pear", "apple"]) == "pear"
    assert largest(x for x in [1.5, 0.5]) == 1.5


def test_largest_hints(mypy_errors):
    assert_typed(mypy_errors, largest, typecheck_ch08.check_ex5)


# Exercise 6 ---------------------------------------------------------------
PRICES = {"AAPL": 190.0, "MSFT": 410.0, "NVDA": 120.0}


def test_best_symbol():
    assert best_symbol(PRICES, lambda a, b: a < b) == "NVDA"
    assert best_symbol(PRICES, lambda a, b: a > b) == "MSFT"
    with pytest.raises(ValueError):
        best_symbol({}, lambda a, b: a < b)


def test_best_symbol_hints(mypy_errors):
    assert_typed(mypy_errors, best_symbol, typecheck_ch08.check_ex6)


# Exercise 7 ---------------------------------------------------------------
def test_make_url():
    assert make_url("https://x.com") == "https://x.com"
    assert make_url("https://x.com", "api", "v1") == "https://x.com/api/v1"
    assert (
        make_url("https://x.com", "q", page="2", sort="asc")
        == "https://x.com/q?page=2&sort=asc"
    )


def test_make_url_base_is_positional_only():
    assert make_url("https://x.com", "a") == "https://x.com/a"  # the valid call works
    with pytest.raises(TypeError):
        make_url(base="https://x.com")


def test_make_url_hints(mypy_errors):
    assert_typed(mypy_errors, make_url, typecheck_ch08.check_ex7)


# Exercise 8 ---------------------------------------------------------------
def test_parse_side():
    assert parse_side("buy") == "BUY"
    assert parse_side(" Sell ") == "SELL"
    with pytest.raises(ValueError, match="unknown side"):
        parse_side("hold")


def test_fail_and_parse_side_hints(mypy_errors):
    with pytest.raises(ValueError, match="boom"):
        fail("boom")
    assert get_type_hints(fail)["return"] is NoReturn
    assert "fail(" in inspect.getsource(parse_side)
    assert_typed(mypy_errors, fail, parse_side, typecheck_ch08.check_ex8)


# Everything ---------------------------------------------------------------
def test_whole_file_passes_mypy_strict(mypy_errors):
    assert not mypy_errors, "\n".join(msg for _, _, msg in mypy_errors)
    assert exercises_ch08.__doc__  # keep the module docstring
