import random

from exercises_ch01 import Inbox, Playlist, Temperature, Vector

SONGS = ["intro", "verse", "chorus", "bridge", "outro"]


# Exercise 1 ---------------------------------------------------------------
def test_playlist_defines_only_len_and_getitem():
    for name in ("__iter__", "__contains__", "__reversed__"):
        assert name not in vars(Playlist), f"don't define {name}: get it for free"


def test_playlist_len_and_index():
    p = Playlist(SONGS)
    assert len(p) == 5
    assert p[0] == "intro"
    assert p[-1] == "outro"


def test_playlist_slicing():
    assert Playlist(SONGS)[1:3] == ["verse", "chorus"]


def test_playlist_iteration_in_and_reversed():
    p = Playlist(SONGS)
    assert list(p) == SONGS
    assert "chorus" in p
    assert "solo" not in p
    assert list(reversed(p)) == SONGS[::-1]


def test_playlist_works_with_stdlib():
    assert random.choice(Playlist(SONGS)) in SONGS
    assert sorted(Playlist(SONGS)) == sorted(SONGS)


# Exercise 2 ---------------------------------------------------------------
def test_vector_eq():
    assert Vector(1, 2) == Vector(1, 2)
    assert Vector(1, 2) != Vector(2, 1)


def test_vector_sub_and_neg():
    assert Vector(5, 7) - Vector(2, 3) == Vector(3, 4)
    assert -Vector(1, -2) == Vector(-1, 2)


def test_vector_operators_return_new_objects():
    v = Vector(1, 1)
    w = v - Vector(0, 0)
    assert w is not v
    assert (v.x, v.y) == (1, 1)


def test_vector_rmul():
    assert 3 * Vector(1, 2) == Vector(3, 6)
    assert 3 * Vector(1, 2) == Vector(1, 2) * 3


# Exercise 3 ---------------------------------------------------------------
def test_temperature_repr_and_str():
    t = Temperature(21.5)
    assert repr(t) == "Temperature(21.5)"
    assert str(t) == "21.5°C"
    assert f"{t}" == "21.5°C"  # f-strings use __str__
    assert repr([t]) == "[Temperature(21.5)]"  # containers use __repr__


# Exercise 4 ---------------------------------------------------------------
def test_inbox_truthiness_via_len():
    assert "__bool__" not in vars(Inbox), "use only __len__"
    assert not Inbox()
    assert Inbox(["hi"])
    assert len(Inbox(["a", "b"])) == 2
