"""
inspect.py
----------
EDA-Inspektion. Alle Sub-Funktionen folgen dem gleichen Muster:

  section_header("title")  ← Trennlinie mit Titel
  show_df(result_df)       ← einheitliche Tabelle
  return result            ← dict oder DataFrame (immer)

Rundung: cfg.DECIMAL_PLACES (Standard 3) gilt überall.

Schnellstart:
    from wgnd.inspect import inspect
    inspect(df)                               # alle Sektionen

    from wgnd.inspect import inspect_missing, inspect_outlier_detail
    inspect_missing(df)
    inspect_outlier_detail(df, "annual_income", hue="is_churned")
    iqr = iqr_values(df, "income")
"""

from __future__ import annotations

import warnings
import numpy as np
import pandas as pd

from wgnd.core._output import console, section_header, show_df, warn, success, error, log as _log
from wgnd.core.config import cfg

# Runden: zentral aus config
_D = cfg.DECIMAL_PLACES


def _r(x) -> float | str:
    """Rundet auf cfg.DECIMAL_PLACES, gibt x zurück wenn nicht numerisch."""
    try:
        return round(float(x), _D)
    except (TypeError, ValueError):
        return x


# ─── Orchestrator ─────────────────────────────────────────────────────────────

_ALL_SECTIONS = [
    "dimensions", "memory", "dtypes", "names",
    "missing", "duplicates", "numeric", "categorical",
    "correlations", "outliers",
]

_SECTION_FN: dict = {}


def inspect(
    df: pd.DataFrame,
    sections: list[str] | None = None,
    columns: list[str] | None = None,
    title: str | None = None,
) -> None:
    """
    Vollständige EDA-Übersicht.

    Args:
        df:       Eingabe-DataFrame.
        sections: Teilmenge (None → alle).
                  Werte: 'dimensions', 'memory', 'dtypes', 'names',
                  'missing', 'duplicates', 'numeric', 'categorical',
                  'correlations', 'outliers'
        columns:  Spaltenliste — wird an 'numeric', 'categorical', 'outliers' weitergegeben.
        title:    Alternativer Titel — wird an 'numeric', 'categorical' weitergegeben.
    """
    _COLUMNS_SUPPORT = {"numeric", "categorical", "outliers"}
    _TITLE_SUPPORT   = {"numeric", "categorical"}

    to_run = sections or _ALL_SECTIONS
    for name in to_run:
        fn = _SECTION_FN.get(name)
        if fn is None:
            warn(f"Unknown section: '{name}' — skipped.")
            continue
        try:
            kwargs = {}
            if columns is not None and name in _COLUMNS_SUPPORT:
                kwargs["columns"] = columns
            if title is not None and name in _TITLE_SUPPORT:
                kwargs["title"] = title
            fn(df, **kwargs)
        except Exception as exc:
            error(f"Error in '{name}': {exc}")
    return None


# ─── 1 · Dimensions ───────────────────────────────────────────────────────────

def inspect_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Shape, Duplikate und leere Zeilen/Spalten.

    Ausgabe-Spalten: metric | count | pct
    Prozent nur wo sinnvoll (duplicates, empty rows, empty cols).

    Returns:
        DataFrame mit: metric, count, pct
    """
    rows, cols   = df.shape
    dupes        = int(df.duplicated().sum())
    empty_rows   = int(df.isna().all(axis=1).sum())
    empty_cols   = int(df.isna().all(axis=0).sum())

    def _pct(n, total):
        return f"{_r(n / total * 100)}%" if total else "—"

    records = [
        ("rows",              rows,       ""),
        ("columns",           cols,       ""),
        ("duplicates",        dupes,      _pct(dupes, rows)),
        ("empty rows (all NaN)", empty_rows, _pct(empty_rows, rows)),
        ("empty cols (all NaN)", empty_cols, _pct(empty_cols, cols)),
    ]
    result_df = pd.DataFrame(records, columns=["metric", "count", "pct"])

    section_header("dimensions")
    show_df(result_df)
    return result_df


# ─── 2 · Memory ───────────────────────────────────────────────────────────────

def inspect_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Speicherverbrauch pro Spalte, sortiert absteigend.

    Returns:
        DataFrame mit: column, dtype, memory_kb, memory_pct
    """
    mem      = df.memory_usage(deep=True)
    total_kb = mem.sum() / 1024

    records = []
    for col in df.columns:
        kb = mem.get(col, 0) / 1024
        records.append({
            "column":     col,
            "dtype":      str(df[col].dtype),
            "memory_kb":  _r(kb),
            "memory_pct": _r(kb / total_kb * 100) if total_kb else 0,
        })

    result_df = (
        pd.DataFrame(records)
        .sort_values("memory_kb", ascending=False)
        .reset_index(drop=True)
    )

    section_header("memory")
    show_df(result_df)
    _log(f"Total: {_r(total_kb)} KB  ({_r(total_kb/1024)} MB)")
    return result_df


