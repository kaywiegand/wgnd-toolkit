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

### Schritt 1 — ZIP entpacken

```
wgnd/
├── src/wgnd/
├── examples/
│   ├── data/customers.csv
│   └── wgnd_examples.ipynb
├── tests/
└── pyproject.toml
```

### Schritt 2 — Ordner in VS Code öffnen

**Datei → Ordner öffnen** → den `wgnd/` Ordner auswählen.

### Schritt 3 — Terminal: **Strg + `**

### Schritt 4 — Python + Jupyter Erweiterung (einmalig)

**Strg + Shift + X** → `Python` (Microsoft) + `Jupyter` (Microsoft) installieren.

### Schritt 5–8 — Umgebung einrichten

```bash
pip install uv            # uv einmalig installieren

uv venv                   # .venv/ erstellen

# Aktivieren
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # Mac/Linux

uv pip install -e ".[dev]"  # alle Dependencies + wgnd selbst

python -m ipykernel install --user --name wgnd --display-name "Python (wgnd)"
```

### Schritt 9 — Notebook öffnen

`examples/wgnd_examples.ipynb` doppelklicken → Kernel **Python (wgnd)** wählen.

### Schritt 10 — Ausführen

**Run All** (▶▶) oder Zelle für Zelle mit **Shift + Enter**.

> **Häufige Probleme**
>
> `ModuleNotFoundError: wgnd` → Kernel-Picker: ist **Python (wgnd)** gewählt?
> Wenn nicht: Schritte 5–8 wiederholen, VS Code neu starten.
>
> `jinja2 not found` → `uv pip install jinja2`
>
> `nbformat` Fehler → `uv pip install nbformat`
>
> Windows PowerShell: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## 2 · Package in ein Projekt einbinden

```toml
# pyproject.toml des Projekts
dependencies = [
    "wgnd @ git+https://github.com/dein-user/wgnd.git",
]
```

```bash
uv pip install -e ".[dan]"   # DAN-Projekt
uv pip install -e ".[dsc]"   # DSC-Projekt (+ sklearn, xgboost, shap)
```

**Erste Zelle jedes Notebooks:**

```python
from wgnd.core.theme import setup
setup()
# → ✓ wgnd theme activated
```

---

## 3 · Package-Struktur

```
wgnd/
├── src/wgnd/
│   ├── core/
│   │   ├── config.py       ← Farben, Größen, Formate (einzige Wahrheitsquelle)
│   │   ├── theme.py        ← setup(), apply_theme(), mpl_style()
│   │   └── _output.py      ← section_header(), info_box(), show_df()
│   │
│   ├── inspect.py          ← EDA: inspect() + 9 Sub-Funktionen
│   ├── clean.py            ← Bereinigung: Duplikate, Nullwerte, Typen, Outlier
│   ├── features.py         ← Feature Engineering: Datum, Encoding, Scaling
│   ├── viz.py              ← Charts für Reports & Dashboards (Plotly)
│   ├── models.py           ← DSC: Train, CV, Metriken, Export
│   └── utils.py            ← load(), save(), timer, memory_report
│
├── examples/
│   ├── data/customers.csv
│   └── wgnd_examples.ipynb
└── tests/
```

---

## 4 · Module im Überblick

### `wgnd.inspect` — EDA

| Funktion | Chart |
|---|---|
| `inspect(df)` | alle |
| `inspect_dimensions(df)` | — |
| `inspect_dtypes(df)` | — |
| `inspect_missing(df)` | missingno Heatmap |
| `inspect_duplicates(df)` | — |
| `inspect_names(df)` | — |
| `inspect_numeric_stats(df)` | Boxplot |
| `inspect_categorical_stats(df)` | Barplot |
| `inspect_correlations(df)` | Heatmap |
| `inspect_outliers(df)` | Violin |

```python
from wgnd.inspect import inspect, inspect_missing

inspect(df)                    # alle Sektionen
result = inspect_missing(df)   # anzeigen + Daten zurückbekommen
```

### `wgnd.clean` — Bereinigung

```python
from wgnd.clean import clean, drop_duplicates, fill_missing

df_clean = clean(df, fill_strategy="median")   # alles auf einmal
df = drop_duplicates(df)
df = fill_missing(df, strategy="median")
```

### `wgnd.viz` — Charts

```python
from wgnd.viz import bar, bar_reference, scatter, distribution
from wgnd.viz import time_series, heatmap, pairplot, boxplot, stacked_bar_pct

fig = bar(df, x="city", y="revenue")
fig.show()
fig.write_html("reports/revenue.html")   # Export für Stakeholder
```

### `wgnd.utils` — Helfer

```python
from wgnd.utils import load, save, timer, downcast

df = load("data/raw/sales.csv")
save(df_clean, "data/processed/sales.parquet")

@timer
def my_pipeline(df): ...

df_small = downcast(df)
```

