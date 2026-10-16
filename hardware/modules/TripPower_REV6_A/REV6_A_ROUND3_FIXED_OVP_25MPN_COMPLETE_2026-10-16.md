# TripPower Weg A – REV6 Round3: 32-V-Neustart, vollständige 25er-MPN-BOM und native KiCad10-Prüfung

> **VERBINDLICHE KORREKTUR 16.10.2026 (Round 10, TI Rev.G):** Die unten ursprünglich getroffene Aussage `Factory-OVP = NO-GO` ist **falsch**. Ich hatte den Vorzeichenbezug der OVP-Hysterese verwechselt. Bei Rückkehr auf 32.0 V ist `VIN_SYS=32.0V < V_FACTORY_OVP_FALL_MIN=32.7V`, d.h. **werkseitige OVP garantiert in der idealen statischen Herstellerspezifikation die Wiederfreigabe** mit 0.7V Mindestabstand. Sie ist für 32V-Normalbetrieb, OVP >32 bis ≤36V **geeignet**, wenn OVP pin8 nach GND gezogen wird. Das frühere 100k/12k/4.22k-Netz (Round3) ist nach TI §9.4 zusätzlich **bei externem Verpol-FET nicht herstellerkonform**, weil nur100k zwischen `IN_SYS` und `UVLO` statt vorgeschrieben ≥300k liegen. Die historische 25er-Baseline bleibt zum Vergleich archiviert, **nicht fertigungskonform**; neue getrennte [23er-Fabrik-OVP-Version](TripPower_REV6_A_FACTORY_OVP.kicad_sch) mit 330k und eigener KiCad-10-ERC/Netlist/BOM ist der korrigierte Forschungsstand. Hersteller: https://www.ti.com/lit/ds/symlink/tps2663.pdf, §§6.5, 8.3.3/4, 9.4.

**Stand:** 16.10.2026 | **Branch:** `design/trippower-a` | **Status:** Entwicklungsprototyp, ausdrücklich **NO FAB**.

