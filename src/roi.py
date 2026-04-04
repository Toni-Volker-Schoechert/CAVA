"""
Zuletzt editiert: 2026-04-02
Modulname: roi.py
Maintainer: Toni Schoechert

Modulbeschreibung:
    Funktionen für die polygonale Region of Interest (ROI).

    Dieses Modul umfasst:
    - interaktive Auswahl einer Polygon-ROI
    - Erzeugung einer Binärmaske aus der Polygon-ROI
    - Anwenden der Polygonmaske auf Bilder oder Edge-Bilder

Inputs:
    - frame / image : np.ndarray
        Eingabebild im OpenCV-Format
    - polygon_points : list[tuple[int, int]]
        Polygonpunkte der ROI

Outputs:
    - Polygonpunkte
    - Binärmaske
    - maskiertes Bild

Hinweise:
    - Die ROI wird einmal im ersten Frame festgelegt.
    - Da die Kamera statisch ist, kann dieselbe ROI-Maske für alle Frames
      wiederverwendet werden.
    - Für die Kantendetektion ist es meist besser, zuerst die Edges zu
      berechnen und erst danach die Maske anzuwenden.
"""

from __future__ import annotations

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import PolygonSelector


def select_polygon_roi(
    frame,
    window_name: str = "Polygon-ROI auswählen"
) -> list[tuple[int, int]]:
    """
    Öffnet ein Matplotlib-Fenster zur Auswahl einer polygonalen ROI.

    Parameters
    ----------
    frame : np.ndarray
        Eingabebild im BGR-Format.
    window_name : str
        Fenstertitel.

    Returns
    -------
    list[tuple[int, int]]
        Polygonpunkte als Liste von (x, y)-Koordinaten.
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    roi_store: dict[str, list[tuple[int, int]] | None] = {"points": None}

    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title(window_name)
    ax.imshow(frame_rgb)
    ax.set_title("Polygon setzen, mit Enter abschließen, dann Fenster schließen")

    def on_select(vertices):
        """
        Callback nach abgeschlossener Polygonauswahl.
        """
        points = [(int(x), int(y)) for x, y in vertices]
        if len(points) >= 3:
            roi_store["points"] = points

    selector = PolygonSelector(ax, on_select)
    plt.show()

    points = roi_store["points"]
    if points is None:
        raise RuntimeError("Keine gültige Polygon-ROI ausgewählt.")

    return points


def create_polygon_mask(
    image_shape: tuple,
    polygon_points: list[tuple[int, int]]
) -> np.ndarray:
    """
    Erzeugt eine Binärmaske aus Polygonpunkten.

    Parameters
    ----------
    image_shape : tuple
        Shape des Bildes, z. B. frame.shape oder edges.shape.
    polygon_points : list[tuple[int, int]]
        Polygonpunkte als Liste von (x, y)-Koordinaten.

    Returns
    -------
    np.ndarray
        Binärmaske mit 255 innerhalb und 0 außerhalb des Polygons.
    """
    height, width = image_shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    polygon = np.array(polygon_points, dtype=np.int32)
    cv2.fillPoly(mask, [polygon], 255)

    return mask


def apply_polygon_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Wendet eine Polygonmaske auf ein Bild an.

    Parameters
    ----------
    image : np.ndarray
        Eingabebild oder Edge-Bild.
    mask : np.ndarray
        Binärmaske der ROI.

    Returns
    -------
    np.ndarray
        Maskiertes Bild.
    """
    return cv2.bitwise_and(image, image, mask=mask)