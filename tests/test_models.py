"""
test_models.py
--------------
Tests für wgnd.models.ModelTracker + save_model.

Nutzt tmp_path für alle Datei-Operationen; keine echten Modelle nötig
(ein Dummy mit ``fit``/``predict`` reicht als Export-Objekt).
"""

import os

import pandas as pd
import pytest

from wgnd.models import ModelTracker, save_model


class _DummyModel:
    """Minimaler Platzhalter – muss nur joblib-serialisierbar sein."""

    def __init__(self, tag="m"):
        self.tag = tag


def test_save_model_writes_joblib(tmp_path):
    joblib = pytest.importorskip("joblib")
    folder = tmp_path / "models"
    save_model(_DummyModel(), "demo", folder=str(folder))

    path = folder / "demo.joblib"
    assert path.exists()
    assert joblib.load(path).tag == "m"


def test_add_entry_computes_metrics_and_logs_csv(tmp_path):
    pytest.importorskip("sklearn")
    csv = tmp_path / "models" / "tracking.csv"
    tracker = ModelTracker(csv_path=str(csv))

    # Perfekte Vorhersage → F1 == 1.0
    y_true = [0, 1, 0, 1]
    y_pred = [0, 1, 0, 1]
    run_id = tracker.add_entry("perfect", _DummyModel(), "feat_set", ["a"], y_true, y_pred)

    assert run_id == 0
    assert csv.exists()
    df = pd.read_csv(csv)
    row = df.iloc[0]
    assert row["F1-Score"] == 1.0
    assert row["Recall"] == 1.0
    assert row["Precision"] == 1.0
    assert bool(row["Is_Best"]) is True
    # F1 >= threshold → Modell wurde exportiert
    assert row["Model_File"].startswith("export/")
    assert (csv.parent / "export" / "000_perfect.joblib").exists()


def test_is_best_flag_tracks_improvement(tmp_path):
    pytest.importorskip("sklearn")
    csv = tmp_path / "tracking.csv"
    tracker = ModelTracker(csv_path=str(csv))

    y_true = [0, 1, 0, 1]
    weak = [0, 0, 0, 1]      # niedriger F1
    strong = [0, 1, 0, 1]    # perfekter F1

    tracker.add_entry("weak", _DummyModel(), "fs", ["a"], y_true, weak)
    tracker.add_entry("strong", _DummyModel(), "fs", ["a"], y_true, strong)

    df = tracker.get_results()
    assert bool(df.loc[0, "Is_Best"]) is True    # erster Run ist per Definition best
    assert bool(df.loc[1, "Is_Best"]) is True    # verbessert → neuer Bestwert


def test_low_f1_below_threshold_is_csv_only(tmp_path):
    pytest.importorskip("sklearn")
    csv = tmp_path / "tracking.csv"
    # Schwelle künstlich hoch → nichts wird exportiert
    tracker = ModelTracker(csv_path=str(csv), export_threshold=0.99)

    y_true = [0, 1, 0, 1]
    poor = [0, 0, 0, 0]      # F1 == 0, kein neuer Bestwert (best startet bei 0)

    tracker.add_entry("poor", _DummyModel(), "fs", ["a"], y_true, poor)
    df = tracker.get_results()
    assert df.loc[0, "Model_File"] == "No"
    assert not (csv.parent / "export" / "000_poor.joblib").exists()


def test_persistence_reloads_existing_csv(tmp_path):
    pytest.importorskip("sklearn")
    csv = tmp_path / "tracking.csv"
    y_true = [0, 1, 0, 1]

    t1 = ModelTracker(csv_path=str(csv))
    t1.add_entry("first", _DummyModel(), "fs", ["a"], y_true, [0, 1, 0, 1])

    # Neue Instanz lädt die bestehende Historie
    t2 = ModelTracker(csv_path=str(csv))
    assert len(t2.get_results()) == 1
    run_id = t2.add_entry("second", _DummyModel(), "fs", ["a"], y_true, [0, 1, 0, 1])
    assert run_id == 1
    assert len(pd.read_csv(csv)) == 2
