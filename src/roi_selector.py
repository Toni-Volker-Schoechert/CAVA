"""
Zuletzt editiert: 2026-04-02
Modulname: roi_selector
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul kapselt die Auswahl der Region of Interest (ROI).
    Da die Kamera im Prüfstand statisch ist, wird die ROI einmal am Anfang
    ausgewählt und dann für alle Frames weiterverwendet.

Input:
    - Ein OpenCV-Frame (BGR)

Output:
    - ROI als Tupel (x, y, width, height)

Relevante Hinweise:
    - Die ROI-Auswahl erfolgt interaktiv über cv2.selectROI.
    - Wird keine sinnvolle ROI gewählt, wird ein Fehler ausgelöst.
"""

from __future__ import annotations

import cv2


def select_roi(frame, window_name: str = "ROI auswählen") -> tuple[int, int, int, int]:
    """
    Öffnet ein interaktives Fenster zur Auswahl der ROI.

    Args:
        frame: BGR-Bild, auf dem die ROI gewählt wird.
        window_name: Name des Auswahlfensters.

    Returns:
        tuple[int, int, int, int]: (x, y, w, h)

    Raises:
        ValueError: Wenn keine gültige ROI ausgewählt wurde.
    """
    roi = cv2.selectROI(window_name, frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow(window_name)

    x, y, w, h = roi
    if w <= 0 or h <= 0:
        raise ValueError("Keine gültige ROI ausgewählt.")

    return int(x), int(y), int(w), int(h)
