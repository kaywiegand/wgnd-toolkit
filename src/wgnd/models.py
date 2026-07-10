"""
wgnd.models
-----------
Modell-Tracking für Klassifikations-Experimente.

Enthält:
  - save_model()   – joblib-Export eines (Pipeline-)Modells.
  - ModelTracker   – persistentes CSV-Log über Runs mit Smart-Export der
                     Modell-Dateien (nur bei neuem Bestwert oder F1 >= Schwelle).

Klassifikations-spezifisch (F1 / Recall / Precision / ROC-AUC). Der Import von
scikit-learn/joblib erfolgt bewusst modul-lokal, damit der Basis-Import von
``wgnd`` ohne das ``dsc``-Extra nicht bricht.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd


def save_model(model, name: str, folder: str = "../data/04_models/") -> None:
    """Speichert ein Modell als joblib-Datei unter ``folder/<name>.joblib``."""
    import joblib

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{name}.joblib")
    joblib.dump(model, path)
    print(f"💾 Model file written: {path}")


class ModelTracker:
    """
    Persistentes Tracking von Klassifikations-Runs.

    Jeder ``add_entry`` berechnet F1/Recall/Precision/ROC-AUC, hängt eine Zeile
    an ein CSV an und exportiert das Modell nur dann als joblib, wenn es sich
    lohnt (neuer Bestwert **oder** F1 >= ``export_threshold``). So bleibt der
    Modell-Ordner schlank, während das CSV die volle Historie behält.

    Args:
        csv_path:         Pfad zur Tracking-CSV. Der Ordner (und ein
                          ``export/``-Unterordner) wird bei Bedarf angelegt.
        export_threshold: F1-Grenze, ab der ein Modell exportiert wird.
    """

    def __init__(
        self,
        csv_path: str = "../data/04_models/model_results_tracking.csv",
        export_threshold: float = 0.30,
    ):
        self.csv_path = csv_path
        self.base_dir = os.path.dirname(self.csv_path)
        self.export_dir = os.path.join(self.base_dir, "export/")
        self.export_threshold = export_threshold
        self.results: list[dict] = []

        for folder in [self.base_dir, self.export_dir]:
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)

        if os.path.exists(self.csv_path):
            try:
                self.results = pd.read_csv(self.csv_path).to_dict("records")
            except Exception:
                self.results = []

    def add_entry(
        self,
        model_name: str,
        model_obj,
        features_name: str,
        features_list,
        y_true,
        y_pred,
        y_proba=None,
        description: str = "",
    ) -> int:
        """Berechnet Metriken, loggt eine Zeile und exportiert das Modell smart."""
        from sklearn.metrics import (
            f1_score,
            precision_score,
            recall_score,
            roc_auc_score,
        )

        # 1. Metrics
        f1 = f1_score(y_true, y_pred)
        rec = recall_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred)
        auc = roc_auc_score(y_true, y_proba) if y_proba is not None else 0.0

        current_idx = len(self.results)

        # 2. Is this a new best F1?
        current_best_f1 = 0.0
        if self.results:
            current_best_f1 = max(r.get("F1-Score", 0) for r in self.results)

        is_best = f1 > current_best_f1
        is_worthy = f1 >= self.export_threshold

        # 3. Build entry
        filename_short = f"{str(current_idx).zfill(3)}_{model_name}"
        file_saved = "No"

        # 4. Smart export: only persist the model file when it is worth keeping
        if is_best or is_worthy:
            filename_for_save = os.path.join("export", filename_short)
            save_model(model_obj, filename_for_save, folder=self.base_dir)
            file_saved = f"export/{filename_short}.joblib"

        entry = {
            "Run_ID": current_idx,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Model": model_name,
            "F1-Score": round(f1, 4),
            "Recall": round(rec, 4),
            "Precision": round(prec, 4),
            "ROC-AUC": round(auc, 4),
            "Model_File": file_saved,
            "Is_Best": is_best,
            "Description": description,
        }

        self.results.append(entry)
        pd.DataFrame(self.results).to_csv(self.csv_path, index=False)

        # Terminal feedback
        if is_best:
            status = "🏆 NEW BEST & SAVED"
        elif is_worthy:
            status = f"✅ >= {self.export_threshold:.2f} & SAVED"
        else:
            status = "🔈 CSV only (F1 too low)"
        print(f"ID {current_idx}: F1={f1:.4f} -> {status}")

        return current_idx

    def get_results(self) -> pd.DataFrame:
        """Gibt die komplette Tracking-Historie als DataFrame zurück."""
        return pd.DataFrame(self.results)
