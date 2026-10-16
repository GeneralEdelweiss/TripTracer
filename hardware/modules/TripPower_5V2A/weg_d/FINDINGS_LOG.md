# TripPower Weg D – fortlaufendes Forschungsprotokoll

**Aktiver Scope seit REV6 (16.10.2026):** einfachste wirtschaftlich und elektrisch qualifizierbare 10–32V-/zentral geklemmte 58V-Eingangsschutzarchitektur; 200V/350ms und +125°C sind **nur historische Archivforschung**. F_MAIN und Halter stets off-board, keine Schmelzsicherung oder Einmal-Thermosicherung auf TripPower. Änderungen ausschließlich auf design/trippower-d-load-dump.

## 2026-10-16 – ROUND 10: offizielles TI-Modell versucht, belastbare Eingangsgrenzen getrennt

**[ENTSCHEID]** TPS26631 Weg A bleibt kleinste **Laborplattform**, keine Serien-/Fahrzeugfreigabe. Hauptbericht [Round10 58V Eingangsmodell und Messplan](WEG_D_ROUND10_TPS26631_VENDOR_MODEL_58V_EVIDENCE_2026-10-16.md), [29 Pin-/Pad-Messpunkte](ROUND10_58V_PAD_STRESS_MATRIX_2026-10-16.csv), [ausgeführtes passives TI-Eq14/RLC-Modell](tps26631_ti_eq14_passive_step.py) und [Python-Tests](test_tps26631_ti_eq14_passive_step.py).

**[SPICE ZUGRIFFSSTATUS]** TI TPS2663 PSpice Rev A SLVMD03A.ZIP offiziell vorhanden. Web-Download als application/zip nicht textlesbar; Container-Download scheitert, curl(6) kann www.ti.com nicht auflösen; ngspice/Xyce/PSpice/ltspice nicht installiert. **Kein offizielles TI-PSpice-Modell ausgeführt, keine konkrete Kompatibilitätsdiagnose möglich!** Später ZIP-SHA256, Simulatorversion, Subcircuit-Pinmapping, Modell-Log und Kurvendaten sichern.

**[HERSTELLER UNABHÄNGIGER GEGENCHECK]** TI Rev G §9.5.1 Eq14 Vpeak≈VIN+Iload√(L/C). Hypothetisch58V+I1.75A,L0.8µH,Ceff0.5µF≈60.21V; I3A≈61.79V. L5µH,I3A,Ceff0.5µF≈67.49V. Ceff für60V in dieser idealisierten Rechnung0.613µF /1.8µF /11.25µF. **Nicht** behaupten, dass bei58V tatsächlich 3A gleichzeitig abgeschaltet werden: OVP könnte viel früher wirken.

**[PASSIV-FLANKENMODELL LOKAL AUSGEFÜHRT]** Separates 2-state RK4 RLC mit Eingangsstufe bei eFuse-OFF (KEINE TI-Makromodellrechnung). M8-Bezug: Quelle ist tatsächliche maximal58V M8-Spannung, L nur ab M8 nach Q201/PCB. Lokale L0.05µH, R0.08Ω,Ceff0.5µF, Rise1µs =>59.83V; Rise0.2µs =>74.28V. Insgesamt **288 angenommene** Parameterfälle,139>60V und88≥67V, NICHT Statistik oder Messung. Vor-M8-Kabelinduktivität nicht als lokal L beim58V-M8-Quellbezug mischen. Bisheriges Round9 60/144 ist ein anderes, internes Lastabschaltmodell.

**[NEUER A-STAND]** Aktuelles A-BOM R202=12.0kΩ ERA-8AEB123V **jetzt identisch** KiCad-Blatt. L101 aktuell Bourns SRP7050TA-150M 15µH / Isat6A. C201/C202 je1µF100V KEMET, Buck-C101/C108 je4.7µF100V AVX; DC-Bias-Ceff weiterhin unbekannt. **Bleibender analoge P0:** TI §9.4 empfiehlt IN_SYS–UVLO mindestens300kΩ, A-R201 ist100k. OVP falling des aktuellen100k/12k/4.22k Teilers etwa30.02..31.67V; garantierter Wiederanlauf nach 58→32V weiter **nicht belegt**.

**[MESS-/SICHERHEITSGATE]** 29 kritische Pin-/FET-/MLCC-Domänen getrennt messen; U201 IN/IN_SYS 60V empfohlen und67V absolut, niedrige OVP/DRV/BGATE-Grenzen einzeln, LMR VIN80V empfohlen. M8-Fall am echten Stecker max58V inkl Ringing, Quelle10/32/36/58, Kabel-R/L, 36V400ms, 58V350ms, 10V-Volllast, Q201/U201-Short, +60C 2A/+85C safe-OFF, FRAM/USB/RAW-Fehler. Nur extern F_MAIN/Halter, keine Platinen-Schmelzsicherung/PPTC-Pflicht. **Kein echter Laborversuch.** CI-Workflow mit neuen Stdlib-Tests und JSON-Ausgabe ergänzt, noch kein bestätigter grüner Run.

---

## 2026-10-16 – ROUND 9: TPS26631 58V/350ms RLC-Eingangsmodell und echte A-Schaltplanprüfung