---

## 5 · Chart-Guide — einheitlicher Look

### 5.1 Farbsystem

Das Package verwendet vier klar getrennte Farbrollen.
Alle Werte kommen aus `cfg` — nie hardcoded in Charts schreiben.

```python
from wgnd.core.config import cfg
```

| Rolle | Variable | Farbe | Wann benutzen |
|---|---|---|---|
| Kategorisch | `cfg.PALETTE_CATEGORICAL` | 7 Farben (Blau→Orange) | bar, scatter, pie – Gruppen |
| Sequential | `cfg.PALETTE_BUSINESS` | Blau hell→dunkel | Heatmaps mit positivem Bereich |
| Divergent | `cfg.PALETTE_DIVERGENT` | Grün↔Creme↔Rot | Korrelations-Heatmaps |
| Signal Amber | `cfg.COLOR_SIGNAL` | `#ffa600` | Mittelwert-Linie, Trendlinie, Grenzwert |
| Signal Positiv | `cfg.COLOR_POSITIVE` | `#488f31` | explizit gute Werte |
| Signal Negativ | `cfg.COLOR_NEGATIVE` | `#de425b` | Risiko, Fehler, kritisch |
| Neutral | `cfg.COLOR_NEUTRAL` | `#8c8c8c` | neutrale Referenzlinien |

**Regel:** Rot/Grün nur einsetzen wenn die Semantik stimmt.
Mittelwerte, Trendlinien → immer `COLOR_SIGNAL` (Amber).

---

### 5.2 Plotly — fertige Chart-Funktionen

Alle `viz.*`-Funktionen liefern sofort das richtige Theme:

```python
from wgnd.viz import bar, bar_reference, heatmap, stacked_bar_pct
from wgnd.core.config import cfg

# Einfaches Balkendiagramm
fig = bar(df, x="city", y="revenue", title="Revenue by City")
fig.show()

# Balken mit Referenzlinie (Mittelwert automatisch)
fig = bar_reference(df, x="city", y="churn_pct",
                    ref_label="Ø Churn",
                    title="Churn Rate by City")
fig.show()

# Gestapelt in Prozent (Churn-Rate nach Gruppe)
fig = stacked_bar_pct(df, cat_col="international_plan",
                      target_col="is_churned",
                      title="Churn Rate by International Plan")
fig.show()

# Korrelations-Heatmap (divergente Farbskala)
fig = heatmap(df, title="Feature Correlations")
fig.show()
```

---

### 5.3 Plotly — eigene Charts mit `apply_theme()`

Für alles was die fertigen Funktionen nicht abdecken:

```python
import plotly.graph_objects as go
from wgnd.core.theme import apply_theme
from wgnd.core.config import cfg

# Beispiel: Doppelachsen-Chart (Volumen + Rate)
fig = go.Figure()

fig.add_trace(go.Bar(
    x=stats.index,
    y=stats["count"],
    name="Volume",
    marker_color=cfg.PALETTE_CATEGORICAL[0],
    opacity=0.8,
))

fig.add_trace(go.Scatter(
    x=stats.index,
    y=stats["churn_rate"],
    name="Churn Rate",
    mode="lines+markers",
    line=dict(color=cfg.COLOR_NEGATIVE, width=2),
    yaxis="y2",
))

fig.update_layout(
    yaxis2=dict(overlaying="y", side="right", showgrid=False),
)

apply_theme(fig,
    title="Volume vs. Churn Rate by Brand",
    xlabel="Brand",
    ylabel="Count",
)
fig.show()
```

```python
# Beispiel: Linie mit Risiko-Zonen (axvspan-Äquivalent in Plotly)
fig = go.Figure()

fig.add_vrect(x0=3, x1=5,
    fillcolor=cfg.PALETTE_CATEGORICAL[0], opacity=0.15,
    annotation_text="Risk Zone", annotation_position="top left",
    line_width=0)

fig.add_vrect(x0=5, x1=11,
    fillcolor=cfg.COLOR_NEUTRAL, opacity=0.08,
    annotation_text="Churn Zone",
    line_width=0)

fig.add_trace(go.Scatter(
    x=csc_churn_rate.index,
    y=csc_churn_rate.values,
    line=dict(color=cfg.PALETTE_CATEGORICAL[0], width=2),
    name="Churn Rate",
))

apply_theme(fig,
    title="Avg. Churn Rate by Customer Service Calls",
    xlabel="Customer Service Calls",
    ylabel="Churn Rate",
)
fig.show()
```

---

### 5.4 Matplotlib — bestehende Charts vereinheitlichen

Für Matplotlib-Charts (bestehende Notebooks) gibt `mpl_style()` alle nötigen
Kwargs auf einen Schlag:

