"""
Zuletzt editiert: 2026-04-04
Modulname: main
Maintainer: Toni Schoechert

Modulbeschreibung:
    Einstiegspunkt des Programms.

    Ziel dieses Stands:
    - gemeinsame Infrastruktur beibehalten
    - nur noch den einfachen Canny-Ansatz verwenden
    - den Code übersichtlich und gut testbar halten
    - spätere Erweiterung, z. B. mit U-Net, vorbereiten

Architektur:
    - data_loader, roi, visualizer, exporter bleiben gemeinsam
    - die eigentliche Segmentierungslogik steckt in einer Methoden-Datei
    - die Methode liefert eine standardisierte Struktur zurück
"""

from __future__ import annotations

import sys
from typing import Any

import cv2

from analysis_common import calculate_area
from config import CONFIG
from data_loader import load_media, select_file
from exporter import save_results_csv
from method_canny_simple import METHOD_NAME as CANNY_METHOD_NAME, run_method as run_canny_simple
from processor import preprocess_for_methods
from roi import apply_polygon_mask, create_polygon_mask, select_polygon_roi
from utils import ensure_directory
from visualizer import build_overlay, show_visualization


METHOD_RUNNERS = {
    CANNY_METHOD_NAME: run_canny_simple,
}


def debug_print(message: str) -> None:
    """
    Gibt Debugmeldungen nur aus, wenn Debug aktiviert ist.
    """
    if CONFIG["debug"]["enabled"] and CONFIG["debug"]["print_messages"]:
        print(message)


def select_input_and_load_media() -> tuple[str, str, list, float]:
    """
    Lässt den Benutzer eine Datei auswählen und lädt sie als Bild oder Video.
    """
    file_path = select_file()
    print(f"Ausgewählte Datei: {file_path}")

    media_type, frames, fps = load_media(file_path)
    print(f"Medientyp: {media_type}")
    print(f"Anzahl Frames: {len(frames)}")
    print(f"FPS: {fps:.3f}")

    return file_path, media_type, frames, fps


def initialize_roi(first_frame) -> tuple[list[tuple[int, int]], Any, float]:
    """
    Wählt die polygonale ROI einmal im ersten Frame aus und erzeugt die Maske.
    """
    roi_points = select_polygon_roi(
        first_frame,
        window_name=CONFIG["window_names"]["roi_selection"],
    )
    print(f"Gewählte Polygon-ROI: {roi_points}")

    roi_mask = create_polygon_mask(first_frame.shape, roi_points)
    roi_area_px2 = float(cv2.countNonZero(roi_mask))
    return roi_points, roi_mask, roi_area_px2


def get_wait_key_ms(media_type: str) -> int:
    """
    Liefert die Anzeigedauer für cv2.waitKey abhängig vom Medientyp.
    """
    return (
        CONFIG["visualization"]["wait_key_ms_image"]
        if media_type == "image"
        else CONFIG["visualization"]["wait_key_ms_video"]
    )


