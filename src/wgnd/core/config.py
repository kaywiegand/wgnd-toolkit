"""
core/config.py
--------------
Einzige Stelle um den Look von wgnd anzupassen.

Struktur:
  Zahlen & Formate   DECIMAL_PLACES, MPL_FIGSIZE, ...
  Farb-Rollen        COLOR_SIGNAL, COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_NEUTRAL
  Paletten           PALETTE_CATEGORICAL, PALETTE_DUAL, PALETTE_SEQ, PALETTE_DIV
  Chart-Basis        CHART_BG, CHART_GRID, CHART_AXIS, ...
  Tabellen           TABLE_*
  Analyse            CORR_HIGH_THRESHOLD, IQR_MULTIPLIER

Paletten-Konzept:
  CATEGORICAL  → mehrere Kategorien unterscheiden (10 Farben, viridis+PRGn Familie)
  DUAL         → exakt 2 Kategorien (max. Kontrast)
  SEQ          → Intensität / Magnitude als Colormap-Name → cfg.PALETTE_SEQ
  DIV          → Abweichung von Nullpunkt als Colormap-Name → cfg.PALETTE_DIV

Verwendung:
    from wgnd.core.config import cfg
    cfg.PALETTE_CATEGORICAL       # Liste von 10 Hex-Farben
    cfg.PALETTE_DUAL              # [dunkel-lila, gelb-grün]
    cfg.PALETTE_SEQ               # "viridis"  → sns.color_palette(cfg.PALETTE_SEQ)
    cfg.PALETTE_DIV               # "PRGn"     → sns.color_palette(cfg.PALETTE_DIV)
    cfg.COLOR_SIGNAL              # Amber
    cfg.ACTIVE_PALETTE            # aktuell gesetzte Palette (default: CATEGORICAL)
"""


