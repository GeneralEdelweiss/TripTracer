# TripTracer / TripPower – Gesamtprüfung aller 12 Branches nach REV6 (16.10.2026)

**Status:** unabhängiger Managementvergleich der aktuell in GitHub vorhandenen Artefakte. **Keine Fertigungs-, Fahrzeug-, Sicherheits-, Lastdump- oder Temperaturfreigabe.** Die Elektrostände von A/C/D wurden bei dieser Prüfung **nicht** geändert; dieser Bericht auf `design/trippower-review` ist ausschließlich eine Entscheidungshilfe.

## 1. Tatsächliche Branch-HEADs und Rolle

| Branch | GitHub HEAD | Änderung seit vorigem dokumentierten REV6-Handoff | Stand |
|---|---|---:|---|
| `design/trippower-a` | `711a05ac9864c3883f91c8cccd16f398e770da02` | +42 Commits | Neuer isolierter REV6-A-Schaltplan mit echter nativer KiCad10-CI |
| `design/trippower-b` | `7bca14333aa6c39ded055786b1bd3a13246fffe0` | +7 | Unabhängige REV6-FMEA/Installation/Prüfmatrix, Modelle |
| `design/trippower-c` | `bbfdc7f09d888790e5ecbbbbc3291fb45a351273` | +8 | TPS26631-/TPS26600-/RECOM-Vergleich, OVLO-Neustartanalyse, teilbepreiste BOM |
| `design/trippower-d-load-dump` | `3522b02494b178c9491036ce33e54ad211222922` | +6 | Neue bedingte LTC4368-2-Schutzarchitektur, Fehler-/Sicherungsprüfung |
| `main` | `9ef856eeca1a04a3d1a8f5ffd5fa4767b5bbd588` | 0 | V1-Hauptprojekt, REV6-Dokumentation vorhanden |
| `design/solid-state-power-v1` | `afae9f85839cc9b4f9fe61c98221c6222f98da16` | 0 | Geerbte experimentelle REV5-Basis, keine REV6-Freigabe |
| `design/trippower-36v` | `b1f068c1c42b0ae2e80b08b2c71a699e38082dc8` | 0 | Historischer 36V-Vergleich |
| `design/trippower-80v` | `ce210b8cdddc00b6437b56bd792873ea08c38be8` | 0 | Historische 80V-Buck-Variante mit alternativen L101/C306 |
| `design/trippower-review` | `22945fd409e4e98333de13c55285d204609d63cd` **vor diesem Bericht** | 0 | Managementvergleich, keine elektrische Produktvariante |
| `design/01d-input-protection-review-20261013` | `4646ae4344f37fd9ec135539c82f6f08273bb51b` | historisch | Ältere Schutzprüfung |
| `snapshot/2026-10-13-before-solid-state` | `07b6ae6c82a02aa866dadd50f507025a7d0c8587` | historisch | Archiv |
| `snapshot/2026-10-13-with-01d-review` | `4646ae4344f37fd9ec135539c82f6f08273bb51b` | historisch | Archiv |

