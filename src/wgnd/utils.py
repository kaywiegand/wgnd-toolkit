"""
utils.py
--------
Allgemeine Helfer.

load/save nicht enthalten — pandas direkt verwenden:
    df = pd.read_csv("data/raw/file.csv")
    df.to_parquet("data/processed/file.parquet")
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Callable

import pandas as pd

from wgnd.core._output import console, section_header, show_df
from wgnd.core.config import cfg


def timer(func: Callable) -> Callable:
    """
    Decorator: misst und zeigt die Laufzeit einer Funktion.

    Verwendung:
        @timer
        def my_pipeline(df): ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start   = time.perf_counter()
        result  = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        console.print(f"[dim]⏱  {func.__name__} → {elapsed:.3f}s[/]")
        return result
    return wrapper


def memory_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Speicherverbrauch pro Spalte, sortiert absteigend.

    Nützlich zusammen mit inspect_dtypes um Speicher-Flaschenhälse zu finden.

    Returns:
        DataFrame mit: column, dtype, memory_kb, memory_pct
    """
    dp       = cfg.DECIMAL_PLACES
    mem      = df.memory_usage(deep=True)
    total_kb = mem.sum() / 1024

    records = []
    for col in df.columns:
        kb = mem.get(col, 0) / 1024
        records.append({
            "column":     col,
            "dtype":      str(df[col].dtype),
            "memory_kb":  round(kb, dp),
            "memory_pct": round(kb / total_kb * 100, dp) if total_kb else 0,
        })

    result_df = (
        pd.DataFrame(records)
        .sort_values("memory_kb", ascending=False)
        .reset_index(drop=True)
    )
    show_df(result_df)
    return result_df


def downcast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduziert Speicherbedarf durch Downcast numerischer Typen.

    int64 → int32/int16, float64 → float32 wo möglich.

    Returns:
        Optimierter DataFrame (Kopie).
    """
    dp     = cfg.DECIMAL_PLACES
    result = df.copy()
    before = result.memory_usage(deep=True).sum() / 1024

    for col in result.select_dtypes(include=["int64", "int32"]).columns:
        result[col] = pd.to_numeric(result[col], downcast="integer")
    for col in result.select_dtypes(include=["float64"]).columns:
        result[col] = pd.to_numeric(result[col], downcast="float")

    after  = result.memory_usage(deep=True).sum() / 1024
    saving = before - after
    console.print(
        f"[dim]downcast: {round(before, dp)} KB → {round(after, dp)} KB  "
        f"(saved {round(saving, dp)} KB = "
        f"{round(saving/before*100, dp) if before else 0}%)[/]"
    )
    return result
