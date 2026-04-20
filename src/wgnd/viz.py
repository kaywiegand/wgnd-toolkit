"""
viz.py
------
Matplotlib/Seaborn Chart-Helfer für wgnd.

Alle Funktionen:
  → Geben die (fig, ax) oder (fig, axes) zurück – anpassbar
  → Nutzen automatisch das wgnd-Theme (nach setup())
  → Kein Plotly – reines Matplotlib/Seaborn

Eigene Charts (Muster):
    from wgnd.core.theme import mpl_style
    from wgnd.core.config import cfg
    import matplotlib.pyplot as plt
    import seaborn as sns

    style = mpl_style()
    fig, ax = plt.subplots(figsize=(12, 6))
    # ... Chart-Code ...
    ax.set_title("Titel", **style["title"])
    ax.set_xlabel("X",    **style["label"])
    ax.axhline(mean,      **style["signal"])   # Amber: Mittelwert
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(cfg.CHART_AXIS)
    plt.tight_layout()
    plt.show()
"""

from __future__ import annotations

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from wgnd.core.config import cfg
from wgnd.core.theme import mpl_style


# ─── Palette-Preview ──────────────────────────────────────────────────────────

def show_palettes() -> None:
    """
    Zeigt alle wgnd-Farbpaletten als farbige Streifen.

    Nützlich zum Nachschlagen im Notebook.
    """
    palettes = {
        "PALETTE_CATEGORICAL (kategorisch)": cfg.PALETTE_CATEGORICAL,
        "PALETTE_BUSINESS (sequential)":     cfg.PALETTE_BUSINESS,
        "PALETTE_DIVERGENT (divergent)":     cfg.PALETTE_DIVERGENT,
        "Signals":                           [
            cfg.COLOR_SIGNAL,
            cfg.COLOR_POSITIVE,
            cfg.COLOR_NEGATIVE,
            cfg.COLOR_NEUTRAL,
        ],
    }
    signal_labels = ["SIGNAL (Amber)", "POSITIVE (Grün)",
                     "NEGATIVE (Rot)", "NEUTRAL (Grau)"]

    n_groups = len(palettes)
    fig, axes = plt.subplots(n_groups, 1, figsize=(12, n_groups * 1.4))

    for ax, (name, colors) in zip(axes, palettes.items()):
        labels = signal_labels if name.startswith("Signals") else colors
        for i, (color, label) in enumerate(zip(colors, labels)):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
            ax.text(i + 0.5, 0.5, label, ha="center", va="center",
                    fontsize=8, color="white" if _is_dark(color) else "#333",
                    fontweight="bold")
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines[:].set_visible(False)
        ax.set_ylabel(name, fontsize=10, rotation=0, ha="right",
                      va="center", labelpad=8, color=cfg.CHART_LABEL)

    fig.suptitle("wgnd · Color Palettes", fontsize=14, color=cfg.CHART_TITLE,
                 x=0.04, ha="left", y=1.02)
    plt.tight_layout()
    plt.show()


