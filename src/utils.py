"""
Zuletzt editiert: 2026-04-02
Modulname: utils
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul enthält kleine Hilfsfunktionen, die von mehreren anderen
    Modulen verwendet werden können.

Input:
    - Unterschiedlich, je nach Hilfsfunktion

Output:
    - Unterschiedlich, je nach Hilfsfunktion

Relevante Hinweise:
    - Noch bewusst klein gehalten.
    - Gut geeignet für Logging-Helfer, Pfadaufbereitung, Formatierung,
      spätere Zeitstempel-Utilities oder Kalibrierungsfunktionen.
"""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    """
    Stellt sicher, dass ein Verzeichnis existiert.

    Args:
        path: Verzeichnis oder Pfad, der erstellt werden soll.

    Returns:
        Path: Das erzeugte bzw. bereits vorhandene Verzeichnis.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path