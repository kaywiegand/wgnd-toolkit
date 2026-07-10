"""
wgnd – Wiegand Data Toolkit v0.3.0
===================================
EDA & Visualisierung für DAN & DSC Projekte.

Schnellstart (erste Notebook-Zelle):
    from wgnd import setup, inspect
    from wgnd import success, warn, log, info_box, show_df, section_header

Modellierung (DSC, benötigt das ``dsc``-Extra: scikit-learn/joblib):
    from wgnd import ModelTracker, save_model
EDA-Notizen:
    from wgnd import EdaNotes, notes
"""

__version__ = "0.3.0"
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
    from wgnd.notes import EdaNotes, notes
except Exception:
    pass

# Modell-Tracking separat kapseln: hängt an scikit-learn (dsc-Extra). Fehlt es,
# bleibt der Basis-Import trotzdem intakt.
try:
    from wgnd.models import ModelTracker, save_model
except Exception:
    pass
