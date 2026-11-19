import tracemalloc

from exercises_ch02 import (
    TRADE_LINES,
    make_grid,
    parse_trade,
    run,
    skus,
    split_ends,
    tail,
    top_n,
    total_length,
)


# Exercise 1 ---------------------------------------------------------------
def test_skus():
    assert skus(["black", "white"], ["S", "M"]) == ["black-S", "black-M", "white-S", "white-M"]
    assert skus([], ["S"]) == []


def test_total_length_with_list_and_generator():
    assert total_length(["ab", "cde"]) == 5
    assert total_length(w for w in ["x", "yy", "zzz"]) == 6


# Exercise 2 ---------------------------------------------------------------
def test_split_ends():
    assert split_ends("hello") == ("h", ["e", "l", "l"], "o")
    assert split_ends((1, 2)) == (1, [], 2)
    assert split_ends(range(5)) == (0, [1, 2, 3], 4)


# Exercise 3 ---------------------------------------------------------------
def test_run_go():
    assert run(["go", "north"]) == "go north"
    assert run(["go", "west"]) == "go west"
    assert run(["go"]) == "go where?"


def test_run_pick_and_drop():
    assert run(["pick", "up", "lamp"]) == "picked up lamp"
    assert run(["drop"]) == "drop what?"
    assert run(["drop", "key"]) == "dropped 1 items"
    assert run(["drop", "key", "map"]) == "dropped 2 items"


def test_run_move_needs_ints():
    assert run(["move", 3, 4]) == "moved to (3, 4)"
    assert run(["move", "3", "4"]) == "unknown command"


def test_run_unknown():
    assert run(["dance"]) == "unknown command"
    assert run(["go", "north", "fast"]) == "unknown command"
    assert run("go north") == "unknown command"  # str is not matched as a sequence


# Exercise 4 ---------------------------------------------------------------
def test_parse_trade():
    assert [parse_trade(line) for line in TRADE_LINES] == [
        ("AAPL", "BUY", 100, 189.5),
        ("MSFT", "SELL", 25, 411.2),
        ("NVDA", "BUY", 7, 118.03),
    ]


def test_parse_trade_full_width_columns():
    # a 6-letter symbol fills characters 0-5 completely, with no space after it
    assert parse_trade("GOOGLESELL  3     150.00") == ("GOOGLE", "SELL", 3, 150.0)


def test_parse_trade_uses_slice_objects():
    import exercises_ch02

    slices = [v for v in vars(exercises_ch02).values() if isinstance(v, slice)]
    assert len(slices) >= 4, "define SYMBOL, SIDE, QTY, PRICE as slice objects"


# Exercise 5 ---------------------------------------------------------------
def test_make_grid_shape():
    assert make_grid(2, 3) == [["_", "_", "_"], ["_", "_", "_"]]
    assert make_grid(1, 2, fill=0) == [[0, 0]]


def test_make_grid_rows_are_independent():
    g = make_grid(3, 3)
    g[1][2] = "X"
    assert g == [["_", "_", "_"], ["_", "_", "X"], ["_", "_", "_"]]


# Exercise 6 ---------------------------------------------------------------
def test_top_n():
    words = ["kiwi", "fig", "banana", "apple", "date"]
    assert top_n(words, 3) == ["banana", "apple", "date"]
    assert top_n(words, 1) == ["banana"]


def test_top_n_leaves_input_alone():
    words = ["kiwi", "fig", "banana"]
    top_n(words, 2)
    assert words == ["kiwi", "fig", "banana"]


# Exercise 7 ---------------------------------------------------------------
def test_tail():
    assert tail(["a", "b", "c", "d"], 2) == ["c", "d"]
    assert tail(["a"], 3) == ["a"]


def test_tail_keeps_only_n_lines_in_memory():
    lines = (f"line {i:07d}" for i in range(300_000))
    tracemalloc.start()
    result = tail(lines, 3)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert result == ["line 0299997", "line 0299998", "line 0299999"]
    assert peak < 1_000_000, f"peak memory {peak:,} bytes: don't build a full list"
