"""
Zuletzt editiert: 2026-04-02
Modulname: analyzer
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul enthält die Bildanalyse.
    Es sucht Konturen im Kantenbild und bestimmt daraus eine aktuell als relevant
    angenommene Öffnungskontur. Anschließend kann deren Fläche berechnet werden.

Input:
    - Kantenbild (binary / edge image)

Output:
    - Gefundene Kontur oder None
    - Flächenwert in Pixel²

Relevante Hinweise:
    - Aktuell wird als einfacher Startansatz die größte gültige Kontur gewählt.
    - Das ist bewusst nur ein Prototyp und nicht zwingend die tatsächliche
      innere Herzklappenöffnung.
    - Die Auswahlstrategie kann später leicht gegen bessere Heuristiken,
      Formtests oder Segmentierungsverfahren ersetzt werden.
"""

from __future__ import annotations

import cv2
import numpy as np


def find_opening_contour(
    edges: np.ndarray,
    min_contour_area_px2: float = 50.0,
    use_external_contours_only: bool = True,
):
    """
    Findet eine Kandidatenkontur für die Öffnung.

    Args:
        edges: Kantenbild.
        min_contour_area_px2: Minimale Fläche, damit kleine Störungen ignoriert werden.
        use_external_contours_only: Wenn True, werden nur äußere Konturen gesucht.

    Returns:
        contour | None:
            Größte gültige Kontur oder None, wenn nichts Geeignetes gefunden wurde.
    """
    retrieval_mode = cv2.RETR_EXTERNAL if use_external_contours_only else cv2.RETR_LIST
    contours, _ = cv2.findContours(edges, retrieval_mode, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    valid_contours = [c for c in contours if cv2.contourArea(c) >= min_contour_area_px2]
    if not valid_contours:
        return None

    # Für den ersten Prototyp nehmen wir die größte gültige Kontur.
    # Diese Logik ist leicht verständlich und einfach austauschbar.
    return max(valid_contours, key=cv2.contourArea)


def calculate_area(contour) -> float:
    """
    Berechnet die Fläche einer Kontur in Pixel².

    Args:
        contour: OpenCV-Kontur.

    Returns:
        float: Fläche in Pixel², bei None -> 0.0
    """
    if contour is None:
        return 0.0
    return float(cv2.contourArea(contour))