def process_frame(
    frame,
    frame_index: int,
    fps: float,
    roi_mask,
    roi_points: list[tuple[int, int]],
    roi_area_px2: float,
) -> dict[str, Any]:
    """
    Verarbeitet genau einen Frame und gibt Ergebnis- sowie Debugdaten zurück.
    """
    method_name = CONFIG["method"]["name"]
    if method_name not in METHOD_RUNNERS:
        raise ValueError(f"Unbekannte Methode: {method_name}")

    time_sec = frame_index / fps if fps else 0.0

    debug_print(f"\n--- Frame {frame_index} ---")
    debug_print(f"Aktive Methode: {method_name}")
    debug_print("Vorverarbeitung gestartet.")

    preprocess_debug = preprocess_for_methods(frame, CONFIG)
    source_image = preprocess_debug["source_image"]
    normalized_image = preprocess_debug["normalized_image"]
    preprocessed = preprocess_debug["preprocessed"]

    debug_print("Methodenspezifische Analyse gestartet.")
    method_output = METHOD_RUNNERS[method_name](
        frame=frame,
        preprocess_debug=preprocess_debug,
        roi_mask=roi_mask,
        roi_points=roi_points,
        roi_area_px2=roi_area_px2,
        config=CONFIG,
    )

    contour = method_output["contour"]
    area_px2 = calculate_area(contour)
    area_ratio_roi = area_px2 / roi_area_px2 if roi_area_px2 > 0 else 0.0
    masked_frame = apply_polygon_mask(frame, roi_mask)

    debug_print(method_output["debug_summary"])
    debug_print(f"ROI-Anteil: {area_ratio_roi:.5f}")

    overlay = build_overlay(
        frame=masked_frame,
        contour=contour,
        area_px2=area_px2,
        frame_index=frame_index,
        time_sec=time_sec,
        roi_points=roi_points,
        method_name=method_name,
    )

    result_row = {
        "frame": frame_index,
        "time_sec": time_sec,
        "area_px2": area_px2,
        "area_ratio_roi": area_ratio_roi,
        "contour_found": contour is not None,
        "luminance_mode": CONFIG["preprocessing"]["luminance_mode"],
        "background_normalization_enabled": CONFIG["preprocessing"]["use_local_background_normalization"],
        "clahe_enabled": CONFIG["preprocessing"]["use_clahe"],
        "filter_mode": CONFIG["preprocessing"]["filter_mode"],
        **method_output["result_fields"],
    }

    return {
        "result_row": result_row,
        "overlay": overlay,
        "source_image": source_image,
        "normalized_image": normalized_image,
        "preprocessed": preprocessed,
        "method_debug_images": method_output["debug_images"],
    }


def export_results(results: list[dict]) -> None:
    """
    Exportiert die gesammelten Frame-Ergebnisse als CSV.
    """
    output_dir = ensure_directory(CONFIG["export"]["output_dir"])
    output_csv = output_dir / CONFIG["export"]["csv_filename"]
    written_path = save_results_csv(results, output_csv)
    print(f"CSV gespeichert unter: {written_path}")


def main() -> int:
    """
    Hauptfunktion des Programms.
    """
    try:
        _, media_type, frames, fps = select_input_and_load_media()
        first_frame = frames[0]
        roi_points, roi_mask, roi_area_px2 = initialize_roi(first_frame)
        wait_key_ms = get_wait_key_ms(media_type)

        results: list[dict] = []
        final_overlay = None

        for frame_index, frame in enumerate(frames):
            frame_output = process_frame(
                frame=frame,
                frame_index=frame_index,
                fps=fps,
                roi_mask=roi_mask,
                roi_points=roi_points,
                roi_area_px2=roi_area_px2,
            )

            results.append(frame_output["result_row"])
            final_overlay = frame_output["overlay"]

            show_visualization(
                overlay_image=frame_output["overlay"],
                source_image=frame_output["source_image"],
                normalized_image=frame_output["normalized_image"],
                preprocess_image=frame_output["preprocessed"],
                method_debug_images=frame_output["method_debug_images"],
                wait_key_ms=wait_key_ms,
                window_names=CONFIG["window_names"],
                debug_config=CONFIG["debug"],
            )

        export_results(results)

        if (
            not CONFIG["debug"]["enabled"]
            and CONFIG["debug"]["show_final_result_when_not_debug"]
            and final_overlay is not None
        ):
            show_visualization(
                overlay_image=final_overlay,
                source_image=None,
                normalized_image=None,
                preprocess_image=None,
                method_debug_images=None,
                wait_key_ms=0,
                window_names=CONFIG["window_names"],
                debug_config=CONFIG["debug"],
            )

    except KeyboardInterrupt as exc:
        print(str(exc))
        return 1
    except Exception as exc:
        print(f"Fehler: {exc}")
        return 1
    finally:
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
