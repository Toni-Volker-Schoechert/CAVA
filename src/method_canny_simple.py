"""
Zuletzt editiert: 2026-04-04
Modulname: method_canny_simple
Maintainer: Toni Schoechert

Modulbeschreibung:
    Einfacher Canny-basierter Ansatz ohne Segment-Bridging.

    Ziel:
        Mit möglichst wenig Heuristik testen, ob gute Aufnahmebedingungen
        bereits ausreichen.

    Ablauf:
        1. Canny auf dem vorverarbeiteten Bild
        2. moderate Kanten-Nachbearbeitung
        3. Kanten für die Regionensuche etwas verdicken
        4. freie Innenregionen innerhalb der ROI bestimmen
        5. größte gültige Innenregion auswählen

Hinweis:
    Dieses Verfahren ist bewusst einfach gehalten und dient als saubere
    Referenz für die nächsten Kameratests.
"""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from analysis_common import (
    calculate_area,
    extract_enclosed_regions_from_barrier,
    resolve_min_contour_area,
)
from processor import (
    compute_gradient_based_canny_thresholds,
    detect_edges,
    erode_binary_mask,
    postprocess_edges,
)
from roi import apply_polygon_mask
from visualizer import draw_region_analysis_image, draw_roi_comparison_image


METHOD_NAME = "canny_simple"


def run_method(
    frame: np.ndarray,
    preprocess_debug: dict[str, np.ndarray],
    roi_mask: np.ndarray,
    roi_points: list[tuple[int, int]],
    roi_area_px2: float,
    config: dict,
) -> dict[str, Any]:
    """
    Führt den einfachen Canny-Ansatz für einen Frame aus.
    """
    method_cfg = config["methods"][METHOD_NAME]
    preprocessed = preprocess_debug["preprocessed"]
    scharr_magnitude = preprocess_debug["scharr_magnitude"]

    threshold_roi = erode_binary_mask(
        roi_mask,
        method_cfg["threshold_roi_erosion_kernel_size"],
    )

    if method_cfg["canny_mode"] == "gradient_quantiles":
        threshold_1, threshold_2 = compute_gradient_based_canny_thresholds(
            preprocessed,
            roi_mask=threshold_roi,
            q_low=method_cfg["canny_gradient_q_low"],
            q_high=method_cfg["canny_gradient_q_high"],
        )
    else:
        threshold_1 = method_cfg["canny_threshold_1"]
        threshold_2 = method_cfg["canny_threshold_2"]

    raw_edges_full = detect_edges(
        preprocessed,
        threshold_1=threshold_1,
        threshold_2=threshold_2,
        use_l2gradient=method_cfg["canny_use_l2gradient"],
        aperture_size=method_cfg["canny_aperture_size"],
    )

    # Die ROI wird bewusst erst nach Canny angewendet. So wird entlang des
    # Polygonrands keine künstliche Kante erzeugt.
    raw_edges = apply_polygon_mask(raw_edges_full, roi_mask)

    refined_edges = postprocess_edges(
        raw_edges,
        roi_mask=roi_mask,
        close_kernel_size=method_cfg["post_close_kernel_size"],
        close_iterations=method_cfg["post_close_iterations"],
        dilate_iterations=method_cfg["post_dilate_iterations"],
        remove_small_components=method_cfg["post_remove_small_components"],
        min_component_size=method_cfg["post_min_component_size"],
    )

    # Die Barriere für die Regionensuche darf etwas toleranter sein als das
    # eigentliche Kantenbild. Kleine Restlücken können dadurch oft noch
    # kompensiert werden.
    barrier_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    barrier = cv2.dilate(
        refined_edges,
        barrier_kernel,
        iterations=method_cfg["barrier_dilate_iterations"],
    )
    barrier = cv2.bitwise_and(barrier, barrier, mask=roi_mask)

    effective_min_contour_area = resolve_min_contour_area(
        roi_area_px2=roi_area_px2,
        min_contour_area_mode=method_cfg["min_contour_area_mode"],
        min_contour_area_px2=method_cfg["min_contour_area_px2"],
        min_contour_area_factor=method_cfg["min_contour_area_factor"],
    )

    all_contours, valid_contours, valid_areas, free_regions = extract_enclosed_regions_from_barrier(
        barrier_mask=barrier,
        roi_mask=roi_mask,
        min_contour_area_px2=effective_min_contour_area,
    )

    selected_contour = None
    if valid_contours:
        selected_contour = valid_contours[int(np.argmax(valid_areas))]

    masked_frame = apply_polygon_mask(frame, roi_mask)
    debug_images = {
        "threshold_roi": draw_roi_comparison_image(masked_frame, roi_mask, threshold_roi, roi_points),
        "canny_input": preprocessed,
        "scharr_magnitude": scharr_magnitude,
        "raw_edges": raw_edges,
        "refined_edges": refined_edges,
        "barrier": barrier,
        "free_regions": free_regions,
        "region_analysis": draw_region_analysis_image(
            masked_frame,
            roi_points=roi_points,
            all_contours=all_contours,
            valid_contours=valid_contours,
            selected_contour=selected_contour,
            title_lines=[
                f"Thresholds: {threshold_1} / {threshold_2}",
                f"All regions: {len(all_contours)}",
                f"Valid regions: {len(valid_contours)}",
                f"Area [px^2]: {calculate_area(selected_contour):.2f}",
            ],
        ),
    }

    result_fields = {
        "method": METHOD_NAME,
        "canny_threshold_1": threshold_1,
        "canny_threshold_2": threshold_2,
        "num_all_regions": len(all_contours),
        "num_valid_regions": len(valid_contours),
        "min_contour_area_px2_effective": effective_min_contour_area,
        "selected_mode": "enclosed_region" if selected_contour is not None else "none",
    }

    debug_summary = (
        f"Regionen gefunden: {len(all_contours)}, "
        f"gültig: {len(valid_contours)}, "
        f"gewählte Fläche: {calculate_area(selected_contour):.2f} px²"
    )

    return {
        "contour": selected_contour,
        "debug_images": debug_images,
        "result_fields": result_fields,
        "debug_summary": debug_summary,
    }
