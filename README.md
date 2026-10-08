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
    "wgnd @ git+https://github.com/kaywiegand/wgnd-toolkit.git@v0.3.0",
    # DSC-Projekt (+ scikit-learn, xgboost, joblib):
    # "wgnd[dsc] @ git+https://github.com/kaywiegand/wgnd-toolkit.git@v0.3.0",
]
```

```bash
uv pip install -e .          # im Projekt — zieht wgnd mit
```

Der Tag fixiert die Version — ein Update heißt: Tag in der `pyproject.toml` anheben,
neu installieren, Kernel neu starten.

**Parallel am Toolkit entwickeln** — lokal verlinken statt Tag:

```bash
uv pip install -e ../wgnd-toolkit
# → Änderungen wirken nach Kernel-Neustart
```

**Erste Zelle jedes Notebooks:**

```python
from wgnd import setup, cfg, inspect
from wgnd import success, warn, log, info_box, show_df, section_header

setup()
```

---

## 3 · Package-Struktur

```
wgnd-toolkit/
├── src/wgnd/
│   ├── core/
│   │   ├── config.py       ← Farben, Paletten, Größen (einzige Wahrheitsquelle)
│   │   ├── theme.py        ← setup(), mpl_style()
│   │   └── _output.py      ← section_header(), info_box(), show_df(), log(), success(), warn(), error()
│   │
│   ├── inspect.py          ← EDA: inspect() + 11 Sub-Funktionen, iqr_values()
│   ├── viz.py              ← Charts (Matplotlib/Seaborn)
│   ├── models.py           ← ModelTracker + save_model (DSC, benötigt dsc-Extra)
│   ├── notes.py            ← EdaNotes: kategorisierter EDA-Notiz-Sammler
│   ├── utils.py            ← timer, memory_report, downcast
│   └── __init__.py         ← Direkt-Exports: setup, cfg, inspect, ModelTracker, EdaNotes, ...
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
| `inspect_memory(df)` | Speicherverbrauch |
| `inspect_dtypes(df)` | Datentypen, Missing, Eindeutigkeit |
| `inspect_missing(df)` | Fehlwert-Analyse + Heatmap |
| `inspect_duplicates(df)` | Duplizierte Zeilen |
| `inspect_names(df)` | Spaltennamen auf Sonderzeichen prüfen |
| `inspect_numeric_stats(df, columns=None, title="numeric stats")` | Deskriptive Statistik |
| `inspect_categorical_stats(df, columns=None, title="categorical stats")` | Häufigkeitsanalyse |
| `inspect_correlations(df)` | Korrelationsmatrix |
| `inspect_outliers(df)` | IQR-basierte Ausreißer-Übersicht |
| `inspect_outlier_detail(df, col)` | Detailanalyse einer Spalte |
| `iqr_values(df, col)` | IQR-Kennwerte einer Spalte als Dict |

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

Alle Funktionen geben `(fig, ax)` bzw. `(fig, axes)` zurück.

| Funktion | Beschreibung |
|---|---|
| `bar(data, x, y, orient="v", ref_val=None, highlight_top_n=None)` | Balken, optional Referenzlinie und Top-N-Highlight |
| `stacked_bar(df, cat_col, target_col, normalize=True)` | Gestapelte Balken, Prozent oder absolut |
| `dual_axis(df, x, y_bar, y_line)` | Balken links + Linie rechts — gibt `(fig, ax1, ax2)` zurück |
| `line(data, x, y, hue=None, ref_lines=None, spans=None)` | Linie mit Referenzlinien und Span-Markierungen |
| `scatter_highlight(df, x, y, highlight_mask=None, hue=None)` | Scatter mit hervorgehobener Gruppe |
| `grid_histplot(df, columns=None, hue=None, multiple="stack")` | Histogramm-Grid über numerische Spalten |
| `grid_scatter(df, combinations, hue=None)` | Scatter-Grid für `(x, y)`-Paare |
| `show_palettes()` | Alle Paletten als Farbstreifen |

```python
from wgnd.viz import bar, scatter_highlight, grid_histplot

fig, ax = bar(df, x="city", y="revenue", title="Revenue by City")
fig, ax = scatter_highlight(df, x="trip_distance", y="fare_amount",
                            highlight_mask=df["fare_amount"] > 100)
fig, axes = grid_histplot(df, hue="is_churned", multiple="fill")
```

### `wgnd.plotly_theme` — Plotly im wgnd-Look

Extra: `pip install "wgnd[plotly]"`. Palette und Chart-Farben kommen aus `cfg`.

| Funktion | Beschreibung |
|---|---|
| `register(name="wgnd", default=True)` | Template registrieren und als Plotly-Default setzen |
| `template()` | `plotly.graph_objects.layout.Template` ohne Registrierung |
| `sequential_scale(n)` / `diverging_scale(n)` | Hex-Listen aus `cfg.PALETTE_SEQ` / `cfg.PALETTE_DIV` |