class WgndConfig:

    # ── Zahlen & Formate ──────────────────────────────────────────────────
    DECIMAL_PLACES:   int         = 2
    MPL_FIGSIZE: tuple[int, int]  = (12, 6)
    MPL_DPI:     int              = 120

    # ── UI / rich-Output ──────────────────────────────────────────────────
    PRIMARY_COLOR: str = "#34618d"   # Header, Panels
    WARN_COLOR:    str = "#ffa600"   # Package-Warnungen
    ERROR_COLOR:   str = "#de425b"   # Fehler, kritische Werte
    DIM_COLOR:     str = "#6b6b6b"   # Sekundärtext

    # ── Signal-Farben ─────────────────────────────────────────────────────
    COLOR_SIGNAL:   str = "#ffa600"   # Amber  → Schwellwert, Trendlinie
    COLOR_POSITIVE: str = "#25ac82"   # Teal-Grün  → positiv (aus CATEGORICAL [6])
    COLOR_NEGATIVE: str = "#de425b"   # Rot    → negativ / Risiko
    COLOR_NEUTRAL:  str = "#8c8c8c"   # Grau   → neutrale Referenzlinie

    # ── Annotation-Farben — fix, palette-unabhängig ───────────────────────
    ANNO_MEAN:     str = "#ffa600"   # Amber  → Mittelwert-Linie
    ANNO_MEDIAN:   str = "#34618d"   # Blau   → Median-Linie
    ANNO_IQR_SOFT: str = "#ffa600"   # Amber  → 1.5× IQR Bounds
    ANNO_IQR_HARD: str = "#de425b"   # Rot    → 3× IQR Bounds
    ANNO_REF:      str = "#8c8c8c"   # Grau   → neutrale Referenzlinie

    # ── Paletten ──────────────────────────────────────────────────────────
    # Categorical: 10 Farben aus viridis + PRGn Familie — perceptually distinct
    PALETTE_CATEGORICAL: list[str] = [
        "#481c6e",   # [0] dunkel lila  (viridis)
        "#894f98",   # [1] lila         (PRGn)
        "#34618d",   # [2] blau         (viridis)
        "#c4a8d0",   # [3] hell lila    (PRGn)
        "#24878e",   # [4] teal         (viridis)
        "#a9dca3",   # [5] hell grün    (PRGn)
        "#25ac82",   # [6] grün-teal    (viridis)
        "#3c954d",   # [7] dunkel grün  (PRGn)
        "#98d83e",   # [8] gelb-grün    (viridis)
        "#146b30",   # [9] sehr dunkel grün (PRGn)
    ]

    # Dual: 2 Farben mit maximalem Kontrast — für binäre Vergleiche
    PALETTE_DUAL: list[str] = [
        "#481c6e",   # dunkel lila  (CATEGORICAL[0])
        "#98d83e",   # gelb-grün    (CATEGORICAL[8])
    ]

    # Sequential + Diverging: Seaborn/Matplotlib Colormap-Namen
    PALETTE_SEQ: str = "viridis"   # für Heatmaps, Intensität
    PALETTE_DIV: str = "PRGn"      # für Abweichungen von Nullpunkt

    # Farblisten für LinearSegmentedColormap.from_list() und ähnliche APIs
    # Konsistent mit PALETTE_DIV (PRGn-Familie) und PALETTE_CATEGORICAL
    PALETTE_DIVERGENT: list[str] = [
        "#762a83",  # dunkel lila  (PRGn Extrem neg)
        "#9970ab",  # mittel lila
        "#c2a5cf",  # hell lila
        "#f7f7f7",  # Creme/Weiß  (Nullpunkt)
        "#a6dba0",  # hell grün
        "#5aae61",  # mittel grün
        "#1b7837",  # dunkel grün (PRGn Extrem pos)
    ]

    PALETTE_BLUE_RANGE: list[str] = [
        "#084594",  # dunkel blau (Sequential, Intensität hoch)
        "#2171b5",
        "#4292c6",
        "#6baed6",
        "#9ecae1",
        "#c6dbef",
        "#deebf7",  # hell blau  (Intensität niedrig)
    ]

    PALETTE_OCEAN: list[str] = [
        "#1a3a5c",  # dunkel navy
        "#2E86AB",  # blau
        "#45b7d1",  # hell blau
        "#96e6a1",  # hell grün
        "#d4a843",  # amber
        "#e07b39",  # orange
        "#c0392b",  # rot
    ]

    PALETTE_PINK_TEAL: list[str] = [
        "#c51b7d",  # dunkel pink
        "#de77ae",
        "#f1b6da",
        "#fde0ef",
        "#e6f5d0",
        "#b8e186",
        "#7fbc41",
        "#4d9221",
        "#25ac82",  # teal (aus CATEGORICAL)
        "#276419",  # dunkel grün
    ]

    # ── Standard-Palette ──────────────────────────────────────────────────
    PALETTE_STANDARD = PALETTE_CATEGORICAL

    def __init__(self) -> None:
        self.ACTIVE_PALETTE: list[str] = self.PALETTE_STANDARD

    def palette_n(self, n: int) -> list[str]:
        """Pick n evenly-spaced colors from PALETTE_CATEGORICAL.

        Immer gleichmäßig über die Palette verteilt — kein hardcoding von Indices.
        n=2 gibt PALETTE_DUAL zurück (garantierter Max-Kontrast).

        Beispiele:
            colors = cfg.palette_n(3)   # 3 Farben, gleichmäßig verteilt
            colors = cfg.palette_n(2)   # DUAL: [dunkel-lila, gelb-grün]
        """
        if n <= 0:
            return []
        if n == 1:
            return [self.PALETTE_CATEGORICAL[0]]
        if n == 2:
            return self.PALETTE_DUAL
        palette = self.PALETTE_CATEGORICAL
        if n >= len(palette):
            return palette
        indices = [round(i * len(palette) / n) for i in range(n)]
        return [palette[i] for i in indices]

    def use_palette(self, name: str, n: int = 10, show: bool = False) -> None:
        """
        Aktive Palette wechseln.

        Eigene Paletten:    'categorical', 'dual'
        Seaborn-Paletten:   beliebiger Seaborn-Name, n = Anzahl Farben

        Beispiele:
            cfg.use_palette("categorical")
            cfg.use_palette("tab10")
            cfg.use_palette("viridis", n=8, show=True)
        """
        registry = {
            "categorical": self.PALETTE_CATEGORICAL,
            "dual":        self.PALETTE_DUAL,
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
    HEADER_LINE_WIDTH: int             = 55
    MAX_DISPLAY_ROWS:  int             = 20

    # ── Analyse ───────────────────────────────────────────────────────────
    CORR_HIGH_THRESHOLD: float = 0.8
    CORR_MID_THRESHOLD:  float = 0.5
    IQR_MULTIPLIER:      float = 1.5


cfg = WgndConfig()


def _is_dark(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140
