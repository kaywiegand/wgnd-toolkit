# PROCESS_LOG.md – wgnd-toolkit

> Projektverlauf und Einstiegspunkt für neue Claude-Sessions.

---

## Projekt-Übersicht

| Feld | Inhalt |
| :--- | :--- |
| Paket | `wgnd` |
| Repo | `git@github.com:kaywiegand/wgnd-toolkit.git` |
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

### 2026-05-11 — Dokumentation angelegt

- `CLAUDE.md`, `ROADMAP.md`, `PROCESS_LOG.md` erstellt
