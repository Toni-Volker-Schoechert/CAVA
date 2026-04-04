"""
Zuletzt editiert: 2026-04-04
Modulname: config
Maintainer: Toni Schoechert

Modulbeschreibung:
    Zentrale Projektkonfiguration.

    Ziel dieses aufgeräumten Stands:
    - gemeinsame Infrastruktur beibehalten
      (data_loader, roi, visualizer, debug, export)
    - nur noch den einfachen Canny-Ansatz verwenden
    - den Code bewusst übersichtlich halten
    - nur die wichtigsten Parameter zum Testen neuer Aufnahmen anbieten

Hinweis:
    Der Aufbau bleibt absichtlich so, dass später weitere Methoden,
    z. B. ein U-Net, ergänzt werden können. Aktuell ist jedoch nur noch
    der Canny-Ansatz aktiv.
"""

from pathlib import Path


CONFIG = {
    "method": {
        # Aktive Methode.
        # Der Name bleibt bewusst erhalten, damit der Aufbau später leicht
        # erweitert werden kann. Im aktuellen Stand gibt es aber nur diese
        # eine Methode.
        "name": "canny_simple",
    },
    "window_names": {
        "roi_selection": "Polygon-ROI auswählen",
        "final_overlay": "Ergebnis",
        "debug_overlay": "Debug - Overlay",
        "method_debug": {
            "threshold_roi": "Debug - Threshold ROI",
            "canny_input": "Debug - Canny Input",
            "scharr_magnitude": "Debug - Scharr Magnitude",
            "raw_edges": "Debug - Raw Edges",
            "refined_edges": "Debug - Refined Edges",
            "barrier": "Debug - Barrier",
            "free_regions": "Debug - Free Regions",
            "region_analysis": "Debug - Region Analysis",
        },
    },
    "preprocessing": {
        # Wahl des Helligkeitskanals.
        # "gray" | "lab_l"
        "luminance_mode": "lab_l",

        # Optionale lokale Hintergrundnormalisierung.
        # Diese ist oft nützlicher als aggressive Kontrastverstärkung,
        # wenn langsame Beleuchtungsverläufe die Kanten abschwächen.
        "use_local_background_normalization": True,
        "background_normalization_sigma": 10.0,

        # Glättung vor Canny.
        # "none" | "gaussian" | "bilateral"
        "filter_mode": "bilateral",
        "gaussian_kernel_size": (5, 5),
        "gaussian_sigma": 0,
        "bilateral_d": 7,
        "bilateral_sigma_color": 40,
        "bilateral_sigma_space": 40,

        # Optionale milde lokale Kontrastverstärkung.
        # Nur vorsichtig einsetzen und immer mit der Variante ohne CLAHE
        # vergleichen.
        "use_clahe": True,
        "clahe_clip_limit": 3.0,
        "clahe_tile_grid_size": (16, 16),
    },
    "methods": {
        "canny_simple": {
            # Canny-Schwellenbestimmung.
            # "gradient_quantiles": Schwellen aus Scharr-Gradienten
            # "manual": feste Werte aus canny_threshold_1 / _2
            "canny_mode": "gradient_quantiles",
            "threshold_roi_erosion_kernel_size": 15,
            "canny_threshold_1": 30,
            "canny_threshold_2": 90,
            "canny_gradient_q_low": 0.1,
            "canny_gradient_q_high": 0.7,
            "canny_use_l2gradient": True,
            "canny_aperture_size": 3,

            # Moderate Kanten-Nachbearbeitung.
            # Ziel: kleine Unterbrechungen glätten, ohne die Kanten unnötig
            # stark zu verkleben.
            "post_remove_small_components": True,
            "post_min_component_size": 20,
            "post_close_kernel_size": 5,
            "post_close_iterations": 1,
            "post_dilate_iterations": 0,

            # Zusätzliche Verdickung nur für die Regionensuche.
            # Das ist oft sinnvoller als Canny selbst aggressiver zu machen,
            # wenn die Kante fast geschlossen ist.
            "barrier_dilate_iterations": 3,

            # Mindestfläche der finalen Öffnung.
            "min_contour_area_mode": "relative",
            "min_contour_area_px2": 50.0,
            "min_contour_area_factor": 0.001,
        },
    },
    "visualization": {
        "wait_key_ms_image": 0,
        "wait_key_ms_video": 30,
    },
    "debug": {
        "enabled": True,
        "print_messages": True,

        # Die globalen Zwischenbilder sind im aktuellen Stand standardmäßig
        # ausgeblendet, weil sie oft redundant sind. Die relevanten Bilder
        # liefert direkt die Methode.
        "show_source_image": True,
        "show_normalized_image": True,
        "show_preprocess": False,
        "show_method_debug_images": True,
        "show_overlay": True,
        "show_final_result_when_not_debug": True,
    },
    "export": {
        "output_dir": Path("outputs"),
        "csv_filename": "results.csv",
    },
}
