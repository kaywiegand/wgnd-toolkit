# wgnd · Wiegand Data Toolkit

> Wiederverwendbare Bausteine für DAN & DSC Projekte.
> Konsistenter Workflow, einheitlicher Look, null Boilerplate.

---

## Inhaltsverzeichnis

1. [VS Code Setup — Beispiel-Notebook öffnen](#1-vs-code-setup--beispiel-notebook-öffnen)
2. [Package in ein Projekt einbinden](#2-package-in-ein-projekt-einbinden)
3. [Package-Struktur](#3-package-struktur)
4. [Module im Überblick](#4-module-im-überblick)
5. [Chart-Guide — einheitlicher Look](#5-chart-guide--einheitlicher-look)
6. [Konfiguration anpassen](#6-konfiguration-anpassen)
7. [Tests](#7-tests)

---

## 1 · VS Code Setup — Beispiel-Notebook öffnen

### Schritt 1 — Ordner in VS Code öffnen

**Datei → Ordner öffnen** → den `wgnd-toolkit/` Ordner auswählen.

```
wgnd-toolkit/
├── src/wgnd/
├── examples/
│   ├── data/customers.csv
│   └── wgnd_examples.ipynb
├── tests/
└── pyproject.toml
```

### Schritt 2 — Terminal öffnen: **Strg + `**

### Schritt 3 — Python + Jupyter Extension (einmalig)

**Strg + Shift + X** → `Python` (Microsoft) + `Jupyter` (Microsoft) installieren.

### Schritt 4 — Umgebung einrichten

```bash
pip install uv                    # uv einmalig installieren

uv venv                           # .venv/ erstellen

source .venv/bin/activate         # Mac/Linux
.venv\Scripts\activate            # Windows

uv pip install -e ".[dev]"        # alle Dependencies + wgnd selbst

python -m ipykernel install --user --name wgnd --display-name "Python (wgnd)"
```

### Schritt 5 — Notebook öffnen

`examples/wgnd_examples.ipynb` doppelklicken → Kernel **Python (wgnd)** wählen → **Run All**.

> **Häufige Probleme**
>
> `ModuleNotFoundError: wgnd` → Kernel-Picker: ist **Python (wgnd)** gewählt?
> Wenn nicht: Schritte 4 wiederholen, VS Code neu starten.

---

## 2 · Package in ein Projekt einbinden

```toml
# pyproject.toml des Projekts
dependencies = [
    "wgnd @ git+https://github.com/kaywiegand/wgnd-toolkit.git@main",
]
```

```bash
uv pip install -e ".[dan]"   # DAN-Projekt
uv pip install -e ".[dsc]"   # DSC-Projekt (+ sklearn, xgboost, shap)
```

**Nach jedem Push ins wgnd-toolkit — Update ziehen:**

```bash
uv pip install -e ".[dan]" --refresh-package wgnd
# → Kernel neu starten
```

**Erste Zelle jedes Notebooks:**

```python
from ny_taxi_routes.notebook import *
setup_plotting()
```

---

## 3 · Package-Struktur

```
wgnd-toolkit/
├── src/wgnd/
│   ├── core/
│   │   ├── config.py       ← Farben, Paletten, Größen (einzige Wahrheitsquelle)
│   │   ├── theme.py        ← setup(), apply_theme(), mpl_style()
│   │   └── _output.py      ← section_header(), info_box(), show_df(), log(), success(), warn()
│   │
│   ├── inspect.py          ← EDA: inspect() + 9 Sub-Funktionen
│   ├── viz.py              ← Charts (Matplotlib/Seaborn)
│   └── __init__.py         ← Direkt-Exports: setup, cfg, inspect, success, warn, log, ...
│
├── examples/
│   ├── data/customers.csv
│   └── wgnd_examples.ipynb
└── tests/
```

---

## 4 · Module im Überblick

### `wgnd.inspect` — EDA

| Funktion | Beschreibung |
|---|---|
| `inspect(df, sections=[...])` | Mehrere Sektionen auf einmal — gibt `None` zurück |
| `inspect_dimensions(df)` | Shape, Duplikate, leere Zeilen/Spalten |
| `inspect_dtypes(df)` | Datentypen, Missing, Eindeutigkeit |
| `inspect_missing(df)` | Fehlwert-Analyse + Heatmap |
| `inspect_duplicates(df)` | Duplizierte Zeilen |
| `inspect_names(df)` | Spaltennamen auf Sonderzeichen prüfen |
| `inspect_numeric_stats(df, columns=None, title="numeric stats")` | Deskriptive Statistik |
| `inspect_categorical_stats(df, columns=None, title="categorical stats")` | Häufigkeitsanalyse |
| `inspect_correlations(df)` | Korrelationsmatrix |
| `inspect_outliers(df)` | IQR-basierte Ausreißer-Übersicht |
| `inspect_outlier_detail(df, col)` | Detailanalyse einer Spalte |

```python
from wgnd import inspect
from wgnd.inspect import inspect_missing, inspect_numeric_stats

inspect(df)                                    # alle Sektionen, gibt None zurück
inspect(df, sections=["numeric", "missing"])   # Auswahl

result = inspect_missing(df)                   # einzelne Funktion gibt DataFrame zurück
result = inspect_numeric_stats(df, columns=["fare_amount", "trip_distance"],
                               title="numeric stats – fare & distance")
```

### Output-Funktionen

Alle direkt aus `wgnd` importierbar:

```python
from wgnd import success, warn, log, info_box, show_df, section_header

success("73% der Fahrten starten in Manhattan")
warn("15% fehlende Werte in 'dropoff_location'")
log("Median Fahrzeit: 12 min")
log("Auffälligkeit gefunden", symbol="→", color="orange")

info_box({"Median Fahrzeit": "12 min", "Ausreißer": "3.2%"}, title="Erkenntnisse")

show_df(df.head(10))                  # mit Index (Standard)
show_df(df.head(10), show_index=False) # ohne Index
```

### `wgnd.viz` — Charts

```python
from wgnd.viz import bar, bar_reference, scatter, distribution
from wgnd.viz import time_series, heatmap, pairplot, boxplot, stacked_bar_pct

fig, ax = bar(df, x="city", y="revenue", title="Revenue by City")
fig, ax = scatter(df, x="trip_distance", y="fare_amount")
```

---

## 5 · Chart-Guide — einheitlicher Look

### 5.1 Farbsystem

Alle Werte kommen aus `cfg` — nie hardcoded in Charts schreiben.

```python
from wgnd import cfg
# oder: from wgnd.core.config import cfg
```

**Signal-Farben** (sparsam einsetzen — nur wenn Semantik stimmt):

| Variable | Farbe | Wann benutzen |
|---|---|---|
| `cfg.COLOR_SIGNAL` | `#ffa600` Amber | Mittelwert-Linie, Trendlinie, Schwellwert |
| `cfg.COLOR_POSITIVE` | `#488f31` Grün | explizit positiv |
| `cfg.COLOR_NEGATIVE` | `#de425b` Rot | Risiko, Fehler, kritisch |
| `cfg.COLOR_NEUTRAL` | `#8c8c8c` Grau | neutrale Referenzlinien |

**Paletten:**

| Variable | Beschreibung | Einsatz |
|---|---|---|
| `cfg.ACTIVE_PALETTE` | Aktive Palette (Standard: Ocean) | bar, scatter, groupby |
| `cfg.PALETTE_OCEAN` | Blau → Orange (7 Farben) | kategorische Gruppen |
| `cfg.PALETTE_PINK_TEAL` | Pink → Teal (10 Farben) | zweite Datenserie |
| `cfg.PALETTE_BLUE_RANGE` | Sequential Blau dunkel→hell | Heatmaps |
| `cfg.PALETTE_DIVERGENT` | Grün ↔ Creme ↔ Rot | Korrelations-Heatmaps |

**Palette wechseln:**

```python
# Zur Laufzeit im Notebook:
cfg.use_palette("pink_teal")   # ocean | pink_teal | blue_range | blue_light

# Standard dauerhaft ändern — in src/wgnd/core/config.py:
PALETTE_STANDARD = PALETTE_BLUE_RANGE   # ← hier tauschen
```

---

### 5.2 Matplotlib — eigene Charts

```python
import matplotlib.pyplot as plt
from wgnd.core.theme import mpl_style
from wgnd import cfg

style = mpl_style()
fig, ax = plt.subplots(figsize=(12, 6))

data.plot(kind="barh", color=cfg.ACTIVE_PALETTE[0], ax=ax)

ax.set_title("Städte-Ranking", **style["title"])
ax.set_xlabel("Churn Rate", **style["label"])
ax.axvline(mean, **style["refline"], label=f"Ø {mean:.1f}")
ax.axvline(threshold, **style["signal"], label="Threshold")
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.show()
```

**Seaborn:**

```python
import seaborn as sns
from wgnd import cfg

sns.heatmap(corr_matrix,
    annot=True, fmt=".2f",
    cmap=cfg.PALETTE_DIVERGENT,
    center=0,
    linewidths=0.5,
)
```

---

## 6 · Konfiguration anpassen

Alle Einstellungen in `src/wgnd/core/config.py` — eine Änderung wirkt überall:

```python
class WgndConfig:
    # Standard-Palette — hier einmalig wechseln:
    PALETTE_STANDARD = PALETTE_OCEAN   # → PALETTE_BLUE_RANGE, PALETTE_PINK_TEAL, ...

    # Signal-Farben
    COLOR_SIGNAL   = "#ffa600"
    COLOR_POSITIVE = "#488f31"
    COLOR_NEGATIVE = "#de425b"
    COLOR_NEUTRAL  = "#8c8c8c"

    # Chart-Basis
    CHART_BG       = "#ffffff"
    CHART_GRID     = "#e8e8e8"
    CHART_AXIS     = "#b0b0b0"
    CHART_TITLE    = "#222222"

    # Tabellen
    TABLE_ROW_ODD   = "#ffffff"
    TABLE_ROW_EVEN  = "#f5f5f5"
    TABLE_HEADER_BG = "#e0e0e0"
    TABLE_TEXT      = "#000000"

    # Zahlen & Formate
    DECIMAL_PLACES = 3
```

---

## 7 · Tests

```bash
pytest tests/                                           # alle Tests
pytest tests/ -v --tb=short                             # verbose
pytest tests/ --cov=src/wgnd --cov-report=term-missing  # Coverage
```

---

_Entwickelt für DAN- und DSC-Projekte im Wiegand-Workflow._
