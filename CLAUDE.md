# CLAUDE.md – wgnd-toolkit

> Projektspezifische Anweisungen für Claude Code.
> Ergänzt die globale CLAUDE.md aus dem wgnd-workspace.

---

## Projekt

| Feld | Inhalt |
| :--- | :--- |
| Paket | `wgnd` |
| Typ | Python Toolkit (eigene Infrastruktur) |
| Repo | `git@github.com:kaywiegand/wgnd-toolkit.git` |
| Lokaler Pfad | `/Users/kaywiegand/Workspace/wgnd-toolkit` |

## Kontext-Einstieg

1. `PROCESS_LOG.md` lesen — aktueller Stand, letzte Änderungen
2. `ROADMAP.md` lesen — offene Features und Backlog
3. Globale `CLAUDE.md` aus `/Users/kaywiegand/Workspace/` gilt weiterhin

## Struktur

```
src/wgnd/
├── __init__.py          ← öffentliche API
├── inspect.py           ← EDA-Funktionen (inspect, inspect_*)
├── viz.py               ← Chart-Funktionen
├── core/
│   ├── config.py        ← WgndConfig — alle Farben, Paletten, Konstanten
│   ├── theme.py         ← matplotlib/seaborn Theme-Setup
│   └── _output.py       ← section_header, show_df, log, success, warn, error
```

## Wichtige Konventionen

- `cfg` ist Singleton — alle Farben/Paletten über `cfg.*`
- `ACTIVE_PALETTE` → Datenfüllung (wechselbar via `cfg.use_palette()`)
- `ANNO_*` → Annotation-Linien (Mean, Median, IQR) — fix, palette-unabhängig
- `show_df()` nutzt IPython Display + pandas Styler (kein Rich)
- `section_header`, `log`, `success`, `warn`, `error` → plain `print()` + ANSI (kein Rich)
- `info_box`, `console` → Rich (für Reports)

## Lokales Entwickeln

In Projekten die wgnd nutzen — einmalig lokal verlinken:
```bash
uv pip install -e /Users/kaywiegand/Workspace/wgnd-toolkit
```
Danach reicht Kernel-Neustart. Kein `--refresh-package` nötig.