**[KONDITIONALES ENTSCHEID / NO HARDWARE RELEASE]** Weg A TPS26631 bleibt die kleine REV6-Prüf-/Laborarchitektur, nicht als 58V-Serienhardware bereits qualifiziert. Die 58V-Mess-/Eingangskondensator-/MOSFET-/OVP-Anforderungen werden präzise durch [Round9 Bericht](WEG_D_ROUND9_TPS26631_58V_RLC_EVIDENCE_2026-10-16.md), [reproduzierbares dynamisches Netzwerk](tps26631_58v_network.py), [neun Regressionstests](test_tps26631_58v_network.py) und [SPICE-RLC-Template ausdrücklich unvalidiert](tps26631_input_sensitivity_unvalidated.cir) eingegrenzt. **Keine neue LTC4368-Schaltung, keine große TVS, keine Schmelzsicherung auf TripPower.**

**[GITHUB QUELLE / REALE A-SCHALTPLÄNE]** Auf design/trippower-a direkt 01_TPS26631_REV6.kicad_sch, 02_5V_LMR38020_REV6.kicad_sch und 25-part CSV gelesen. U201 TPS26631, Q201 SQM100N10-10_GE3 100V reverse, Q202 BSS138; C201 1µF100V an VIN_FUSED/IN_SYS **hinter** Reverse-Q201, C202 1µF100V OUT, Buck C101+C108 je4,7µF100V vor dem LMR. Alle DC-biased Ceff unbekannt. **Drift:** gezeichnet **R201100k / R20212,0k MPN ERA-8AEB123V / R2034,22k**; gegebene A-BOM führt **R202 12,4k MPN RT1206BRD0712K4L**. Nochmals nativ synchronisieren, keine BOM/Zener-/Teilerfreigabe.

**[ANALOGER P0 BLOCKER]** Hersteller-OVP Rising1,176..1,224V; Falling1,09..1,15V. Gezeichneter 100k+12,0k+4,22k-Teiler -> OV Rising grob32,39..33,71V und Falling30,02..31,67V (ohne Toleranz/Leckstrom). **Nach 58→32V ist ein garantierter automatischer Wiederanlauf nicht möglich**. Allgemeines extremes Teilerfenster zum gleichzeitig spätestens36V OFF und exakt32V ON: k_min≥0,034000, k_max<0,0340625, 0,184% Gesamtfenster **vor** Widerstandstoleranzen, Temperatur und Pinleck ±150nA. 0,1%-Widerstände allein können zu ungenau sein. Ebenfalls **TI RevG §9.4: mindestens 300k Widerstand über IN_SYS–UVLO bei Reverse-Q201 empfohlen**, A-R201 ist100k direkt IN_SYS→UVLO. Dies erfordert eine eigene gezielte Herstelleranpassung, nicht bloß mehr Eingangskapazität.

**[HERSTELLER / t_OFF]** TPS26631 VIN normalmax60V/ABS67V 350ms; 75V nur10ms@25°C; relevante BGATE-GND81, BGATE-IN_SYS14, DRV-GND72, DRV-IN_SYS20 und niedrige OVP/SHDN/ILIM/dVdT-Pinmax. TI RevG 8,5–14µs OV-Pin→FLT ist **keine** universale MOSFET-GATE-Aus-Bedingung! TI bietet originales TPS2663 PSpice SLVMD03A ZIP auf https://www.ti.com/product/TPS2663 an. Dieses Original-Makromodell wurde **nicht** ausgeführt. Kein ngspice installiert; SPICE-Template ist nicht validiert und enthält ausdrücklich ideale eFuse-Approximation.

**[REDUZIERTE DYNAMISCHE RECHNUNG]** 4-State scipy RLC-Netzwerk (Source R0,25Ω/CableR0,1Ω/L0,8µH, Q201-R0,01Ω, C201eff0,5µF, C202eff0,5µF, LMR-inputCeff3µF, ESR/ESL pauschal, 32→58V rise20µs, OV-delay14µs +2µs fall) ergibt typisch im MODELL V_IN_SYS_peak~59,06V, OUT+LMR~40,9V. **144 Sensitivitätsfälle** Lcable0,2/1/3/5µH × C201eff0,2/0,5/1µF × delay2/14/100µs × buck5/10W × RAW0/0,5A: **60 über60V IN_SYS**, **2 ≥67V IN_SYS**; Modellexempel L5µH/C201eff0,5µF/delay14µs/buck10W/RAW0,5A ≈67,26V. Diese **Szenariozahlen sind keine garantierten Bauteilwerte, keine statistische Ausfallwahrscheinlichkeit und keine gemessenen Fahrzeugwerte**. Weitere Fälle Start10V, 32→36, 58→32, short10/32/58, unplug, Reverse-Q201 D-S-SHORT und interner eFuse-D-S-SHORT im Modell. Q201-Drain aus R*I+L*dI/dt ist nur approximiert; BGATE/DRV/OVP/GND-ESD/Coss/SW nicht simulierbar. Ohne gemessenes R/L/Ceff kein lokaler Vmax.

