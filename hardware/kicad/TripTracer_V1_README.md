# TripTracer V1 – eigenständige KiCad-Projektdateien und Entwicklungsstand

**Stand:** 13.10.2026, Arbeitsrevision A1. **KEINE ERC-/DRC-/Automotive-/Fertigungsfreigabe.** Die alte V0.3 bleibt unverändert als Vergleichsstand erhalten.

## Projekt in KiCad 10 öffnen

Im Repository den kompletten Ordner `hardware/kicad/` herunterladen bzw. klonen. **`TripTracer_V1.kicad_pro`** öffnen; die gleichnamige **`TripTracer_V1.kicad_sch`** (Hauptschaltplan) und **`TripTracer_V1.kicad_pcb`** (PCB-Dokument) gehören dazu.

Projektlokale Bibliotheken über `sym-lib-table`/`fp-lib-table`: `Tripmaster_Sym.kicad_sym`, `TripTracer_V1.kicad_sym`, `Tripmaster.pretty/`, `Tripmaster_3dmodels.3dshapes/`. **Keiner der Symbol-/Footprint-/3D-Pfade benötigt ein festes Windows-Laufwerk.** Die V1 greift teilweise noch auf die alte Projektbibliothek zu; bei Umzug beide Bibliotheken mitkopieren.

## Alle Schaltplanseiten in einem Fenster durchblättern

**Nicht die acht einzelnen Baugruppendateien öffnen.** Einmal in KiCad 10 `TripTracer_V1.kicad_pro` öffnen und im Projektmanager den **Schaltplaneditor** starten (alternativ `TripTracer_V1.kicad_sch` öffnen). Dieses Root-Dokument referenziert alle acht Unterseiten über hierarchische Sheet-Symbole. Damit sind **9 Seiten insgesamt** in **einem** Schaltplanprojekt erreichbar.

- **Hierarchie-Navigator:** Im Schaltplaneditor über das Hierarchie-Navigator-Symbol links einschalten. Die Liste zeigt das Hauptblatt und alle acht Baugruppen. Ein Klick auf einen Seitennamen wechselt direkt dorthin.
- **Vorherige/nächste Seite:** Die Pfeile der oberen Symbolleiste verwenden. Alternativ auf dem Hauptblatt einen Block doppelt anklicken, um in ihn zu wechseln; mit dem Aufwärtspfeil zum Hauptblatt zurück.
- **Dateien müssen zusammenbleiben:** `TripTracer_V1.kicad_sch` und `01_Eingangsschutz.kicad_sch` bis `08_Radsensoren.kicad_sch` im `hardware/kicad/`-Ordner belassen. Bei GitHub-Desktop-Pull wird das gesamte Projekt synchronisiert.
- **Abnahme jeder Änderung:** Neue oder umbenannte Seiten müssen im Navigator sichtbar sein, ohne Datei-suchen-Dialog oder fehlende Unterseiten. Root-Hierarchie, elektrische Blatt-Verknüpfungen und Seitennummern prüfen; ein funktionierender Navigationsbaum belegt noch **keine** korrekte elektrische Verbindung.

