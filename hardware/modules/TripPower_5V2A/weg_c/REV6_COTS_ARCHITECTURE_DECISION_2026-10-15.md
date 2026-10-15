# TripPower Weg C – REV6 COTS-Neuentwurf (15.10.2026)

**Verbindliche REV6-Entscheidung:** C1/C2-HV und die alten 200V-Ansätze sind Historie. Gesucht wird 10..32V/5V2A, Abschaltung 32..36V, nur am Eingang auf 58V/350ms *zentral begrenzter* Lastabwurf, -20..+70C, 2A bis Ta60C, 85C safe OFF, RAW0.5A Ziel, FRAM-first mit optionalem lokalem Backup. Einbau nur in nachweislich zentral begrenzten Fahrzeugen. Keine unabhängige 200V-Surge-Erwartung. Alle absoluten Maximalwerte gelten an Bauteilpads **inklusive Ringing**, nicht nur am M8.

## 1. Herstellerbasierte Kandidaten

**A – bevorzugter Engineering-Kandidat, nicht fertigungsgenehmigt:** 5A/100V Schottkydiode (Diodes SDT5A100SB-13; alternativ AEC-Q101 STPST5H100SBY), TI TPS26631PWPR 4.5..60V/67V abs eFuse, intern **fixed OVP** rising 33.2..35.4 V und falling 32.7..35.0 V wenn OVP an GND, sowie TI LMR38020SQDDARQ1 4.2..80V/2A als 5V-Buck. EIN externer Induktor. Einfache Rückpolsperre, eFuse begrenzt Last-/Kurzschlussstrom, Buck erzeugt 5V, eFuse enthält PG/FLT. Beschaffbare Schutz-/Reglerteile. Tradeoff: Diode bei Eingang 10V und voller Last ~1W Hitze, PVIN_eFuse 58V lässt nur 2V bis **recommended max 60V** (und 9V bis 67V abs). An jeder IC-Padspitze/ESL testen. **Ohne getrennte RAW-eFuse ist RAW0.5A lediglich erlaubter Verbrauch, nicht Strombegrenzung auf 0.5A!** TPS26631-ILIM geschätzt ~2.4A nominal (R_ILIM ca 7.5k), bei dynamischem 2x/3x fault muss RAW Leitung auf volle fault profile ausgelegt werden. 10V und 32V inkl tolerierter seriellem Diode-Drop, eFuse-UVLO, VinBuck messen. **TPS26631 UVLO** nicht naiv auf GND: internes UVLO kann nahe 15.5V liegen; nach TI-Referenz für niedrige Schwelle UVLO passend an IN_SYS >300k ziehen, unter 10V darf reset. **TPS26631 SHDN Pin 13 absolut max 5.5V**, NICHT direkt an Fahrzeug/ACC anschließen; ACC/RUN-Latch muss als sichere Niedervolt-Logik mit definierter OFF-Stellung gelöst sein. Das ist ein noch offenes implementierungskritisches Gate.

**B – maximal integrierte Schutzlösung und möglicher billigster Endkandidat:** TI TPS26600PWPR als ONE-chip Reverse-polarity and reverse-current-blocking 4.2..60V, 62V **absolute maximum**, 150mOhm total integrated 2x MOSFETs, ILIM bis 2.23A, getrennt OVP-Teiler für guaranteed Betrieb bei 32V (Factory OVP min ca 31V bei entsprechender Variante, daher nicht factory übernehmen), gleiche TI LMR38020/15uH 5V2A-Referenz. Vermeidet externe Schottky, dessen ~1W Wärme und eventuell Supportteile; benötigt 0.1%-OVLO-Teiler und fachlich überprüfte hysteresis mit 32V restart. **P0: nur 4V zwischen nominal 58V an der Buchse und 62V ABS-MAX-Pad**, keine garantierte Live-Freigabe ohne worst-case Connector-zu-Pin-L/C, mehrfacher Pulse, Ripple, parasitäre Peaks und TVS? Große Eingangskondensatoren können Ringing reduzieren, aber keine universelle Spannungsobergrenze schaffen. Geeignet nur bei spezifizierter harter ≤58V-am-IC-pad-Grenze mit Marge und realem Pad-Test. Fixed factory OVLO allein wäre unpassend; externe Schwellen auch bezüglich Eingangslaststrom prüfen.