**[LABOR PLAN]** Round9 §7: professionell strom-/energiebegrenzte 58V/350ms transient source, max5A≈101,5J / max10A≈203J bei 350ms Rechteck als grobe obere Quellenergie; abgeschirmt/Not-AUS, externer sicherer Fuse-Halter (NIE TripPower), kurze+lange vermessene M8-Leitungen, differential probes≥100MHz, Scope≥100MHz/≥500MS/s, DC-bandbreitefähige Stromsonde. M8, Q201 D/S/G, TPS IN1–3/IN_SYS6/OUT18–20/GATE4/DRV5/OVP8/UVLO7/SHDN13/GND9, C201/202 pad, LMR VIN/SW, RAW/USB/PWR_FAIL temperatur- und Kurzschlusssensitiv messen. Exakte 32V-Wiederkehr, 10V/2A-Start, 36V400ms, 58V350ms, L/C/ESR/wave/10x Puls, +60 Vollast/+85 safe-OFF, MOSFET-/eFuse-SHORT und Kabel-Energie. **Realtest nie durchgeführt**, daher ausdrückliches No-Go für Fahrzeug/PCB-Freigabe.

**[MINIMALMASSNAHMEN]** Hersteller-OV-Recovery und 300k/MPN-Drift zuerst bereinigen; danach lokale 100V-Automotive-MLCC-Ceff/ESR-Daten @58V, kurze reverse-FET/eFuse C201-Schleife, HF-Messung und ggf RC-Dämpfung. Keine SMBJ58A als angeblicher 67V-IC-Schützer; ihre maximale Klemmspannung bei spez. Puls liegt deutlich höher. Erst nach gemessenem und nicht dämpfbarem VIN_PAD>60V gezielt LTC4368-2 (VIN100, VOUT/SENSE80V, MOSFET SOA) neu bewerten. Keine PPTC ohne Nachweis. FRAM-first und USB/RTC-Backfeed bleiben TripTracer/Interface-Gate.

**[CI-Status]** Workflow .github/workflows/trippower-d-rev6-analysis.yml mit scipy/numpy-Tests/MATRIX-JSON-Upload aktualisiert; keine aus diesem Schritt belegte erfolgreiche GitHub-Actions-Ausführung, weder native KiCad10-ERC/DRC noch Mess-/PSPICE-Qualifikation.

---

## 2026-10-16 – ROUND 8: TPS26631/TPS26600/LTC4368, sichere Einsparung statt 200V-Überbau

**[Managementdaten verifiziert]** Neu gelesen: AGENTS.md, docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md, HARDWARE_REQUIREMENTS PWR-44–56 und docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md, alter Weg-D-REV6-Bericht/Log; Weg A KiCad/BOM/CI auf design/trippower-a und Weg B Hersteller-FMAIN+58V-Halter auf design/trippower-b.

**[Hauptdokument]** [Round8 – technischer Dreiwegevergleich/FMEA/Abnahmegates](WEG_D_REV6_ROUND8_TPS26631_TPS26600_LTC4368_DECISION_2026-10-16.md); [Round8 – Kosten/Bestückpositionsmatrix mit off-board-scope](WEG_D_REV6_ROUND8_BOM_AND_COST_2026-10-16.md); [CSV aller tatsächlichen Weg-A-KiCad-Positionen und Ersatz-Planpositionen](WEG_D_REV6_ROUND8_BOM_MATRIX_2026-10-16.csv); [reproduzierbare Rechnungen](rev6_round8_compare.py) und [arithmetische Unit-Tests](test_rev6_round8.py).

**[HERSTELLER-PINLIMITS]** TI TPS26631 IN_SYS/IN/OUT abs67V für350ms, max60V operating; 75V **nur 10ms @25°C**, B_GATE max81V und BGATE−IN_SYS max14V, DRV72V und DRV−IN_SYS20V; Niedervolt-OVP/SHDN/ILIM/PLIM/MODE/dVdT max5.5V. TPS26600 IN/IN–OUT abs62V für350ms, 70V nur10ms@25°C, OVP/ILIM/dVdT/MODE etc max5V gegen RTN; 60V operating. LTC4368 VIN2.5..60V operating, 100V protection; VOUT/SENSE abs80V, OV20V, RETRY5V, UV/SHDN/FAULT80V; FET VDS separat! Quellen https://www.ti.com/lit/ds/symlink/tps2663.pdf , https://www.ti.com/lit/ds/symlink/tps2660.pdf , https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4368.pdf . Nominale positive +58V Reserve zu VIN-ABS 9/4/42V, **aber 42V bei LTC gilt NUR VIN**; an LTC VOUT/SENSE gelten80V.

**[NEUER TPS26600-ENTSCHEID]** TPS26600PWPR internes back-to-back 150mΩ 16-HTSSOP, spart Weg-A 100V-reverse FET Q201 und Gate-Helfer Q202 (provisorisch A25→B23 Positionen vor gemeinsamen Temperatur-/RAW-Blocks), aber R_ILIM max2.23A (am 5.36k HerstellerTest R_trip min2.11A), and VIN abs62V. Beispiel (5V2A, eta=.8,Vin10, RAW.5A)=I1.75A: R_on typ150mΩ→0.459W Tj, typ ΘJA38.6→+17.7K zu ambient (ohne Pcb-/hot Rds). Cold/start/2A+RAW Margin nur~0.36A zum min2.11A beim max-current-setting; nicht automatisch sichere Inrush/SD-Pulsfolge. **Factory-OVP 31..34V** würde bereits bei 31..32V normal Abschalten → **programmierbarer externer OVP-Teiler Pflicht**. TI typisch6µs OVP-to-FLT kein garantierter Last-OFF. **NO-GO als V1-Leitarchitektur ohne maximal lokal <=60V mit Margin und +60°C-Lastnachweis**; ohne clamp unter62V keine reale Mehrsicherheit trotz zwei Teilen weniger.

