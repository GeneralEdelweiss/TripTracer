# TripTracer V1 – eigenständige KiCad-Projektdateien und Entwicklungsstand

**Stand:** 13.10.2026, Arbeitsrevision A1. **KEINE ERC-/DRC-/Automotive-/Fertigungsfreigabe.** Die alte V0.3 bleibt unverändert als Vergleichsstand erhalten.

## Laufende Feldstudie: relaislose Versorgung (noch **nicht** im Schaltplan implementiert)

Die neu bevorzugte Entwicklungsrichtung ist **Variante 3: elektronische, MCU-unabhängig sicher begrenzte Einschalt-/HOLD-Schaltung mit zwei separat abschaltbaren Leistungspfaden, ohne daueraktiven 5-V-Relaishilfsbuck**. Siehe [SOLID_STATE_POWER_ARCHITECTURE.md](../../docs/SOLID_STATE_POWER_ARCHITECTURE.md). Die bestehende Relais-Baugruppe `01_Eingangsschutz`, die Seite `01A_AUX_5V` und die alten ACC-/HOLD-Seiten `01B`/`01C` wurden bewusst **noch nicht überschrieben**. Sie bilden derzeit nur den bisherigen Schaltungsstand und sind für Variante 3 **nicht verwendungsfertig**. `01D_INPUT_PROTECTION` enthält ausschließlich einen **unverdrahteten** eFuse-Kandidaten, nicht den vollständig geschützten Hauptpfad.

