# TripPower Weg A – Round5: Fehlerpolitik, A23-UVLO und reale Host-Grenze (2026-10-16)

**Branch:** `design/trippower-a`. **Entscheidung:** bestehendes A23-Factory-OVP-KiCad als Hauptschaltung beibehalten, **kein elektrisch geänderter Pfad**; falsche historische OVP-Notizen im A23-Sheet aktualisiert. **STATUS: NO FAB / NO VEHICLE.**

## Quelle und Provenienz
Vor Entscheidung direkt aus GitHub gelesen: `AGENTS.md`, `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, `docs/HARDWARE_REQUIREMENTS.md` PWR44–56, `docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md`, `hardware/modules/TripPower_5V2A/POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md`, A-Round4, A-native Evidence und aktuelle B-Round10, C-Round10, D-Round10 auf ihren eigenen Branches. Vor Änderung beide tatsächlich vorhandenen getrennten A25/A23-KiCad-Wurzeln, A23-Schutz-, Buck-Blätter, beide Bestell-BOMs, echte Host-Hierarchien `01_Eingangsschutz` mit `01H/01I`, `02_5V_Buck`, `03_3V3_USB` gelesen.
Hersteller: [TI TPS2663 SLVSE94G RevG](https://www.ti.com/lit/ds/symlink/tps2663.pdf) §§6.1,6.3,6.5,6.6,8.3.1,8.3.2.1,8.3.3,8.3.4,8.3.7.1.2,8.3.12,8.4/Table8-1,9.4/9.5; [TI LMR38020-Q1 SNVSBS6B RevB](https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf) §§7,8.2,Table8-1. Einzelpreis-/Bestandsangaben nur Händlersnapshots, **keine** garantierte sofortige Verfügbarkeit bei 100 Stück.

## 1. MODE / PGTH – verbindliche A23-Hauptvariante
**U201.MODE12=GND → AUTO-RETRY** nach Current-Limit-Timeout oder Tj-Übertemperatur. TI Tabelle 8-1: `MODE=OPEN` wäre LATCH, nur Rücksetzung per SHDN low→high, UVLO low→high oder IN_SYS power-cycle, **nicht** durch normale OV→32V-Rückkehr; hierfür existiert kein nachgewiesener automatischer Host-Resetpfad. Die REV6-Pflicht für automatisch stabiles Wiederanlaufen nach Temperatur/Fehlerende spricht gegen einen ohne Host-Reset wartungsbedürftigen Latch. Diese Wahl ist **bedingt**, nicht der Nachweis der Kurzschluss-Gefahrlosigkeit.

**U201.PGTH16=GND → immer LOW am TPS-eigenen PGOOD17**; bei OV/UV-Recovery wird mit `C203=100nF` dVdT statt Fast-Recovery neu gestartet. **WICHTIGE ELEKTRISCHE NEBENWIRKUNG:** TPS26631 erlaubt 2×IOL-Überstrompuls gemäß TI §8.3.7.1.2 nur **nach PGOOD HIGH**. Bei PGTH-GND steht er somit nicht zur Verfügung; der Limitierungsbetrieb beginnt mit rund 1×IOL (~3A nominal über R204 6.04k). Die schnellen internen Kurzschluss-/Transientenspitzen sind damit **nicht auf 3A oder RAW0.5A begrenzt**. Der andere U101-Buck-PG-Pfad über R501/R502/Q501 ist davon unabhängig und bleibt erhalten. PGTH=FLOAT wäre kein gleichwertig garantierter Fast-Restart oder PGOOD-HIGH-Ersatz, denn ohne PGTH-Spannungsfühler fehlt eine definierte VOUT-Schwelle. Dafür keine zusätzliche widersprüchliche KiCad-Hauptversion erzeugen. Hersteller-Retry-TSD-Delay MIN/TYP/MAX **500/648/800ms** (nach zulässiger Abkühlung); keine sicher berechnete Energie pro Retry ohne P(V,T)-Messung.

### Fehler-Wiederherstellungsmatrix
| Zustand | Elektrisches Soll | Auto / Grenze |
|---|---|---|
| 32→36/58→**32V** normal, ohne OCP | Factory OVP bis35.4V rising aus; falling MIN32.7V; dann C203/dVdT | Automatisch, sofern IN_SYS bei 32V-Rückkehr incl Rauschen **<32.7V** und keine zusätzliche Fault-Latch-/Versorgungsgrenze; Labortest offen. |
| 10V-Start / Eingangsdroop | Einwiderstand-UVLO keine harte 9V-Schwelle; Buck+eFuse eigene UVLO | Bei stabiler Versorgung automatische Freigabe; 5V2A+RAW0.5A bei10V, Leitungsdrop und Brownoutflattern messen. |
| Permanenter RAW-Hardshort | eFuse schützt gesamten Ausgang ungefähr 3A, zeit-/thermisch abgeschaltet | Auto-Retry pulst erneut; **NO-GO als selektiver RAW0.5A-Schutz**. Host-RAW-Zweig braucht realen 0.5A-Limiter/Fehlerenergiemessung. |
| Wiederholte Überstromlast | 1×IOL, ~162ms typ time limit vor OFF oder frühere TSD, keine garantierte 2×Pulse | Auto-Retry erst nach Delay; thermische Worst-Case-Fehlerenergie/Leiterbahnhitze ungemessen, Freigabestopp. |
| Internes Tj-TSD | TI typ165°C Tj, Auto-Retry nach abgekühlter Tj | **Kein** Umgebung85°C-OFF! Fehlersicherer externer Ambient-Interlock erforderlich. |
| Einschalten mit großem COUT | über C203 begrenzte Ramp; TI interne Thermal Regulation und Timeout typ2.54s | Bei fehlgeschlagenem Ladeaufbau auto-retry; Ripple/Strom/Laderampe/Wärme bei kaltem10V messen; kein unbegrenztes COUT-Versprechen. |

**Latch-Forschungsentscheidung:** Ohne nachgewiesenen Hardware-Resetpfad und Abgleich mit Temperatur-Wiederanlauf keine MODE=OPEN-Projektvariante als alternative Hauptschaltung. Bei unvermeidlich heißem Dauerfehler trotz RAW-Branch-Schutz/Netzprüfung **MODE=OPEN plus eindeutig spezifizierte hardwareseitige Fehlerentriegelung neu bewerten**. Keine verdeckte MODE-Kombination.

## 2. UVLO A23 vs A24 und DC-Bias
**A23 gewählt:** Yageo `AC1206FR-07330KL` 330k/1%/100ppm/K zwischen IN_SYS6 und UVLO7: TI bei externer Q201-Verpolung mindestens300k. Rmin −20..+70°C **325.215k**, bei+85°C **324.720k**. UVLO bei lokal10V mit ±150nA Pinleck ≥9.9498V > TI1.224V rising. Keine absichtlich programmierte eigene Unterspannungsabschaltung unter10V.
**A24 nur als mathematische Probe:** 330k zu UVLO, 56k nach GND → rising ca **7.859..8.699V**, falling ca **7.281..8.176V** bei ±1.45% und ±150nA; 68k → rising ca **6.671..7.389V**, falling ca **6.180..6.945V**. Diese Schwellen liegen unter10V und garantieren weder einen 10V-Steckerstart noch sauberen Buck-Brownout oder die Sicherheit eines Sensor-Hängers. Die Zusatzposition/Divider-Entnahme verbessert bisher keinen nachgewiesenen Fehlerfall. **A23 solange behalten, bis der Mess-Brownout zwischen 10 und ~6V ein echtes Problem zeigt.** Bei nominal10V, η80%, 5V2A+RAW0.5A fließen idealisiert ca **1.75A** am Eingang, realer Stecker-/Q201-/Draht-/Inrush-Drop ist zu messen.

**Buck unverändert:** `LMR38020SQDDARQ1`, 400kHz (R103), 15µH Bourns `SRP7050TA-150M` Irms3.5A/Isat6A, 3×22µF/25V Taiyo `MCAST32MSB7226KPNA01`, 2×4.7µF/100V AVX `12101C475K4Z2A`, 100nF HF. Nominal FB 100k/24.9k → 5.016V bei exakt1V Referenz. Ideal L-Ripple ~0.417A pp@10V, ~0.703A pp@32V bei15µH, 2A; bei −20% Induktivität höher. TI Table8-1 bestätigt nominell 15µH und 3×22µF für 400kHz 48→5V/2A. **Hersteller-Ceff(5V,Ta,Age) und Ceff(32/58V,Ta) bislang nicht nachgewiesen**, ebenso L101 Hot-Isat/EMV/PCB-Thermik/regulatorische Toleranzen. Keine Bauteile ohne Nachweis entfernen.

## 3. Reale Systemhierarchie – keine Schein-Integration
Tatsächlich aktive Root `hardware/kicad/TripTracer_V1.kicad_sch` referenziert `01_Eingangsschutz.kicad_sch` (mit **`01I_LM74800_INPUT`, `01H_ACC_HOLD_GATE`, `01C_HOLD_TIMER`**), `02_5V_Buck`, `03_3V3_USB`, weitere. Die **A23-Root wird von TripTracer_V1 aktuell NICHT referenziert**. Deshalb zwei alternative Topologien, nicht gleichzeitig als fertige A23-Hardware verbinden. Keine historische K101-Relaisbestückung unterstellen.

| Funktion/Signale aus echten Blättern | Aktuell nachgewiesen | Offene elektrische Brücke vor Systemfreigabe |
|---|---|---|
| TripPower 5V/RAW | A23 `5V_OUT`, `VIN_PROTECTED_UNFUSED` und TP202 als bloßes RAW-Testpad | Kein 2A-Kontakt, 0.5A-selektiver RAW-Highside-Limiter, Hoch-/Teilkurzschluss- und Leiterbahnschutz; `VIN_PROTECTED_UNFUSED` ist nicht schon selektiv geschützt. |
| 85°C Ambient OFF | A23 SHDN13 offen, interne TI-Enable-Pullup ON; TPS Tj-Schalter keine Ambient-Abschaltung | **Hardware-default-OFF** in realer Eingangspfad/HOLD-Freigabe, Temperatur-Schwell-/Hyst-Failsafe bei Sensor offen/kurz/Versorgung weg/MCU hängt/USB-only; SHDN allein bei offenem Draht ungeeignet. |
| ACC/RUN/HOLD | Host 01I: `VEHICLE_ACC_RAW`, `VEHICLE_BAT_RAW`, `ACC_PROTECTED_IN`, `BUCK_ENABLE`, `HV_PROTECTED_AFTER_EFUSE`; 01H: `HOLD_TIMER_GRANTED_3V3`, `ACC_START_BASE`, `BUCK_ENABLE` | Noch kein nachgewiesener integrierter Funktionspfad der A23 über diese Netze; OFF<1mA, Debounce, ACC-off-SD-Flush und MCU-Stall-FailSafe am gesamten System prüfen. |
| PWR_FAIL | A23 TPS-PGOOD ungenutzt; **Buck PG6→Q501**, `PWR_OK_SINK_FAIL_RELEASE` an TP501, pullup extern fail-HIGH | Geeigneter Host 3V3-Pullup/ESD und unabhängige Unterspannungsprüfung, 0µs Warnzeit bei M8-Abriss; nicht auf RTC-Zelle zurückspeisen. |
| USB | Host `03_3V3_USB`: `USB_VBUS_RAW`, `V5_BUCK_RAW`, `V5_SYS`, `USB_ACTIVE_N` und U301/U302-Mux/Regler | Systemnetzliste und VIN=0/USB-only/simuliertes GND-off/MCU high Gegenstrom-Pfad prüfen; nicht als fertiger BAT/RAW/USB-Backfeed-Schutz ausgeben. |
| FRAM/SD | REV6-FRAM-first ist funktional verbindlich; aktive `07_Speicher_RTC.kicad_sch` wurde eingesehen | Verbindliche FRAM-/SD-Transaktions-Firmware und echte Integrations-/Backup- und Lasttests; 0µs-M8 Vorwarnzeit, CR1220 niemals ungeprüft für ESP+microSD benutzen. |
| F_MAIN | In A23 **0** bestückte Fuse/Halter/Einmal-Thermosicherung | Vor BAT+/ACC-Kabel quellnahe passende externe Leitungsschutzsicherung; optional zugängliche Gerätesicherung ausschließlich Hauptplatine; DC-Puls/Leitungsschutz messen. |

## 4. Kosten und Beschaffung (23 echte KiCad-/Order-BOM-Positionen)
| Module je Bestellung | A23 Bauteile €/Stück netto | Gesamtpreis aller Modul-Bauteile netto | Nur alternative A24 €/Stück netto |
|---:|---:|---:|---:|
| 1 | 20.2570 | 20.2570 | 20.3430 (mit68k) |
| 10 | 13.5610 | 135.6100 | 13.5830 |
| 100 | 10.6266 | 1062.6600 | 10.6416 |

Alle 23 vorhandenen A23-MPNs/Footprints gegen tatsächliche bestellte CSV/native KiCad-Export testen. Bestehende konkrete Hauptteile: TPS26631PWPR, SQM100N10-10_GE3, BSS138LT1G, LMR38020SQDDARQ1, SRP7050TA-150M, keramische Typen siehe CSV. **Keine vollständige Echtzeit-Vorratsgarantie für 23/23 MPNs.** Beispielsweise Mouser-Webanzeige TPS26631PWPR ungefähr **57 sofort lieferbar** und deutlich spätere angekündigte Nachlieferung (Abfrage/Indexstand kann sich ändern). Ein Angebot für 100 bestückte Geräte ist somit keine Sofortfertigungszusage. **Nicht enthalten:** PCB, Stencil, Bestückung, Stecker, RAW/Temperatur-Hardware, Host-System, externe Fahrzeug-Fuse/Halter/Kabel, Versand, MwSt, EMV/Labor/Ausschuss.

## 5. Reproduzierbare neu eingeführte Gates
`tools/trippower_a_rev6_round5_fault_policy.py` erstellt Grenz-/Wiederanlauf-JSON; `tools/test_trippower_a_rev6_round5_fault_policy.py` überprüft unabhängig 330k-Hot-Minimum, factory OVP, 56/68k-Corners, MODE/PGTH/2×Pulse-Negativbehauptung, reale Host-Unterseiten, Stückliste/Preisaddition und veraltete falsche Schaltplanannotation. GitHub-Actions `trippower-a-rev6.yml` führt diese Tests **zusätzlich** zu vier nativen KiCad10-ERC, Netlist/Pin-Differenz/BOM durch.

**Nachweis für diesen Commit:** nach Actions-RUN ausdrücklich SHA, Jobresultat, Logtext ERC0 und Prüfzahlen verifizieren; keinen neuen PASS vor Ausführung behaupten. Kein PCB in A23 vorhanden, daher kein PCB-DRC. Die alte A25-Referenz bleibt elektrisch und dokumentarisch separat.

## 6. Priorisierte Freigabestopps
1. **P0:** 58V/350ms an M8 vs **max60V an TPS IN/IN_SYS und 67V ABS**, einschließlich TI Eq14, M8→IC-L/C/R/Dauer/Ringing, Vin-SW/BGATE/DRV/UVLO und MOSFET-Fault. Weg D Round10 ohne ausgeführtes TI-PSpice; Hersteller-Modell und Oszilloskop/Quellprofil fehlen.
2. **P0:** +85°C **hardware-sicherer Ambient-OFF** selbst bei MCU-/Sensor-/Enable-Pfad-Fehler; 0.5A RAW **selektiver Teil-/Hardshort-Schutz**, Auto-Retry-Wärme/Leiterbahn-/Steckertests. Nicht durch reine Software lösen.
3. **P1:** A23 in echter TripTracer-Hierarchie/Stecker integrieren, ACC/HOLD/USB/PWR_FAIL/FRAM verbinden und Backfeed/OFF<1mA beweisen. Alte eigenständige 01I-Hochvolt-Architektur nicht parallel ohne Systementscheidung betreiben.
4. **P1:** 10V/5V2A+RAW0.5A−20/+60C Start/Drops, 32→36→58→32 dynamische Recovery, effektive MLCC-Kapazitäten, 15µH-Hot-Isat, 5V-Ripple/Regelschleife und +60°C Vollastthermik/PCB/Layout/EMV.
5. **P1:** 23/23 konkrete Liveverfügbarkeiten, Footprint-Pad/EP/Pin-Geometrie/manuelle Herstellermechanik, Fertigungsdesign, PCB-DRC **erst nach PCB-Erstellung**.

**Fazit:** A23 unverändert in Leistungspfad und bestückten 23 Positionen, KiCad-Warntext jetzt korrekt; die besseren Hersteller-/Fehlerregressionen begrenzen Schein-PASS, nicht die noch offenen realen Risiken.
