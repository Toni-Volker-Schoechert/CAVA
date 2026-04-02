"""
Zuletzt editiert: 2026-04-02
Modulname: visualizer
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul kümmert sich um die visuelle Debug-Ausgabe.
    Es zeichnet gefundene Konturen und Messwerte in das Bild ein und zeigt
    zusätzlich optional das Kantenbild an.

Input:
    - Original-ROI (BGR)
    - Kantenbild
    - erkannte Kontur
    - Flächenwert
    - Frame-Metadaten für Anzeige

Output:
    - Fensteranzeige über OpenCV

Relevante Hinweise:
    - ESC beendet die Verarbeitung über KeyboardInterrupt.
    - Die Anzeige ist vor allem für Entwicklung und Tuning gedacht.
"""

from __future__ import annotations

import cv2
import numpy as np


def build_overlay(
    frame: np.ndarray,
    contour,
    area_px2: float,
    frame_index: int,
    time_sec: float,
) -> np.ndarray:
    """
    Erzeugt ein annotiertes Bild für die Debug-Anzeige.

    Args:
        frame: ROI-Bild im BGR-Format.
        contour: Gefundene Kontur oder None.
        area_px2: Gemessene Fläche in Pixel².
        frame_index: Aktueller Frame-Index.
        time_sec: Zeitstempel in Sekunden.

    Returns:
        np.ndarray: Annotiertes Bild.
    """
    overlay = frame.copy()

    if contour is not None:
        cv2.drawContours(overlay, [contour], -1, (0, 255, 0), 2)

    text_lines = [
        f"Frame: {frame_index}",
        f"Time [s]: {time_sec:.3f}",
        f"Area [px^2]: {area_px2:.2f}",
    ]

    y = 25
    for line in text_lines:
        cv2.putText(
            overlay,
            line,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        y += 28

    return overlay


def show_debug(
    overlay: np.ndarray,
    edges: np.ndarray,
    overlay_window_name: str = "Debug Overlay",
    edges_window_name: str = "Debug Edges",
    show_edges: bool = True,
    wait_key_ms: int = 30,
) -> None:
    """
    Zeigt Debug-Fenster an.

    Args:
        overlay: Annotiertes BGR-Bild.
        edges: Kantenbild.
        overlay_window_name: Fenstertitel für Overlay.
        edges_window_name: Fenstertitel für Edges.
        show_edges: Falls True, wird auch das Edges-Fenster angezeigt.
        wait_key_ms: Delay für cv2.waitKey.

    Raises:
        KeyboardInterrupt: Bei ESC-Abbruch.
    """
    cv2.imshow(overlay_window_name, overlay)
    if show_edges:
        cv2.imshow(edges_window_name, edges)

    key = cv2.waitKey(wait_key_ms) & 0xFF
    if key == 27:  # ESC
        raise KeyboardInterrupt("Verarbeitung durch Benutzer abgebrochen.")