## 1. Verbindliche Dokumente und unveränderter Projektumfang
Gelesen: `AGENTS.md`, `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, `docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md`, `docs/HARDWARE_REQUIREMENTS.md` PWR-44–56, neuester REV6-Gesamtreview `docs/TRIPPOWER_ALL_BRANCHES_REVIEW_REV6_2026-10-16.md` aus `design/trippower-review`, vorheriger `REV6_A_ROUND2_OVP_RIPPLE_TEMP_RAW_2026-10-16.md`, letzter nativer CI-Bericht sowie beide tatsächlichen REV6-Schaltplanblätter und die 25er-BOM. Die historische REV5 ist **nicht verändert**; 200V/350ms ungedämpft und +125°C Volllast sind **keine REV6-Anforderungen**.

**Hardware jetzt nativ umgesetzte Änderungen am isolierten REV6-Hauptschema:** R202 12.4k→12k ±0.1% (Panasonic `ERA-8AEB123V`), R204 6.04k ILIM Yageo nicht lagernd→Vishay `CRCW12066K04FKEAHP` AEC-Q200, L101 15uH wenig dokumentierter Fangcheng→Bourns `SRP7050TA-150M` AEC-Q200 (lokaler KiCad-MPN-Footprint), 5V-Sensepad TP502 **nicht bestückt** auf Buck-Blatt ergänzt. **Bestückzahl bleibt25**, kein Sicherungshalter, keine Schmelz- oder Einmal-Thermosicherung; F_MAIN externe Fahrzeugleitung bzw. ggf. TripTracer-Hauptplatine. Die weiterhin **nicht qualifizierten** alternativen isolierten 26er-Schaltblätter mit T201 67F080 oder F201 RAW-PPTC werden nicht in Hauptvariante integriert.

## 2. Priorität 1: TI-Werks-OVP objektiv ausgeschlossen
Hersteller [TI TPS2663 RevG 2024](https://www.ti.com/lit/ds/symlink/tps2663.pdf):
| Modus | MIN | TYP | MAX |
| --- | ---: | ---: | ---: |
| Factory OVP rising | 33.2V | 34.33V | 35.4V |
| Factory OVP falling | 32.7V | 33.89V | 35.0V |
| Factory UVLO rising | 15.1V | - | 15.9V |

**NO-GO** für nur werksseitig voreingestelltes OVP: Selbst das **MIN fall 32.7V** liegt oberhalb genau32V → Ausgang kann nach OV bei stabil32V OFF bleiben. Factory UVLO rising ≥15.1V gefährdet10V-Start. **Mindestens drei extern programmierte R201/R202/R203** bleiben deshalb.

**Elektrisch geänderte 0,1%-Präzisionsteiler:** R201 Yageo `RT1206BRD07100KL`100k, R202 Panasonic `ERA-8AEB123V`12.0k, R203 Yageo `RT1206BRD074K22L`4.22k; nach Hersteller 25ppm/K für diese konkreten Kandidaten. `tools/trippower_a_rev6_limits.py` verwendet Vref rise1.176..1.224V, fall1.09..1.15V, unabhängige ±150nA UV/OV-Lecks, Rtol±0.1%, angenommen unabhängige ±25ppm/K über45K (25→70°C und 25→−20°C).

| Dynamikgrenze **nur statisches Pinmodell** | MIN [V] | TYP [V] | MAX [V] |
| --- | ---: | ---: | ---: |
| Programmierte OVP rising | **32.2233** | **33.0483** | **33.8795** |
| Programmierte OVP falling/release | **29.8645** | **30.9002** | **31.8332** |
| UVLO rising | **8.3767** | **8.5983** | **8.8213** |

**[HISTORISCHE 25er-Teilerrechnung, NICHT jetzt qualifiziert:]** 10V liegt oberhalb UVLO-max **8.8213V**, 32V liegt unter OVP-rise-min **32.2233V**, spätestens36V wird ausgeschaltet (OVP-rise-max33.8795V), falling max31.8332V gibt bei32V nominell **166.8mV statische Rückkehrreserve**. Das ist **keine garantierte dynamische Gesamtsystemfreigabe**: VIN-Sollwert/+Noise/ESD, Schaltpunkt-Verzögerung, tatsächliche Widerstands-TCR-/-Temperatur, Ground-Shift, Sättigung, IC-Eingangs-/externes Relais und Lastwechsel sind zu prüfen. 10V unter Last 5V2A + RAW0.5A: angenommene 80% Buck-Wirkungsgrad ergibt Eingangsstrom ca1.75A; Spannungsabfälle/Kaltstart müssen gemessen werden. OV bei36V/400ms, stabil32V-Rückkehr aus Puls, UND Temperatur-UVLO separat laborqualifizieren; kein hysteresis PASS durch reine Gleichungswerte.

## 3. 58V/350ms – keine neue unbewiesene TVS
**TPS26631** 4.5..60V Betriebs-, 67V absoluter Eingangsbereich, nur **2V Betriebsmarge** und **9V ABS-Marge** über angenommenen58V Klemmpotential *am Eingangspad*. Leitung L plus Eingangskondensator C kann bei raschem 32→58V-Sprung vor FET-OVP eine Resonanz aufbauen; `tools/trippower_a_rev6_ringing.py` zeigt als Beispiel L0.5uH, C1uF, Rs0.05Ω einen Spitzenwert **über67V**, obwohl vor dem Kabel nur58V liegen. Das ist Sensitivität, **keine** echte Fahrzeugpulsmessung. 1Ω Seriendämpfung bei10V/1.75A erzeugt 1.75V Verlust und 3.0625W, daher **kein** naiv bestücktes Leistungs-R. Ebenso kein beliebiger TVS ohne zeit-/thermisch belastbare garantierte Klemmschwelle unter60V. Priorität: Oszilloskop direkt bei U201-IN1/2/3 und IN_SYS6, FET-Q201 D/S/G, eFuse OUT18/19/20, Eingang-M8/Hostseite, geschützte VIN, Buck-VIN, RAW, 5V_OUT bei realem Rsrc/Lsrc, 36V/400ms und 58V/350ms auch Abschaltung/Re-Entry/Repeat, -20..+70°C. Wenn **keine** nachweisbare Pinobergrenze ≤60V unter allen zulässigen Einsatzfällen: **HARD ARCHITECTURE STOP**, höher spannungsfester Frontend-IC prüfen (z.B. LTC4368-2 auf Weg D), keinen zusätzlichen unbewiesenen Zener.

## 4. Bauteile, Temperatur, ACC/USB/PGOOD und RAW
**L101 neu** Bourns `SRP7050TA-150M` 15uH (±20% nominal), 3.5A Irms /6A Isat, 92mΩ DCRmax, AEC-Q200, lokale portable `Tripmaster:L_Bourns_SRP7050TA_150M` nach empfohlenem 8.4×3.5mm Gesamt-Landpattern mit 2.5mm Spalt. `tools/trippower_a_rev6_buck_thermal_envelope.py` modelliert bei 400kHz Lmin12uH, 5V2A, VIN10/32V den Spulenripple, Ipeak und DC-Kupferverlust (rund0.37W am 92mΩ-Maximum). Dieser Nachweis ist **kein** +60°C-Board-Tj-/DCR/Isat-/AC-Verlust-/Derating-PASS: Oszilloskop SW/5VOUT, thermisches Hottest bei+60°C, PCB-Kupfer, alle Ausgangs-MLCCs und 5V Lastsprünge nachprüfen. C104–C106 Taiyo Yuden 22uF25V `MCAST32MSB7226KPNA01` AEC-Q200 ersetzen EOL-Murata, aber **Ceff(5V,−20..70°C, X7R, Alterung)** muss über echten OEM-Plot/Bias oder LCR-Messung belegt werden. C101/C108 KYOCERA AVX100V AEC-FLEXITERM, R204 Vishay HP AEC-Q200 lagernd.

**+85°C ambient SAFE-OFF:** Hauptschema besitzt **keinen qualifizierten Temperaturschalter**. Der Sensor `67F080` im isolierten +1-Teil-Prototyp schließt bei 75..85°C an seinem eigenen Körper, aber die auf `SHDN13` erwarteten wenigen µA liegen unter Sensata erprobtem Kontakt-Wetting-Level (10mA bei5V), also kein qualifizierter Safety-Switch. Ein unabhängiger stromgetriebener Schutz-/Host-Temperaturkontakt an der externen TripTracer-Relaissteuerung ist möglich, darf aber ohne Hersteller-58V-/Kontakt-/Restart-Nachweis nicht als umgesetzt gelten. **STOP** bis Temperaturfühler und reproduzierbare lokale Umgebungstemperatur/85C OFF auch während USB+M8 dokumentiert sind.

**RAW0.5A:** Hauptschaltung teilt den eFuse-Gesamtstrom ~3A mit 5V-Buck, der RAW-Kabelast hat noch keine selektive 0.5A-Grenze. Isolierter Bourns `MF-LSMF075/72X-2` 72V automatisch rückstellender +1-Teil-Prototyp bleibt Forschung, Ihold bei+60°C nur0.5A, bei+70°C0.44A, Hot-Kurzschluss/-Puls/I²t unbekannt. Nach PWR55 keinerlei schmelzende Sicherung/Fuseholder auf Modul; F_MAIN physisch externe Fahrzeugleitung und/oder **zusätzliche** Hauptplatine ohne Ersatz quellnaher Leitungssicherung. RAW nur mit nachgewiesenem Kabel-/Kurz-/PPTC-Derating freigeben.

**PWR_FAIL**: Q501 BVSS123LT1G +R501/R502 (3 bestückte Positionen bereits in25), LMR38020-Q1 PG6. Der Host sieht `PWR_OK_SINK_FAIL_RELEASE` LOW=gesund / hochohmig=kein5V; Host-Pullup nur eigene isolierte logische 3V3-domain und **nie** RTC-Primärknopfzelle oder VBUS nach BAT/RAW. PG ist **kein garantiert vorzeitiger** M8-loss-Trigger und weder RTC noch microSD durch CR1220 gepuffert. Neues TP502 am `5V_OUT` zusätzlich zu TP501 PWR_FAIL zur Messung, **kein** 2A-Lastanschluss. ACC-/RUN-/MCU-HOLD, USB-PowerMux, HARNESS BAT/ACC-Sicherung, 2A/0.5A-geeignete Verbindung, host Temp/M8-Interface müssen auf der TripTracer-Hauptplatine umgesetzt werden; falls nicht vorhanden muss es ergänzt werden. Bei ACC-off+BATT alive normales SD-close, bei hartem M8-loss FRAM-first/SD-Recovery.

**BAT+-OFF <1mA** ist **Host-Leitungsstrom** im System inklusive Relais-/USB-/RTC-/ACC-Detektion. TripPower kann nach abgeschaltetem Eingangsrelais aus BAT+0A sehen, aber dies garantiert **nicht** gesamt BAT-OFF <1mA. Nachweisen bei12/24V und warmem Leckstrom.

## 5. Tatsächliche bestückte BOM und Nettokosten
`REV6_A_25_PART_ORDER_BOM_2026-10-15.csv` ist auf **25 von 25 konkrete, separat vendor-gelistete MPN/Referenzen und EUR-Netto-Preisstaffeln** aktualisiert. Nicht dabei: PCB, Bestückarbeitszeit, Versand/MwSt, host-carrier connector, External F_MAIN/holder, Kabel, ACC-Relais, USB-Mux, Backup, Temp-Abschalter, optionaler RAW-Prototyp. Kostensnapshot **keine garantierte Mischwarenkorb-Bestellmöglichkeit bei einem Händler**; alle SKU/Bestände und Order-MOQ kurz vor Bestellung neu validieren.

| Bestückte REV6-Option | Teile | EUR netto pro Stk bei1 | bei10 | bei100 |
| --- | ---: | ---: | ---: | ---: |
| **Basis führende REV6 A** | **25** | **20.7630** | **13.9910** | **11.0217** |
| Isolierter T201 Sensata 67F080 Thermostat Forschungsstand | 26 | 28.6130 | 21.6610 | 17.9317 |
| Isolierter F201 Bourns RAW 72V PPTC Forschungsstand | 26 | 21.6320 | 14.6430 | 11.4997 |
| **Historischer REV5** | 57 AUTO / 58 RUN | unvollständig | unvollständig | unvollständig |

**T201 und F201 nicht gemeinsam zur Prototyp-Hauptvariante hinzugefügt; kein 27er Kombinationsschema.** Nur Haupt-KiCad ist die 25er-Basis.

## 6. Reproduzierbare GitHub-Actions-/KiCad10-Gates
Unter `tools/`: `trippower_a_rev6_limits.py` (TI factory rising/falling vs programmable 32V), `test_trippower_a_rev6.py` (UV/OV hysteresis, OEM no-go, L/C/RLC), `trippower_a_rev6_buck_thermal_envelope.py` (L/Irms/DCR, +60°C Stop), `check_trippower_a_rev6_native_netlist.py` (U201/Q201/Q202/PUllup/TP501+TP502, NO F_MAIN parts), `check_trippower_a_rev6_thermo_netlist.py` und `check_trippower_a_rev6_raw_pptc_netlist.py` (isolierte Delta-Sicherungen), `check_trippower_a_rev6_procurement.py` (native KiCad BOM vs25 KiCad-MPN vs Händler-Preisstaffeln, failure on mismatches).

Workflow `.github/workflows/trippower-a-rev6.yml` macht native KiCad10-ERC für 25er Root, 26er nur-T201 und26er nur-F201; exportiert alle drei echten BOMs, fordert 25/25-MPN-Preisgleichheit zum installierten symbol; Python-Testmodell und JSON-Artifacts. **Kein PCB vorhanden: PCB-DRC nicht anwendbar.**

**Echte erfolgreiche GitHub-Actions mit spezifischem Commit / Job-ID am Ende der Arbeit aufschreiben.** Ein erfolgreiches CI bedeutet weder +85°C noch 58V- oder 5V2A@+60°C-Hardwarefreigabe. Bis realer Prüfstand und PCB/Mechanik/Fehlerenergie geschlossen sind: **NO FAB, NO INSTALL**.
