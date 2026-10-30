"""
Export des résultats vers JSON pour le frontend
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any


EXPORTS_DIR = Path(__file__).parent.parent / "exports"


def export_to_json(data: dict, filename: str, metadata: dict = None) -> Path:
    """
    Exporte des données vers un fichier JSON dans le dossier exports/

    Args:
        data: Les données à exporter
        filename: Nom du fichier (sans extension)
        metadata: Métadonnées optionnelles (titre, source, etc.)

    Returns:
        Path du fichier créé
    """
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator": "Outsiders Python",
            **(metadata or {}),
        },
        "data": data,
    }

    filepath = EXPORTS_DIR / f"{filename}.json"

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=_json_serializer)

    print(f"Exported: {filepath}")
    return filepath


def _json_serializer(obj: Any) -> Any:
    """Sérialise les objets non-JSON (numpy, pandas, etc.)"""
    import numpy as np
    import pandas as pd

    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
