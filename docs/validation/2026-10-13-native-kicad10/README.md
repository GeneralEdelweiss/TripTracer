# TripTracer – tatsächliche KiCad-10-Prüfung

Stand: 13.10.2026 (Europe/Berlin). **NICHT FREIGEGEBEN.**

## Zugriff und geprüfter Stand

- Windows-PC: KiCad 10.0.6 unter `D:\KiCad\bin`; Version nativ ausgeführt.
- Separate vollständige Git-Kopie von `GeneralEdelweiss/TripTracer`, Branch `design/solid-state-power-v1`, Ausgangscommit `a0ec16d310463e900b83ff38154f0dbbbcae9b54`.
- Das vorhandene Repository `D:\GitHub\TripTracer` steht auf main und enthält Änderungen an zwei Projektdateien; es wurde nicht verändert.
- Projekteinstieg: `hardware/kicad/TripTracer_V1.kicad_pro`. KiCad-Manager gestartet; Prozess und Fenstertitel `TripTracer_V1 — KiCad 10.0` bestätigt. Root-Schaltplaneditor ebenfalls gestartet. Seine sichtbare Darstellung und die Navigation wurden nicht per UI überprüft. Keine Behauptung eines durchgeklickten Hierarchie-Navigators.
- Root-ERC, Netzlistenexport und SVG-Export erfassen 13 Seiten (Root, acht Hauptseiten, vier Schutz-Unterseiten). Alle referenzierten Seiten wurden geladen.
- Sandboxzugriff auf KiCad-Benutzereinstellungen war zunächst verweigert; die eigentlichen Prüfläufe wurden mit genehmigtem Zugriff durchgeführt. Die Prüflogdateien enthalten die tatsächlichen Konsolenausgaben.

## Native Ergebnisse

| Prüfung | Vorher | Nachher | Ergebnis |
|---|---:|---:|---|
| Root-ERC, alle Schweregrade inkl. Ausschlüsse | 349 | 347 | Exitcode 5, nicht bestanden |
| ERC Fehler | 74 | 73 | 56 unverbundene Pins, 6 ungetriebene Eingänge, 11 ungetriebene Versorgungspins verbleiben |
| ERC Warnungen | 275 | 274 | 270 außerhalb des Verbindungsrasters, 4 Labels an nur einem Pin verbleiben |
| PCB-DRC mit Schaltplan-Parität und Zonenfüllung | 14 | 14 | Exitcode 5, nicht bestanden |
| Schaltplan/PCB-Parität | 209 | 209 | 35 fehlende Footprints auf PCB, 32 Symbol-/Footprint-Abweichungen, 142 Netzkonflikte |
| Unverbundene PCB-Elemente | 0 | 0 | Kein Bestehensnachweis: PCB ohne zugewiesene elektrische Netze und ohne Routing |
| Netzlistenexport | Exit 0 | Exit 0 | Erfolgreich |
| SVG-Gesamtexport | – | Exit 0 | 13 Seiten, keine vollständige visuelle Abnahme |

DRC: vier Kupfer-Abstandsverstöße, vier Loch-Abstandsverstöße, vier Lötstoppbrücken, fehlender Edge.Cuts-Umriss und eine Warnung wegen abweichendem U201-Footprint. USB-J201 hat überlappende, netzlose Padpaare A1/B12, A4/B9, A9/B4, A12/B1; Lochabstand 0,1944 mm gegenüber 0,25 mm Regel. Kein willkürliches Verschieben von USB-Pads oder Absenken der Regeln vorgenommen.

PCB-Bestand strukturell: 21 Footprints, nur Netz 0, keine Leiterbahnsegmente, keine Vias, keine Zonen. Eine DRC-Aussage zu belastbaren Strompfaden, Rückstromführung oder Thermik ist daraus nicht möglich.

## Nachweisbare Korrektur in 02_5V_Buck.kicad_sch

Die sieben lokalen GND-Labels wurden zu globalen GND-Labels geändert. Vorher lag die Buck-Masse auf `/5-V-Synchronbuck (elektrischer Entwurf)/GND`, getrennt von Geräte-GND. Die native Netzliste bestätigt danach genau neun geänderte Pin-Netz-Zuordnungen: U101 Pins 1/9; C101 Pin 1; C103 Pin 2; C104/C105 Pin 1; C106/C107 Pin 2; R102 Pin 1. Alle liegen nun auf globalem GND. Alle anderen Pin-Netz-Zuordnungen sind unverändert; automatischer Vorher/Nachher-Vergleich bestätigt.

Keine Schutzfunktion entfernt, keine Prüfschweregrade geändert, keine Ausschlüsse oder dekorativen PWR_FLAGs ergänzt. BOM und Teilekosten unverändert; keine neuen Bauteile/Beschaffung. `git diff --check` ohne Befund.

## Buck, BUCK_ENABLE und Footprints

