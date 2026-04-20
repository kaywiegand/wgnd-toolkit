"""
core/config.py  (theme_config)
------------------------------
Einzige Stelle um den Look von wgnd anzupassen.

Struktur:
  Zahlen & Formate   DECIMAL_PLACES, MPL_FIGSIZE, ...
  Farb-Rollen        COLOR_SIGNAL, COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_NEUTRAL
  Paletten           PALETTE_*  (kategorisch, sequential, divergent)
  Chart-Basis        CHART_BG, CHART_GRID, CHART_AXIS, ...
  Tabellen           TABLE_*
  Analyse            CORR_HIGH_THRESHOLD, IQR_MULTIPLIER

Verwendung:
    from wgnd.core.config import cfg
    cfg.COLOR_SIGNAL
    cfg.PALETTE_CATEGORICAL
    cfg.DECIMAL_PLACES
"""


class WgndConfig:

    # ── Zahlen & Formate ──────────────────────────────────────────────────
    DECIMAL_PLACES:   int   = 3      # Nachkommastellen überall im Package
    MPL_FIGSIZE: tuple[int,int] = (12, 6)
    MPL_DPI:     int   = 120

    # ── UI / rich-Output ──────────────────────────────────────────────────
    PRIMARY_COLOR: str = "#004c6d"   # Header, Panels
    WARN_COLOR:    str = "#ffa600"   # Package-Warnungen
    ERROR_COLOR:   str = "#de425b"   # Fehler, kritische Werte
    DIM_COLOR:     str = "#6b6b6b"   # Sekundärtext

    # ── Signal-Farben ─────────────────────────────────────────────────────
    # Sparsam einsetzen — nur wenn die Semantik stimmt.
    COLOR_SIGNAL:   str = "#ffa600"   # Amber  → Mittelwert, Trendlinie, Schwellwert
    COLOR_POSITIVE: str = "#488f31"   # Grün   → explizit positiv
    COLOR_NEGATIVE: str = "#de425b"   # Rot    → explizit negativ / Risiko
    COLOR_NEUTRAL:  str = "#8c8c8c"   # Grau   → neutrale Referenzlinie

    # ── Kategorische Palette — 7 Farben harmonisch ────────────────────────
    # Quelle: learnui.design  — keine Standard-Signalfarben
    # Einsatz: bar, scatter, pie, groupby
    PALETTE_CATEGORICAL: list[str] = [
        "#003d5c",   # Deep Blue
        "#31497e",   # Indigo
        "#674f95",   # Purple
        "#a14e9a",   # Violet
        "#d44c8d",   # Pink
        "#f9596f",   # Coral
        "#ff7a47",   # Orange
    ]

    # ── Pink → Teal — zweite kategorische Palette ─────────────────────────
    # Einsatz: zweite Datenserie, Vergleichs-Palette
    PALETTE_PINK_TEAL: list[str] = [
        "#d44c8d",
        "#f9596f",
        "#ff7a47",
        "#003d5c",
        "#00546e",
        "#006b71",
        "#008162",
        "#009446",
        "#65a31c",
        "#b1aa00",
    ]

    # ── Business Blues sequential (9 Stufen, dunkel→hell) ─────────────────
    # Einsatz: Heatmaps mit positivem Bereich, single-color Füllungen
    PALETTE_BLUE_RANGE: list[str] = [
        "#004c6d", "#215d7e", "#366e8f", "#4a80a1",
        "#5e93b3", "#71a5c6", "#84b9d9", "#98ccec", "#ace0ff",
    ]

    # ── Business Blues Light sequential ───────────────────────────────────
    PALETTE_BLUE_LIGHT: list[str] = [
        "#004c6d", "#125e7f", "#217192", "#3085a5", "#3e99b7",
        "#4dadc9", "#5dc2dc", "#6dd7ed", "#7eedff",
    ]

    # ── Divergente Palette (13 Stufen Grün↔Creme↔Rot) ────────────────────
    # Einsatz: Korrelations-Heatmaps, Abweichungen vom Nullpunkt
    PALETTE_DIVERGENT: list[str] = [
        "#00876c", "#4b9a76", "#75ad83", "#9bc193", "#bed4a7",
        "#e0e8be", "#fffcd7",
        "#f5e2b1", "#efc68f", "#eaa872", "#e5885e", "#de6553", "#d43d51",
    ]

    # ── Chart-Stil ────────────────────────────────────────────────────────
    CHART_BG:        str = "#ffffff"
    CHART_GRID:      str = "#e8e8e8"   # dezentes Hellgrau
    CHART_AXIS:      str = "#b0b0b0"   # Achsenlinien, etwas dunkler
    CHART_AXIS_TEXT: str = "#6b6b6b"   # Tick-Labels
    CHART_TITLE:     str = "#222222"   # fast schwarz
    CHART_LABEL:     str = "#444444"   # Achsen-Titel

    # ── Tabellen ──────────────────────────────────────────────────────────
    TABLE_ROW_ODD:   str = "#ffffff"
    TABLE_ROW_EVEN:  str = "#f5f5f5"
    TABLE_HEADER_BG: str = "#e0e0e0"
    TABLE_TEXT:      str = "#000000"   # immer schwarz

    # ── rich Panel ────────────────────────────────────────────────────────
    PANEL_PADDING:     tuple[int, int] = (0, 1)
    HEADER_LINE_WIDTH: int = 55
    MAX_DISPLAY_ROWS:  int = 20

    # ── Analyse ───────────────────────────────────────────────────────────
    CORR_HIGH_THRESHOLD: float = 0.8
    CORR_MID_THRESHOLD:  float = 0.5
    IQR_MULTIPLIER:      float = 1.5


cfg = WgndConfig()