**C – wirklich anderes Herstellermodul statt diskreter Buck:** gleiche 100V Schottky + TPS26631 mit fixed 33.2..35.4 V OV-Abschaltung, aber statt Buck+Spule ein eingepacktes 5V3A-RECOM **RPH-3.0-CT** (4.5..55V Modul mit interner Spule, Ausgangsspannungsvariante/Pinout laut Herstellerteilnummer noch zu prüfen). Nur +55V module Vin max, daher bereits ein Ausfall der eFuse-Off-Funktion beim 58V-Puls über dem Moduleingangslimit! Hersteller-Derating bei Ta70/85 und all-component-125C nicht mit 5V2A im Fahrzeug gleichsetzen. BGA-/QFN-Hotplate-/Stencil-Handbestückung, Modul ca10x12mm. IC-Referenzpartzahl + Leistungsversion überprüfen. **C nicht für Schaltplan bevorzugt** aufgrund engerer Surge-Reserve und höherer Kosten.

**D – optionale alternative Power-Management-Architektur:** TI LM74930-Q1 4..65V integrierte ideale Diode/OVLO/Überstrom-Steuerung mit EXTERNEN Leistungs-MOSFETs, Shunt, Supportpassives + LMR38020. Keine zwingende eFuse, aber bei REV6 meist mehr Positionen/PCB als A/B; echter Buck58 toleriert, Controller65V max nur 7V Margin; gefährlicher Q-short bleibt F_MAIN-kritisch. Erst bei wirklich besserer Referenzschutzfunktion nachrücken.

### Vergleich in Systemfunktionen

| Funktion | A TPS26631 + Diode | B TPS26600 integriert | C TPS26631 + Modul |
|---|---|---|---|
| +10V-/32V-Betrieb | plausible Bausteinratings; UVLO und Schaltstrom nachzuweisen | plausible Bausteinratings; ILIM & OVP-Teiler auslegen | Regler VIN passend, Modellversion/Bewertung noch offen |
| OVP OFF oberhalb32 bis 36 | integrierter, garantierter fixed 33.2..35.4 rising | präziser externer Teiler zwingend | gleiche TPS26631 fixed OVP |
| Wiederanlauf nach OV | fixed 32.7..35.0 falling: bei stabil 32V fällt eFuse-In nach Diode unter 32V, also **kein garantierter 32V restart**! | external OVLO-hysteresis ebenfalls muss alle 10..32V wieder freigeben | wie A |
| 36V/400ms | eFuse nominal abschaltend; C-ESL-Spitzen zu prüfen | OVLO extern; 62V abs reichlich Reserve zu36 | eFuse nominal OFF |
| 58V/350ms | 60V oper/67V abs eFuse; kleine Spannungsspitzenmarge | 62V abs -> nur4V pad-Marge | 55V module nur bei sicher abschaltendem eFuse |
| -20..60°C 5V2A | Diode Hitze, eFuse, Spule, Buck messtechnisch offen | FET-Ron ~150mOhm, sonst Buck & L; wahrscheinlich thermisch gut | Modulherstellerkurve bei hohen Ta offen |
| RAW0.5A eigenständig gesichert | nur gemeinsame ILIM, separater Lowcost branch current limit für echte 0.5A nötig | gleich | gleich |
| Optionales Backup | FRAM-first, off-isolated PG/FAIL to mainboard; keine Batterie am 5V2A-Pfad | gleich | gleich |
| Bewertung | **bedingt bevorzugt wegen 67V abs statt62V, weniger OVP Passiva** | **geringste Teilezahl wahrscheinlich**, aber Sicherheits-P0 | teurer, 55V Limit/Derating |

