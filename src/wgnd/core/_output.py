"""
core/_output.py
---------------
Zentrales Output-Modul: alles was der User sieht geht durch hier.

Drei Output-Kanäle:
  1. section_header()  – Teal-Trennlinie zwischen Sektionen
  2. info_box()        – Rich Panel für kompakte Key-Value Ausgaben
  3. show_df()         – pandas DataFrame mit IPython.display() (Notebook)
                         oder Plaintext-Fallback (Terminal / Script)

Internes Logging (Fehler, Warnungen) nutzt das Standard-logging-Modul –
NICHT für User-Output bestimmt, sondern für Debugging.

Alle anderen wgnd-Module importieren ausschließlich von hier:
    from wgnd.core._output import section_header, show_df, info_box, warn
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from wgnd.core.config import cfg

# ── Öffentliche Console-Instanz (für info_box und eigene Rich-Ausgaben) ───
console = Console()

# ── Interner Logger ───────────────────────────────────────────────────────
_log = logging.getLogger("wgnd")


def _c(hex_color: str) -> str:
    """Hex-Farbe → ANSI true-color escape (Vordergrund)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"

_RESET = "\033[0m"
_BOLD  = "\033[1m"


# ═════════════════════════════════════════════════════════════════════════════
# Öffentliche Output-Funktionen
# ═════════════════════════════════════════════════════════════════════════════

def section_header(title: str) -> None:
    """Druckt eine farbige Trennlinie mit Titel."""
    pad = max(0, cfg.HEADER_LINE_WIDTH - len(title))
    print(f"\n{_BOLD}{_c(cfg.PRIMARY_COLOR)}{'─' * 3}  {title.upper()}  {'─' * pad}{_RESET}")


def info_box(data: dict[str, Any], title: str = "") -> None:
    """
    Rendert ein Rich Panel mit Key-Value Paaren.

    Ideal für kompakte Zusammenfassungen (z.B. inspect_dimensions):
        ╭─ DIMENSIONS ──────────────────────────────╮
        │  shape      (891 × 12)                    │
        │  memory     83.7 KB                       │
        ╰───────────────────────────────────────────╯

    Args:
        data:  Geordnetes Dict: Label → Wert.
        title: Paneltitel (leer = kein Titel in der Rahmenzeile).
    """
    table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    table.add_column(style=f"dim", min_width=18, no_wrap=True)
    table.add_column()

    for key, val in data.items():
        table.add_row(str(key), str(val))

    panel_title = f"[bold {cfg.PRIMARY_COLOR}]{title}[/]" if title else None
    console.print(
        Panel(
            table,
            title=panel_title,
            title_align="left",
            border_style=cfg.PRIMARY_COLOR,
            padding=cfg.PANEL_PADDING,
        )
    )


def show_df(
    df: pd.DataFrame,
    caption: str | None = None,
    highlight_col: str | None = None,
    highlight_threshold: float = 0.0,
    highlight_style: str | None = None,
    show_index: bool = True,
) -> None:
    """
    Zeigt einen DataFrame an – mit HTML-Styling in Jupyter, Plaintext sonst.

    Stil:
      - Text immer schwarz
      - Gerade/ungerade Zeilen abwechselnd weiß / hellgrau
      - Header: etwas dunkleres Grau
      - Highlights für auffällige Werte in roter Schrift

    Args:
        df:                  Der anzuzeigende DataFrame.
        caption:             Optionaler Text oberhalb der Tabelle.
        highlight_col:       Spaltenname, in dem Werte > threshold hervorgehoben werden.
        highlight_threshold: Schwellwert für die Hervorhebung.
        highlight_style:     CSS-Style-String. Standard: rote Schrift.
    """
    if caption:
        print(f"{_c(cfg.DIM_COLOR)}{caption}{_RESET}")

    try:
        from IPython.display import display as ipy_display  # type: ignore

        _highlight_style = highlight_style or f"color: {cfg.ERROR_COLOR}; font-weight: 500"

        # Spalten-Typen klassifizieren
        float_cols = df.select_dtypes(include="float").columns.tolist()
        num_cols   = df.select_dtypes(include="number").columns.tolist()

        # Prozent-Spalten: Name enthält 'pct' oder endet auf '_%'
        pct_cols    = [c for c in float_cols
                       if "pct" in str(c).lower() or str(c).endswith("_%")]
        other_float = [c for c in float_cols if c not in pct_cols]

        # Formatierung: pct → 2 Stellen + %, rest → DECIMAL_PLACES Stellen
        fmt = {}
        for col in pct_cols:
            fmt[col] = f"{{:.2f}}%"
        for col in other_float:
            fmt[col] = f"{{:.{cfg.DECIMAL_PLACES}f}}"

        styler = (
            df.style
            .format(fmt)
            .set_table_styles([
            # ── Header ────────────────────────────────────────────────
            {"selector": "thead th", "props": [
                ("background-color", cfg.TABLE_HEADER_BG),
                ("color",            cfg.TABLE_TEXT),
                ("font-size",        "12px"),
                ("font-weight",      "500"),
                ("padding",          "5px 14px 5px 0"),
                ("border-bottom",    f"1px solid {cfg.CHART_AXIS}"),
                ("text-align",       "left"),
            ]},
            # ── Datenzellen ───────────────────────────────────────────
            {"selector": "td", "props": [
                ("font-size",  "12px"),
                ("padding",    "3px 14px 3px 0"),
                ("color",      cfg.TABLE_TEXT),
            ]},
            # ── Gerade Zeilen ─────────────────────────────────────────
            {"selector": "tr:nth-child(even) td", "props": [
                ("background-color", cfg.TABLE_ROW_EVEN),
            ]},
            # ── Ungerade Zeilen ───────────────────────────────────────
            {"selector": "tr:nth-child(odd) td", "props": [
                ("background-color", cfg.TABLE_ROW_ODD),
            ]},
            # ── Hover ─────────────────────────────────────────────────
            {"selector": "tr:hover td", "props": [
                ("background-color", "#eef3f8"),
            ]},
        ])
        )
        if num_cols:
            styler = styler.apply(
                lambda col: [
                    "text-align: right" if col.name in num_cols else "text-align: left"
                    for _ in col
                ],
                axis=0,
            )
        if not show_index:
            styler = styler.hide(axis="index")

        if highlight_col and highlight_col in df.columns:
            styler = styler.map(
                lambda v: _highlight_style
                if isinstance(v, (int, float)) and v > highlight_threshold
                else "",
                subset=[highlight_col],
            )

        ipy_display(styler)

    except ImportError:
        print(df.to_string(index=False, max_rows=cfg.MAX_DISPLAY_ROWS))


def warn(msg: str) -> None:
    """Zeigt eine gelbe Warnmeldung."""
    print(f"{_c(cfg.WARN_COLOR)}⚠  {msg}{_RESET}")
    _log.warning(msg)


def error(msg: str) -> None:
    """Zeigt eine rote Fehlermeldung."""
    print(f"{_BOLD}{_c(cfg.ERROR_COLOR)}✗  {msg}{_RESET}")
    _log.error(msg)


def success(msg: str) -> None:
    """Zeigt eine grüne Erfolgsmeldung."""
    print(f"{_c(cfg.PRIMARY_COLOR)}✓  {msg}{_RESET}")


def log(msg: str, symbol: str | None = None, color: str | None = None) -> None:
    """Neutrale Ausgabe. Symbol und Farbe optional."""
    prefix = f"{symbol}  " if symbol else ""
    clr    = color or cfg.PRIMARY_COLOR
    print(f"{_c(clr)}{prefix}{msg}{_RESET}")
