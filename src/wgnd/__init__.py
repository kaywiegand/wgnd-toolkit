"""
wgnd – Wiegand Data Toolkit v0.2.0
===================================
EDA & Visualisierung für DAN & DSC Projekte.

Schnellstart (erste Notebook-Zelle):
    from wgnd import setup, inspect
    from wgnd import success, warn, log, info_box, show_df, section_header
"""

__version__ = "0.2.0"
__author__  = "Wiegand"

try:
    from wgnd.core.theme import setup
    from wgnd.core.config import cfg
    from wgnd.core._output import (
        success, warn, error, log,
        info_box, show_df, section_header,
        console,
    )
    from wgnd.inspect import inspect
except Exception:
    pass