# ─── 3 · Dtypes ───────────────────────────────────────────────────────────────

def inspect_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Datentypen, Nullwerte und Eindeutigkeit pro Spalte.

    Returns:
        DataFrame mit: column, dtype, missing_cnt, missing_pct, unique, unique_pct
    """
    rows = len(df)
    records = []
    for col in df.columns:
        nulls  = int(df[col].isna().sum())
        unique = int(df[col].nunique(dropna=True))
        records.append({
            "column":      col,
            "dtype":       str(df[col].dtype),
            "missing_cnt": nulls,
            "missing_pct": _r(nulls / rows * 100) if rows else 0,
            "unique":      unique,
            "unique_pct":  _r(unique / rows * 100) if rows else 0,
        })

    result_df = pd.DataFrame(records)
    section_header("dtypes")
    show_df(result_df, highlight_col="missing_cnt", highlight_threshold=0)
    return result_df


# ─── 4 · Names ────────────────────────────────────────────────────────────────

def inspect_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Spaltennamen auf Leerzeichen, Sonderzeichen und Ziffernstart prüfen.

    Returns:
        DataFrame mit: name, has_spaces, has_special, starts_with_digit, length
    """
    import re
    records = []
    for col in df.columns:
        records.append({
            "name":              col,
            "has_spaces":        " " in str(col),
            "has_special":       bool(re.search(r"[^a-zA-Z0-9_]", str(col))),
            "starts_with_digit": str(col)[0].isdigit() if col else False,
            "length":            len(str(col)),
        })
    result_df = pd.DataFrame(records)
    issues    = result_df[
        result_df["has_spaces"] | result_df["has_special"] | result_df["starts_with_digit"]
    ]

    section_header("column names")
    if issues.empty:
        success("All column names are Python-compatible.")
    else:
        warn(f"{len(issues)} column(s) with naming issues:")
        show_df(issues)
    _log(f"All {len(df.columns)}: {', '.join(df.columns.tolist())}")
    return result_df


# ─── 5 · Missing Values ───────────────────────────────────────────────────────

def inspect_missing(
    df: pd.DataFrame,
    chart: str | None = "heatmap",
    transpose: bool = True,
) -> pd.DataFrame:
    """
    Fehlwert-Analyse: Tabelle + optionaler Chart.

    Args:
        df:         Eingabe-DataFrame.
        chart:      'heatmap' → Seaborn isnull().T Heatmap (empfohlen)
                    None      → kein Chart
        transpose:  True → Features auf y-Achse (Standard, gut lesbar).

    Returns:
        DataFrame mit: column, missing_cnt, missing_pct
        (nur Spalten mit Fehlwerten, sortiert nach missing_pct absteigend)
    """
    rows   = len(df)
    counts = df.isna().sum()
    cols_w = counts[counts > 0]

    section_header("missing values")

    if cols_w.empty:
        success("No missing values.")
        return pd.DataFrame(columns=["column", "missing_cnt", "missing_pct"])

    result_df = (
        pd.DataFrame({
            "column":      cols_w.index,
            "missing_cnt": cols_w.values,
            "missing_pct": (cols_w / rows * 100).round(_D).values,
        })
        .sort_values("missing_pct", ascending=False)
        .reset_index(drop=True)
    )
    show_df(result_df, highlight_col="missing_cnt", highlight_threshold=0)

    if chart == "heatmap" and len(cols_w) >= 1:
        _plot_missing_heatmap(df, transpose)

    return result_df


