# BACKLOG — wgnd-toolkit
### Offene Tasks für das Python-Toolkit

Prio: `1` = hoch, `2` = mittel, `3` = niedrig

---

| # | Beschreibung | Prio | Entdeckt in |
| :--- | :--- | :--- | :--- |
| 1 | **Toolkit-Konsolidierung: lokale Forks → `wgnd-toolkit`** — Cross-Projekt-Scan 2026-07-09: 3 Nachzügler mit lokalem Toolkit-Fork (`us-used-vehicle-resales`, `quito-traffic-jam` mit kollidierendem `src/wgnd/`, `zomato-restaurant` mit doppeltem `src/models.py` + `src/wgnd/`), während `zh-tram-flow`/`zh-tram-data`/`nyc-taxi-routes`/`kaggle-titanic` `wgnd` bereits extern konsumieren. **`ModelTracker` lebt nur in den 3 Forks, nicht im Toolkit.** Aufgaben: (a) `ModelTracker` (beste Version aus us-used `models.py`) + generische Helfer (`printing`, `process`-Split/Save) ins Toolkit promoten, `inspect`/`viz`/`utils`-Duplikate abgleichen; (b) Release/Version-Bump; (c) 3 Nachzügler: lokale Forks löschen, Imports auf `wgnd` repointen, Notebooks retesten; (d) READMEs auf echte wgnd-Nutzung heben. Gebündelt machen, nicht projektweise. Tie-in: #2. | 1 | 2026-07-09 (Toolkit-Scan us-used) |
| 2 | **wgnd-Packages als Framework positionieren** — Portfolio-Story: „Ich baue nicht nur Modelle, ich baue die Infrastruktur." READMEs von `wgnd-toolkit`/`wgnd-scaffolding`/`wgnd-skills` überarbeiten, GitHub-Profil anpassen. Verwandt: `wgnd-ai-dev-toolchain` (Case-Doku zum Zusammenspiel). | 1 | 2026-05-13 |
| 3 | **Polars-Unterstützung prüfen** — welche Funktionen müssen umgestellt werden. | 2 | zh-tram-flow Setup |
| 4 | **`inspect_correlations`** — Korrelationstabelle nach Heatmap als Print statt DataFrame, `display()` statt `print()` verwenden. | 3 | EDA 2026-05-12 |

---

> Angelegt 2026-08-29 beim Workspace-Backlog-Cleanup. Diese Items lagen vorher in `Workspace/docs/BACKLOG.md`.
