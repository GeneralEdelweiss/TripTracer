# TripTracer – GPS Rally & Trip Computer

Privates Entwicklungsprojekt eines selbstgebauten GPS-Tripmasters, universell fuer Rallye, Touren und Fahrzeuge. Zentraler, portabler Entwicklungsstand inklusive KiCad-10-Schaltplan, Bibliotheken, STEP-Modellen, erstem Gehaeuse und experimenteller Firmware.

## Projektstand (Oktober 2026)

| Teil | Stand | Bemerkung |
| --- | --- | --- |
| Schaltplan | V0.3 | 69 Instanzen, 25 Footprinttypen; strukturell geprueft, ERC nicht ausgefuehrt |
| Leiterplatte | Offen | **Keine geroutete, freigegebene PCB-Datei** |
| Symbole/Footprints/3D | V0.3 | Projektlokal und zentrale Kopie, Geometrie und Modelle noch zu verifizieren |
| Gehaeuse | V0.1 | Front/Rueckdeckel, Kappe, Referenzgeometrie als STEP/STL; Passprobe offen |
| Firmware | V0.1 | Experimenteller ESP32-S3-Prototyp, noch nicht mit V0.3 abgeglichen |

## Verzeichnisse

- `hardware/kicad/`: originaler V0.3-Schaltplan, projektlokale Symbole, Footprints, STEP-Modelle, Bibliothekstabellen
- `hardware/pcb/`: spaeteres Layout, momentan nur Hinweis
- `symbols/`, `footprints/`, `3dmodels/`: aus V0.3 uebernommene zentrale Bibliothekskopien
- `catalog/`: V0.3-BOM, Pin-/Netztabellen, Strukturpruefberichte, Modellinventar
- `mechanics/prototype_v0.1/`: mechanischer Prototyp (STEP/STL)
- `firmware/prototype_v0.1/`: PlatformIO-Prototyp
- `docs/`: Architektur, Datenblatt-URLs, Preview und offene Punkte
- `tools/legacy_generation/`: reproduzierbare Skripte der V0.3, **nicht ungefragt erneut ausfuehren**, da UUIDs neu vergeben werden koennen
- `integration/`: Bibliothekseinbindung auf weiteren Rechnern
- `releases/`: erst nach Freigabe fuellen

## Oeffnen

1. Repository klonen, KiCad 10 installieren.
2. `hardware/kicad/Tripmaster_V0_3.kicad_pro` oeffnen.
3. Bibliothekstabellen und 3D-Modelle aus demselben Ordner unveraendert belassen.
4. ERC in KiCad ausfuehren und Ergebnisse einzeln pruefen; keine PCB-Fertigungsdateien aus diesem Stand ableiten.
5. Hinweise in `docs/OPEN_ITEMS.md` beachten.

## Sicherheit und Revisionshinweise

- Es gibt **keine nachgewiesene Freigabe fuer Fahrzeugbetrieb** (Load Dump/EMV/ESD/Verpolung).
- In V0.3 ist USB-C ein selbstversorgter Datenanschluss; die Elektronik muss zum Flashen zusaetzlich ueber J1 versorgt werden.
- V0.1-Mechanik und -Firmware haben andere Revisionsnummern als V0.3 und sind nicht automatisch kompatibel.
- Keine fruehen Platzhalterfootprints aus V0.1/V0.2 als freigegebenen Produktionsstand nutzen.