def _plot_missing_heatmap(df: pd.DataFrame, transpose: bool = True) -> None:
    """Seaborn-Heatmap für Fehlwerte — Features auf y-Achse."""
    import matplotlib.pyplot as plt
    import seaborn as sns
    from wgnd.core.theme import mpl_style

    style   = mpl_style()
    null_df = df.isnull()
    data    = null_df.T if transpose else null_df

    fig_h = max(4, data.shape[0] * 0.35) if transpose else max(4, cfg.MPL_FIGSIZE[1])
    fig, ax = plt.subplots(figsize=(cfg.MPL_FIGSIZE[0], fig_h))

    sns.heatmap(
        data,
        cbar=False,
        cmap=["#f5f5f5", cfg.ACTIVE_PALETTE[3]],
        xticklabels=False,
        yticklabels=True,
        ax=ax,
        linewidths=0,
    )
    for i in range(data.shape[0] + 1):
        ax.axhline(i, color="white", lw=0.8)

    ax.set_title("Missing Data Pattern", **style["title"])
    ax.set_xlabel("Records (row index)", **style["label"])
    ax.set_ylabel("Features" if transpose else "Records", **style["label"])
    ax.tick_params(axis="y", labelsize=10)
    plt.tight_layout()
    plt.show()


# ─── 6 · Duplicates ───────────────────────────────────────────────────────────

def inspect_duplicates(
    df: pd.DataFrame,
    subset: list[str] | None = None,
) -> pd.DataFrame:
    """
    Duplizierte Zeilen analysieren.

    Returns:
        DataFrame aller duplizierten Zeilen (keep=False).
        Leer wenn keine Duplikate vorhanden.
        Tipp: result.head(10) für Vorschau.
    """
    dupes_df = df[df.duplicated(subset=subset, keep="first")].copy()
    count    = len(dupes_df)
    rows     = len(df)

    def _pct(n):
        return f"{_r(n / rows * 100)}%" if rows else "—"

    records = [
        ("total rows",           rows,         ""),
        ("duplicates",           int(count),   _pct(count)),
        ("unique rows",          rows - count, _pct(rows - count)),
    ]
    result_meta = pd.DataFrame(records, columns=["metric", "count", "pct"])

    section_header("duplicates")
    show_df(result_meta)

    if count == 0:
        success("No duplicates found.")
    else:
        _log("Duplicate rows returned — use result.head(10) to inspect.")

    return dupes_df


# ─── 7 · Numeric Stats ────────────────────────────────────────────────────────

def inspect_numeric_stats(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    title: str = "numeric stats",
) -> pd.DataFrame:
    """
    Deskriptive Statistik für numerische Spalten.

    Args:
        columns: Optionale Spaltenliste — None → alle numerischen Spalten.
        title:   Alternativer Section-Header (z.B. "numeric stats – fare columns").
    """
    num_df = df[columns].select_dtypes(include="number") if columns else df.select_dtypes(include="number")

    section_header(title)

    if num_df.empty:
        warn("No numeric columns found.")
        return pd.DataFrame()

    desc  = num_df.describe().T.round(_D)
    stats = desc[["count", "mean", "50%", "std", "min", "25%", "75%", "max"]].copy()
    stats = stats.rename(columns={"50%": "median"})

    stats.insert(0, "missing_pct",    (num_df.isna().sum() / len(df) * 100).round(_D))
    stats["mean_median_diff"]         = (stats["mean"] - stats["median"]).round(_D)
    stats["skewness"]                 = num_df.skew().round(_D)

    stats.index.name = "column"
    result_df = stats.reset_index()

    show_df(result_df)
    return result_df


# ─── 8 · Categorical Stats ────────────────────────────────────────────────────

def inspect_categorical_stats(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    title: str = "categorical stats",
) -> pd.DataFrame:
    """
    Häufigkeitsanalyse für kategorische Spalten.

    Args:
        columns: Optionale Spaltenliste — None → alle kategorischen Spalten.
        title:   Alternativer Section-Header.
    """
    cat_df = df[columns].select_dtypes(include=["object", "category", "bool", "string"]) if columns else df.select_dtypes(include=["object", "category", "bool", "string"])

    section_header(title)

    if cat_df.empty:
        warn("No categorical columns found.")
        return pd.DataFrame()

    rows    = len(df)
    records = []
    for col in cat_df.columns:
        nulls   = int(df[col].isna().sum())
        vc      = df[col].value_counts()
        top_val = vc.index[0] if len(vc) else None
        top_cnt = int(vc.iloc[0]) if len(vc) else 0
        records.append({
            "column":             col,
            "missing_pct":        _r(nulls / rows * 100),
            "missing_cnt":        nulls,
            "uniques":            int(df[col].nunique()),
            "top_value":          str(top_val),
            "top_value_cnt":      top_cnt,
            "top_value_freq_pct": _r(top_cnt / rows * 100) if rows else 0,
        })

    result_df = pd.DataFrame(records)
    show_df(result_df, highlight_col="missing_cnt", highlight_threshold=0)
    return result_df


