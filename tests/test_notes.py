"""
test_notes.py
-------------
Tests für wgnd.notes.EdaNotes. Kein HTML-Rendering (show() braucht IPython),
nur die Zustands-Logik.
"""

import pytest

from wgnd.notes import EdaNotes, notes


def test_add_and_categories():
    n = EdaNotes()
    n.add("clean", "drop dup rows")
    n.add("FEATURE", "log-transform price")
    assert n._notes["CLEAN"] == ["drop dup rows"]
    assert n._notes["FEATURE"] == ["log-transform price"]


def test_invalid_category_raises():
    n = EdaNotes()
    with pytest.raises(ValueError):
        n.add("nope", "x")


def test_remove_and_clear():
    n = EdaNotes()
    n.add("model", "try xgboost")
    n.add("model", "tune C")
    n.remove("model", 0)
    assert n._notes["MODEL"] == ["tune C"]

    n.add("investigate", "weird outlier")
    n.clear("model")
    assert n._notes["MODEL"] == []
    assert n._notes["INVESTIGATE"] == ["weird outlier"]

    n.clear()
    assert all(v == [] for v in n._notes.values())


def test_singleton_importable():
    assert isinstance(notes, EdaNotes)
