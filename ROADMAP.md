# ROADMAP.md – wgnd-toolkit

---

## Status

| Phase | Beschreibung | Status |
| :--- | :--- | :--- |
| 0 | Core: config, theme, output, inspect, viz | ✅ Stabil |
| 1 | Polars-Support | 🟡 In Arbeit |
| 2 | Backlog-Features | 📋 Geplant |

---

## Phase 1 — Polars-Support

Ziel: alle Toolkit-Funktionen akzeptieren sowohl `pd.DataFrame` als auch `pl.DataFrame`.

- [ ] `_ensure_pandas(df, max_rows)` — zentrale Konvertierungsfunktion in `core/`
- [ ] `show_df()` — Polars auto-convert
- [ ] `inspect_*` — Polars auto-convert am Eingang
- [ ] Warning wenn Frame > 500k Zeilen übergeben wird

---

## Phase 2 — Backlog

- [ ] `PALETTE_EDA` + `cfg.use_palette("eda")` — gedämpfte EDA-Palette vs. Report-Palette
- [ ] `show_df` — Text linksbündig, Zahlen rechtsbündig überall konsistent
- [ ] `cfg.DECIMAL_PLACES` Default 3 → 2
- [ ] Alle `inspect_*` — `return_df=True` Parameter (Standard: None zurückgeben)
- [ ] `axes`-Pattern für Chart-Funktionen — externes Grid-Layout
- [ ] Parquet Import/Export — `read_parquet(path)` / `write_parquet(df, path)`
