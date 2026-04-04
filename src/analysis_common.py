"""
Zuletzt editiert: 2026-04-04
Modulname: analysis_common
Maintainer: Toni Schoechert

Modulbeschreibung:
    Gemeinsame Hilfsfunktionen für die Kontur- und Regionsanalyse.

    Dieses Modul enthält nur die einfachen, wirklich verwendeten Bausteine:
    - Flächenberechnung
    - Auflösung der minimalen Konturfläche
    - Extraktion gültiger Regionen innerhalb der ROI
    - Ableitung eingeschlossener Innenregionen aus einer Barriere-Maske

Hinweis:
    Die Regionslogik ist bewusst einfach gehalten. Eine Region gilt als
    ungültig, wenn sie die ROI-Grenze berührt. Das entspricht praktisch der
    Idee eines Flood-Fill von außen: Alles, was mit dem Rand verbunden ist,
    gehört zum Außenbereich.
"""

from __future__ import annotations

import cv2
import numpy as np


def calculate_area(contour) -> float:
    """
    Berechnet die Fläche einer Kontur in Pixel².
    """
    if contour is None:
        return 0.0
    return float(cv2.contourArea(contour))


def resolve_min_contour_area(
    roi_area_px2: float,
    min_contour_area_mode: str = "absolute",
    min_contour_area_px2: float = 50.0,
    min_contour_area_factor: float = 0.05,
) -> float:
    """
    Bestimmt die effektiv verwendete minimale Konturfläche.

    Modi:
        - absolute: fester Pixelwert
        - relative: Anteil der ROI-Fläche
    """
    if min_contour_area_mode == "relative":
        return roi_area_px2 * min_contour_area_factor
    return min_contour_area_px2


def extract_valid_regions_from_mask(
    candidate_mask: np.ndarray,
    roi_mask: np.ndarray,
    min_contour_area_px2: float,
) -> tuple[list[np.ndarray], list[np.ndarray], list[float], np.ndarray]:
    """
    Extrahiert Kandidatenregionen, die vollständig innerhalb der ROI liegen.

    Ablauf:
        1. Maske auf ROI beschränken
        2. Connected Components bestimmen
        3. Komponenten verwerfen, die die ROI-Grenze berühren
        4. kleine Komponenten verwerfen

    Rückgabe:
        - alle gefundenen Konturen
        - gültige Konturen
        - gültige Flächen
        - die tatsächlich verwendete Binärmaske innerhalb der ROI
    """
    working_mask = np.zeros_like(candidate_mask, dtype=np.uint8)
    working_mask[(candidate_mask > 0) & (roi_mask > 0)] = 255

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        (working_mask > 0).astype(np.uint8),
        connectivity=8,
    )

    small_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    roi_inner = cv2.erode(roi_mask, small_kernel, iterations=1)
    roi_boundary = cv2.subtract(roi_mask, roi_inner)
    labels_touching_boundary = set(np.unique(labels[roi_boundary > 0]))

    all_contours: list[np.ndarray] = []
    valid_contours: list[np.ndarray] = []
    valid_areas: list[float] = []

    for label_id in range(1, num_labels):
        region_mask = np.zeros_like(working_mask, dtype=np.uint8)
        region_mask[labels == label_id] = 255

        contours, _ = cv2.findContours(
            region_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        if not contours:
            continue

        contour = max(contours, key=cv2.contourArea)
        contour_area = float(cv2.contourArea(contour))
        all_contours.append(contour)

        if label_id in labels_touching_boundary:
            continue
        if contour_area < min_contour_area_px2:
            continue

        valid_contours.append(contour)
        valid_areas.append(contour_area)

    return all_contours, valid_contours, valid_areas, working_mask


def extract_enclosed_regions_from_barrier(
    barrier_mask: np.ndarray,
    roi_mask: np.ndarray,
    min_contour_area_px2: float,
) -> tuple[list[np.ndarray], list[np.ndarray], list[float], np.ndarray]:
    """
    Bestimmt freie Innenregionen aus einer Barriere-Maske.

    Idee:
        - Kanten wirken als Barriere
        - freie Pixel innerhalb der ROI werden als Regionen betrachtet
        - Regionen mit Kontakt zum ROI-Rand gehören zum Außenbereich
        - nur vollständig eingeschlossene Regionen bleiben übrig
    """
    free_mask = np.zeros_like(barrier_mask, dtype=np.uint8)
    free_mask[(roi_mask > 0) & (barrier_mask == 0)] = 255

    return extract_valid_regions_from_mask(
        candidate_mask=free_mask,
        roi_mask=roi_mask,
        min_contour_area_px2=min_contour_area_px2,
    )