**REV6 maßgeblich:** `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, PWR-44–54 und `POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md`: 10–32V, unter10V Reset erlaubt; >32..≤36V OFF; 36V/400ms und nur **am Modul wirklich begrenzter** 58V/350ms-24V-Lastdump; −20..+70°C, 5V/2A bis+60°C, bis+85°C gefahrlos OFF; RAW0.5A als Ziel; BAT-OFF <1mA/Ziel0.5mA; FRAM-first statt pauschaler SD-CR1220-Holdgarantie; für nicht zentral geklemmte Fahrzeuge extern qualifizierter Vorschaltschutz. **58V bezeichnet nicht automatisch die maximalen internen Pinspitzen.**

## 2. Vier technische Entwicklungswege

### A: Am weitesten als echter KiCad-Prototyp – 25 bestückte Positionen, aber nicht vollständig

Neues eigenständiges `hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_pro` mit 2 Blättern: TPS26631 (4.5–60V operating, 67V abs; industriell/catalog, kein AEC-Q1), externe Reverse-FET-/DRV-Beschaltung und 80V-TI-LMR38020-Q1 als 5V2A Buck mit fail-high PGOOD. Native Stückliste **25 echte bestückte Positionen** (historisch REV5 57 AUTO/58 RUN), jedoch **keine komplette System-/Produkt-BOM**: +85°C Ambient-Safe-Off-Temperaturpfad fehlt, RAW0.5A nicht selektiv begrenzt, ACC/M8/USB/Stecker/F_MAIN teils außerhalb Prototyp und nicht fertig qualifiziert, 5V2A/+60°C nicht gemessen; kein PCB/DRC. OVP-Rise laut Modell 32.337..35.863V, UVLO nominal8.465V. **OVP-Fall-/32V-Wiederanlauf nach einem 58V-Puls muss gemeinsam mit C präzise geprüft werden**, nicht nur Rise. TPS26631 VIN hat nur2V von 58V zur 60V empfohlenen Maximalgrenze; Pad-Ringing/ESD/Faults bleiben P0.

BOM: 14/25 Positionen historisch preisbelegt, **Netto-Teilpreissumme** 15.789/10.632/8.4331 EUR für1/10/100, kein voller Einkaufspreis. Murata `GRM32ER71E226KE15L` **EOL** und fehlende aktuelle Händlerstückzahl, weiteres 6.04k ILIM Teil nicht lagernd, Buck-Spule/Footprints/Thermik zu qualifizieren.

**Echter Actions-Job:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38814076115 , `completed/success` direkt per Job API geprüft; native KiCad10 ERC, vollständige Netzliste, BOM Export und Prüfskripte. GitHub-Aktions-Lauf auf Commit `48433b193...`, und seitdem nur 2 Dokumentänderungen am A-Branch, **keine neuen Elektroschaltplanänderungen**. Dieser Erfolg ersetzt keine Messung.

### B: Vertrauenswürdiger unabhängiger Gatekeeper, keine neue Hardware

`weg_b/WEG_B_ROUND7_REV6_PRACTICAL_SAFETY_AUDIT_2026-10-15.md` plus 23-Fälle Prüfmatrix, 20-Fälle FMEA, 12 Rechentests als Quellmodell. Beste Erkenntnis: 58V an M8 **nicht automatisch** 58V am IC; gefährliche Fehler mit sub-Fuse Strom, UVLO/OVLO-Hysterese, RAW und USB-/Zellen-Backfeed getrennt testen. "Safe-OFF bis +85°C" nicht mit Halbleiter-Tj-Übertemperaturschutz verwechseln. Kein separat bestätigter erfolgreicher **neuer REV6-B-CI-Lauf** in dieser Prüfung; alte bestandene Runs betreffen ältere REV5/ROUND6-Stände.

**Wichtiger praktischer Fund:** ein von B benannter 58VDC-/125°C-Inline-Sicherungshalter **Littelfuse `0FHM0001ZXJ-RED`** ist auf der Herstellerproduktseite ausdrücklich mit maximal58VDC und maximal125°C aufgeführt: https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0001zxj-red . Er ist **als Spannungs-/Temperaturkandidat** mit Littelfuse MINI® 997 58V zu prüfen; elektrische, mechanische, DC-Clearing-, Kabel-, Derating- und Lieferanten-/Halter-Kombinationsprüfung **noch nicht bestanden**. Diese Information an D/C/A weitergeben.

### C: Neue preiswertere Alternativen und wichtigster Neustartbefund

`weg_c/REV6_COTS_ARCHITECTURE_DECISION_2026-10-15.md`:
- C-A: 100V-Schottky + TPS26631 eFuse + 80V-LMR38020, **nicht** als fertige freigegebene Schaltung; 2V operating Headroom bei max58V + Ringing. In der default fixed OVLO/OVP-Variante **KEIN garantierter automatischer Neustart bei stabil32V nach OV**, denn max/falling thresholds zu hoch. Externer Präzisionsteiler nötig; auch `A` muss kontrollieren, dass dessen anders dimensioniertes Dreiernetz im WORST CASE bei32V wieder freigibt.
- C-B: TPS26600 mit internem Reverse-Schutz, ohne Schottky und potenziell billiger, aber **nur 62V absolute max**; von58V nur 4V bis ABS, daher P0 bei Leitungs-L/PAD-Ringing.
- C-C: Modul RPH-3.0-CT mit externem Schutz, aber eigenem max55V, wenn Schutz-FET kurzgeschlossen potenziell gefährdet.
- Rechengates für 0.1%-OVP: C-A TPS26631 100k/3.78k rise32.210–33.685V, fall max31.649V (**nach Seriendiode muss reale Schottky Vf beim Restart unter0.351V liegen**, nicht garantiert); C-B TPS26600 100k/3.74k rise32.381–34.055V, fall max31.275V (statische 32V-Freigabe belegt, dynamisches 58V-Pad NO-GO bis getestet).
- 35/34/23 **Scope-Positionen**, also System-Sammelblöcke mit externen Pflichten, **nicht** echte KiCad-Bestückcounts, 12/11/4 davon bepreist. Netto Teilpreisuntergrenzen A 14.387/10.304/8.049, B 13.126/9.409/7.388, C 13.199/11.632/10.126 EUR bei1/10/100; keine Vollkosten und **nicht direkt mit A-25-Positionen vergleichbar**.

**CI** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38812555462 `completed/success`, native REV6-KiCad10 ERC/Netlist **nicht** ausgeführt (kein entsprechender neuer KiCad-Entwurf), Rechen/BOM-Tests bestanden.

### D: LTC4368-2 mit größerer elektrischer Toleranz, aber teurer und ohne KiCad

`weg_d/REV6_58V_ARCHITECTURE_STOPGO_2026-10-15.md`: Direktbuck allein ≠ OVP/Reverse/OCP; kleine 58V-SMBJ58A klemmt möglicherweise erst bei93.6V, schützt **nicht** 67V eFuse-AbsMax. Bevorzugt **ADI LTC4368HMS-2#WPBF**, AEC-Variante, Back-to-back 100V-FETs, Shunt, verstellbare OVLO und 80V Buck. Externe Schutzfrontend-Teile statt hochenergetischer 200V-TV S. Die Wahl ist nur **ARCHITEKTUR-KANDIDAT**, weil 58V-Pads/Hot-FET-SOA, +85°C-Thermalausschalter, RAW0.5A, Installations-F_MAIN/Halter und Pinwerte fehlen. Es liegt kein nativer REV6-D-KiCad/DRC/Actions-Echtlauf vor.

Preisgruppen nur Untergrenzen: LTC4368+2x-Vishay-VergleichsFET+Buck+F_MAIN 18.23/13.344/10.6309 EUR netto 1/10/100 **ohne** notwendige weitere Passiv-/Temperatur-/RAW-/Stecker-/Halter-/PCB-Teile. 58VDC F_MAIN MINI `0997004.WXN` (4A) ist ein plausibler Kandidat, aber 58VDC-Freigabe **plus** DC-Arc/Rsrc/Temperatur am tatsächlichen Sicherungsort sowie Halter-Koordination bleiben offen. **D-Halter-TBD veraltet gegenüber B-Littelfuse-FHM-Fund – cross-check, nicht automatisch Schaltung freigeben.**

## 3. Wichtigste Cross-Branch-Fehler und Entwurfsentscheidungen

1. **32V-OVP-Restart:** *A* hat den OVLO-Aufstieg modelliert; *C* zeigt den problematischen Abstieg/default fixed-OVP, sodass das **A-OVLO-Falling-/Hysterese-Gate inklusive Eingang-R/L, 32V-Versorgung, 10V-Start und VIN-Abfall** zwingend priorisiert werden muss.
2. **58V-Klemmpfad:** *A TPS26631 60V recommended /67V abs* nur2V nominale Regelreserve, *C TPS26600 62V abs* nur4V absolute Reserve. Die **extern gemessene Spitzen-Spannung** am Eingang samt interner Resonanz ist der Start der Auswahl – kein unbewiesenes „58V ist unter60V“.
3. **+85°C-Safe-OFF:** A hat **keine eigene Umgebungstemperaturabschaltung**, C/D ebenfalls nicht qualifiziert. Chip-Tj165°C Thermal Shutdown ≠ Ambient+85°C sicherer OFF. Ein Sensor/Auswerteschalter ggf. auf TripTracer oder TripPower muss systematisch geplant und bepreist werden.
4. **RAW0.5A:** A hat nur ~3A gemeinsamen Strompfad; C/D ebenso separate Leitungs-/Kurzschlussbegrenzung offen. Keine 0.5A-Schutzbehauptung ohne eigener Fehlerstromgrenze oder Kabel-/Kontakt-Nachweis.
5. **USB/Backup:** FRAM bleibt ohne Zelle nichtflüchtig; bei hartem M8-Abzug keine Vorwarnung/erfolgreiche microSD-Flush-Garantie ohne Energiespeicher. Keine Primärzellen-Rückladung oder Backfeed in M8/USB/RAW.
6. **F_MAIN/Halter:** B hat jetzt einen konkret herstellerbelegten 58VDC-/125°C-MINI-Halter (Littelfuse FHM, siehe Herstellerquelle), den A/C/D gemeinsam zum typgenauen 58V/4A-MINI 997 prüfen sollen.
7. **BOM-Vergleich fair:** A25 sind **bestückte Elemente nur des isolierten, noch funktionsunvollständigen Moduls**, C35/34/23 sind **vorgesehene Scope-Positionen inklusive Systemperipherie**, D-Preise **unvollständige Teilgruppen**. Keine vollständige direkte BOM-/Systemkostenrangliste schon möglich.
8. **Installation:** Alle REV6-Entwürfe **nur für nachweislich zentral gedämpfte 12/24V-Fahrzeuge mit max58V am M8**, keine ungedämpfte200V-Zusage. Fehlanschluss ist relevantes Produkt-/Etikett-/Anleitungsthema.

## 4. Nächste konkrete Gate-Aufgaben

**A:** Wiederanlauf-V_HYS bei32V nach OV und vollständiges Datenblatt-Falling; AEC/industrial eFuse- und +60°C 2A, Ceff/Induktor/BOM-EOL; eigens +85°C-safe-OFF, RAW-Fault, Mainboard-USB/PWR_FAIL-Schnittstelle hinzufügen oder ihren Ort belegen. Vor PCB neues MPN/EOL fixieren.

**B:** Gegen die reale A-Netzliste 32V-Restart und TPS26631-58V Pad-Max prüfen; 58V-Fuse+FHM-Holder als konkrete *Kombination* inkl. Hersteller-DC-Clearing/Temperatur/Leitungsquerschnitt sichern; 23+ Testfälle gegen A/C/D priorisieren.

**C:** TPS26600-Versorgung als alternative wirklich fertig zeichnen, aber **erst** worst-case 62V-ABS inkl RLC sowie 10–32V/OV-Hys/5.5V-SHDN und RAW-Branch klären; A25- und D-System-Scope in *identische BOM-Grenzen* bringen. C-A Schottky 32V-Restart auf Null-Last Vf(T) nachweisen.

**D:** Konkretes Referenzdesign des LTC4368HMS-2#WPBF inklusive 0.1%-TCR-Teiler, FETs/Shunt, Temp-Safe-Off, 58V-Surge, Kurzschluss/Fuse und RAW0.5A entscheiden; B's FHM-Halter übernehmen, wenn Datenblatt-/Integration freigegeben; dann isoliertes KiCad10 ERC/Netlist.

**Produktleitung:** Vor Auswahl 58V-Max am echten M8 (Pulsform, Flanken, R/L, negative Impulse) und Lastbudget/Temperatur/Schutzfunktionen für TripPower vs TripTracer festlegen. Erst danach gemeinsame Entscheidung zwischen A eFuse (kleiner), C TPS26600 (weniger Passiva, geringere HV-Marge), D LTC4368 (aufwendiger, größerer VIN-ABS-Puffer). **Noch keine PCB-/Materialbestellung.**

## Herstellerbeleg bei dieser unabhängigen Prüfung
- Littelfuse original: https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0001zxj-red (58VDC, Max Temperature125°C, AWG14, MINI 58V fuse compatible).
- TI TPS26631: https://www.ti.com/product/de-de/TPS2663/part-details/TPS26631PWPR (4.5–60V operating, 67V abs; Catalog/Industrial, Externfet-Vorgaben). Aktuelle Verfügbarkeit/AEC nicht aus einem verifizierten Lagerbestand für gesamte BOM extrapolieren.