**[TPS26631 / WEG A]** native 25 Teile, 0 KiCad-10 ERC-Verstöße nach GitHub Actions 38814076115 (aus docs/TRIPPOWER_A_REV6_NATIVE_ERC_BOM_CI_2026-10-15.md). Reverse-SQM100N10-10_GE3 plus BSS138, U201 TPS26631PWPR 31mΩ, 6A-Familie, A R_ILIM6.04k ca2.98A, VIN abs67. Silicon-FET-on @1.75A typ ~0.095W (kein 60°C-Thermikfreigabe). OVP per A divider statisch 32.34..35.86V, reale OV-fall-Recovery/150nA-Leck/Fet-timing noch nicht vollständig. **Bester kosten-/aufwandsoptimierter P0-TESTPFAD** unter streng gemessenem local VIN<=60V mit Maximalspur, keine Fahrzeugfreigabe.

**[LTC4368]** Automotive #W mit 100V-VIN-Fault hat echten Sicherheits-Headroom bei lokalem transienten Overshoot; zwei externe 100V N-FETs + Shunt und vier 0.1%-R plus Gate passives. LTC OV-Gate fast2..6µs mit2.2nF, nicht garantierte FET-VDS-/CIN-Schaltwelle; 60V operating auch hier. Shunt15mΩ Itrip normal2.67..4A, bei VOUT≈0 etwa2.0..4.67A (separat die ±70mV-Grenze). Beispiel bei 1.75A zwei MOSFETs je6mΩ typ -> Ptotal0.03675W, Shunt 0.046W. Entscheidend bleiben Einschalt-SOA/kurzschlussbedingte Pulsenergie bei+60°C, GATE Qg, Rückspeisung; zwei Common-Source MOSFETs **keine doppelt unabhängige Sperre gegen Q1 D-S-Kurzschluss** (andere Bodydiode kann VIN→OUT treiben). **KONDITIONALER BACKUP-KANDIDAT** nur wenn 58V-Ringing die TPS-Grenze gefährdet und die LTC-80V-Ausgangsdomäne/100V-FETs geprüft sind. Nicht automatisch neues KiCad, kein nachgewiesener Kostenvorteil.

**[KLEINE TVS UND FUSES]** Keine TVS blind in REV6-Main-BOM. SMBJ58A Vclamp93.6V bei spez. Puls schützt nicht die 62-/67V-ICs; TI TVS5800 max75V bei25A/8–20µs auch nicht die 62/67V-Pins. TVS-OPEN/SHORT nur falls real bestückt analysieren. **Auf TripPower 0 Schmelzsicherungen, 0 Halter, 0 Einmal-SMD-/Thermofuses, 0 PPTCs im Leitkonzept.** Externe Fahrzeug-Sicherung 0997004.WXN (4A 58VDC) und 0FHM0001ZXJ-RED (58VDC-Halter, B Round7) **NUR Harness/System**, mit tatsächlicher V_breaker/Temp/total-clearing/Fuse-I²t und Kabel-/Kontaktprüfung; keine Garantie aus 58V Nennwert. Optionale Sicherung auf großer TripTracer Hauptplatine schützt nicht das Kabel.

**[BOM GESAMTANFORDERUNGEN]** CSV enthält alle25 Weg-A-Teile, Variantenfrontends8 vs10 vs13 und gemeinsamen15 Buck/PG, plus fehlende Temperatur-/RAW-/mechanischen Pflichtteile als UNBEKANNT, Hauptplatinen-/Fahrzeugkosten OFFBOARD. Real bepreiste Halbleiterblöcke (EUR net pro Stück 1/10/100): **TPS31+reverse+helper7.942/5.556/4.3091**, **TPS00 3.440/2.594/2.1495**, **LTC4368+2provisional FET13.430/9.700/7.6412** ohne Kelvin-Shunt. Preisbeleg 14/25 A-Teile, EOL 3x Murata Ausgangs-MLCCs; **KEIN** vollständig bepreister fertigungsfähiger Variantenpreis. Kein Phantom-0-Euro für Temperatur, RAW, USB, Source-F_MAIN.

**[FAULT/FRAM FIRST]** F_MAIN wird bei schädlichem 0.3-1A Teilfehler ggf. nicht auslösen; Temperatur-Open/Short+85°C-Gesamtschutz und RAW0.5A-Ast dürfen nicht fehlen. PWR_FAIL fail-high/hoch-Z nur wenn main5V nutzbar und passende separate Logik, RTC-Primärzelle nicht dauerhaft leeren. M8-Abziehen ohne garantierte Warnzeit; FRAM zuvor atomar sichern, SD-Recovery danach. USB darf niemals über interne FET-Bodydiode/ESD nach BAT/RAW zurückspeisen.

