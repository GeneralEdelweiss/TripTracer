# TripPower Weg D – fortlaufendes Forschungsprotokoll

**Scope:** dedizierter Load-Dump-IC bzw. speziell für 200V/350ms ausgelegter passiver Schutz. Änderungen nur auf design/trippower-d-load-dump.

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