```python
import matplotlib.pyplot as plt
from wgnd.core.theme import mpl_style
from wgnd.core.config import cfg

style = mpl_style()

fig, ax = plt.subplots(figsize=(12, 6))

# Chart-Code (unverändert aus bisherigen Projekten)
data.plot(kind="barh", color=cfg.PALETTE_CATEGORICAL[0], ax=ax)

# Theme drauf mappen
ax.set_title("Städte-Ranking", **style["title"])
ax.set_xlabel("Churn Rate", **style["label"])
ax.set_ylabel("", **style["label"])

# Referenz-Linie (neutral, grau)
ax.axvline(mean, **style["refline"], label=f"Ø {mean:.1f}")

# Signal-Linie (Amber — Schwellwert, Grenzwert)
ax.axvline(threshold, **style["signal"], label="Threshold")

# Spines aufräumen
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color(cfg.CHART_AXIS)

plt.tight_layout()
plt.show()
```

**Seaborn-Charts:**

```python
import seaborn as sns
from wgnd.core.config import cfg

# Heatmap mit divergenter Palette
sns.heatmap(corr_matrix,
    annot=True, fmt=".2f",
    cmap=cfg.PALETTE_DIVERGENT,   # oder "RdBu_r" wenn du Seaborn-Skala willst
    center=0,
    linewidths=0.5,
)
ax.set_title("Correlation Matrix", **mpl_style()["title"])
```

---

### 5.5 Plotly — was noch möglich ist

Plotly kann deutlich mehr als Basis-Charts:

| Feature | Funktion | Beispiel |
|---|---|---|
| **Geo-Karten** | `px.scatter_geo`, `px.choropleth` | Länder/Städte auf Weltkarte |
| **Mapbox** | `px.scatter_mapbox` | Punkte auf OpenStreetMap |
| **3D Scatter** | `px.scatter_3d` | 3 Dimensionen gleichzeitig |
| **Sunburst** | `px.sunburst` | Hierarchische Anteile |
| **Sankey** | `go.Sankey` | Fluss-Diagramme |
| **Animate** | `px.scatter(animation_frame=...)` | Zeitanimation |
| **Subplots** | `make_subplots()` | Mehrere Charts in einem |
| **Dash** | `import dash` | Interaktives Dashboard |

```python
# Geo-Karte (Koordinaten-Scatter)
import plotly.express as px
from wgnd.core.theme import apply_theme

fig = px.scatter_geo(
    df,
    lat="pickup_latitude",
    lon="pickup_longitude",
    color="is_outlier",
    color_discrete_map={True: cfg.COLOR_NEGATIVE, False: cfg.PALETTE_CATEGORICAL[0]},
    title="Pickup Coordinates",
)
apply_theme(fig)
fig.show()

# Subplot-Grid (Boxplot + Histogram nebeneinander)
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2, subplot_titles=["Boxplot", "Histogram"])
fig.add_trace(go.Box(y=df[col], name=col,
    marker_color=cfg.PALETTE_CATEGORICAL[0]), row=1, col=1)
fig.add_trace(go.Histogram(x=df[col],
    marker_color=cfg.PALETTE_CATEGORICAL[0], opacity=0.75), row=1, col=2)
apply_theme(fig, title=f"Distribution: {col}")
fig.show()
```

---

## 6 · Konfiguration anpassen

Alle Farben in `src/wgnd/core/config.py` — eine Änderung wirkt überall:

```python
class WgndConfig:
    # Kategorische Palette (7 Farben, learnui.design)
    PALETTE_CATEGORICAL = ["#003d5c", "#31497e", "#674f95", ...]

    # Signal-Farben (sparsam einsetzen)
    COLOR_SIGNAL   = "#ffa600"   # Amber  → Mittelwert, Schwellwert
    COLOR_POSITIVE = "#488f31"   # Grün   → explizit positiv
    COLOR_NEGATIVE = "#de425b"   # Rot    → explizit negativ

    # Chart-Basis
    CHART_BG       = "#ffffff"
    CHART_GRID     = "#e8e8e8"   # dezentes Hellgrau
    CHART_AXIS     = "#b0b0b0"   # etwas dunkler
    CHART_TITLE    = "#222222"   # fast schwarz

    # Tabellen (schwarz auf abwechselnd weiß/hellgrau)
    TABLE_ROW_ODD  = "#ffffff"
    TABLE_ROW_EVEN = "#f5f5f5"
    TABLE_HEADER_BG = "#e0e0e0"
    TABLE_TEXT     = "#000000"
```

---

## 7 · Tests

```bash
pytest tests/                                          # 44 Tests
pytest tests/ -v --tb=short                            # verbose
pytest tests/ --cov=src/wgnd --cov-report=term-missing # Coverage
```

---

_Entwickelt für DAN- und DSC-Projekte im Wiegand-Workflow._
