"""
Zuletzt editiert: 2026-04-04
Modulname: visualizer
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul kümmert sich um die visuelle Ausgabe des Projekts.

    Es stellt Funktionen bereit für:
    - das finale Ergebnisbild / Overlay
    - methodenspezifische Debugbilder
    - die zentrale Anzeige der Zwischenstufen

Designziel:
    Der Visualizer kennt keine konkrete Methodenlogik. Die Methode liefert
    einfach benannte Debugbilder. Dadurch bleibt die Anzeige kompatibel mit
    späteren Erweiterungen, z. B. einem U-Net.
"""

from __future__ import annotations

import cv2
import numpy as np


def _ensure_bgr(image: np.ndarray | None) -> np.ndarray | None:
    """
    Wandelt Graubilder für die Anzeige in BGR um.
    """
    if image is None:
        return None
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image.copy()


def draw_roi_comparison_image(
    frame: np.ndarray,
    roi_mask: np.ndarray,
    inner_roi_mask: np.ndarray,
    roi_points: list[tuple[int, int]] | None = None,
) -> np.ndarray:
    """
    Zeigt äußere ROI und innere Threshold-ROI in einem Bild.
    """
    image = _ensure_bgr(frame)
    if image is None:
        raise ValueError("Frame darf nicht None sein.")

    if roi_points is not None and len(roi_points) >= 3:
        polygon = np.array(roi_points, dtype=np.int32)
        cv2.polylines(image, [polygon], True, (255, 0, 0), 2)

    inner_contours, _ = cv2.findContours(inner_roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if inner_contours:
        cv2.drawContours(image, inner_contours, -1, (0, 255, 255), 2)

    cv2.putText(
        image,
        "Blue: ROI, Yellow: Threshold ROI",
        (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return image


def draw_region_analysis_image(
    frame: np.ndarray,
    roi_points: list[tuple[int, int]] | None,
    all_contours: list[np.ndarray],
    valid_contours: list[np.ndarray],
    selected_contour,
    title_lines: list[str],
) -> np.ndarray:
    """
    Erzeugt ein Debugbild für die Regionsanalyse.

    Farbcodierung:
        - blau: ROI
        - rot: alle gefundenen Konturen
        - gelb: gültige Konturen
        - grün: ausgewählte Kontur
    """
    image = _ensure_bgr(frame)
    if image is None:
        raise ValueError("Frame darf nicht None sein.")

    if roi_points is not None and len(roi_points) >= 3:
        polygon = np.array(roi_points, dtype=np.int32)
        cv2.polylines(image, [polygon], True, (255, 0, 0), 2)

    for contour in all_contours:
        cv2.drawContours(image, [contour], -1, (0, 0, 255), 1)

    for contour in valid_contours:
        cv2.drawContours(image, [contour], -1, (0, 255, 255), 1)

    if selected_contour is not None:
        cv2.drawContours(image, [selected_contour], -1, (0, 255, 0), 2)

    y = 28
    for line in title_lines:
        cv2.putText(image, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        y += 26

    return image


def build_overlay(
    frame: np.ndarray,
    contour,
    area_px2: float,
    frame_index: int,
    time_sec: float,
    roi_points: list[tuple[int, int]] | None = None,
    method_name: str | None = None,
) -> np.ndarray:
    """
    Erzeugt das finale Ergebnisbild.
    """
    overlay = _ensure_bgr(frame)
    if overlay is None:
        raise ValueError("Frame darf nicht None sein.")

    if roi_points is not None and len(roi_points) >= 3:
        polygon = np.array(roi_points, dtype=np.int32)
        cv2.polylines(overlay, [polygon], isClosed=True, color=(255, 0, 0), thickness=2)

    if contour is not None:
        cv2.drawContours(overlay, [contour], contourIdx=-1, color=(0, 255, 0), thickness=2)

    text_lines = [
        f"Frame: {frame_index}",
        f"Time [s]: {time_sec:.3f}",
        f"Area [px^2]: {area_px2:.2f}",
    ]
    if method_name:
        text_lines.append(f"Method: {method_name}")

    y = 28
    for line in text_lines:
        cv2.putText(
            overlay,
            line,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        y += 30

    return overlay


def _show_single_image(window_name: str, image: np.ndarray | None) -> None:
    """
    Zeigt ein einzelnes Bild nur dann an, wenn es existiert.
    """
    if image is not None:
        cv2.imshow(window_name, image)


def _handle_key(wait_key_ms: int) -> None:
    """
    Liest die Tastatureingabe und erlaubt Abbruch mit ESC.
    """
    key = cv2.waitKey(wait_key_ms) & 0xFF
    if key == 27:
        raise KeyboardInterrupt("Verarbeitung durch Benutzer abgebrochen.")


def show_visualization(
    overlay_image: np.ndarray,
    wait_key_ms: int,
    window_names: dict,
    debug_config: dict,
    source_image: np.ndarray | None = None,
    normalized_image: np.ndarray | None = None,
    preprocess_image: np.ndarray | None = None,
    method_debug_images: dict[str, np.ndarray] | None = None,
) -> None:
    """
    Zentrale Steuerfunktion für die Anzeige.
    """
    debug_enabled = debug_config.get("enabled", False)

    if not debug_enabled:
        if debug_config.get("show_final_result_when_not_debug", True):
            _show_single_image(window_names["final_overlay"], overlay_image)
            _handle_key(wait_key_ms)
        return

    if debug_config.get("show_source_image", False):
        _show_single_image(window_names.get("debug_source", "Debug - Source Image"), source_image)

    if debug_config.get("show_normalized_image", False):
        _show_single_image(window_names.get("debug_normalized", "Debug - Normalized Image"), normalized_image)

    if debug_config.get("show_preprocess", False):
        _show_single_image(window_names.get("debug_preprocess", "Debug - Preprocess"), preprocess_image)

    if debug_config.get("show_method_debug_images", True) and method_debug_images is not None:
        method_window_names = window_names.get("method_debug", {})
        for key, image in method_debug_images.items():
            window_name = method_window_names.get(key, f"Debug - {key}")
            _show_single_image(window_name, image)

    if debug_config.get("show_overlay", True):
        _show_single_image(window_names["debug_overlay"], overlay_image)

    _handle_key(wait_key_ms)
