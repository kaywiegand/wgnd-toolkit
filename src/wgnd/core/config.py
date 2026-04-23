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
    COLOR_SIGNAL:   str = "#ffa600"   # Amber  → Schwellwert, Trendlinie
    COLOR_POSITIVE: str = "#488f31"   # Grün   → explizit positiv
    COLOR_NEGATIVE: str = "#de425b"   # Rot    → explizit negativ / Risiko
    COLOR_NEUTRAL:  str = "#8c8c8c"   # Grau   → neutrale Referenzlinie

    # ── Annotation-Farben — fix, palette-unabhängig ───────────────────────
    # Für Linien/Marker in Charts: Mean, Median, IQR-Bounds, Referenz.
    # Wechseln der ACTIVE_PALETTE hat keinen Einfluss darauf.
    ANNO_MEAN:     str = "#ffa600"   # Amber  → Mittelwert-Linie
    ANNO_MEDIAN:   str = "#004c6d"   # Dunkelblau → Median-Linie
    ANNO_IQR_SOFT: str = "#ffa600"   # Amber  → 1.5× IQR Bounds
    ANNO_IQR_HARD: str = "#de425b"   # Rot    → 3× IQR Bounds
    ANNO_REF:      str = "#8c8c8c"   # Grau   → neutrale Referenzlinie

    # ── Paletten ──────────────────────────────────────────────────────────
    # Alle Paletten stehen zur Auswahl — aktive Palette: cfg.ACTIVE_PALETTE
    # Wechseln mit: cfg.use_palette("ocean") oder cfg.use_palette("pink_teal")

    PALETTE_OCEAN: list[str] = [        # Standard — Blau → Orange (learnui.design)
        "#003d5c",   # Deep Blue
        "#31497e",   # Indigo
        "#674f95",   # Purple
        "#a14e9a",   # Violet
        "#d44c8d",   # Pink
        "#f9596f",   # Coral
        "#ff7a47",   # Orange
    ]

    PALETTE_PINK_TEAL: list[str] = [    # Pink → Teal
        "#d44c8d", "#f9596f", "#ff7a47",
        "#003d5c", "#00546e", "#006b71",
        "#008162", "#009446", "#65a31c", "#b1aa00",
    ]

    PALETTE_BLUE_RANGE: list[str] = [   # Sequential Blau dunkel→hell
        "#004c6d", "#215d7e", "#366e8f", "#4a80a1",
        "#5e93b3", "#71a5c6", "#84b9d9", "#98ccec", "#ace0ff",
    ]

    PALETTE_BLUE_LIGHT: list[str] = [   # Sequential Blau hell
        "#004c6d", "#125e7f", "#217192", "#3085a5", "#3e99b7",
        "#4dadc9", "#5dc2dc", "#6dd7ed", "#7eedff",
    ]

    PALETTE_DIVERGENT: list[str] = [    # Divergent Grün↔Creme↔Rot
        "#00876c", "#4b9a76", "#75ad83", "#9bc193", "#bed4a7",
        "#e0e8be", "#fffcd7",
        "#f5e2b1", "#efc68f", "#eaa872", "#e5885e", "#de6553", "#d43d51",
    ]

    # ── Standard-Palette — hier wechseln um den Default zu ändern ────────
    PALETTE_STANDARD = PALETTE_BLUE_RANGE

    def __init__(self) -> None:
        self.ACTIVE_PALETTE: list[str] = self.PALETTE_STANDARD

    def use_palette(self, name: str, n: int = 8, show: bool = False) -> None:
        """
        Aktive Palette wechseln.

        Eigene Paletten: 'ocean', 'pink_teal', 'blue_range', 'blue_light'
        Seaborn-Paletten: 'deep', 'muted', 'pastel', 'viridis', 'rocket', ...
            → beliebiger Seaborn-Name, n = Anzahl Farben

        Beispiel:
            cfg.use_palette("ocean")
            cfg.use_palette("viridis", n=6, show=True)
        """
        registry = {
            "ocean":      self.PALETTE_OCEAN,
            "pink_teal":  self.PALETTE_PINK_TEAL,
            "blue_range": self.PALETTE_BLUE_RANGE,
            "blue_light": self.PALETTE_BLUE_LIGHT,
        }
        if name in registry:
            self.ACTIVE_PALETTE = registry[name]
        else:
            import seaborn as sns
            try:
                self.ACTIVE_PALETTE = sns.color_palette(name, n).as_hex()
            except Exception:
                raise ValueError(
                    f"Unbekannte Palette: '{name}'. "
                    f"Eigene: {list(registry)} — oder beliebiger Seaborn-Name."
                )
        self._propagate_palette()
        if show:
            self.show_palette()

    def _propagate_palette(self) -> None:
        """Überträgt ACTIVE_PALETTE sofort auf matplotlib und seaborn."""
        try:
            import matplotlib as mpl
            mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=self.ACTIVE_PALETTE)
        except Exception:
            pass
        try:
            import seaborn as sns
            sns.set_palette(self.ACTIVE_PALETTE)
        except Exception:
            pass

    def show_palette(self) -> None:
        """Zeigt die aktive Palette als horizontalen Farbstreifen mit Index."""
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        colors = self.ACTIVE_PALETTE
        n = len(colors)
        fig, ax = plt.subplots(figsize=(n * 0.9, 0.8))

        for i, color in enumerate(colors):
            ax.add_patch(mpatches.Rectangle((i, 0), 1, 1, color=color))
            ax.text(i + 0.5, -0.25, str(i), ha="center", va="top",
                    fontsize=9, color="#444444")

        ax.set_xlim(0, n)
        ax.set_ylim(-0.4, 1)
        ax.axis("off")
        plt.tight_layout()
        plt.show()


    # ── Chart-Stil ────────────────────────────────────────────────────────
    CHART_BG:        str = "#ffffff"
    CHART_GRID:      str = "#e8e8e8"
    CHART_AXIS:      str = "#b0b0b0"
    CHART_AXIS_TEXT: str = "#6b6b6b"
    CHART_TITLE:     str = "#222222"
    CHART_LABEL:     str = "#444444"

    # ── Tabellen ──────────────────────────────────────────────────────────
    TABLE_ROW_ODD:   str = "#ffffff"
    TABLE_ROW_EVEN:  str = "#f5f5f5"
    TABLE_HEADER_BG: str = "#e0e0e0"
    TABLE_TEXT:      str = "#000000"

    # ── rich Panel ────────────────────────────────────────────────────────
    PANEL_PADDING:     tuple[int, int] = (0, 1)
    HEADER_LINE_WIDTH: int = 55
    MAX_DISPLAY_ROWS:  int = 20

    # ── Analyse ───────────────────────────────────────────────────────────
    CORR_HIGH_THRESHOLD: float = 0.8
    CORR_MID_THRESHOLD:  float = 0.5
    IQR_MULTIPLIER:      float = 1.5


cfg = WgndConfig()


def _is_dark(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140
