"""
Zuletzt editiert: 2026-04-02
Modulname: config
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul enthält die zentrale Konfiguration des Projekts.
    Hier werden Standardwerte für Vorverarbeitung, Edge Detection,
    Analyse, Anzeige und Export gesammelt, damit sie nicht über den
    gesamten Code verstreut sind.

Input:
    - Keine direkten Laufzeitinputs.

Output:
    - Ein Dictionary CONFIG mit zentralen Einstellungen.

Relevante Hinweise:
    - Diese Werte sind Startwerte und müssen je nach Bildmaterial angepasst werden.
    - Gerade die Canny-Schwellen und die minimale Konturfläche sind stark
      vom Kontrast, der Beleuchtung und dem Prüfstand abhängig.
"""

from pathlib import Path


CONFIG = {
    "window_names": {
        "roi_selection": "ROI auswählen",
        "debug_overlay": "Debug Overlay",
        "debug_edges": "Debug Edges",
    },
    "preprocessing": {
        "gaussian_kernel_size": (5, 5),
        "gaussian_sigma": 0,
    },
    "edge_detection": {
        "canny_threshold_1": 50,
        "canny_threshold_2": 150,
    },
    "analysis": {
        "min_contour_area_px2": 50.0,
        "use_external_contours_only": True,
    },
    "visualization": {
        "wait_key_ms_image": 0,
        "wait_key_ms_video": 30,
        "font_scale": 0.7,
        "line_thickness": 2,
        "show_edges": True,
        "show_overlay": True,
    },
    "export": {
        "output_dir": Path("outputs"),
        "csv_filename": "results.csv",
    },
}
