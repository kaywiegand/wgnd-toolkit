"""
core/theme.py
-------------
Matplotlib & Seaborn Theme für wgnd.

  setup()       Theme aktivieren (erste Notebook-Zelle)
  mpl_style()   kwargs-Dict für konsistente Achsengestaltung

Das Theme wird beim Import von wgnd automatisch aktiviert wenn
WGND_AUTO_SETUP=1 gesetzt ist. Manuell reicht:

    from wgnd.core.theme import setup
    setup()

Danach haben alle plt.* und sns.* Charts automatisch den richtigen Look.
"""

from __future__ import annotations
import warnings
from wgnd.core.config import cfg


def setup_matplotlib() -> None:
    """Setzt Matplotlib rcParams auf wgnd-Stil."""
    try:
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                plt.style.use("seaborn-v0_8-white")
            except OSError:
                plt.style.use("default")

        mpl.rcParams.update({
            # Figur
            "figure.figsize":     cfg.MPL_FIGSIZE,
            "figure.dpi":         cfg.MPL_DPI,
            "figure.facecolor":   cfg.CHART_BG,

            # Achsen
            "axes.facecolor":     cfg.CHART_BG,
            "axes.edgecolor":     cfg.CHART_AXIS,
            "axes.linewidth":     0.8,
            "axes.spines.top":    False,
            "axes.spines.right":  False,
            "axes.titlecolor":    cfg.CHART_TITLE,
            "axes.titlesize":     14,
            "axes.titleweight":   "normal",
            "axes.titlelocation": "left",    # Titel immer linksbündig
            "axes.titlepad":      14,
            "axes.labelcolor":    cfg.CHART_LABEL,
            "axes.labelsize":     12,
            "axes.labelpad":      8,
            "axes.prop_cycle":    mpl.cycler(color=cfg.ACTIVE_PALETTE),

            # Grid – dezent, nur horizontale Linien (sauberer)
            "axes.grid":          True,
            "axes.grid.axis":     "y",
            "grid.color":         cfg.CHART_GRID,
            "grid.linewidth":     0.8,

            # Ticks
            "xtick.color":        cfg.CHART_AXIS_TEXT,
            "ytick.color":        cfg.CHART_AXIS_TEXT,
            "xtick.labelsize":    11,
            "ytick.labelsize":    11,

            # Schrift
            "font.family":        "sans-serif",
            "font.size":          11,
            "text.color":         cfg.CHART_TITLE,

            # Legende
            "legend.frameon":     True,
            "legend.framealpha":  0.9,
            "legend.edgecolor":   cfg.CHART_GRID,
            "legend.fontsize":    10,

            # Linien
            "lines.linewidth":    1.8,
        })
    except Exception as e:
        warnings.warn(f"Matplotlib-Theme Fehler: {e}", stacklevel=2)


def setup_seaborn() -> None:
    """Setzt Seaborn-Defaults auf wgnd-Stil."""
    try:
        import seaborn as sns
        sns.set_theme(
            style="white",
            palette=cfg.ACTIVE_PALETTE,
            rc={
                "axes.spines.top":   False,
                "axes.spines.right": False,
                "axes.titlelocation": "left",
                "axes.titleweight":   "normal",
            }
        )
    except ImportError:
        pass


def setup() -> None:
    """
    Aktiviert wgnd-Theme für Matplotlib und Seaborn.

    Erste Code-Zelle in jedem Notebook:
        from wgnd.core.theme import setup
        setup()
    """
    setup_matplotlib()
    setup_seaborn()

    from wgnd.core._output import console
    console.print(
        f"[{cfg.PRIMARY_COLOR}]✓  wgnd theme activated[/] "
        f"[dim](matplotlib · seaborn)[/]"
    )


def mpl_style() -> dict:
    """
    kwargs-Dict für konsistente Matplotlib-Achsengestaltung.

    Nützlich für Custom-Charts mit direkten ax-Methoden.

    Beispiel:
        style = mpl_style()
        ax.set_title("Titel", **style["title"])
        ax.set_xlabel("X",    **style["label"])
        ax.axhline(mean,      **style["signal"])   # Amber: Mittelwert
        ax.axhline(ref,       **style["refline"])  # Grau: neutrale Linie
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["left","bottom"]].set_color(cfg.CHART_AXIS)
        ax.tick_params(colors=cfg.CHART_AXIS_TEXT, labelsize=11)
    """
    return {
        "title":   dict(loc="left", fontsize=14, color=cfg.CHART_TITLE,
                        pad=14, fontweight="normal"),
        "label":   dict(fontsize=12, color=cfg.CHART_LABEL, labelpad=8),
        "ticks":   dict(colors=cfg.CHART_AXIS_TEXT, labelsize=11),
        "refline": dict(color=cfg.COLOR_NEUTRAL, linewidth=1.2,
                        linestyle="--", alpha=0.8),
        "signal":  dict(color=cfg.COLOR_SIGNAL, linewidth=1.5,
                        linestyle="--", alpha=0.9),
        "pos":     dict(color=cfg.COLOR_POSITIVE, linewidth=1.5,
                        linestyle="--"),
        "neg":     dict(color=cfg.COLOR_NEGATIVE, linewidth=1.5,
                        linestyle="--"),
    }