**[CI NACHWEISKLASSE]** Workflow `.github/workflows/trippower-d-rev6-analysis.yml` auf Weg-D-Branch für arithmetische Python3.11-Testfälle hinzugefügt; damit werden selbst bei grünem CI **KEINE** nativen KiCad-10-ERC/Netlist-/PCB-DRC-, Hot-SOA- oder Labor-Ergebnisse bewiesen. Ein erfolgreicher Action-Run wurde in diesem Chat **noch nicht unabhängig verifiziert**.

**[NO-GO/GO KONKRET]** TPS26600 als Standard **NO-GO** bis extrem kleine nachgewiesene Spitzenreserve/Strombudget; LTC4368 **NO-GO für unbegründeten Extra-KiCad-Entwurf**, bedingtes Safety-Upgrade bei tatsächlich gefährlichem Overshoot. TPS26631 Weg A **P0-Labortest weiterführen**; weder A ERC0 noch dieses Dokument ist eine 58V/350ms/85°C/RAW/ISO-Freigabe. Nächstes einziges technisches Gate: realer 58V/350ms-M8-Kabel-/Ein-/Ausschalt-Peak auf ALLEN Pins und 10V/2A+RAW/T60/C/RLC zusammen, Sicherungskoordination extern. Bei Peak>60V operativ/67V ABS aus TPS31 erst LTC-Alternative mit Hersteller-Fet-SOA, VOUT80 und neuen Vollkosten qualifizieren.

---

## 2026-10-15 – REV6, Nachtrag: 58-V-begrenzter Eingang statt 200-V-Test-A

**[ANFORDERUNGSWECHSEL – verbindlich]** docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md hat Vorrang. 10..32V, OV-OFF >32..≤36, 36V/400ms, nur **58V/350ms am M8-Connector nach Fahrzeugklemme**, Ta -20..70°C, 5V/2A bis +60°C, sichere Abschaltung +85°C, RAW0.5A, BAT-OFF<1mA (Ziel0.5mA), FRAM-first und einfache fail-high PG-Schnittstelle. Früherer 200V/125°C-STOP ist **HISTORISCH** für V1, aber die Fehlermethodik bleibt relevant. Die 200V-Schutzstufe bleibt optionale externe Nachrüstung, nicht V1-BOM.

**[ARCHITEKTURMATRIX, HERSTELLER]** V1 80V-LMR38020-Buck ohne eigenständige OVP/Verpol/RAW-OCP -> **NO-GO als vollständiger REV6-Schutz**. V2 TI TPS26631 plus kleine SMBJ58A -> **NO-GO mangels lokaler Max-Padbeweis**: eFuse VIN 60V operating/67V abs, TVS max93.6V bei geprüftem Puls, kein sicheres 67V-Clamp. V3 **ADI LTC4368HMS-2#WPBF** 60V Betrieb/100V VIN fault, separate abs VOUT/SENSE80V, 2 externe antiparallele 100V-MOSFETs, OV/UV/OCP/Rückstrom -> **KONDITIONALER ARCHITEKTUR-GO**, nicht freigegebene Leiterplatte. ADI-24V-Herstellerreferenz und Distributor-Präzisionsgrenzen dokumentiert: [technischer REV6-Bericht](REV6_58V_ARCHITECTURE_STOPGO_2026-10-15.md).

**[BESONDERS WICHTIG – SHUTDOWN- UND RESTART-TOLERANZEN]** OV rising=0.4925..0.5075V, Hysterese20..32mV. Proposed Teiler top-down 475k/1.5M/121k/30.2k (effektiv je ≤±0.25% über Fertigung+TCR+Ta) -> OV trip **34.50..35.91V**, OV-fall/recover **32.26..34.49V** (ohne ~±0.02V+ je relevanten Sense-Pin-Leckstrom und PCB). Standard ±1%-Widerstände reichen für die gleichzeitigen worst-case 36V-Aus /32V-Restart **nicht**. Reproduzierbar [rev6_limits.py](rev6_limits.py) und [test_rev6.py](test_rev6.py), derzeit keine native KiCad/CI-Ausführung behauptet. Bisher kein exakter 0.1%-MPN/CT. **PROVISIONELL, nicht abnahmefähig**.

**[SHUNT-/LEISTUNGSAUSLEGUNG, RECHNUNG]** 15mΩ-Sense => Stromtrip 2.67..4.0A (40..60mV, ohne Shunt-Toleranz). 5V2A@10V η80% +0.5A RAW -> 1.75A Modell-Eingang, gemessener η/Ipeak fehlt. Der RAW-Abzweig und sein 0.5A-Kurzschluss müssen separat abgesichert/begrenzt werden. Bei T_A60°C + 32V 2A sinkt die tatsächliche Regler-Thermikmarge; 85°C ambient sicher OFF aus IC-Tj150°C-Thermikauslösung zu folgern ist ein Fehler: **Temperatursensor/SHDN MPN noch offen**.

**[KURZPULS-TV S optional]** TI TVS5800 58V VRWM und 75V max bei spezifischem 25A/8–20µs kann gegen HF-Ringing helfen, besitzt aber kein 350ms-58V-Derating-Prädikat und ist catalog/6pin-QFN. SMBJ58A clamped bis93.6V bei 10/1000us, NICHT als unter67V- oder unter80V-Begrenzer. TVS-OPEN/SHORT nur in komplett durch F_MAIN qualifizierter Architektur akzeptieren. NO TVS in Leit-BOM ohne nachgewiesenen Nutzen/Messwerte.

