"""
Zuletzt editiert: 2026-04-02
Modulname: processor
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul übernimmt die Vorverarbeitung der Bilddaten.
    Dazu gehören aktuell:
        - Umwandlung nach Graustufen
        - Rauschreduktion per Gaussian Blur
        - Edge Detection per Canny

Input:
    - BGR-Frame oder ROI als NumPy-Array

Output:
    - Graustufenbild
    - geglättetes Bild
    - Kantenbild (Edges)

Relevante Hinweise:
    - Canny ist ein guter Startpunkt für Debugging und erste Tests.
    - Für robuste Segmentierung kann später Thresholding oder Morphologie
      besser geeignet sein.
"""

from __future__ import annotations

import cv2
import numpy as np


def preprocess_frame(
    frame: np.ndarray,
    gaussian_kernel_size: tuple[int, int] = (5, 5),
    gaussian_sigma: int | float = 0,
) -> np.ndarray:
    """
    Führt die Grundvorverarbeitung auf einem BGR-Frame durch.

    Args:
        frame: Eingabebild im BGR-Format.
        gaussian_kernel_size: Kernelgröße für den Gaussian Blur.
        gaussian_sigma: Sigma-Wert für den Gaussian Blur.

    Returns:
        np.ndarray: Vorgefiltertes Graustufenbild.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, gaussian_kernel_size, gaussian_sigma)
    return blurred


def detect_edges(
    gray_or_blurred_frame: np.ndarray,
    threshold_1: int = 50,
    threshold_2: int = 150,
) -> np.ndarray:
    """
    Führt Canny Edge Detection aus.

    Args:
        gray_or_blurred_frame: Vorverarbeitetes Graustufenbild.
        threshold_1: Untere Canny-Schwelle.
        threshold_2: Obere Canny-Schwelle.

    Returns:
        np.ndarray: Binäres Kantenbild.
    """
    return cv2.Canny(gray_or_blurred_frame, threshold_1, threshold_2)
