"""
plotly_theme.py
---------------
Plotly-Template im wgnd-Look (Palette, Chart-Farben und Schrift aus ``cfg``).

Benötigt das ``plotly``-Extra (``pip install "wgnd[plotly]"``); der Import von ``wgnd``
selbst bleibt davon unberührt.

Verwendung:
    from wgnd.plotly_theme import register, sequential_scale
    register()                                   # setzt Template "wgnd" als Plotly-Default
    px.choropleth_map(..., color_continuous_scale=sequential_scale())
"""

from __future__ import annotations

from wgnd.core.config import cfg

TEMPLATE_NAME = "wgnd"


def sequential_scale(n: int = 9) -> list[str]:
    """Hex-Farben der sequentiellen Palette (``cfg.PALETTE_SEQ``), niedrig → hoch."""
    import matplotlib as mpl
    from matplotlib.colors import to_hex

    cmap = mpl.colormaps[cfg.PALETTE_SEQ]
    return [to_hex(cmap(i / (n - 1))) for i in range(n)]


def diverging_scale(n: int = 9) -> list[str]:
    """Hex-Farben der divergierenden Palette (``cfg.PALETTE_DIV``)."""
    import matplotlib as mpl
    from matplotlib.colors import to_hex

    cmap = mpl.colormaps[cfg.PALETTE_DIV]
    return [to_hex(cmap(i / (n - 1))) for i in range(n)]


def template():
    """Plotly-``Template`` mit wgnd-Farben."""
    try:
        import plotly.graph_objects as go
    except ImportError as exc:  # pragma: no cover
        raise ImportError('plotly fehlt: pip install "wgnd[plotly]"') from exc

    axis = dict(
        gridcolor=cfg.CHART_GRID,
        linecolor=cfg.CHART_AXIS,
        zerolinecolor=cfg.CHART_AXIS,
        tickfont=dict(color=cfg.CHART_AXIS_TEXT),
        title=dict(font=dict(color=cfg.CHART_LABEL)),
    )
    return go.layout.Template(
        layout=dict(
            colorway=list(cfg.PALETTE_CATEGORICAL),
            paper_bgcolor=cfg.CHART_BG,
            plot_bgcolor=cfg.CHART_BG,
            font=dict(color=cfg.CHART_LABEL),
            title=dict(font=dict(color=cfg.CHART_TITLE)),
            xaxis=axis,
            yaxis=axis,
            colorscale=dict(sequential=sequential_scale(), diverging=diverging_scale()),
            legend=dict(font=dict(color=cfg.CHART_LABEL)),
        )
    )


def register(name: str = TEMPLATE_NAME, default: bool = True):
    """Template unter ``name`` registrieren, optional als Plotly-Default setzen."""
    import plotly.io as pio

    tpl = template()
    pio.templates[name] = tpl
    if default:
        pio.templates.default = name
    return tpl