Die Bedienung entspricht der [offiziellen KiCad-10-Dokumentation zur Navigation zwischen Schaltplanseiten](https://docs.kicad.org/10.0/en/eeschema/eeschema.html#navigating-between-sheets). Dieser Punkt ist in `AGENTS.md` dauerhaft als Pflicht festgelegt.

## Baugruppenstatus

| Blatt | Inhalt | Stand |
|---|---|---|
| `01_Eingangsschutz.kicad_sch` | 9–36-V-M8, eFuse, externer Verpol-MOSFET, TVS, Pufferelkos, Ladestrombegrenzung, ACC-Sense | **Noch nicht verschaltet** |
| `02_5V_Buck.kicad_sch` | LMR36520 als Reglerkandidat, Spule, 5-V-Feedback, Bootstrap/VCC-Kondensatoren und Ausgangskondensatoren | **9 reale Symbolinstanzen mit vorläufiger Verdrahtung; Bauteilauslegung/Pin-Footprint-Freigabe offen** |
| `03_3V3_USB.kicad_sch` | 3,3-V-LDO, Bordnetz/USB-Priorisierung, 5-V-Laborteststecker | **Noch nicht verschaltet** |
| `04_ESP32_USB.kicad_sch` | ESP32-S3-MINI-1-N8, USB-C-Buchse, 2×5,1-kΩ-CC-Rd, USBLC6-2SC6, D+/D−-Serienwiderstände, BOOT/EN-Pull-ups, lokale Kondensatoren | **12 echte Symbolinstanzen verdrahtet; übrige GPIOs und Quellenentkopplung fehlen** |
| `05_GNSS.kicad_sch` | MAX-M10N, UART/TIMEPULSE, U.FL und geschützter Antennen-Bias | **Noch nicht verschaltet** |
| `06_Display_Tasten.kicad_sch` | Riverdi 50-polig / SPI / 15-V-Backlight, sechs FILN-Tasten | **Noch nicht verschaltet** |
| `07_Speicher_RTC.kicad_sch` | interne microSD, FRAM, RTC/CR1220, I²C-Sensoren | **Noch nicht verschaltet** |
| `08_Radsensoren.kicad_sch` | zwei getrennte Radimpulse, geschaltete 5-V-Sensorversorgung, JST-GH-Erweiterung | **Noch nicht verschaltet** |

**Vorläufige, aus beiden verdrahteten V1-Baugruppen abgeleitete BOM:** [TripTracer_V1_BOM_DRAFT.csv](TripTracer_V1_BOM_DRAFT.csv). Alle 21 Positionen sind derzeit lediglich Entwurfs-/Prüfpositionen, keine freigegebene Bestellliste.

## PCB-Dokument bereits angelegt

`TripTracer_V1.kicad_pcb` enthält **21 reale, aus dem Schaltplan referenzierte Footprint-Instanzen**: die 9 Buck-Bauteile und 12 MCU-/USB-Bauteile. Für die bisherigen Footprints wurden bestehende lokale Hersteller-/Geometrieentwürfe wiederverwendet; einzelne Landpatterns sind noch ungeprüft.

**Achtung:** Die PCB ist eine **Vorplatzierung**. Sie enthält noch **keine verbindliche Edge.Cuts-Outline, keine zugeordneten Netze, keine gerouteten Tracks/Vias und keine vollständigen Komponenten**. Das Rechteck auf **Dwgs.User ist KEIN Platinenumriss** und darf nicht als Gerber/Fertigungsgrundlage benutzt werden. Über KiCad `Werkzeuge → Leiterplatte aus Schaltplan aktualisieren` müssen die später gültigen Netze auf die PCB übertragen und alle verbliebenen Funktionsgruppen ergänzt werden.

Projekt-Einstellungen in `TripTracer_V1.kicad_pro`: 1,6 mm PCB-Dicke, bevorzugt zwei Kupferlagen; DRC-Mindestabstände sind **vorläufig** und bei JLCPCB mit dem tatsächlichen Stack-up abzugleichen. 35 µm/1 oz bleibt verbindliches Konstruktionsziel (HW-71).

## Wichtige aktuelle Risiken

1. **V1 kann noch nicht eingeschaltet werden:** Die geschützte 9–36-V-Einspeisung, echte Pufferladung, 5-V-Quellenwahl und 3,3-V-LDO sind noch nicht verdrahtet.
2. **Buck U101:** LMR36520 ist ein **Kandidat**, noch keine Volllast-/Thermik-/90-%-Wirkungsgrad-Freigabe. Pin 1 PGND, 2 VIN, 3 EN, 4 PG, 5 FB, 6 VCC, 7 BOOT, 8 SW, thermisches Pad 9. Pin-kompatibler V0.3-LMR36510-Footprint ist **noch gegen aktuelles TI-Package-Drawing zu prüfen**. https://www.ti.com/lit/ds/symlink/lmr36520.pdf
3. **L101:** Symbol zeigt **15 µH als vorläufigen Entwurfswert**, während der derzeit verwendete Fußabdruck den alten **Bourns-22-µH-Typ** bezeichnet. **Nicht als freigegebenen 15-µH-Bauteilsatz bestellen.** Erst L-Wert/Isat/DCR und den Hersteller-Footprint festlegen.
4. **USB-C:** Die D+/D−-, CC- und ESD-Grundbeschaltung ist entworfen. Die **USB-VBUS-Versorgung für Firmware/MSC ohne M8 sowie Quellen-Rückspeisesperre** fehlen auf `03_3V3_USB`. Kein Betrieb allein über USB möglich, solange diese Schaltung nicht fertig ist.
5. **GPIOs:** ESP32-S3-MINI-1-N8 vorhanden, aber weitere Pins für Display, Tasten, GNSS, microSD, Radgeber und Erweiterung müssen konfliktfrei zugeordnet werden. GPIO0/3/45/46 und native GPIO19/20 besonders prüfen.
6. **PCB-Fertigung:** Bei fünf nackten PCBs möglichst zwei SMD-bestückt und drei unbestückt; erst nach ERC, DRC, Bauteil-/Footprint-Abgleich und Einkaufstest zu bestellen.

## Was geprüft wurde – und was nicht

- **Geprüft durch Struktur-Abgleich:** alle 8 Blattdateien existieren, `TripTracer_V1.kicad_pro` und `.kicad_pcb` sind vorhanden, **21 Symbol-Referenzen entsprechen den 21 platzierten PCB-Footprints**, ihre hierarchischen Schaltplan-UUID-Pfade wurden zugeordnet.
- **Nicht durchgeführt:** Öffnung der V1 in einer installierten KiCad-10-Anwendung, native Schema-Parser-/ERC-Prüfung, DRC/DFM, Datenblatt-Freigabe sämtlicher Footprints, Netzsynchronisierung, realer Boardtest.
- Das Vorhandensein einer PCB-Datei oder die Strukturprüfung bedeutet **nicht**, dass die PCB funktionsfähig oder fertig geroutet ist.

## Nächste Baugruppe

Als nächsten Schaltplanarbeitsschritt **`01_Eingangsschutz`** mit TVS, eFuse mit passendem externem Verpol-MOSFET, strombegrenztem Hochvolt-Elko-Puffer und ACC-Sense datenblattbasiert aufbauen. Danach **`03_3V3_USB`** mit LDO, USB/Bordnetz/Laboreinspeisung, galvanischer und logischer Rückspeisesicherheit. Erst dann PCB-Netze übertragen und die Stromversorgung validieren.

Verbindlich: [Hardwareanforderungen](../../docs/HARDWARE_REQUIREMENTS.md) / [Schematic Review](../../docs/PROTOTYPE_V1_SCHEMATIC_REVIEW.md).