**[F_MAIN]** Littelfuse 0997004.WXN **4A, 58VDC, 1kA DC** und -40..125°C erster Kandidat. OEM-typisches Hot-Derating ~2.4A bei Ta80°C; 3A-Typ nur ~1.8A, kritisch bei modeliertem 1.75A. 4A Short-/Arc/Total Clearing, Kabel/Pin/Masse und **mind.58VDC zugelassener Sicherungshalter** offen; die häufigen Shop-MINI-Halter sind nur **32VDC**, NICHT automatisch passend. Höherer DC-Typ bei höherem tatsächlichen Fuse-Voltage-Transient. Keine unzulässig verschmolzene PCB-Sicherung.

**[FRAM-FIRST, KEIN MCU-SD-BACKUPZWANG]** Ein abruptes Abziehen erlaubt 0 Vorwarnzeit. FRAM muss bereits committed sein. Ein fail-high-PWR_FAIL vom echten MAIN_5V-Good und localem UV-Latch wird durch TripTracer-AON-Domain gepullt, **nicht** permanent von CR1220 versorgt. LTC FAULT ist **LOW bei FAULT**, also nicht direkt fail-HIGH. Keine Backfeed-Pfade in Main/BAT+/ACC/RAW/USB; Thermik- und USB-GND-Reversetest nötig.

**[KOSTEN]** siehe [REV6_BOM_COST_DECISION_2026-10-15.md](REV6_BOM_COST_DECISION_2026-10-15.md): bepreiste **Bauteil-Teilgruppen** (1/10/100 €/Gerät netto) V1 4.800/3.644/2.990; V2 9.110/6.854/5.608; V3 LTC4368+2xSiR870+LMR+F_MAIN **18.230/13.344/10.631**. Kein fertiger Gesamt-BOM-Preis: exakter 100V-AEC-FET, Kelvin-Shunt, 0.1%-R, RETRY, F_MAIN-Halter, Thermal-off, RAW, Buckpassives, USB/PG sind **TBD**. LTC #W automotive Mouser 833 sofort lagernd, 7.57/5.88/4.99€ für1/10/100; #PBF ohne W nicht gleichsetzen. SiR870 100V ist nur Demo-Kosten- und Funktionsvergleich, AEC/Serienstand ungeprüft.

**[EIGENE NO-GO-/GO-ENTSCHEIDUNG]** V3 bestes und einfachstes *technisch plausibles Gesamt-Schutz-IC*, aber **NO-GO für freizugebenden KiCad-V1-Prototyp** bis (1) M8/L/58V local pad max, (2) F_MAIN/58V-Halter, (3) exact AEC100V FET/shunt/passive, (4) 85°C-Hot-off, (5) RAW-Ausgangsfehler geklärt. KiCad10-CLI ist in aktueller Arbeitsumgebung nicht vorhanden; kein native ERC/Netlist-/DRC behauptet. REV5, A/B/C unberührt.

---

## 2026-10-15 – Round 6: definitive konditionale Stop/Go-Entscheidung

**[MANAGEMENT REVIEW VERARBEITET]** docs/TRIPPOWER_A_B_C_D_REVIEW_ROUND6_2026-10-15.md auf design/trippower-review; aktueller REV5/Backup-Scope unverändert. Vollständiger Prüfbericht: [WEG_D_ROUND6_CONDITIONAL_STOP_DECISION_2026-10-15.md](WEG_D_ROUND6_CONDITIONAL_STOP_DECISION_2026-10-15.md). [BOM und Kosten](ROUND6_BOM_COST_MATRIX_2026-10-15.md), [reproduzierbarer Szenario-Rechner](load_dump_scenarios.py), [arithmetische Tests](test_round6.py).

**[HERSTELLERBELEG – NICHT AUFGELÖST]** Original-AN-1003 (TSC), p3: SOA-Fig5 bei202V/350ms **Ri≈4,5Ω**; Prosa sagt zuerst4,5Ω, rechnet dann bei **3,5Ω**; Table1/Oszillogramm **3,5Ω/42,8A/61,2V/2619W @25°C**. Das beweist *ein* 25°C-Messbeispiel, keine Seriengarantie. TSC-DS E2310 Vc58,1V @114A **10/1000µs** darf NICHT als 350ms-Maximalwert gelten.

**[RECHNUNG]** idealisierte konstante 61,2V-Klemme, 200V/350ms, Ri3,5Ω: E_TVS **849J Rechteck** / **343J linearer Abfall 200→28V** / **224J exponentiell 200→45,2V**. Bei Ri4,5Ω **661/267/174J**. Nur Szenario, keine ISO-Wellenformen, keine Tj-Simulation. E235/125°C unzulässig extrapoliert. Maximaler Temperaturspielraum 25→175=150K, 125→175=50K, keine Hersteller-Energie-derating-Bestätigung. **D1 NO-GO für 125°C** ohne OEM-Hot-Grenze.

**[PAD-RISIKO]** OEM-Vc61,2V > 60V-Q302 und nur 3,8V bis65V-VS, 18,8V bis80V-Buck. L1µH×42,8A/10µs ergibt rechnerisch +4,28V =>65,48V bei additiver Polarität; L0,5µH×42,8A/1µs +21,4V=>82,6V. Bei TVS OPEN: 200V (+Ringing) an nachfolgendem Pfad. **Keine garantierte VIN_PAD,max-Grenze**; TVS allein nicht austauschen.

