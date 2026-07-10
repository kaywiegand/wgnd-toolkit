# PROCESS_LOG.md – wgnd-toolkit

> Projektverlauf und Einstiegspunkt für neue Claude-Sessions.

---

## Projekt-Übersicht

| Feld | Inhalt |
| :--- | :--- |
| Paket | `wgnd` |
| Repo | `git@github.com:kaywiegand/wgnd-toolkit.git` |
| Letzte Version | `v0.3.0` — ModelTracker, save_model, EdaNotes (lokal getaggt, Push separat) |
| Status | ⚠️ In Arbeit — Phase 1 Polars-Support |
| Nächster Schritt | `_ensure_pandas()` implementieren, inspect + show_df updaten |

---

## Architektur-Entscheidungen

| Entscheidung | Begründung |
| :--- | :--- |
| Plain `print()` + ANSI statt Rich für log/success/warn | Rich erzeugt in Jupyter pro Call einen eigenen HTML-Block mit Margin → zu viel Abstand |
| `info_box` + `console` bleiben mit Rich | Nur dort bringt Rich echten Mehrwert (Panel-Rahmen für Reports) |
| `ACTIVE_PALETTE` für Datenfüllung, `ANNO_*` für Linien | Saubere Trennung: Palette wechseln ändert nie Annotation-Farben |
| `cfg.use_palette()` propagiert sofort zu mpl + seaborn | Einmal setzen — alle nachfolgenden Charts nutzen die neue Palette |
| Polars-Support via `_ensure_pandas()` Konvertierung | Einfachste Lösung: Polars-Frame am Eingang konvertieren, restliche Logik bleibt pandas |

---

## Verlauf

### 2026-07-10 — v0.3.0: ModelTracker + EdaNotes promotet (Workspace-Konsolidierung)

**Kontext:** Cross-Projekt-Scan (Workspace-BACKLOG #24) — der selbstgebaute
`ModelTracker` lebte nur in lokalen Projekt-Forks (Referenz: `us-used-vehicle-resales`),
nicht im Toolkit. Bündel-Aktion: genuin allgemeine Bausteine **einmal** hierher heben.

**Neu (additiv, abwärtskompatibel — kein bestehender öffentlicher Name geändert):**
- `models.py` — `ModelTracker` (persistentes CSV-Log, Smart-joblib-Export bei neuem
  Bestwert **oder** F1 ≥ `export_threshold`, `Is_Best`-Flag, `get_results`) + `save_model`.
  scikit-learn/joblib bewusst **funktions-lokal** importiert → Basis-Import ohne `dsc`-Extra
  bleibt intakt.
- `notes.py` — `EdaNotes` (kategorisierter Notiz-Sammler mit HTML-Ausgabe) + `notes`-Singleton.
- `__init__.py` — neue Symbole gegated re-exportiert, Version `0.2.0 → 0.3.0`.
- `tests/test_models.py` + `tests/test_notes.py` — Metriken/CSV/`Is_Best`/Smart-Export bzw.
  Notes-State. Gesamt-Suite **33 grün**.

**Bewusst NICHT promotet** (bleiben projekt-lokal): `printing` (Dublette zu `section_header`),
`process`-Split-Funktionen (projekt-spezifisch, hängen an lokalen Inspektoren),
`inspect_run_full` (LogReg-/`Good-Bad`-spezifisch). `inspect`/`viz`/`utils` unangetastet.

**Consumer:** `us-used-vehicle-resales` migriert (konsumiert nun `wgnd.ModelTracker` etc.).
`quito-traffic-jam` + `zomato-restaurant` als nicht-migrierbar ausgegliedert
(Workspace-BACKLOG #25/#26). Release lokal getaggt `v0.3.0` — Push separat.

### 2026-04-22/23 — Große Refactor-Session (DAN_NewYork-Taxi-Routes)

**Fixes:**
- `show_df` crash: `hide(axis=None)` → Guard mit `if not show_index`
- Numeric columns nicht rechtsbündig: `set_properties` durch `apply()` ersetzt
- `select_dtypes(include="integer")` → `include="number"` (erfasst nullable Int64)
- `inspect_duplicates`: `keep=False` → `keep="first"` — count stimmt jetzt mit `len(result)` überein
- `inspect()` Fehler in allen Sektionen: `.hide(axis=None)` war Ursache

**Features:**
- `log()` → plain `print()` + ANSI (kein Rich mehr) — kompakter Abstand in Jupyter
- `section_header`, `success`, `warn`, `error` → alle plain `print()` + ANSI
- `ANNO_MEAN`, `ANNO_MEDIAN`, `ANNO_IQR_SOFT`, `ANNO_IQR_HARD`, `ANNO_REF` in Config
- `cfg.use_palette()` propagiert sofort zu `mpl.rcParams` und `sns.set_palette()`
- `cfg.use_palette(name, n, show=True)` + `cfg.show_palette()` — Farbvorschau
- Seaborn-Paletten via `cfg.use_palette("viridis", n=8)`
- `inspect()` akzeptiert `columns` + `title` Parameter
- `inspect_outlier_detail()` akzeptiert `figsize` Parameter
- `inspect_duplicates` gibt nur zu löschende Zeilen zurück (`keep="first"`)
- `_is_dark()` Hilfsfunktion für Lesbarkeit auf dunklen Farbflächen

### 2026-05-14 — Palette-System überarbeitet

**Konzept:** Paletten nach Rolle statt nach Aussehen benannt.

**Neu:**
- `PALETTE_CATEGORICAL` — 10 Farben aus viridis + PRGn Familie (Option A)
- `PALETTE_DUAL` — 2 Farben mit max. Kontrast für binäre Vergleiche
- `PALETTE_SEQ = "viridis"` — Colormap-Name für Heatmaps / Intensität
- `PALETTE_DIV = "PRGn"` — Colormap-Name für Abweichungen vom Nullpunkt
- `show_palettes()` in viz.py zeigt neues System

**Entfernt:** `PALETTE_OCEAN`, `PALETTE_PINK_TEAL`, `PALETTE_BLUE_RANGE`, `PALETTE_BLUE_LIGHT`, `PALETTE_DIVERGENT`

**Warum:** Sequential-Palette war fälschlicherweise als Default gesetzt → ähnliche Blautöne in kategorischen Charts kaum unterscheidbar.

### 2026-05-11 — Dokumentation angelegt

- `CLAUDE.md`, `ROADMAP.md`, `PROCESS_LOG.md` erstellt
