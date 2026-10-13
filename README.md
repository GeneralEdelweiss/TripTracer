# TripTracer – GPS-Rallye- und Tripcomputer

Eigenentwickelter GPS-Tripmaster für Rallye, Touren und Fahrzeuge. Zentrales privates GitHub-Repository für KiCad 10, Firmware, 3D-Modelle und Gehäuse.

## Aktueller Entwicklungsstand

- **Elektronik V0.3:** Ein editierbarer KiCad-10-Schaltplan mit 69 Bauteilinstanzen, 25 Footprint-Typen, Symbolbibliothek und STEP-Modellen liegt aus früherer Entwicklung vor. Strukturelle Prüfung bestanden, aber **kein KiCad-ERC/DRC durchgeführt**.
- **Leiterplatte:** Es existiert **noch kein fertig geroutetes oder zur Fertigung freigegebenes PCB**.
- **Mechanik V0.1:** CAD-Prototyp mit Gehäusefront, Rückdeckel, Tasterkappe und PCB-Referenz.
- **Firmware V0.1:** Experimentelles ESP32-S3-/PlatformIO-Projekt, **nicht mit V0.3 abgeglichen**.

Die Bauteile sind u. a. **ESP32-S3-MINI-1-N8**, **u-blox MAX-M10N-00B**, **EA DOGL128W-6** mit **EA LED68X51-A**, **LMR36510ADDAR** sowie **I²C-FRAM MB85RC256VPNF**.

### Dateiimport

Die Quellbestände werden als geprüftes Archiv **`TripTracer-Project-Bundle.zip`** importiert. Vor dem ersten Import enthält dieses Repository bewusst nur die Projektstruktur und Dokumentation. Siehe [imports/README.md](imports/README.md).

Nach dem Import:
- `hardware/kicad/`: V0.3-Schaltplan und projektlokale Bibliotheken.
- `symbols/`, `footprints/`, `3dmodels/`: wiederverwendbare Bibliothek.
- `catalog/`: Bauteile, Netzlisten, Prüfberichte, Inventar.
- `mechanics/prototype_v0.1/`: STEP/STL-Gehäuseprototyp.
- `firmware/prototype_v0.1/`: experimentelle ESP32-Firmware.
- `docs/`: Entwurfsstand, offene Punkte und Quellen.
- `integration/`: Pfadkonfiguration für weitere Rechner.
- `releases/`: erst für später freigegebene Stände.

**Wichtig:** Keine Fertigungs- oder Fahrzeugfreigabe. Die USB-C-Buchse ist im V0.3-Schaltplan nur ein datenbasierter Anschluss; zum Firmware-Flashen muss das Gerät zusätzlich über J1 mit Strom versorgt werden.

Das ältere lokale KiCad-Dateinamensschema `Tripmaster_V0_3` wird zur Erhaltung von Bibliotheksreferenzen beibehalten, obwohl der Projektname nun **TripTracer** lautet.