```python
from wgnd.plotly_theme import register, sequential_scale
register()
fig = px.choropleth_map(df, geojson=gj, locations="id", color="share",
                        color_continuous_scale=sequential_scale())
```

### `wgnd.models` — Modell-Tracking (DSC)

Klassifikations-Tracking. Benötigt das `dsc`-Extra (`scikit-learn`, `joblib`);
scikit-learn wird erst beim Loggen eines Runs importiert, der Basis-Import von
`wgnd` bleibt ohne das Extra intakt.

| API | Beschreibung |
|---|---|
| `ModelTracker(csv_path=..., export_threshold=0.30)` | Persistentes CSV-Log über Runs |
| `.add_entry(name, model, feat_name, feat_list, y_true, y_pred, y_proba=None, description="")` | Loggt F1/Recall/Precision/ROC-AUC, exportiert Modell smart (neuer Bestwert **oder** F1 ≥ Schwelle), `Is_Best`-Flag |
| `.get_results()` | Historie als DataFrame |
| `save_model(model, name, folder=...)` | joblib-Export eines Modells |

```python
from wgnd import ModelTracker, save_model

tracker = ModelTracker(csv_path="../data/04_models/model_results_tracking.csv")
run_id = tracker.add_entry("logreg_v1", pipe, "base_feats", feats, y_val, y_pred, y_proba)
tracker.get_results()
```

### `wgnd.notes` — EDA-Notizen

```python
from wgnd import EdaNotes, notes   # 'notes' ist eine importfertige Singleton-Instanz

notes.add("CLEAN", "Duplikate in 'id' droppen")
notes.add("FEATURE", "log-Transform auf 'price'")
notes.show()                       # rendert eine kompakte HTML-Box im Notebook
```

### `wgnd.utils` — Helfer

```python
from wgnd.utils import timer, memory_report, downcast

@timer                             # Laufzeit der Funktion ausgeben
def my_pipeline(df): ...

memory_report(df)                  # Speicher pro Spalte, absteigend
df = downcast(df)                  # int64/float64 → kleinere Typen (Kopie)
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
| `cfg.COLOR_POSITIVE` | `#25ac82` Teal-Grün | explizit positiv |
| `cfg.COLOR_NEGATIVE` | `#de425b` Rot | Risiko, Fehler, kritisch |
| `cfg.COLOR_NEUTRAL` | `#8c8c8c` Grau | neutrale Referenzlinien |

**Annotation-Farben** (fix — ändern sich beim Palettenwechsel nicht):

| Variable | Farbe | Einsatz |
|---|---|---|
| `cfg.ANNO_MEAN` | `#ffa600` Amber | Mittelwert-Linie |
| `cfg.ANNO_MEDIAN` | `#34618d` Blau | Median-Linie |
| `cfg.ANNO_IQR_SOFT` | `#ffa600` Amber | 1.5× IQR Bounds |
| `cfg.ANNO_IQR_HARD` | `#de425b` Rot | 3× IQR Bounds |
| `cfg.ANNO_REF` | `#8c8c8c` Grau | neutrale Referenzlinie |

**Paletten** — nach Rolle benannt, nicht nach Aussehen:

| Variable | Beschreibung | Einsatz |
|---|---|---|
| `cfg.ACTIVE_PALETTE` | Aktive Palette (Standard: `PALETTE_CATEGORICAL`) | Datenfüllung in allen Charts |
| `cfg.PALETTE_CATEGORICAL` | 10 Farben, viridis + PRGn Familie | mehrere Kategorien unterscheiden |
| `cfg.PALETTE_DUAL` | 2 Farben, maximaler Kontrast | binäre Vergleiche |
| `cfg.PALETTE_SEQ` | Colormap-Name `"viridis"` | Heatmaps, Intensität |
| `cfg.PALETTE_DIV` | Colormap-Name `"PRGn"` | Abweichung vom Nullpunkt, Korrelationen |

`cfg.palette_n(n)` liefert `n` gleichmäßig verteilte Farben aus `PALETTE_CATEGORICAL`.

**Palette wechseln:**

```python
# Zur Laufzeit im Notebook — wirkt sofort auf matplotlib + seaborn:
cfg.use_palette("dual")                    # eigene: categorical | dual
cfg.use_palette("viridis", n=8, show=True) # oder jeder Seaborn-Name

from wgnd.viz import show_palettes
show_palettes()                            # alle Paletten als Farbstreifen

# Standard dauerhaft ändern — in src/wgnd/core/config.py:
PALETTE_STANDARD = PALETTE_CATEGORICAL     # ← hier tauschen
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
    cmap=cfg.PALETTE_DIV,
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
    PALETTE_STANDARD = PALETTE_CATEGORICAL   # → PALETTE_DUAL

    # Signal-Farben
    COLOR_SIGNAL   = "#ffa600"
    COLOR_POSITIVE = "#25ac82"
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
    DECIMAL_PLACES = 2
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