- `BUCK_ENABLE` enthält ausschließlich U101 Pin 3 (EN), keinen ACC-/MCU-HOLD-Treiber. ERC bestätigt `pin_not_driven` und `isolated_pin_label`. Nicht mit VIN verbunden: die sicher dimensionierte relaislose Start-/HOLD-Steuerung fehlt.
- `HV_PROTECTED_AFTER_EFUSE` enthält U101 VIN und C101/C106/C107, aber keinen speisenden Schutz-Ausgang. Der Strompfad ist elektrisch nicht integriert.
- C106/C107 sind in der nativen Netzliste zwischen VIN und Buck-GND angebunden; nach Korrektur globales GND.
- BOOT: U101/7–C102/1; SW: U101/8–C102/2–L101/1; VCC: U101/6–C103/1; FB: U101/5–R101/1–R102/2. PGOOD nur U101/4, ohne Verbraucher/Pull-up; nicht als funktionsfähiges Diagnosesignal behauptet.
- LMR36520-Pinbelegung gegen [TI-Datenblatt SNVSBF0C, Rev. C](https://www.ti.com/lit/ds/symlink/lmr36520.pdf), Abschnitt 5, geprüft: 1 PGND, 2 VIN, 3 EN, 4 PG, 5 FB, 6 VCC, 7 BOOT, 8 SW; lokales Symbol stimmt damit überein. Thermisches Pad lokal als Pad 9, an GND.
- Der weiterhin LMR36510 benannte lokale DDA-Footprint besitzt Pads 1–9. TI nennt LMR36510/LMR36520 pin-kompatibel. Numerischer Vergleich mit DDA0008B-Landpattern: Padgröße 1,55 × 0,60 mm, Raster 1,27 mm, Reihenabstand 5,4 mm, EP 2,71 × 3,40 mm passen zur TI-Beispielzeichnung. Dies ersetzt keine vollständige Masken-/Pastenschablonen-/Thermalvia-/Pin-1-/3D-/Bestückungsprüfung.
- Alle in der exportierten Netzliste referenzierten lokalen Footprintdateien existieren. Für sämtliche Komponenten mit Footprint stimmen die Mengen der nummerierten Symbolpins und Footprintpads überein. Das belegt nur Nummern-Vollständigkeit, keine allgemeine Hersteller-Pinoutfreigabe oder korrekte Geometrie aller Bauteile.
- Lokale Bibliothekstabellen verwenden `${KIPRJMOD}`. Der Buck-Modellpfad ist ebenfalls relativ. U201 weicht laut DRC von der Bibliothekskopie ab; vollständiger 3D-/Gehäuseabgleich offen.

## Offene elektrische und mechanische Sperrpunkte

1. Der tatsächliche Schaltplan enthält weiterhin K101/Mikrorelais, Hilfsversorgung und TPS26631. Die beschlossene Variante C mit LM74930-Q1 und relaisloser Selbsthaltung ist noch nicht umgesetzt. Schutzteile nicht blind entfernt; diese Migration benötigt den vollständigen elektrischen Entwurf einschließlich Shunt/MOSFETs, Fehlerabschaltung, ACC/HOLD und thermischem Nachweis.
2. Buck-Enable und gespeister geschützter VIN fehlen. GPIO-/Power-Schnittstellen sind überwiegend unvollständig; alle ERC-Befunde stehen in den Rohberichten. Netzliste zeigt außerdem z.B. beide C201-Pins auf GND; die beabsichtigte Beschaltung muss anhand der jeweiligen Baugruppe geklärt werden. Kein pauschales Markieren offener MCU-Pins als NC.
3. PCB muss aus dem vollständigen Schaltplan synchronisiert, mit geprüften Footprints aufgebaut und geroutet werden. Umriss/Bohrungen/Stecker-/Gehäusepositionen fehlen als freigegebene Mechanik. Null Luftlinien bei diesem Stand sind bedeutungslos.
4. Alle 270 Rasterwarnungen, übrige elektrische Fehler und USB-Geometrie-/U201-Bibliotheksabweichungen bleiben offen. Kein Raster-Rundungsverfahren angewendet, das Verbindungen verändern könnte.
5. Vollständige visuelle Prüfung aller Schaltplanseiten, Hierarchie-Navigation in der UI, Pin-1-/Steckeransicht, Gehäusepassung, 3D-Kollisionen und Bestückbarkeit nicht abgeschlossen.
6. Keine Laborprüfung: 6-V-Motorstart, 9–36-V-Lastbetrieb, Kurzschluss, Dauerfehler/Retry, Temperatur, Rückspeisung, USB-Power-Path und Automotive-Transienten weiterhin ungetestet. Keine elektrische, mechanische, Fertigungs- oder Fahrzeugfreigabe.

## Reproduktion

KiCad 10.0.6, aus Repository-Root; Ausgabeordner vorher anlegen:

```text
kicad-cli sch erc --severity-all --exit-code-violations --format json -o erc.json hardware/kicad/TripTracer_V1.kicad_sch
kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity --refill-zones --exit-code-violations --format json -o drc.json hardware/kicad/TripTracer_V1.kicad_pcb
kicad-cli sch export netlist -o TripTracer.net hardware/kicad/TripTracer_V1.kicad_sch
kicad-cli sch export svg -o schematic-svg/ hardware/kicad/TripTracer_V1.kicad_sch
```

Rohdateien: `erc-before/after.json`, `drc-before/after.json`, gleichnamige Konsolenlogs, `TripTracer.net`, `TripTracer-after.net`, `verification.json`, `structural-audit-before.json`; SVG-Seiten in `schematic-svg/`. Korrektur und Prüfbelege werden ausschließlich auf `design/solid-state-power-v1` lokal committet; kein Push und keine Änderung an main.
