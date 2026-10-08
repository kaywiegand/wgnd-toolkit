# BACKLOG — wgnd-toolkit
### Offene Tasks für das Python-Toolkit

Prio: `1` = hoch, `2` = mittel, `3` = niedrig

---

| # | Beschreibung | Prio | Entdeckt in |
| :--- | :--- | :--- | :--- |
| 1 | **Toolkit-Konsolidierung: Rest** — `ModelTracker`/`EdaNotes` sind promotet (v0.3.0), `us-used-vehicle-resales` ist migriert (→ `PROCESS_LOG.md` 2026-07-10). Offen: (a) `quito-traffic-jam` (kollidierendes `src/wgnd/`) und `zomato-restaurant` (doppeltes `src/models.py` + `src/wgnd/`) — galten als nicht direkt migrierbar, Entscheidung migrieren oder so lassen; (b) `inspect`/`viz`/`utils`-Duplikate der Forks gegen das Toolkit abgleichen; (c) READMEs der Consumer auf echte wgnd-Nutzung heben. Tie-in: #2. | 1 | 2026-07-09 (Toolkit-Scan us-used) |
| 2 | **wgnd-Packages als Framework positionieren** — Portfolio-Story: „Ich baue nicht nur Modelle, ich baue die Infrastruktur." READMEs von `wgnd-toolkit`/`wgnd-scaffolding`/`wgnd-skills` überarbeiten, GitHub-Profil anpassen. Verwandt: `wgnd-ai-dev-toolchain` (Case-Doku zum Zusammenspiel). | 1 | 2026-05-13 |
| 3 | **`inspect_correlations`** — Korrelationstabelle nach Heatmap als Print statt DataFrame, `display()` statt `print()` verwenden. | 3 | EDA 2026-05-12 |
| 4 | **Tests für `viz`, `utils`, `config`, `_output`** — bisher nur `inspect`, `models`, `notes` abgedeckt. | 3 | Cleanup 2026-10-08 |
| 5 | **CI** — GitHub-Actions-Workflow für pytest + ruff. | 3 | Cleanup 2026-10-08 |
| 6 | **Dependencies entschlacken** — `ipykernel`, `nbformat` aus den Laufzeit-Dependencies ins `dev`-Extra; vorher gegen die Consumer-Projekte prüfen. | 3 | Cleanup 2026-10-08 |
| 7 | **Beispiel-Notebook** — komplett durchlaufen lassen (seit dem Paletten-Umbau ungeprüft), toten `numpy`-Import entfernen. | 3 | Cleanup 2026-10-08 |
| 8 | **LICENSE** — zurückgestellt, Toolkit ist primär für den Eigengebrauch. | 3 | Cleanup 2026-10-08 |

Polars-Support steht in `ROADMAP.md` (Phase 1), nicht hier.

---

> Angelegt 2026-08-29 beim Workspace-Backlog-Cleanup. Diese Items lagen vorher in `Workspace/docs/BACKLOG.md`.