# ─── 9 · Correlations ─────────────────────────────────────────────────────────

def inspect_correlations(
    df: pd.DataFrame,
    target: str | None = None,
    method: str = "pearson",
    threshold: float = 0.0,
    show_pairplot: bool = False,
    pairplot_hue: str | None = None,
) -> dict:
    """
    Korrelationsmatrix + optionales Target-Ranking + Seaborn-Pairplot.

    Args:
        df:             Eingabe-DataFrame.
        target:         Zielvariable → extra Ranking-Tabelle nach |r|.
        method:         'pearson', 'spearman', 'kendall'.
        threshold:      Nur Paare mit |r| ≥ threshold in Paar-Tabelle.
        show_pairplot:  True → Seaborn Pairplot (scatter matrix mit KDE-Diagonale).
        pairplot_hue:   Farbgruppierung im Pairplot.

    Returns:
        dict mit 'matrix', 'pairs', 'target'
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap
    from wgnd.core.theme import mpl_style

    num_df = df.select_dtypes(include="number")
    section_header("correlations")

    if num_df.shape[1] < 2:
        warn("At least 2 numeric columns required.")
        return {}

    corr = num_df.corr(method=method).round(_D)
    cols = corr.columns.tolist()

    # ── Target-Ranking ────────────────────────────────────────────────────
    target_df = pd.DataFrame()
    if target and target in num_df.columns:
        t = (
            corr[target].drop(labels=[target])
            .rename("r").reset_index()
            .rename(columns={"index": "feature"})
        )
        t["|r|"] = t["r"].abs().round(_D)
        t["r"]   = t["r"].round(_D)
        target_df = t.sort_values("|r|", ascending=False).reset_index(drop=True)
        show_df(target_df, caption=f"Target correlation ranking: '{target}'")

    # ── Paar-Tabelle ──────────────────────────────────────────────────────
    pairs = []
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1:]:
            r = corr.loc[c1, c2]
            if abs(r) >= threshold:
                pairs.append({"col_1": c1, "col_2": c2, "r": _r(r), "|r|": _r(abs(r))})

    pairs_df = (
        pd.DataFrame(pairs).sort_values("|r|", ascending=False).reset_index(drop=True)
        if pairs else pd.DataFrame()
    )

    if threshold > 0 and not pairs_df.empty:
        show_df(pairs_df, caption=f"Pairs with |r| ≥ {threshold}")
    else:
        show_df(corr)

    # ── Heatmap mit PALETTE_DIVERGENT ─────────────────────────────────────
    style = mpl_style()
    n     = len(cols)
    fig, ax = plt.subplots(figsize=(max(8, n * 0.7), max(6, n * 0.6)))

    cmap = LinearSegmentedColormap.from_list(
        "wgnd_div", cfg.PALETTE_DIVERGENT, N=256
    )
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=f".{_D}f",
        cmap=cmap, center=0, vmin=-1, vmax=1,
        linewidths=0.4, linecolor="#eeeeee",
        square=True, ax=ax,
        cbar_kws={"shrink": 0.7, "label": "r"},
    )
    ax.set_title(f"Correlation matrix ({method})", **style["title"])
    plt.tight_layout()
    plt.show()

    # ── Seaborn Pairplot ──────────────────────────────────────────────────
    if show_pairplot:
        hue_col = pairplot_hue or target
        palette = None
        plot_df = num_df.copy()

        if hue_col and hue_col in df.columns:
            plot_df[hue_col] = df[hue_col]
            uvals   = sorted(df[hue_col].dropna().unique())
            palette = {v: cfg.ACTIVE_PALETTE[i % len(cfg.ACTIVE_PALETTE)]
                       for i, v in enumerate(uvals)}

        g = sns.pairplot(
            plot_df.dropna(),
            hue=hue_col if hue_col and hue_col in plot_df.columns else None,
            palette=palette,
            diag_kind="kde",
            plot_kws={"alpha": 0.4, "s": 15, "linewidth": 0},
            diag_kws={"fill": True, "alpha": 0.5},
        )
        g.figure.suptitle(
            "Scatter matrix", y=1.01, fontsize=14,
            color=cfg.CHART_TITLE, ha="left", x=0.04,
        )
        plt.tight_layout()
        plt.show()

    # ── Hohe Korrelationen hervorheben ────────────────────────────────────
    if not pairs_df.empty:
        high = pairs_df[pairs_df["|r|"] >= cfg.CORR_HIGH_THRESHOLD]
        if not high.empty:
            warn(
                f"{len(high)} highly correlated pair(s) (|r| ≥ {cfg.CORR_HIGH_THRESHOLD}): "
                + ", ".join(f"{r['col_1']}↔{r['col_2']}" for _, r in high.head(5).iterrows())
                + ("…" if len(high) > 5 else "")
            )

    return {"matrix": corr, "pairs": pairs_df, "target": target_df}


# ─── 10 · Outliers ────────────────────────────────────────────────────────────

def inspect_outliers(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Ausreißer-Übersicht mit IQR 1.5× und 3× für alle numerischen Spalten.

    Returns:
        DataFrame mit: column, mean, median, mean_med_diff,
                       lower_1.5x, upper_1.5x, outliers_1.5x, outliers_1.5x_%,
                       lower_3x,   upper_3x,   outliers_3x,   outliers_3x_%
    """
    num_df = df[columns] if columns else df.select_dtypes(include="number")

    section_header("outliers")

    if num_df.empty:
        warn("No numeric columns found.")
        return pd.DataFrame()

    records = []
    for col in num_df.columns:
        s  = num_df[col].dropna()
        if len(s) == 0:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr    = q3 - q1
        l15, u15 = q1 - 1.5*iqr,  q3 + 1.5*iqr
        l30, u30 = q1 - 3.0*iqr,  q3 + 3.0*iqr
        c15 = int(((s < l15) | (s > u15)).sum())
        c30 = int(((s < l30) | (s > u30)).sum())

        records.append({
            "column":          col,
            "mean":            _r(s.mean()),
            "median":          _r(s.median()),
            "mean_med_diff":   _r(s.mean() - s.median()),
            "lower_1.5x":      _r(l15),
            "upper_1.5x":      _r(u15),
            "outliers_1.5x":   c15,
            "outliers_1.5x_%": _r(c15 / len(s) * 100),
            "lower_3x":        _r(l30),
            "upper_3x":        _r(u30),
            "outliers_3x":     c30,
            "outliers_3x_%":   _r(c30 / len(s) * 100),
        })

    result_df = (
        pd.DataFrame(records)
        .sort_values("outliers_1.5x", ascending=False)
        .reset_index(drop=True)
    )
    show_df(result_df, highlight_col="outliers_1.5x", highlight_threshold=0)
    _log("→ inspect_outlier_detail(df, col) for boxplot+histogram per feature.")
    return result_df


