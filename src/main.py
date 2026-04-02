"""
Zuletzt editiert: 2026-04-02
Modulname: main
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dies ist der Einstiegspunkt des Programms.
    Das Modul orchestriert den gesamten Ablauf:
        1. Datei auswählen
        2. Bild oder Video laden
        3. ROI auswählen
        4. Vorverarbeitung durchführen
        5. Kanten bestimmen
        6. Kontur der Öffnung schätzen
        7. Fläche berechnen
        8. Debug-Anzeige aktualisieren
        9. Ergebnisse speichern

Input:
    - Benutzerinteraktion für Dateiauswahl und ROI-Auswahl

Output:
    - Terminalausgabe
    - Debug-Fenster
    - CSV-Datei mit Ergebnissen

Relevante Hinweise:
    - Dieser Stand ist bewusst als gut lesbarer und modularer Prototyp aufgebaut.
    - Die aktuelle Konturstrategie ist noch nicht endgültig und dient als
      nachvollziehbarer Startpunkt für weitere Verbesserung.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2

from analyzer import calculate_area, find_opening_contour
from config import CONFIG
from data_loader import load_media, select_file
from exporter import save_results_csv
from processor import detect_edges, preprocess_frame
from roi_selector import select_roi
from utils import ensure_directory
from visualizer import build_overlay, show_debug


def main() -> int:
    """
    Hauptfunktion des Programms.

    Returns:
        int: Exit-Code (0 = Erfolg, 1 = Fehler)
    """
    try:
        # 1) Datei auswählen
        file_path = select_file()
        print(f"Ausgewählte Datei: {file_path}")

        # 2) Medien laden
        media_type, frames, fps = load_media(file_path)
        print(f"Medientyp: {media_type}")
        print(f"Anzahl Frames: {len(frames)}")
        print(f"FPS: {fps:.3f}")

        # 3) ROI anhand des ersten Frames auswählen
        first_frame = frames[0]
        roi = select_roi(first_frame, CONFIG["window_names"]["roi_selection"])
        x, y, w, h = roi
        print(f"Gewählte ROI: x={x}, y={y}, w={w}, h={h}")

        results = []

        # 4) Alle Frames durchlaufen
        for frame_index, frame in enumerate(frames):
            # ROI zuschneiden, weil nur dieser Bereich analysiert werden soll.
            roi_frame = frame[y : y + h, x : x + w]

            # Vorverarbeitung
            preprocessed = preprocess_frame(
                roi_frame,
                gaussian_kernel_size=CONFIG["preprocessing"]["gaussian_kernel_size"],
                gaussian_sigma=CONFIG["preprocessing"]["gaussian_sigma"],
            )

            # Edge Detection
            edges = detect_edges(
                preprocessed,
                threshold_1=CONFIG["edge_detection"]["canny_threshold_1"],
                threshold_2=CONFIG["edge_detection"]["canny_threshold_2"],
            )

            # Konturanalyse
            contour = find_opening_contour(
                edges,
                min_contour_area_px2=CONFIG["analysis"]["min_contour_area_px2"],
                use_external_contours_only=CONFIG["analysis"]["use_external_contours_only"],
            )
            area_px2 = calculate_area(contour)

            # Zeitstempel pro Frame. Bei Bildern ist fps = 1.0.
            time_sec = frame_index / fps if fps > 0 else 0.0

            # Ausgabe im Terminal für schnelles Debugging.
            print(
                f"Frame {frame_index:05d} | "
                f"Zeit: {time_sec:8.3f} s | "
                f"Fläche: {area_px2:10.2f} px^2"
            )

            # Ergebnisdatensatz für späteren Export.
            results.append(
                {
                    "frame": frame_index,
                    "time_sec": time_sec,
                    "area_px2": area_px2,
                    "roi_x": x,
                    "roi_y": y,
                    "roi_w": w,
                    "roi_h": h,
                }
            )

            # Overlay für Debugfenster erzeugen.
            overlay = build_overlay(
                roi_frame,
                contour,
                area_px2=area_px2,
                frame_index=frame_index,
                time_sec=time_sec,
            )

            # Unterschiedliche Anzeigezeiten für Bild und Video.
            wait_key_ms = (
                CONFIG["visualization"]["wait_key_ms_image"]
                if media_type == "image"
                else CONFIG["visualization"]["wait_key_ms_video"]
            )

            show_debug(
                overlay=overlay,
                edges=edges,
                overlay_window_name=CONFIG["window_names"]["debug_overlay"],
                edges_window_name=CONFIG["window_names"]["debug_edges"],
                show_edges=CONFIG["visualization"]["show_edges"],
                wait_key_ms=wait_key_ms,
            )

        # 5) Ergebnisse speichern
        output_dir = ensure_directory(CONFIG["export"]["output_dir"])
        output_csv = output_dir / CONFIG["export"]["csv_filename"]
        written_path = save_results_csv(results, output_csv)
        print(f"CSV gespeichert unter: {written_path}")

    except KeyboardInterrupt as exc:
        print(str(exc))
        return 1
    except Exception as exc:  # bewusst breit für Prototyp und besseres Debugging
        print(f"Fehler: {exc}")
        return 1
    finally:
        # Sauberes Schließen aller OpenCV-Fenster am Ende.
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