**[F_MAIN-HERSTELLERKANDIDAT]** SCHURTER SPT 0001.2509 3,15A, 300VDC, Hersteller-/DigiKey-Nachweis, ~1500A DC, nominal melting I²t33,7 A²s, -55..125°C. TVS-SHORT bei ideal 200V/Ri3,5Ω =57,14A und 350ms ohne Sicherungsöffnung ≈1143 A²s; *nicht reale Sicherungsenergie*. Time-current, total-clearing/DC arc, 9V-Dauerstrom und 125°C-Derating offen. Halter FEU 0031.1751 600VDC aber **nur 85°C ambient**. Kein sicheres heißes 200V-Gesamtsystem nachgewiesen.

**[BESSERER TVS-LABORKANDIDAT]** Bourns SM8S36A-Q (UNIdirectional, nicht -CA): OEM DS Fig ISO16750-2 Test A **10 Pulses, 202V/350ms, Ri graphisch ca2Ω**. 125°C/350ms Vc_max und OPEN-Safe-Failure weiter unbekannt. DigiKey DE aktiv/Bestand beim Snapshot ca2160, 1/10/100 netto **3,740/2,453/1,620€**. TSC TLD8S36AH ist als Herstellerteil bei LCSC/DigiKey ebenfalls aktiv – Reichelt-Restposten ist kein bestätigtes EOL. **No-Go als komplette Architektur**, Bourns nur bei geklärter Hot-SOA eine neue Laboruntersuchung wert.

**[DEDIZIERTER IC FALLBACK]** ADI LTC4366-2 mit 9V-Untergrenze, Timer ohne C rund 1µs, -2 Auto-Retry. OEM-Beispiel 10 elektronische Positionen: Controller, IXTK90N25L2 TO264 250V, 5R, 3C. 35V-Klemme bei 200V angenommen: 1A=165W, 2A=330W linear; frühzeitiges Gate-OFF vermindert Energie, 9V-Startup aber neu zu dimensionieren. DigiKey netto LTC IC 10,42/8,174/6,996€; OEM-FET 37,57€/1, 23,5625€/100. Allein IC+OEM-FET + F_MAIN =48,870€/1 und31,0743€/100, ohne übrige Teile. FET D-S SHORT und OUT→IN-Bodydiode/back-up Rückspeisung ungelöst. **Serien-Gesamtlösung NO-GO**, bedingte Laborforschung ja.

**[WICHTIGE SIGNAL-KORREKTUR]** Frühes PWR_FAIL muss an tatsächlich funktionsfähiges POWER_PATH_GOOD/PG/OV-Off gekoppelt sein, nicht allein an Vorhandensein von BAT+: bei 200V load dump kann der Eingang HIGH bleiben, während die Versorgung bereits trennt. Der Pullup darf im gesunden Fahrbetrieb die Primärzelle nicht dauerhaft entladen. PIN-/Timing-Budget weiter offen.

**[NEUE BACKUP-SCHNITTSTELLE]** Fail-high PWR_FAIL: Open-Drain/Collector von VIN-GOOD aktiv low; bei vollständigem VIN-Verlust durch Backup-Pullup auf separater TripTracer-Kritikschiene high; keine Backupenergie zu BAT+/RAW/USB/5V-main. Kein CR1220/SD-Energienachweis, keine Pin- oder Interface-BOM-Freigabe. Erst Eingang-Power-Mux/RC-Strom/Leckstrom/IRQ-Latenz messen.

**[BOM 1/10/100]** Teilpreise und vollständiges Register notwendiger Funktionen in ROUND6_BOM_COST_MATRIX. Keine vollständig bepreiste Schutz-Ersatzarchitektur möglich, solange 125°C, Pad-/FMAIN-/Open-Fail nicht bestanden sind. Keine Position mit 0€ kaschiert. **Nicht ERC-/DRC-geprüft; kein KiCad-Prototyp**, weil Haupt-P0 offen. Keine Änderung an A, B, C, REV5.

**[ENTSCHEID]** TLD8S36AH als billige vollständige 200V-Eingangsschutzersetzung **NO-GO**, auch Bourns TVS alleine **NO-GO** bis Hersteller/Temperatur/Einzelfehler nachgewiesen. LTC4366 ebenfalls kein direkt einsparender Komplettschutz. Nächster Auftrag nur auf echte OEM-Hot-Grenze, F_MAIN total-clearing und Pad/Backup-Single-Fault fokussieren – **kein** neuer großer Marktüberblick.

---

## 2026-10-15 – Gründung / erstes Screening

**Quelle der Kriterien:** REV5_DESIGN_BASELINE.json auf design/solid-state-power-v1: 9–30V, 5V/2A plus RAW-Aux-Ziel 1A, -40..+125°C, 200V/350ms, F_MAIN austauschbar, Restart bei 30V und sicherer 9V-Start.