def inspect_outlier_detail(
    df: pd.DataFrame,
    col: str,
    hue: str | None = None,
    figsize: tuple | None = None,
    axes: tuple | None = None,
) -> None:
    """
    Boxplot + Histogramm mit IQR-Linien für eine einzelne Spalte.

    Mean (Amber), Median (Blau), IQR 1.5× (Orange), IQR 3× (Dunkelrot).
    Boxplot und Histogramm teilen die x-Achse.

    Args:
        df:      Eingabe-DataFrame.
        col:     Numerische Spalte.
        hue:     Optionale Gruppierungsspalte für Histogramm.
        figsize: Eigene Figurengröße — überschreibt cfg.MPL_FIGSIZE.
        axes:    Tuple (ax_box, ax_hist) — eigene Axes für Grid-Layouts.
                 Wenn übergeben, wird kein plt.show() aufgerufen.

    Beispiel (Grid):
        fig, axs = plt.subplots(3, 2, figsize=(12, 10))
        for i, feat in enumerate(['a', 'b', 'c']):
            inspect_outlier_detail(df, feat, axes=(axs[i, 0], axs[i, 1]))
        plt.show()
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    from wgnd.core.theme import mpl_style

    s        = df[col].dropna()
    q1, q3   = s.quantile(0.25), s.quantile(0.75)
    iqr      = q3 - q1
    mean     = s.mean()
    median   = s.median()
    l15, u15 = q1 - 1.5*iqr, q3 + 1.5*iqr
    l30, u30 = q1 - 3.0*iqr, q3 + 3.0*iqr
    c15      = int(((s < l15) | (s > u15)).sum())
    c30      = int(((s < l30) | (s > u30)).sum())

    style      = mpl_style()
    _own_fig   = axes is None
    if _own_fig:
        fig, (ax_box, ax_hist) = plt.subplots(
            2, 1, sharex=True, figsize=figsize or cfg.MPL_FIGSIZE,
            gridspec_kw={"height_ratios": [1, 2.5]},
        )
    else:
        ax_box, ax_hist = axes

    # Boxplot
    sns.boxplot(
        x=s, ax=ax_box,
        color=cfg.PALETTE_BLUE_RANGE[4],
        flierprops={"markerfacecolor": cfg.COLOR_NEGATIVE,
                    "markeredgecolor": cfg.COLOR_NEGATIVE,
                    "markersize": 4, "alpha": 0.6},
        linewidth=0.8,
    )
    ax_box.set_yticks([])
    ax_box.spines[["left"]].set_visible(False)

    # Histogramm
    palette = None
    if hue and hue in df.columns:
        uvals   = sorted(df[hue].dropna().unique())
        palette = {v: cfg.ACTIVE_PALETTE[i % len(cfg.ACTIVE_PALETTE)]
                   for i, v in enumerate(uvals)}

    sns.histplot(
        data=df, x=col, hue=hue, kde=True,
        palette=palette, alpha=0.6,
        ax=ax_hist, common_norm=False,
    )

    # IQR-Linien auf beiden Achsen
    vlines = [
        (mean,  cfg.COLOR_SIGNAL,   "-",  1.8, f"Mean: {_r(mean)}"),
        (median, cfg.ACTIVE_PALETTE[2], "-", 1.8, f"Median: {_r(median)}"),
        (l15,   cfg.COLOR_SIGNAL,   ":",  1.2, f"1.5× IQR lower"),
        (u15,   cfg.COLOR_SIGNAL,   ":",  1.2, f"1.5× IQR upper  ({c15} outliers)"),
        (l30,   cfg.COLOR_NEGATIVE, ":",  1.2, f"3× IQR lower"),
        (u30,   cfg.COLOR_NEGATIVE, ":",  1.2, f"3× IQR upper  ({c30} outliers)"),
    ]
    for ax in (ax_box, ax_hist):
        for x, color, ls, lw, label in vlines:
            ax.axvline(x, color=color, linestyle=ls, linewidth=lw,
                       label=label if ax is ax_hist else None)

    ax_hist.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax_box.set_title(f"Distribution & outliers: {col}", **style["title"])
    ax_hist.set_xlabel(col, **style["label"])
    ax_hist.set_ylabel("Count", **style["label"])
    for ax in (ax_box, ax_hist):
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(cfg.CHART_AXIS)
    if _own_fig:
        plt.tight_layout()
        plt.show()


def iqr_values(df: pd.DataFrame, col: str) -> dict:
    """
    IQR-Werte für eine einzelne Spalte — schnelle Grenzwert-Berechnung.

    Returns:
        dict mit: q1, q3, iqr, lower_1.5x, upper_1.5x,
                  lower_3x, upper_3x, mean, median,
                  outliers_1.5x, outliers_3x

    Beispiel:
        iqr = iqr_values(df, "annual_income")
        mask_outliers = df["annual_income"] > iqr["upper_1.5x"]
    """
    s        = df[col].dropna()
    q1, q3   = s.quantile(0.25), s.quantile(0.75)
    iqr      = q3 - q1
    l15, u15 = q1 - 1.5*iqr, q3 + 1.5*iqr
    l30, u30 = q1 - 3.0*iqr, q3 + 3.0*iqr
    return {
        "q1":           _r(q1),
        "q3":           _r(q3),
        "iqr":          _r(iqr),
        "lower_1.5x":   _r(l15),
        "upper_1.5x":   _r(u15),
        "lower_3x":     _r(l30),
        "upper_3x":     _r(u30),
        "mean":         _r(s.mean()),
        "median":       _r(s.median()),
        "outliers_1.5x": int(((s < l15) | (s > u15)).sum()),
        "outliers_3x":   int(((s < l30) | (s > u30)).sum()),
    }


# ─── Dispatch ─────────────────────────────────────────────────────────────────

_SECTION_FN.update({
    "dimensions":   inspect_dimensions,
    "memory":       inspect_memory,
    "dtypes":       inspect_dtypes,
    "names":        inspect_names,
    "missing":      inspect_missing,
    "duplicates":   inspect_duplicates,
    "numeric":      inspect_numeric_stats,
    "categorical":  inspect_categorical_stats,
    "correlations": inspect_correlations,
    "outliers":     inspect_outliers,
})
