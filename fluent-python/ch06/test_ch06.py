import inspect

import pytest
from exercises_ch06 import (
    Playlist,
    append_to,
    classify,
    clone_grid,
    count_distinct,
    double_in_place,
    doubled,
    get_setting,
    snapshot,
)


# Exercise 1 ---------------------------------------------------------------
def test_classify():
    a = [1, 2]
    assert classify(a, a) == "same object"
    assert classify(a, [1, 2]) == "equal"
    assert classify(a, [3]) == "different"


def test_count_distinct_counts_objects_not_values():
    x, y = [1], [1]
    assert count_distinct([x, x, y]) == 2
    assert count_distinct([x, x, x]) == 1
    assert count_distinct([]) == 0


# Exercise 2 ---------------------------------------------------------------
def test_clone_grid_is_independent():
    g = [[1, 2], [3, 4]]
    c = clone_grid(g)
    assert c == g and c is not g
    c[0][0] = 99
    c[1].append(5)
    assert g == [[1, 2], [3, 4]]


def test_clone_grid_does_not_use_copy_module():
    import exercises_ch06

    source = inspect.getsource(exercises_ch06.clone_grid)
    assert "copy.copy" not in source and "deepcopy" not in source


# Exercise 3 ---------------------------------------------------------------
def test_snapshot_is_deep():
    config = {"servers": [{"host": "a", "ports": [80]}], "debug": False}
    snap = snapshot(config)
    config["servers"][0]["ports"].append(443)
    config["servers"].append({"host": "b", "ports": []})
    config["debug"] = True
    assert snap == {"servers": [{"host": "a", "ports": [80]}], "debug": False}


# Exercise 4 ---------------------------------------------------------------
def test_append_to_default_is_fresh_each_call():
    assert append_to(1) == [1]
    assert append_to(2) == [2]


def test_append_to_given_list_is_changed():
    lst = ["a"]
    result = append_to("b", lst)
    assert result is lst
    assert lst == ["a", "b"]


def test_append_to_has_no_mutable_default():
    default = inspect.signature(append_to).parameters["target"].default
    assert not isinstance(default, (list, dict, set))


# Exercise 5 ---------------------------------------------------------------
def test_playlist_empty_playlists_are_independent():
    p1, p2 = Playlist(), Playlist()
    p1.add("x")
    assert p2.songs == []


def test_playlist_does_not_change_callers_list():
    mine = ["a", "b", "c"]
    p = Playlist(mine)
    p.remove("b")
    p.add("d")
    assert mine == ["a", "b", "c"]
    assert p.songs == ["a", "c", "d"]


def test_playlist_accepts_any_iterable():
    assert Playlist(("a", "b")).songs == ["a", "b"]
    assert Playlist(s for s in "xy").songs == ["x", "y"]


# Exercise 6 ---------------------------------------------------------------
def test_doubled_returns_new_list():
    nums = [1, 2, 3]
    result = doubled(nums)
    assert result == [2, 4, 6]
    assert nums == [1, 2, 3]
    assert result is not nums


def test_double_in_place_changes_the_same_list():
    nums = [1, 2, 3]
    alias = nums
    assert double_in_place(nums) is None
    assert alias == [2, 4, 6]


# Exercise 7 ---------------------------------------------------------------
def test_get_setting():
    settings = {"timeout": 30, "proxy": None}
    assert get_setting(settings, "timeout") == 30
    assert get_setting(settings, "proxy", "fallback") is None
    assert get_setting(settings, "retries", 3) == 3
    assert get_setting(settings, "retries", None) is None
    with pytest.raises(KeyError):
        get_setting(settings, "retries")