def _is_dark(hex_color: str) -> bool:
    """Prüft ob eine Hex-Farbe dunkel ist (für Textkontrast)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299*r + 0.587*g + 0.114*b) < 140


# ─── Basis-Charts ─────────────────────────────────────────────────────────────

def bar(
    data: pd.Series | pd.DataFrame,
    x: str | None = None,
    y: str | None = None,
    orient: str = "v",
    color: str | None = None,
    ref_val: float | None = None,
    ref_label: str = "Mean",
    highlight_top_n: int | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple | None = None,
) -> tuple:
    """
    Balkendiagramm mit optionaler Referenzlinie.

    Args:
        data:           Series (Index=Kategorien, Values=Werte)
                        oder DataFrame mit x + y Spalten.
        orient:         'v' (vertikal) oder 'h' (horizontal, empfohlen für viele Kategorien).
        color:          Einzelfarbe für alle Balken. Standard: PALETTE_CATEGORICAL[0].
        ref_val:        Referenzlinie (None → kein Ref).
        highlight_top_n: Top-N Balken in PRIMARY_COLOR hervorheben, Rest in NEUTRAL.
        title:          Linksbündiger Titel.

    Returns:
        (fig, ax)

    Beispiel:
        fig, ax = wgnd.viz.bar(df["churn_rate"].sort_values(),
                               orient="h", ref_val=df["churn_rate"].mean(),
                               title="Churn Rate by City")
        plt.show()
    """
    style = mpl_style()

    if isinstance(data, pd.Series):
        cats   = data.index.tolist()
        values = data.values
    else:
        cats   = data[x].tolist()
        values = data[y].values

    n     = len(cats)
    c     = color or cfg.PALETTE_CATEGORICAL[0]
    colors = [c] * n

    if highlight_top_n:
        sorted_idx = np.argsort(values)[::-1]
        colors = [cfg.COLOR_NEUTRAL] * n
        for i in sorted_idx[:highlight_top_n]:
            colors[i] = cfg.PALETTE_CATEGORICAL[0]

    fig, ax = plt.subplots(figsize=figsize or cfg.MPL_FIGSIZE)

    if orient == "h":
        ax.barh(cats, values, color=colors, edgecolor="none")
        if ref_val is not None:
            ax.axvline(ref_val, **style["signal"], label=f"{ref_label}: {ref_val:.1f}")
            ax.text(ref_val * 1.01, 0, f"{ref_label}: {ref_val:.1f}",
                    va="bottom", ha="left", fontsize=10, color=cfg.COLOR_SIGNAL)
        ax.set_xlabel(ylabel or "", **style["label"])
        ax.set_ylabel("", **style["label"])
    else:
        ax.bar(cats, values, color=colors, edgecolor="none")
        if ref_val is not None:
            ax.axhline(ref_val, **style["signal"], label=f"{ref_label}: {ref_val:.1f}")
        ax.set_xlabel(xlabel or "", **style["label"])
        ax.set_ylabel(ylabel or "", **style["label"])
        plt.xticks(rotation=45, ha="right")

    ax.set_title(title, **style["title"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(cfg.CHART_AXIS)
    ax.tick_params(colors=cfg.CHART_AXIS_TEXT, labelsize=11)
    ax.grid(axis="x" if orient == "h" else "y",
            color=cfg.CHART_GRID, linewidth=0.8)
    plt.tight_layout()
    return fig, ax


def stacked_bar(
    df: pd.DataFrame,
    cat_col: str,
    target_col: str,
    normalize: bool = True,
    colors: list | None = None,
    title: str = "",
    orient: str = "v",
    figsize: tuple | None = None,
) -> tuple:
    """
    Gestapelter Balken (Prozent oder absolut).

    Typischer Einsatz: Churn-Rate nach Kundengruppe.

    Args:
        normalize: True → 0–100%, False → absolute Zahlen.
        colors:    Farbliste pro Zielwert. Standard: [NEUTRAL, CATEGORICAL[0]].

    Returns:
        (fig, ax)
    """
    style = mpl_style()
    ct    = pd.crosstab(df[cat_col], df[target_col], normalize="index" if normalize else False)
    if normalize:
        ct *= 100

    c  = colors or [cfg.COLOR_NEUTRAL, cfg.PALETTE_CATEGORICAL[0]]
    fig, ax = plt.subplots(figsize=figsize or cfg.MPL_FIGSIZE)

    ct.plot(kind="barh" if orient == "h" else "bar", stacked=True,
            color=c[:len(ct.columns)], ax=ax, edgecolor="none", width=0.7)

    if normalize:
        suffix = "%"
        lim    = [0, 100]
        if orient == "h":
            ax.set_xlim(*lim)
        else:
            ax.set_ylim(*lim)

    ax.set_title(title or f"{target_col} rate by {cat_col}", **style["title"])
    ax.set_xlabel("" if orient == "h" else "", **style["label"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(cfg.CHART_AXIS)
    ax.tick_params(colors=cfg.CHART_AXIS_TEXT)
    if orient == "v":
        plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig, ax


def dual_axis(
    df: pd.DataFrame,
    x: str,
    y_bar: str,
    y_line: str,
    bar_color: str | None = None,
    line_color: str | None = None,
    ref_val: float | None = None,
    title: str = "",
    figsize: tuple | None = None,
) -> tuple:
    """
    Doppelachsen-Chart: Balken (links) + Linie (rechts).

    Typischer Einsatz: Volumen (Balken) + Rate/Risiko (Linie).

    Returns:
        (fig, ax1, ax2)
    """
    style = mpl_style()
    bc    = bar_color  or cfg.PALETTE_CATEGORICAL[0]
    lc    = line_color or cfg.COLOR_NEGATIVE

    fig, ax1 = plt.subplots(figsize=figsize or (14, 6))

    ax1.bar(df[x], df[y_bar], color=bc, alpha=0.8, edgecolor="none", width=0.7)
    ax1.set_ylabel(y_bar, color=bc, fontsize=12, labelpad=8)
    ax1.tick_params(axis="y", labelcolor=bc)
    plt.xticks(rotation=45, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(df[x], df[y_line], color=lc, linewidth=2, marker="o",
             markersize=4, label=y_line)
    ax2.set_ylabel(y_line, color=lc, fontsize=12, labelpad=8)
    ax2.tick_params(axis="y", labelcolor=lc)

    if ref_val is not None:
        ax2.axhline(ref_val, color=lc, linestyle="--", linewidth=1.2, alpha=0.6,
                    label=f"Ø {ref_val:.3f}")

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper right", frameon=True, fontsize=10)

    ax1.set_title(title or f"{y_bar} vs. {y_line}", **style["title"])
    ax1.spines[["top"]].set_visible(False)
    ax1.grid(axis="y", color=cfg.CHART_GRID, linewidth=0.8)
    plt.tight_layout()
    return fig, ax1, ax2


def line(
    data: pd.Series | pd.DataFrame,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    ref_lines: list[dict] | None = None,
    spans: list[dict] | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple | None = None,
) -> tuple:
    """
    Liniendiagramm mit optionalen Referenzlinien und Span-Markierungen.

    Args:
        ref_lines: [{"y": 0.5, "label": "Threshold", "style": "signal"}]
                   style: 'signal' (amber), 'refline' (grau), 'neg' (rot)
        spans:     [{"x0": 3, "x1": 5, "label": "Risk Zone",
                     "color": cfg.PALETTE_CATEGORICAL[0], "alpha": 0.15}]

    Returns:
        (fig, ax)
    """
    style = mpl_style()
    fig, ax = plt.subplots(figsize=figsize or cfg.MPL_FIGSIZE)

    if isinstance(data, pd.Series):
        ax.plot(data.index, data.values,
                color=cfg.PALETTE_CATEGORICAL[0], linewidth=1.8)
    else:
        if hue:
            for i, (name, group) in enumerate(data.groupby(hue)):
                c = cfg.PALETTE_CATEGORICAL[i % len(cfg.PALETTE_CATEGORICAL)]
                ax.plot(group[x], group[y], color=c, linewidth=1.8, label=str(name))
            ax.legend()
        else:
            ax.plot(data[x], data[y], color=cfg.PALETTE_CATEGORICAL[0], linewidth=1.8)

    for rl in (ref_lines or []):
        s   = rl.get("style", "refline")
        kw  = dict(style.get(s, style["refline"]))
        kw["label"] = rl.get("label", "")
        ax.axhline(rl["y"], **kw)

    for sp in (spans or []):
        ax.axvspan(sp["x0"], sp["x1"],
                   color=sp.get("color", cfg.PALETTE_CATEGORICAL[0]),
                   alpha=sp.get("alpha", 0.15),
                   label=sp.get("label", ""))

    ax.set_title(title, **style["title"])
    ax.set_xlabel(xlabel, **style["label"])
    ax.set_ylabel(ylabel, **style["label"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(cfg.CHART_AXIS)
    if ref_lines or spans:
        ax.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    return fig, ax


def scatter_highlight(
    df: pd.DataFrame,
    x: str,
    y: str,
    highlight_mask: pd.Series | None = None,
    hue: str | None = None,
    ref_h: float | None = None,
    ref_v: float | None = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple | None = None,
) -> tuple:
    """
    Scatterplot mit Hintergrund-/Highlight-Gruppe.

    Typischer Einsatz: Outlier sichtbar machen oder Risiko-Gruppe markieren.

    Args:
        highlight_mask: Boolean-Maske für hervorgehobene Punkte.
                        True → Highlight-Farbe, False → dezentes Grau.
        hue:            Alternativ zur Maske: Farbgruppierung nach Spalte.
        ref_h:          Horizontale Referenzlinie.
        ref_v:          Vertikale Referenzlinie.

    Returns:
        (fig, ax)
    """
    style = mpl_style()
    fig, ax = plt.subplots(figsize=figsize or cfg.MPL_FIGSIZE)

    if highlight_mask is not None:
        ax.scatter(
            df.loc[~highlight_mask, x], df.loc[~highlight_mask, y],
            color=cfg.COLOR_NEUTRAL, alpha=0.3, s=15, label="Normal",
        )
        ax.scatter(
            df.loc[highlight_mask, x], df.loc[highlight_mask, y],
            color=cfg.COLOR_NEGATIVE, alpha=0.8, s=30, edgecolor="white",
            linewidth=0.5, label="Highlighted",
        )
    elif hue:
        uvals = sorted(df[hue].dropna().unique())
        for i, v in enumerate(uvals):
            sub = df[df[hue] == v]
            ax.scatter(sub[x], sub[y],
                       color=cfg.PALETTE_CATEGORICAL[i % len(cfg.PALETTE_CATEGORICAL)],
                       alpha=0.5, s=20, label=str(v))
        ax.legend(title=hue, fontsize=10)
    else:
        ax.scatter(df[x], df[y], color=cfg.PALETTE_CATEGORICAL[0], alpha=0.5, s=20)

    if ref_h is not None:
        ax.axhline(ref_h, **style["signal"])
    if ref_v is not None:
        ax.axvline(ref_v, **style["signal"])

    ax.set_title(title or f"{y} vs. {x}", **style["title"])
    ax.set_xlabel(xlabel or x, **style["label"])
    ax.set_ylabel(ylabel or y, **style["label"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(cfg.CHART_AXIS)
    plt.tight_layout()
    return fig, ax


def grid_histplot(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    hue: str | None = None,
    multiple: str = "stack",
    n_cols: int = 3,
    ref_line: float | None = None,
    figsize_per_plot: tuple = (6, 4),
) -> tuple:
    """
    Grid von Histogrammen – alle numerischen Spalten auf einmal.

    Typischer Einsatz: Verteilung aller Features nach Zielvariable.

    Args:
        multiple: 'stack', 'fill' (relative Anteile), 'layer', 'dodge'.
        ref_line: Horizontale Referenzlinie (z.B. globaler Mittelwert).

    Returns:
        (fig, axes)

    Beispiel:
        fig, axes = grid_histplot(df, hue="is_churned", multiple="fill",
                                   ref_line=df["is_churned"].mean())
        plt.show()
    """
    style     = mpl_style()
    num_cols  = columns or df.select_dtypes(include="number").columns.tolist()
    n_rows    = math.ceil(len(num_cols) / n_cols)
    fw, fh    = figsize_per_plot
    fig, axes = plt.subplots(n_rows, n_cols,
                             figsize=(fw * n_cols, fh * n_rows))
    axes_flat = axes.flatten() if n_rows > 1 else np.array(axes).flatten()

    palette = None
    if hue and hue in df.columns:
        uvals   = sorted(df[hue].dropna().unique())
        palette = {v: cfg.PALETTE_CATEGORICAL[i % len(cfg.PALETTE_CATEGORICAL)]
                   for i, v in enumerate(uvals)}

    for i, col in enumerate(num_cols):
        ax = axes_flat[i]
        sns.histplot(
            data=df, x=col, hue=hue, multiple=multiple,
            palette=palette, ax=ax, bins=20, common_norm=False,
            alpha=0.75,
        )
        if ref_line is not None:
            ax.axhline(ref_line, color=cfg.CHART_AXIS_TEXT,
                       linestyle="--", linewidth=1.5,
                       label=f"Ref: {ref_line:.2f}")
        ax.set_title(f"{col}", **style["title"])
        ax.set_xlabel("", **style["label"])
        ax.spines[["top", "right"]].set_visible(False)

    for j in range(len(num_cols), len(axes_flat)):
        axes_flat[j].axis("off")

    plt.tight_layout()
    return fig, axes


def grid_scatter(
    df: pd.DataFrame,
    combinations: list[tuple[str, str]],
    hue: str | None = None,
    ref_diagonal: bool = False,
    n_cols: int = 3,
    title: str = "",
    figsize_per_plot: tuple = (6, 5),
) -> tuple:
    """
    Grid von Scatterplots für definierte Feature-Kombinations-Liste.

    Typischer Einsatz: strategische Scatterplot-Paare für Risiko-Analyse.

    Args:
        combinations: Liste von (x, y) Spaltenpaaren.
        ref_diagonal: True → 45°-Diagonale einzeichnen (Preis-Vergleiche).

    Returns:
        (fig, axes)
    """
    style    = mpl_style()
    n_plots  = len(combinations)
    n_rows   = math.ceil(n_plots / n_cols)
    fw, fh   = figsize_per_plot
    fig, axes = plt.subplots(n_rows, n_cols,
                              figsize=(fw * n_cols, fh * n_rows))
    axes_flat = np.array(axes).flatten()

    palette = None
    if hue and hue in df.columns:
        uvals   = sorted(df[hue].dropna().unique())
        palette = {v: cfg.PALETTE_CATEGORICAL[i % len(cfg.PALETTE_CATEGORICAL)]
                   for i, v in enumerate(uvals)}

    for i, (xf, yf) in enumerate(combinations):
        ax = axes_flat[i]
        sns.scatterplot(data=df, x=xf, y=yf, hue=hue,
                        palette=palette, alpha=0.4, s=25, ax=ax, linewidth=0)
        if ref_diagonal:
            lims = [
                min(df[xf].min(), df[yf].min()),
                max(df[xf].max(), df[yf].max()),
            ]
            ax.plot(lims, lims, color=cfg.COLOR_NEUTRAL,
                    linestyle="--", linewidth=1, alpha=0.7)
        ax.set_title(f"{xf}\nvs. {yf}", **style["title"])
        ax.spines[["top", "right"]].set_visible(False)

    for j in range(n_plots, len(axes_flat)):
        fig.delaxes(axes_flat[j])

    if title:
        fig.suptitle(title, fontsize=14, color=cfg.CHART_TITLE,
                     ha="left", x=0.04, y=1.01)
    plt.tight_layout()
    return fig, axes