**Wichtiger neuer Rückstart-Konflikt in A:** Die TPS26631 fixed OVP *falling maximum* ist **35V**, *falling minimum* ist **32.7V**. Im Worst Case hat das Eingangssignal des eFuse nach einem 100V-Schottky bei Fahrzeugspannung 32.0V höchstens rund31.8..31.9V und erreicht die minimale Freigabeschwelle von **32.7V nicht**. Somit garantiert factory-fixed TPS26631 zwar Abschalten bei 36V und Betrieb bei 32V aus kaltem Einschalten, aber **nicht** automatischen Neustart bei stabilen 32V nach einem OV-Event! Die reduzierte REV6 verlangt genau dies. Ein konfigurierbarer OVP-Teiler ist hierfür auch bei A nötig, mit rising min>32V und rising max≤36V und falling max≤10V? **Nein** falling max≤32V(minus diode-drop) genügt; ohne ausreichend breite Hysterese ggf. Neustart bei 30V und Wiederanlauf nach >32V prüfen. Aus dem Datenblatt die tolerierten OVP Vref rising/falling verwenden und passives Divider/Interpolation vor endgültiger Freigabe nachrechnen. Factory OVP als *ohne Teile bequemer Weg* fällt für garantierten 32V-Restart **aus**. Diese Korrektur ist zentral.

## 2. Hersteller-5V-/2A-Referenz (LMR38020-Q1)

TI Referenz in LMR38020-Q1 Datenblatt, 5V/2A, fsw 400kHz:
- L = **15uH**, Kandidat Bourns SRP7050TA-150M AEC-Q200, 7.3x6.6x5.0mm, Irated3.5A / Isat6A / DCRmax92mOhm, -40..150°C; Alternative Wuerth 7443251600 16uH, größer/teurer, weniger DCR.
- C_OUT: **3x22uF nominal 16V** (z.B. KEMET C1210C226K4RACTU 1210), Ceff unter 5V/+60 prüfen; TI fordert nach realer DC-Bias-Kurve und Transientenstabilität mindestens wirksames C.
- C_IN bei Buck mindestens **4.7uF +100nF** laut Hersteller; Kandidat 2–3x KEMET C1210C225K1RACAUTO 2.2uF100V (Ceff bei VIN=32V kritisch, daher Nenn-4.4uF ≠ garantierte effektive4.7uF!), HF C1206C104K1RACAUTO 0.1uF100V; entweder höherwertige 4.7uF100V AEC-Kondensator-MPN auswählen oder EVM Ceff-Derating verifizieren.
- C_BOOT 100nF, 16V; R_FBupper 100k, R_FBlower 24.9k (5.0V), R_RT 64.9k for 400kHz (Datenblatt Anwendungsbeispiel), R_EN/5V PG Pullup nach gewähltem Latch/Sensorstatus.
- Integrierter 80V Buck toleriert im Fehlerfall potentiell 58V Eingang, aber ist damit NICHT automatisch für 58V-Dauervollast freigegeben; eFuse muss absperren.
- Für T_A=+60°C und POUT10W: wenn η85% angenommen, Verlust=1.765W über Buck-IC und L. Selbst wenn all diese Verluste im IC wären, mit θJA=45K/W -> Tj ~139°C, unter max150°C aber ohne Margin. **η und tatsächliches θJA/PCB/Spulenerwärmung bei VIN32 und 2A MESSEN**. Kein 2A-Thermiknachweis bisher.
- Niederspannung und gemeinsamer Strom: η85% bei VIN10, angenommener Schottky0.5V und eFuse0.06V => buck input ~9.44V -> 10/0.85/9.44 =1.247A + RAW0.5A = **1.747A**. Ein 2.4A nominelles eFuse ILIM hat 0.65A Headroom für normale Last, aber Startup/Bulk-C und 2x/3x faults separat messen. Diode P approximately 0.5V*1.747A=0.87W, mit Vf0.6 ->1.05W; Hersteller-PCB θ/Tj und AEC-Variante prüfen.

## 3. Dynamische 58V-Pad-Maxima und Fehlerfälle