**[HERSTELLER + HÄNDLER] D1 TLD8S36AH, Taiwan Semiconductor:** Hersteller-Application-Note AN-1003 weist spezielle Load-Dump-SOA und 202V/350ms bei 25°C aus. TSC-Graph Fig5 fordert bei Vs202V/Td350ms ca. Ri4,5Ω, Text/Tabelle nutzen 3,5Ω und nennen 42,8A / 61,2V; Unstimmigkeit **offen**, nicht übergehen. Reichelt DE TLD8S36AH MAG: 1,85€ brutto bei 1, 1,72€ bei 10, 1,572€ bei 100; Restposten. Quelle https://services.taiwansemi.com/storage/resources/application-note-17/AN-1003_Automotive%20circuit%20protection%20of%20load%20dump%20TVS_A1901.pdf und https://www.reichelt.de/de/de/shop/produkt/tvs-diode_unidirektional_36_v_6600_w_do-218ab-273917 . **[STOP]** wegen Hot-SOA/Gen-Ri/F_MAIN/Einzelfehler.

**[HERSTELLER + HÄNDLER] D2 LTC4366HTS8-2#TRMPBF, ADI:** Dedizierter Hochvolt-Surge-Stopper mit externer MOSFET-Steuerung, 9V..>500V System-Spannungsbereich (NICHT direkt am Pin), einstellbare Clamp/Timer, -2 Auto-Retry nach ~9s, H -40..+125°C; 9V mit hohen Lasten kann den MOSFET ohne Timeout erhitzen (Warnung). DigiKey DE 10,42€/1, 8,174€/10, 6,996€/100 netto (nur IC). Quellen https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf und https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4366HTS8-2-TRMPBF/2825884 . **[STOP]** FET-Hot-SOA, 9V/2A, 30V-Restart, MOSFET D-S short und Zusatzstromschutz unbekannt.

**[HERSTELLER] D3 LTC4380-2, ADI:** Surge-Stopper mit Timer und strombasierter Auslegung. DC2178A-B dokumentiert ISO-Test-A-Anwendung im 28-V-Bereich, aber 0,5A und 250-V-1-ms-Anforderung. 2A + RAW / 200V350ms NICHT erwiesen. Quelle https://www.analog.com/media/en/technical-documentation/user-guides/dc2178af.pdf . **[UNVERIFIZIERT für TripPower]**.

**[HISTORISCHE REFERENZEN]** A LM74930-Q1 (Q301 SHORT → A/SOURCE-Pins/Q302 Hochvolt), B und C AP74502HQ (Eingangs-FET D-S SHORT → zweiter MOSFET Bodydiode → 200V-Ausgang), LTC4364, LTC7860, ST LDP01-35AY; vertiefte Daten/Quellen siehe Hauptscreen und Review-Round4. **[STOP]** Keine Variante derzeit im Fahrzeug freigegeben.

**[KONZEPT]** Bei angenommener konstanter Klemme 61,2V und 200V/3,5Ω entsteht initial ca. 40A TVS-Strom; tatsächliche SOA/Energie muss das 350ms-Zeitprofil berücksichtigen. Zwingend alternative Generator-Ri bis niedrigstem Testwert prüfen. Bei LTC4366 mit 35V Clamp und 1A Last fällt initial (200−35)*1A=165W am Serien-FET an, nicht auf 350ms Dauer ohne SOA-Test zulässig.

### Nächste Schritte / Verantwortlichkeit des jeweiligen nächsten Weg-D-Chats

1. Hersteller wegen 3,5Ω vs 4,5Ω und –40/+125°C-SOA / zulässigen Folgepulsen anfragen bzw. Dokumentation gründlicher auswerten.
2. Reales 200V/350ms-Quellprofil und erwartete Ri_min/Flanken klären. Wenn nicht bekannt, plausible Worst-Cases als **Szenario statt Garantie** berechnen.
3. F_MAIN aus Datenblatt mit möglichem 200-V-DC-Fehlerstrom, Ausschaltvermögen/I²t und Kupfer-/Kabelwärme qualifizieren. Beim TVS-SHORT den 200-V-Puls berücksichtigen.
4. Zwei einfache **volle** Architekturvarianten vergleichen: nur D1-TVS + revisionskonformes regulatorisches Downstream / D2-LTC4366 mit 250/300V-FET und gezielter Frühabschaltung; jeweils 9V-Startup und 30V-Restart messen/simulieren.
5. Nur bei wirtschaftlichem Sicherheitsvorteil KiCad-10-Prototyp mit echtem ERC/DRC und kompletter 1/10/100-Stück-BOM; weder „ein IC löst alles“ noch automatisches Fail-Safe behaupten.

## Schema für spätere Einträge

### YYYY-MM-DD – Thema
- **Status:** HERSTELLER / RECHNUNG / SIMULATION / LABOR / BLOCKED / GO
- **Kandidat / MPN / Variant:** ...
- **Beleg (Datenblattabschnitt/URL/Messdatei):** ...
- **Änderung gegen vorherige Annahme:** ...
- **Fehlerrisiko / F_MAIN / Thermik / 9V / 30V / 200V350ms:** ...
- **Gesamt-BOM-/Kostenwirkung (wenn belegt):** ...
- **Nächstes offenes Gate / Commit:** ...

Hinweis: Dieses Log ist eine Struktur für spätere Arbeitsaufträge. Es aktualisiert sich nicht automatisch zwischen Chats; jeden neuen Befund ausdrücklich committen.
