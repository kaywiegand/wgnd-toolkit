"""
wgnd – Wiegand Data Toolkit v0.4.0
===================================
EDA & Visualisierung für DAN & DSC Projekte.

Schnellstart (erste Notebook-Zelle):
    from wgnd import setup, inspect
    from wgnd import success, warn, log, info_box, show_df, section_header

Modellierung (DSC, benötigt das ``dsc``-Extra: scikit-learn/joblib):
    from wgnd import ModelTracker, save_model
Plotly-Theme (Extra ``plotly``):
    from wgnd.plotly_theme import register, sequential_scale
EDA-Notizen:
    from wgnd import EdaNotes, notes
"""

__version__ = "0.4.0"
__author__  = "Wiegand"

from wgnd.core.theme import setup
from wgnd.core.config import cfg
from wgnd.core._output import (
    success, warn, error, log,
    info_box, show_df, section_header,
    console,
)
from wgnd.inspect import inspect
from wgnd.notes import EdaNotes, notes

# scikit-learn/joblib (dsc-Extra) werden in wgnd.models erst beim Aufruf
# importiert — der Import hier bricht auch ohne das Extra nicht.
from wgnd.models import ModelTracker, save_model

__all__ = [
    "setup", "cfg",
    "success", "warn", "error", "log",
    "info_box", "show_df", "section_header", "console",
    "inspect",
    "EdaNotes", "notes",
    "ModelTracker", "save_model",
]