- **Eingangsbedingung der REV6:** max58V gilt an Gerätebuchse *inklusive externem Ringing*, nicht automatisch an eFuse-Pad hinter Kabel-/PCB-/Stecker-/Sicherungsinduktivität, L/C und reverse diode. Bei steiler 58V-Flanke (nicht allein 350ms Mittelwert) Pad-Ringing per transient/scope messen, dass TPS26631 VIN_SYS/VIN <= 60V recommended und <67V abs in all states, TPS26600 <62V abs in all states, LMR38020 <80V oper and package VSW/BOOT ratings, und Modul55V nicht überschritten werden. Ein Kondensator reduziert Ringing, garantiert ohne L/R keine Maximalwerte.
- eFuse OVP turnoff delay TPS26631 **max14us**, was für eine 58V rise in µs **nicht** als bevor-58V Schutzbeleg zählt. Buck VIN bis80V, aber RAW ohne getrennte Sperre kann hochgehen. Eingangskondensator-Spannungsratings100V; 58V/350ms stress ESR/hot leakage.
- Ein eFuse **D-S short** umgeht OVP -> nachfolgender LMR Buck max80V kann bei58V zwar die Spannung vertragen, ist aber unter 58V möglicherweise weiterhin ON, und RAW-Port erhält bis58V. **RAW als für 32V ausgelegter Sensorpfad ohne weitere Trennung darf diese Fehlerspannung nicht als sicher aushalten müssen**, Fault-Matrix mit F_MAIN und FET-SOA.
- Schottky D-S short: Reverse -32V erreicht TPS26631 ohne interne Sperre. Externe Fahrzeug-Sicherung kann einen rein verpolten stromarmen Fehler nicht garantieren. Safe-Fail der seriellen Diode mit spezifizierter TVS/Leitung und unterliegender Elektronik zu prüfen. Schottky open: safe no power. Zener/TVS open/short abhängig ob für Pad-58V-Schutz eingesetzt; nicht als immer OPEN unterstellen.
- F_MAIN austauschbar auf Fahrzeugseite. Sicherung muss Kabel schützen; bei zentral geklemmtem 58V/350ms sind zulässige **Spannungs- und DC-Trennwerte** sowie I²t noch konkret zu dimensionieren. Typische 32V ATO-Blades nicht automatisch als 58V-Trenner ansehen.
- OFF: TPS26631 SHDN **LOW** hat niedrige Stromaufnahme und ist auszuwerten, SHDN floating biases ON and may exceed PWR50 BAT-OFF<1mA. Separate ACC/RUN-Latch/PWR_FAIL und USB disconnect. SHDN pin absmax5.5V -> nie BAT30 direkt verbinden.
- PWR_FAIL: bevorzugt fail-HIGH auf LOGIC-domain pullup, TripPower PG/FLT Open Drain active LOW with proper isolation and no BAT/USB/RTC-cell leakage. PG darf nur status sein, niemals garantierte Frühwarnung bei hart gezogenem M8. FRAM vorher transaktionssicher speichern; optional SD shutdown nur mit unabhängig gemessener Backupenergie.

## 4. Einkauf/Lieferbarkeit/Handbestückung und Kosten

Echte Hersteller-/Distributor-Preisbelege sind der separaten CSV REV6_COTS_VENDOR_BOM_SCOPE_2026-10-15.csv zugeordnet, Netto-Preise Einheit bei 1/10/100, Zeitpunkt 2026-10-15. Die Listen enthalten **alle absehbaren Bauteilgruppen**, auch noch nicht dimensionierte als TBD und ohne erfundenen Nullpreis.

- TPS26631PWPR Mouser DE **3.89/2.96/2.46 EUR**; Vorrat nach Anzeige 57 sofort, 100 Stück nicht voll durch diese Quelle.
- TPS26600PWPR Mouser EU **3.42/2.56/2.12 EUR**, größere Liefermenge verfügbar, aber 62V abs margin.
- LMR38020SQDDARQ1 Mouser DE **3.92/2.98/2.49 EUR**; Lieferbestand distributorenabhängig, neu bestätigen; DigiKey DE zero stock in aktueller Suche.
- SDT5A100SB-13 Diodes 100V 5A Schottky SMB Mouser DE **0.791/0.495/0.321 EUR**; alternativ automotive STPST5H100SBY **1.25/0.613/0.537 EUR**.
- Bourns SRP7050TA-150M 15uH AEC-Q200 DigiKey DE **0.95/0.783/0.6435 EUR**.
- KEMET C1210C225K1RACAUTO 2.2uF100V 1210 X7R AEC-Q200 Mouser **0.628/0.417/0.285 EUR** je.
- C1206C104K1RACAUTO 100nF100V Mouser **0.224/0.101/0.075** je.
- C1210C226K4RACTU 22uF16V X7R DigiKey **0.70/0.439/0.3065** je.
- Modul RPH-3.0-CT Mouser DE **7.89/7.76/7.06** (Temperature-Derating, Module55V danger).

