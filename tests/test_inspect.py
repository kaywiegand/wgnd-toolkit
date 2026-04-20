"""
test_inspect.py
---------------
Tests für wgnd.inspect.

Testet Return-Werte und Datentypen — keine Chart-Ausgaben (show_chart=False).
"""

import numpy as np
import pandas as pd
import pytest
import matplotlib
matplotlib.use("Agg")   # kein Display nötig für Tests

from wgnd.inspect import (
    inspect,
    inspect_dimensions,
    inspect_dtypes,
    inspect_duplicates,
    inspect_memory,
    inspect_missing,
    inspect_names,
    inspect_numeric_stats,
    inspect_categorical_stats,
    inspect_outliers,
    iqr_values,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "age":      np.random.randint(18, 80, n).astype(float),
        "income":   np.random.normal(50_000, 15_000, n),
        "score":    np.random.uniform(0, 1, n),
        "city":     np.random.choice(["Berlin", "München", "Hamburg"], n),
        "category": np.random.choice(["A", "B", "C"], n),
        "target":   np.random.choice([0, 1], n, p=[0.8, 0.2]),
    })
    df.loc[0:9, "age"]   = np.nan
    df.loc[5:12, "city"] = np.nan
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    return df


@pytest.fixture
def clean_df() -> pd.DataFrame:
    np.random.seed(0)
    return pd.DataFrame({
        "x": np.arange(50, dtype=float),
        "y": np.random.randn(50),
        "z": np.random.randn(50),
        "label": np.random.choice(["a", "b"], 50),
    })


class TestInspectDimensions:
    def test_returns_dataframe(self, sample_df):
        result = inspect_dimensions(sample_df)
        assert isinstance(result, pd.DataFrame)
        assert "metric" in result.columns
        assert "count" in result.columns
        assert "pct" in result.columns

    def test_detects_duplicate(self, sample_df):
        result = inspect_dimensions(sample_df)
        dup_row = result[result["metric"] == "duplicates"]["count"].iloc[0]
        assert int(dup_row) >= 1


class TestInspectMemory:
    def test_returns_dataframe(self, sample_df):
        result = inspect_memory(sample_df)
        assert isinstance(result, pd.DataFrame)
        assert "column" in result.columns
        assert "memory_kb" in result.columns

    def test_sorted_descending(self, sample_df):
        result = inspect_memory(sample_df)
        assert result["memory_kb"].is_monotonic_decreasing


class TestInspectDtypes:
    def test_returns_dataframe(self, sample_df):
        result = inspect_dtypes(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_expected_columns(self, sample_df):
        result = inspect_dtypes(sample_df)
        for col in ["column", "dtype", "missing_cnt", "missing_pct", "unique"]:
            assert col in result.columns

    def test_null_counts_correct(self, sample_df):
        result = inspect_dtypes(sample_df)
        age_row = result[result["column"] == "age"].iloc[0]
        assert age_row["missing_cnt"] == sample_df["age"].isna().sum()


class TestInspectMissing:
    def test_returns_dataframe(self, sample_df):
        result = inspect_missing(sample_df, chart=None)
        assert isinstance(result, pd.DataFrame)

    def test_only_cols_with_nulls(self, sample_df):
        result = inspect_missing(sample_df, chart=None)
        assert all(result["missing_cnt"] > 0)

    def test_clean_df_returns_empty(self, clean_df):
        result = inspect_missing(clean_df, chart=None)
        assert len(result) == 0


class TestInspectDuplicates:
    def test_returns_dataframe(self, sample_df):
        result = inspect_duplicates(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_detects_known_duplicate(self, sample_df):
        result = inspect_duplicates(sample_df)
        assert len(result) >= 2

    def test_clean_df_empty(self, clean_df):
        result = inspect_duplicates(clean_df)
        assert len(result) == 0


class TestInspectNumericStats:
    def test_returns_dataframe(self, sample_df):
        result = inspect_numeric_stats(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_mean_median_diff(self, sample_df):
        result = inspect_numeric_stats(sample_df)
        assert "mean_median_diff" in result.columns

    def test_has_missing_pct(self, sample_df):
        result = inspect_numeric_stats(sample_df)
        assert "missing_pct" in result.columns


class TestInspectCategoricalStats:
    def test_returns_dataframe(self, sample_df):
        result = inspect_categorical_stats(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_renamed_columns(self, sample_df):
        result = inspect_categorical_stats(sample_df)
        assert "uniques" in result.columns
        assert "top_value_cnt" in result.columns
        assert "top_value_freq_pct" in result.columns
        assert "missing_pct" in result.columns


class TestInspectOutliers:
    def test_returns_dataframe(self, sample_df):
        result = inspect_outliers(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_iqr_columns(self, sample_df):
        result = inspect_outliers(sample_df)
        assert "lower_1.5x" in result.columns
        assert "upper_1.5x" in result.columns
        assert "outliers_1.5x" in result.columns
        assert "outliers_3x" in result.columns

    def test_has_mean_median_diff(self, sample_df):
        result = inspect_outliers(sample_df)
        assert "mean_med_diff" in result.columns


class TestIqrValues:
    def test_returns_dict(self, clean_df):
        result = iqr_values(clean_df, "x")
        assert isinstance(result, dict)
        assert "lower_1.5x" in result
        assert "upper_1.5x" in result
        assert "outliers_1.5x" in result


class TestInspectOrchestrator:
    def test_returns_dict(self, sample_df):
        result = inspect(sample_df, sections=["dimensions", "dtypes"])
        assert isinstance(result, dict)
        assert "dimensions" in result
        assert "dtypes" in result

    def test_unknown_section_no_crash(self, sample_df):
        result = inspect(sample_df, sections=["dimensions", "UNKNOWN"])
        assert "dimensions" in result
        assert "UNKNOWN" not in result
