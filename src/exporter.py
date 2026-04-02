"""
Zuletzt editiert: 2026-04-02
Modulname: exporter
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul speichert Analyseergebnisse in Dateien.
    Aktuell wird eine CSV-Datei erzeugt, damit die Messwerte später in Excel,
    Python, MATLAB oder anderen Tools weiterverarbeitet werden können.

Input:
    - Liste von Ergebnis-Dictionaries
    - Zielpfad oder Ausgabeverzeichnis

Output:
    - CSV-Datei mit Messwerten

Relevante Hinweise:
    - CSV ist bewusst als einfaches und universelles Austauschformat gewählt.
    - Später können weitere Exporter ergänzt werden, z. B. Excel oder JSON.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_results_csv(results: list[dict], output_path: str | Path) -> Path:
    """
    Speichert Ergebnisse als CSV-Datei.

    Args:
        results: Liste von Dictionaries mit Ergebnisdaten.
        output_path: Zielpfad der CSV-Datei.

    Returns:
        Path: Pfad zur geschriebenen CSV-Datei.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    return output_path