Die berechenbaren **TEILSUMMEN** ohne alle Widerstände/EN/PWR_FAIL/RAW-Schutz/Stecker/F_MAIN/PCB/Versand/Steuer:
- Kandidat A incl 1x diode, TPS26631, LMR38020, 1x L, **2x** 100V 2.2u, 1x HF 100n, **3x**22u: **13.131/9.470/7.479 EUR** (1/10/100). Mindestens 9 belegte Bestückpositionen (1+1+1+1+2+1+3=10 – tatsächlich 10 Positionen!).
- B (TPS26600 instead of diode+TPS26631, same L/C parts): **11.870/8.575/6.818 EUR** (9 belegte Positionen).
- C (TPS26631+diode+RPH module, nominal 2x HF100V MLCC TBD, no buck discrete): **12.571/11.215/9.841 EUR** for only three priced active positions (diode+eFuse+module), no cap; no valid complete system.
These are floor sums only. Actual full BOM count/PCB area cannot be frozen until SHDN/ACC, RAW branch current limit, OVP reenable and VIN ripple resolved.

Physical component package/body only (not board area): LMR HSOIC8 4.9x6=29.4mm², TPS26631 HTSSOP20 4.4x6.5 ≈28.6mm², Schottky SMB ~4.6x3.6=16.6mm², Bourns inductor7.3x6.6=48.2mm²; all 1210 capacitors3.2x2.5=8mm² and 1206 3.2x1.6=5.1mm², plus copper thermal/spacing/connectors. Module body 10x12=120mm² and still frontend/thermals. Real PCB requires placement/DRC and M8 connector footprint so no invented cm² whole-board number. Hand-assembled stencil compatible, PWP exposed pads require hotplate/reflow access, capacitors 1206/1210 and SMB are manual place, inductor7mm easy.

REV5 historical standalone has 57 AUTO / 58 RUN positions for MUCH tougher 200V/125C; **not apples-to-apples** compare without exact interface scope. REV6 removes huge HV-FET/Zener network, RAW goal halves and backup FRAM-first; reduction plausible, actual new position count not proven.

## 5. Decision and blocked native KiCad gate

**Selection conditional:** TPS26631 + diode + TI LMR38020 has best present **safety-margin vs cost balance** over TPS26600 (+5V extra absolute margin, fixed OVP near needed cutoff) and RPH module (55V buck VIN). **BUT** the TPS26631 fixed OVP return at 32V after OV can fail: its falling minimum 32.7V > 32V, worse after diode. This makes fixed-OVP concept **NOT sufficient for REV6-R6-RESTART-08**. Its required additional OVLO divider and exact manufacturer thresholds must be proven to guarantee OFF >32..36 and ON after OV by32. Similar verification needed for TPS26600 and full 58V pad stress. ACC/RUN/SHDN circuit needs separate vendor-qualified tiny HV tolerant IC/logic or verified resistor/transistor input network; pin13 must never exceed5.5V. RAW branch and mainboard interface not frozen.

**Thus no genuine complete, manufacturer-verified schematic and native ERC can currently be honestly delivered.** Better not generate a false electrical diagram missing essential F_MAIN/ACC/UVLO/PWR_FAIL gates. The enclosed reproducible screening test and BOM-scope report are technical output, not KiCad or ISO qualification.

### Next objectively verifiable gate

(1) Derive TPS26631 and TPS26600 EXTERNAL OVP resistor tolerances (guaranteed Vref, hysteresis) that satisfy 32V ON / 36V OFF / restart ≤32V at actual eFuse pad including diode forward drop and leakage. (2) Retrieve TI reference circuit for SHDN ACC+MCU RUN with VIN32 and VIN58, 5.5V pin ABS, <1mA parked. (3) Specify Rsource/L and measure TPS26600/31 pad VIN at 58V/350ms (ringing), short-fault RAW, vehicle fuse DC rating. (4) Set full real MPNs/footprints, perform PCB thermal and transient checks, then standalone KiCad10 complete drawing + ERC/netlist CI + PCB DRC. No free-running old 200V/125C design assumptions.