Der Stand in `main` ist als [GitHub-Commit 07b6ae6](https://github.com/GeneralEdelweiss/TripTracer/commit/07b6ae6c82a02aa866dadd50f507025a7d0c8587) und [Snapshot-Branch](https://github.com/GeneralEdelweiss/TripTracer/tree/snapshot/2026-10-13-before-solid-state) fixiert; auch der 01D-Designreview liegt auf [einem gesonderten Snapshot](https://github.com/GeneralEdelweiss/TripTracer/tree/snapshot/2026-10-13-with-01d-review). **Noch keine vollständige Relaisschaltungs- oder relaislose Verdrahtung; weiterhin keine ERC-/DRC-/Automotive-/Fertigungsfreigabe.**

**Bibliotheksstand 13.10.2026:** In `TripTracer_V1.kicad_sym` ist **LM74930_Q1** als **Bauteilkandidat** hinzugefügt. Die 24 Signalpins stammen aus [TI-Datenblatt Abschnitt 5](https://www.ti.com/document-viewer/LM74930-Q1/datasheet/GUID-B6643230-1306-4331-B855-7D8E87758ADB); dabei sind 8/17/21 NC. **Der physische Exposed Pad `RTN` muss laut Hersteller floating bleiben** und ist erst nach Prüfung der padmäßigen Footprint-Abbildung abzubilden. **Kein Footprint und keine Schaltplanplatzierung zugewiesen.** Das bloße Symbol zählt ausdrücklich **nicht als fertig entworfene Eingangsversorgung, keine ERC/DRC-Freigabe**. [Preis-/Sicherheitsentscheidung](../../docs/POWER_INPUT_80_20_DECISION.md).

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
| `01_Eingangsschutz.kicad_sch` | **TEILENTWURF:** K101 Omron G6S-2F DC5 mit echtem Pad-1/12-Spulenanschluss, NO 4/5, Q111 DMN2056U-Spulentreiber, D111 SS36-Freilauf, R111 100k-Pulldown. **5V_AUX_COIL / RELAY_ENABLE_5V / Schutzketten / ACC-HOLD fehlen noch**. | **Nicht funktionsfähig als Gesamtbaugruppe; ERC/DRC nicht ausgeführt.** |
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

## Baugruppe 01: Relais-Vorprüfung

**Entwurfsstand a4:** Neue hierarchische [01D_INPUT_PROTECTION.kicad_sch](01D_INPUT_PROTECTION.kicad_sch) mit **TPS26631-PWP eFuse-Symbol** (20 Hersteller-Signalpins, U401) als **nicht angeschlossener Kandidat**. [Eingangsschutz-Designreview](../../docs/INPUT_PROTECTION_DESIGN_REVIEW.md): 9–36 V, ACC/BAT+ getrennt geschützt, Always-on-AUX-Ruhestrom und separate vorgeschaltete Verpol-/TVS-Schutzpfade, eFuse hinter Relais, Kontakteinschaltstrom und Kaltstart. **Vor weiteren Leiterbahn-/Footprintarbeiten externes Blocking-FET + Pulldown, Kfz-Transienten, OVP/UVLO/ILIM/dVdT, Hauptstrompfad und PCB-Freigabe prüfen. Kein ERC/DRC.**



**KiCad-Teilstand a3 – 01C max. Nachlauf-Timer:** Die neue hierarchische Unterseite [01C_HOLD_TIMER.kicad_sch](01C_HOLD_TIMER.kicad_sch) ergänzt einen **automotive-TLC555-Q1-Monoflop mit UND-Gatter SN74LVC1G08-Q1**. Der Monoflop wird vom fallenden ACC_DRIVER-Pegel angestoßen; seine Ausgangsfreigabe wird mit `MCU_HOLD_REQ` verundet. `R501=2,2 MΩ, C501=10 µF`: **24,2 s nur nominal**, Keramikkondensator-Toleranz/-DC-Bias und Trigger-/Reset-Übergänge noch ungetestet. `R305` in 01B fixiert den Low-Pegel beim ACC-Abfall. **Die ECU-/GPIO-Zuordnung, realer AC-Eingangsschutz, KiCad-ERC/DRC, Anlauf-/Abschaltmessung und Footprint-Freigabe fehlen.** Nur Architektur/Teilschaltung, nicht funktions- oder serienfreigegeben.

 (13.10.2026)

**KiCad-Fortschritt a2 (ACC-Start und vorbereiteter HOLD-Eingang):** Auf der neuen, hierarchischen [01B_ACC_WAKE.kicad_sch](01B_ACC_WAKE.kicad_sch) sind Q301 MMBT5551 (C408396), Q302 MMBT5401 (C408397), R301–304, C301 und D301/D302 BAT54WS (C5251553) als ein **ACCsparender Einschaltpfad** verdrahtet. Q301 steuert bei vorhandenem geschütztem Zündplus Q302 an; über D301 wird der bestehende Q111-Gate-Eingang `RELAY_ENABLE_5V` eingeschaltet. D302 ist ein **noch nicht gültig gespeister** Ausgang des späteren `HOLD_TIMER_GRANTED_3V3`-Watchdog-/Interlock-Blocks; **direkte MCU-GPIO-Selbsthaltung ist ausdrücklich nicht freigegeben**. Symbole plus vorläufige SOT23/SOD323-Footprints liegen projektlokal, Geometrie/Pin 1 noch endgültig gegen Fertiger prüfen. **Nicht elektrisch vollständig, ERC/DRC nicht ausgeführt.**

**KiCad-Fortschritt a1.1 (5-V-AUX-Unterseite):** Das Relais-Eingangsblatt verlinkt nun die hierarchische [01A_AUX_5V.kicad_sch](01A_AUX_5V.kicad_sch). Dort ist der **LM5164-Q1-Hilfsbuck mit 13 Symbolinstanzen** als gekennzeichneter vorläufiger Schaltungsentwurf verdrahtet (5 V aus geschütztem BAT+, RON/FB, Type-3-Ripple, Bootstrap, Ein-/Ausgangsfilter). **U201 und L201 ohne freigegebene Footprints, ACC-Start/HOLD-Timer und vorgelagerter Kfz-Schutz fehlen; KiCad ERC/DRC nicht durchgeführt.**

**KiCad-Fortschritt a1:** [01_Eingangsschutz.kicad_sch](01_Eingangsschutz.kicad_sch) enthält jetzt die erste real gezeichnete **Teilbeschaltung aus K101, Q111, D111, R111** und globale Schnittstellennetze. Die Relaisschaltung allein ist **nicht vollständig selbstversorgend**: die Hilfs-5V, gültige ACC/HOLD-Logik, eFuse/Schutz und Power-On-Interlock fehlen noch. Neues [portables Relaissymbol](TripTracer_V1.kicad_sym) und [Projektfootprint](Tripmaster.pretty/RLY101_Omron_G6S_2F.kicad_mod) laut Omron-Maßzeichnung, **ohne 3D-Modell** und ohne native KiCad-Freigabe. **Noch nicht** als fertiges/DRC-geprüftes PCB-Bauteil platziert.

[Technischer Designreview mit Bauteilkandidaten, Spulenrechnung, Kosten- und Kompatibilitäts-Gates](../../docs/POWER_RELAY_DESIGN_REVIEW.md). **Omron G6S-2F DC5 (C16707, Extended)** und **TI LM5164QDDARQ1 (C2072225, Kategorie offen)** sind **Kandidaten**, keine freigegebenen/platzierten KiCad-Bauteile. Aktuelle KiCad-Seite 01 enthält **noch keine realen elektrischen Verbindungen**. Keine ERC-/DRC-/Fertigungsfreigabe erfolgt.

## Wichtige aktuelle Risiken

1. **V1 kann noch nicht eingeschaltet werden:** Die geschützte ACC/BAT+-Relaisversorgung, Relais-HOLD-/Failsafe-Ansteuerung, 5-V-Quellenwahl und 3,3-V-LDO sind noch nicht verdrahtet.
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

Als nächsten Schaltplanarbeitsschritt **`01_Eingangsschutz`** auf Basis des [Relais-/Spulenregler-Designreviews](../../docs/POWER_RELAY_DESIGN_REVIEW.md) entwickeln: ACC+BAT+ (M8 1/3/4), monostabiles **5-V-Mikrorelais aus immer aktivem, stromsparendem AUX-Buck**, MCU-HOLD mit Hardware-Failsafe, TVS/eFuse/Verpolschutz und gesicherter Einschaltstrombegrenzung. Der frühere 3-s-HV-Elko-Puffer für kompletten Kabelausfall ist **ersatzlos entfallen**. Danach **`03_3V3_USB`** mit LDO, USB/Bordnetz/Laboreinspeisung, galvanischer und logischer Rückspeisesicherheit. Erst dann PCB-Netze übertragen und die Stromversorgung validieren.

Verbindlich: [Hardwareanforderungen](../../docs/HARDWARE_REQUIREMENTS.md) / [Schematic Review](../../docs/PROTOTYPE_V1_SCHEMATIC_REVIEW.md).
