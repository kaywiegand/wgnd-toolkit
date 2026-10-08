"""
test_plotly_theme.py
--------------------
Tests für wgnd.plotly_theme. Überspringen, wenn das plotly-Extra fehlt.
"""

import pytest

from wgnd.core.config import cfg
from wgnd.plotly_theme import diverging_scale, sequential_scale

plotly = pytest.importorskip("plotly")


def test_sequential_scale_has_n_hex_colors():
    colors = sequential_scale(5)
    assert len(colors) == 5
    assert all(c.startswith("#") and len(c) == 7 for c in colors)


def test_diverging_scale_endpoints_differ():
    colors = diverging_scale(7)
    assert colors[0] != colors[-1]


def test_template_uses_config_palette():
    from wgnd.plotly_theme import template

    assert list(template().layout.colorway) == cfg.PALETTE_CATEGORICAL


def test_register_sets_default():
    import plotly.io as pio

    from wgnd.plotly_theme import register

    previous = pio.templates.default
    try:
        register("wgnd_test", default=True)
        assert pio.templates.default == "wgnd_test"
    finally:
        pio.templates.default = previous