## 6. REV6 Actual analytical divider audit, prices and CI reconciliation (15.10.2026)

**Important override of earlier preliminary statements:** TPS26631 `OVP=GND` factory thresholds rising 33.2–35.4V, falling **32.7–35.0V**: after an OV event it cannot be guaranteed to restart at battery32V, particularly behind a forward Schottky. Consequently the minimal fixed-OVP A variant is invalid for R6-RESTART-08; a two-resistor external OVP divider is necessary. This is *not* a reason to reintroduce old 200V parts.

Manufacturer-specified adjustable OVP comparator thresholds with temperature range, static resistor extremes and maximum signed pin leakage, computed in own `rev6_protection_gates.py`:

| Candidate 0.1% resistor set | Rise MIN at device pin | Rise MAX at device pin | Fall MAX at device pin | Recommended start/stop interpretation |
|---|---:|---:|---:|---|
| A TPS26631 100k upper / 3.78k lower | **32.210V** | **33.685V** | **31.649V** | VIN_TPS=VIN_M8−VfSchottky. At 32V/normal full-load eFuse VIN<32, so remains ON once activated. At 32V after OV, requires Schottky Vf in near-zero-load recovery <0.351V to reach >31.649V; **must qualify Vf(T/I)**. Rising+Schottky Vf remains under36V even with ~1V drop. |
| B TPS26600 100k upper / 3.74k lower | **32.381V** | **34.055V** | **31.275V** | Integrated reverse MOSFET, no series diode; static 32V restart and 36V cutoff works with 0.1% R. 58V pad max62V abs leaves only4V unproven dynamic margin. |

Input leakage maxima A±150nA, B±100nA from actual TI datasheets; 0.1% resistor tolerance. Full integrated UVLO and **EN/SHDN** logic, 58V input dynamics and 60C thermal proof not yet included in a manufacturing design. 100k/3.78k 32V divider draws **308µA**, challenging but not automatically breaching REV6 BAT+ OFF<1mA; when combined with ACC-based leakage, mode current, PG pullup, mainboard OFF budget <0.5mA is not yet guaranteed. A/B resistor candidates do not constitute release MPNs.

**Checked scope BOM, not fully purchasable:** `REV6_COTS_VENDOR_BOM_SCOPE_2026-10-15.csv` includes the M8+board connector, external automotive F_MAIN+holder, ACC logic, PWR_FAIL mainboard supervisor, USB OR-ing, passives and optional separate RAW-eFuse. No missing MPN gets a free cost. The actual confirmed *partial* totals from CI are:

| Candidate | REQUIRED positions in architectural scope (on TripPower + mainboard + vehicle) | With priced MPN | TBD positions | Price floor EUR net /unit at 1 /10 /100 |
|---|---:|---:|---:|---|
| A TPS26631+100V Schottky+LMR80 | 35 | 12 | 23 | **14.387 / 10.304 / 8.049** |
| B TPS26600 integral reverse+LMR80 | 34 | 11 | 23 | **13.126 / 9.409 / 7.388** |
| C TPS26631+Schottky+RECOM module | 23 | 4 | 19 | **13.199 / 11.632 / 10.126** |

These are **lower bounds** for a partially priced *system concept*, not final complete BOM prices, and the 35/34/23 are only provisional scope-position quantities, not counted KiCad placements. All line items have quantity/MPN-or-explicit-TBD/footprint-candidate/price-source for three volume tiers, incl optional RAW branch shown separately, and the external hardware allocated to relevant board/harness. Need manufacturer-specified fixed resistor MPNs and PCB layout before accurate whole-board area.

**Real CI:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38812555462 = success, 13/13 actual Python arithmetic tests plus CSV consistency. Native KiCad10 ERC/Netlist **NOT EXECUTED**, no released REV6 schematic yet, no 58V transient /60°C 2A hardware test. The major P0 blockers are still actual pad peak at eFuse (60V OPER/67V ABS A, 62V ABS B), tolerated 32V restart after diode, +60°C thermal and complete ACC/RUN/RAW safe state. The 58V clamp must be objectively ensured at the M8 port; 200V-test-A installations remain **prohibited** without externally qualified input protection.
