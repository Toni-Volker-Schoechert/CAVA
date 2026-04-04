"""
Zuletzt editiert: 2026-04-04
Modulname: processor
Maintainer: Toni Schoechert

Modulbeschreibung:
    Gemeinsame Vorverarbeitung für den einfachen Canny-Ansatz.

    Dieses Modul kümmert sich bewusst nur um:
    - Auswahl eines Helligkeitskanals
    - optionale Hintergrundnormalisierung
    - optionale Glättung
    - optionale milde CLAHE-Verstärkung
    - Hilfsfunktionen für Canny
    - moderate Kanten-Nachbearbeitung

Hinweis:
    Die eigentliche Segmentierungslogik liegt absichtlich nicht hier,
    sondern getrennt in der Methoden-Datei.
"""

from __future__ import annotations

import cv2
import numpy as np


def extract_luminance(frame: np.ndarray, mode: str = "gray") -> np.ndarray:
    """
    Extrahiert einen Helligkeitskanal aus einem BGR-Bild.
    """
    if mode == "gray":
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if mode == "lab_l":
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, _, _ = cv2.split(lab)
        return l_channel

    raise ValueError(f"Unbekannter luminance mode: {mode}")


def normalize_local_background(gray: np.ndarray, sigma: float = 15.0) -> np.ndarray:
    """
    Entfernt langsame Helligkeitsschwankungen im Bild.
    """
    gray_f = gray.astype(np.float32)
    background = cv2.GaussianBlur(gray_f, (0, 0), sigmaX=sigma, sigmaY=sigma)
    normalized = gray_f - background
    normalized = cv2.normalize(normalized, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def apply_gaussian_blur(
    gray: np.ndarray,
    kernel_size: tuple[int, int] = (3, 3),
    sigma: int | float = 0,
) -> np.ndarray:
    """
    Glättet ein Graustufenbild per Gaussian Blur.
    """
    return cv2.GaussianBlur(gray, kernel_size, sigma)


def apply_bilateral_filter(
    gray: np.ndarray,
    d: int = 7,
    sigma_color: float = 40,
    sigma_space: float = 40,
) -> np.ndarray:
    """
    Wendet einen Bilateral Filter an.
    """
    return cv2.bilateralFilter(gray, d, sigma_color, sigma_space)


def apply_clahe(
    gray: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (16, 16),
) -> np.ndarray:
    """
    Wendet CLAHE vorsichtig auf ein Graustufenbild an.

    Hinweis:
        Diese Verstärkung sollte für Canny eher mild bleiben,
        damit nicht zu viele künstliche Mikrostrukturen entstehen.
    """
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid_size,
    )
    return clahe.apply(gray)


