"""
Zuletzt editiert: 2026-04-02
Modulname: data_loader
Maintainer: Toni Schoechert

Modulbeschreibung:
    Dieses Modul ist für die Auswahl und das Laden von Medien zuständig.
    Es erkennt anhand der Dateiendung, ob es sich um ein Bild oder Video handelt.

Input:
    - Dateipfad, entweder manuell ausgewählt oder direkt übergeben.

Output:
    - media_type: 'image' oder 'video'
    - frames: Liste von OpenCV-Frames (BGR)
    - fps: Bildrate, bei Bildern auf 1.0 gesetzt

Relevante Hinweise:
    - Bilder werden als Liste mit genau einem Frame zurückgegeben.
    - Videos werden aktuell vollständig in den Arbeitsspeicher geladen.
      Das ist für den ersten Prototyp praktisch, aber bei großen Dateien
      später eventuell auf Streaming umzustellen.
"""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import Tk, filedialog

import cv2


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".mpg", ".mpeg"}


def select_file() -> str:
    """
    Öffnet einen Dateidialog zur Auswahl einer Bild- oder Videodatei.

    Returns:
        str: Vollständiger Pfad zur ausgewählten Datei.

    Raises:
        FileNotFoundError: Falls keine Datei ausgewählt wurde.
    """
    root = Tk()
    root.withdraw()
    root.update()

    file_path = filedialog.askopenfilename(
        title="Bild oder Video auswählen",
        filetypes=[
            (
                "Media Files",
                "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.mp4 *.avi *.mov *.mkv *.mpg *.mpeg",
            ),
            ("All Files", "*.*"),
        ],
    )

    root.destroy()

    if not file_path:
        raise FileNotFoundError("Es wurde keine Datei ausgewählt.")

    return file_path


def detect_media_type(file_path: str | os.PathLike[str]) -> str:
    """
    Erkennt den Medientyp über die Dateiendung.

    Args:
        file_path: Pfad zur Datei.

    Returns:
        str: 'image' oder 'video'

    Raises:
        ValueError: Falls der Dateityp nicht unterstützt wird.
    """
    suffix = Path(file_path).suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in VIDEO_EXTENSIONS:
        return "video"

    raise ValueError(f"Nicht unterstützter Dateityp: {suffix}")


def load_media(file_path: str | os.PathLike[str]) -> tuple[str, list, float]:
    """
    Lädt Bild oder Video und gibt eine einheitliche Struktur zurück.

    Args:
        file_path: Pfad zur Bild- oder Videodatei.

    Returns:
        tuple[str, list, float]:
            - media_type: 'image' oder 'video'
            - frames: Liste von Frames im BGR-Format
            - fps: Bildrate, bei Bildern 1.0
    """
    media_type = detect_media_type(file_path)

    if media_type == "image":
        image = cv2.imread(str(file_path))
        if image is None:
            raise ValueError(f"Bild konnte nicht geladen werden: {file_path}")
        return media_type, [image], 1.0

    cap = cv2.VideoCapture(str(file_path))
    if not cap.isOpened():
        raise ValueError(f"Video konnte nicht geöffnet werden: {file_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 1.0

    frames = []
    while True:
        success, frame = cap.read()
        if not success:
            break
        frames.append(frame)

    cap.release()

    if not frames:
        raise ValueError(f"Video enthält keine lesbaren Frames: {file_path}")

    return media_type, frames, fps
