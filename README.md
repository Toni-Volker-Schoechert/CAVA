# Camera-based Analysis of Valve Aperture (CAVA)

Ein modulares Python-Projekt zur Analyse von Bildern und Videos aus einem Herzklappen-Prüfstand.
Ziel ist es, die innere Öffnung der Herzklappe pro Frame zu erkennen, deren Fläche zu berechnen und daraus den Öffnungsgrad über die Zeit zu bestimmen.

## Getestete Umgebung

- Python 3.12
- Ubuntu 24.04
- VS Code

---

## Funktionen im aktuellen Stand

- Auswahl einer Bild- oder Videodatei per Dateidialog
- Automatische Erkennung, ob Bild oder Video geladen wurde
- Manuelle Auswahl einer ROI (Region of Interest)
- Vorverarbeitung des Bildes
- Edge Detection mit Canny
- Kontursuche im ROI
- Flächenberechnung der aktuell erkannten Kontur
- Debug-Anzeige mit Overlay
- Ausgabe der Fläche im Terminal
- Speichern der Ergebnisse als CSV

---

## Geplante Erweiterungen

- Robustere Bestimmung der **inneren** Kontur der Herzklappenöffnung
- Relative Öffnung in Prozent
- Textanzeige unter dem Bild / direkt im Frame
- Export eines annotierten Videos
- Zusätzliche Tabellenformate
- Kalibrierung von Pixel² zu mm²

---

## Repository-Struktur

```text
heart_valve_opening_analyzer/
├─ main.py                  # Einstiegspunkt des Programms
├─ config.py                # Zentrale Konfiguration
├─ data_loader.py           # Laden von Bild/Video und Dateiauswahl
├─ roi_selector.py          # Auswahl der interessanten Region (ROI)
├─ processor.py             # Vorverarbeitung und Edge Detection
├─ analyzer.py              # Konturenanalyse und Flächenberechnung
├─ visualizer.py            # Debug-Anzeige und Overlays
├─ exporter.py              # Export von Ergebnissen als CSV
├─ utils.py                 # Kleine Hilfsfunktionen
├─ requirements.txt         # Python-Abhängigkeiten
├─ .gitignore               # Git-Ignore-Regeln für Python / VS Code
└─ README.md                # Projektdokumentation
```

---

## Einrichtung

### 1. Repository klonen

```bash
git clone <DEIN-REPO-URL>
cd CAVA
```

### 2. Virtuelle Umgebung erstellen

```bash
python3.12 -m venv .venv
```

### 3. Virtuelle Umgebung aktivieren

Unter Linux / Ubuntu:

```bash
source .venv/bin/activate
```

Unter Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Abhängigkeiten installieren

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Nutzung

Programm starten mit:

```bash
python main.py
```

Dann läuft der Workflow so ab:

1. Datei auswählen
2. ROI im ersten Bild / Frame markieren
3. Programm verarbeitet Bild oder Video
4. Debug-Fenster zeigt ROI, Kanten und erkannte Kontur
5. Fläche wird im Terminal ausgegeben
6. Ergebnisse werden als CSV gespeichert

---

## Hinweise zur ROI-Auswahl

Da die Kamera statisch ist, wird die ROI nur **einmal** am Anfang ausgewählt.
Diese ROI wird danach auf alle Frames angewendet.

Das ist hilfreich, weil:

- unwichtige Bildbereiche ignoriert werden
- Rechenzeit gespart wird
- die Kontursuche stabiler wird

---

## Hinweise zur Flächenbestimmung

Der aktuelle Entwicklungsstand verwendet als ersten Ansatz:

- Graustufenbild
- Gaussian Blur
- Canny Edge Detection
- Kontursuche
- Auswahl der größten gültigen Kontur

Das ist für erste Tests gut, aber in realen Prüfstandsbildern oft noch nicht robust genug.
Je nach Material, Beleuchtung und Kontrast kann es sinnvoll sein, später zusätzlich zu nutzen:

- Thresholding
- adaptive Thresholds
- Morphologie (Open / Close)
- Formfilter
- Lagefilter
- Glättung der Kontur

---

## Ausgabeformate

Aktuell wird eine CSV-Datei erzeugt, z. B.:

```text
frame,time_sec,area_px2
0,0.0,1234.5
1,0.04,1250.0
2,0.08,1282.0
```

---

## Bekannte Grenzen des aktuellen Stands

- Die größte Kontur ist nicht immer automatisch die richtige Innenöffnung.
- Die Fläche wird aktuell in **Pixel²** berechnet, nicht in mm².
- Bei Videos wird derzeit das gesamte Video in eine Liste geladen. Für sehr große Videos sollte später auf Streaming umgebaut werden.
- Debug-Fenster sind für Entwicklung praktisch, aber noch nicht für einen produktiven Batch-Betrieb optimiert.

---

## Maintainer

**Toni Schoechert**

---

## Lizenz

Noch keine Lizenz festgelegt.