def compute_scharr_gradient_magnitude(gray: np.ndarray) -> np.ndarray:
    """
    Berechnet die Scharr-Gradientenstärke als Debugbild.

    Zweck:
        Dieses Bild zeigt, wo für Canny starke lokale Helligkeitsänderungen
        vorliegen. Es dient nur dem Debugging und der Einschätzung, ob die
        Vorverarbeitung den echten Rand wirklich stärkt.
    """
    gx = cv2.Scharr(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Scharr(gray, cv2.CV_32F, 0, 1)
    magnitude = cv2.magnitude(gx, gy)

    magnitude_vis = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    return magnitude_vis.astype(np.uint8)


def preprocess_for_methods(frame: np.ndarray, config: dict) -> dict[str, np.ndarray]:
    """
    Führt die gemeinsame Vorverarbeitung aus.

    Reihenfolge:
        1. Helligkeitskanal wählen
        2. optional Hintergrund normalisieren
        3. optional glätten
        4. optional mildes CLAHE anwenden

    Rückgabe:
        - source_image: ursprünglicher Helligkeitskanal
        - normalized_image: nach Hintergrundnormalisierung
        - preprocessed: finales Eingabebild für Canny
        - scharr_magnitude: Gradienten-Debugbild des finalen Eingabebilds
    """
    source_image = extract_luminance(
        frame,
        mode=config["preprocessing"]["luminance_mode"],
    )

    working = source_image

    if config["preprocessing"]["use_local_background_normalization"]:
        normalized_image = normalize_local_background(
            working,
            sigma=config["preprocessing"]["background_normalization_sigma"],
        )
        working = normalized_image
    else:
        normalized_image = working.copy()

    filter_mode = config["preprocessing"]["filter_mode"]
    if filter_mode == "none":
        filtered_image = working
    elif filter_mode == "gaussian":
        filtered_image = apply_gaussian_blur(
            working,
            kernel_size=config["preprocessing"]["gaussian_kernel_size"],
            sigma=config["preprocessing"]["gaussian_sigma"],
        )
    elif filter_mode == "bilateral":
        filtered_image = apply_bilateral_filter(
            working,
            d=config["preprocessing"]["bilateral_d"],
            sigma_color=config["preprocessing"]["bilateral_sigma_color"],
            sigma_space=config["preprocessing"]["bilateral_sigma_space"],
        )
    else:
        raise ValueError(f"Unbekannter filter mode: {filter_mode}")

    if config["preprocessing"]["use_clahe"]:
        preprocessed = apply_clahe(
            filtered_image,
            clip_limit=config["preprocessing"]["clahe_clip_limit"],
            tile_grid_size=config["preprocessing"]["clahe_tile_grid_size"],
        )
    else:
        preprocessed = filtered_image

    scharr_magnitude = compute_scharr_gradient_magnitude(preprocessed)

    return {
        "source_image": source_image,
        "normalized_image": normalized_image,
        "preprocessed": preprocessed,
        "scharr_magnitude": scharr_magnitude,
    }


def erode_binary_mask(mask: np.ndarray, kernel_size: int) -> np.ndarray:
    """
    Erodiert eine Binärmaske mit elliptischem Kernel.
    """
    if kernel_size <= 1:
        return mask.copy()

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    eroded = cv2.erode(mask, kernel, iterations=1)

    if cv2.countNonZero(eroded) == 0:
        return mask.copy()
    return eroded


def compute_gradient_based_canny_thresholds(
    gray: np.ndarray,
    roi_mask: np.ndarray | None = None,
    q_low: float = 0.70,
    q_high: float = 0.92,
) -> tuple[int, int]:
    """
    Bestimmt Canny-Schwellen aus der Gradientenstärke.
    """
    gx = cv2.Scharr(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Scharr(gray, cv2.CV_32F, 0, 1)
    magnitude = cv2.magnitude(gx, gy)

    if roi_mask is not None:
        values = magnitude[roi_mask > 0]
    else:
        values = magnitude.reshape(-1)

    values = values[np.isfinite(values)]
    if values.size == 0:
        return 20, 60

    lower = float(np.quantile(values, q_low))
    upper = float(np.quantile(values, q_high))
    if upper <= lower:
        upper = lower + 1.0

    return int(lower), int(upper)


def detect_edges(
    gray: np.ndarray,
    threshold_1: int,
    threshold_2: int,
    use_l2gradient: bool = True,
    aperture_size: int = 3,
) -> np.ndarray:
    """
    Führt Canny Edge Detection aus.
    """
    return cv2.Canny(
        gray,
        threshold_1,
        threshold_2,
        apertureSize=aperture_size,
        L2gradient=use_l2gradient,
    )


def remove_small_binary_components(binary_image: np.ndarray, min_component_size: int = 20) -> np.ndarray:
    """
    Entfernt sehr kleine zusammenhängende Komponenten aus einem Binärbild.
    """
    binary = (binary_image > 0).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)

    cleaned = np.zeros_like(binary_image)
    for label_id in range(1, num_labels):
        area = int(stats[label_id, cv2.CC_STAT_AREA])
        if area < min_component_size:
            continue
        cleaned[labels == label_id] = 255

    return cleaned


def postprocess_edges(
    edges: np.ndarray,
    roi_mask: np.ndarray | None = None,
    close_kernel_size: int = 3,
    close_iterations: int = 1,
    dilate_iterations: int = 0,
    remove_small_components: bool = True,
    min_component_size: int = 20,
) -> np.ndarray:
    """
    Bereitet ein Kantenbild moderat für die weitere Analyse vor.

    Ziel:
        - kleine isolierte Fragmente entfernen
        - kleine Unterbrechungen glätten
        - die Kanten nicht unnötig stark verbreitern
    """
    refined = edges.copy()

    if remove_small_components:
        refined = remove_small_binary_components(refined, min_component_size=min_component_size)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_kernel_size, close_kernel_size))
    refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel, iterations=close_iterations)

    if dilate_iterations > 0:
        refined = cv2.dilate(refined, kernel, iterations=dilate_iterations)

    if remove_small_components:
        refined = remove_small_binary_components(refined, min_component_size=min_component_size)

    if roi_mask is not None:
        refined = cv2.bitwise_and(refined, refined, mask=roi_mask)

    return refined
