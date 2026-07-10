"""
wgnd.notes
----------
``EdaNotes`` – ein kategorisierter Notiz-Sammler für die explorative Analyse.

Man notiert unterwegs Beobachtungen in vier Kategorien (CLEAN / FEATURE /
MODEL / INVESTIGATE) und rendert sie später als kompakte HTML-Box im Notebook.
``notes`` ist eine importfertige Singleton-Instanz.
"""

from __future__ import annotations


class EdaNotes:
    """Sammelt EDA-Beobachtungen in vier Kategorien und zeigt sie als HTML-Box."""

    _CATEGORIES = ("CLEAN", "FEATURE", "MODEL", "INVESTIGATE")

    def __init__(self):
        self._notes: dict[str, list[str]] = {c: [] for c in self._CATEGORIES}

    def add(self, category: str, note: str) -> None:
        cat = category.upper()
        if cat not in self._notes:
            raise ValueError(
                f"Kategorie '{cat}' ungültig. Erlaubt: {list(self._notes)}"
            )
        self._notes[cat].append(note)

    def remove(self, category: str, index: int) -> None:
        cat = category.upper()
        self._notes[cat].pop(index)

    def show(self) -> None:
        from IPython.display import HTML, display

        config = {
            "CLEAN":       "#e05c5c",
            "FEATURE":     "#e0a85c",
            "MODEL":       "#7c8cf8",
            "INVESTIGATE": "#5cb8a0",
        }

        def section(cat, color):
            items = self._notes[cat]
            if not items:
                return ""
            lis = "".join(f"<li>{i}</li>" for i in items)
            badge = f'<span style="color:{color}">● {cat}</span>'
            return f"""
            <details open>
              <summary style="cursor:pointer; list-style:none;">{badge}
                <span style="color:#555e7a; font-size:0.85em;"> ({len(items)})</span>
              </summary>
              <ul style="color:#9aa0b4; margin:4px 0 0 12px; line-height:1.9;">{lis}</ul>
            </details>"""

        html = f"""
        <div style="background:#161622; border-radius:8px; padding:16px 20px;
                    margin:12px 0; font-size:0.8em; border:1px solid #2a2a3e;">
          <span style="color:#555e7a; letter-spacing:0.08em; font-size:0.9em;">▸ EDA NOTES</span>
          {''.join(section(cat, color) for cat, color in config.items())}
        </div>"""
        display(HTML(html))

    def clear(self, category: str | None = None) -> None:
        if category:
            self._notes[category.upper()] = []
        else:
            for k in self._notes:
                self._notes[k] = []


# Singleton-Instanz – einmal importieren, überall nutzen.
notes = EdaNotes()
