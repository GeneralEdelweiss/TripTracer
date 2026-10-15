**Aktuellste Fortsetzung 15.10.2026:** In [01_Protection_LM74930.kicad_sch](01_Protection_LM74930.kicad_sch) R313–R315 von generischem 3,32k/1206 auf **3,3k Vishay CRCW25123K30FKEGHP / 2512** umgestellt; rechnerisch 9,90k Gesamt, 202V Pulswerte im [Stress-Gate](INPUT_STRESS_GATE_2026-10-15.md). Hersteller [CRCW-HP-Kurven](https://www.vishay.com/docs/20043/crcwhpe3.pdf) + Mouser als *technisch und beschaffungstechnisch plausibler Kandidat*; **85°C/heisse Fehler, 9V dynamisch, Q301-SOA, 2512-Landpattern und echtes KiCad10-ERC der Revision bleiben offen, bis neuer CI-Run abgeschlossen ist**. Bisherige 3,32k und 1206 nicht als aktuelle Modul-Werte verwenden. Nur F_MAIN extern.

# TRIPPOWER – HIER IM NEUEN CHAT STARTEN

**Aktueller verbindlicher Uebergabestand: 14.10.2026, Europa/Berlin.** Dieses Dokument ist die **Prioritaetsquelle fuer den naechsten Chat**, wenn aeltere Vergleichs- oder Planungsdokumente noch veraltete Namen wie `VIN_PROTECTED` / `F302` / `LM74800` fuer die eigenstaendige TripPower-Schaltung enthalten.

**Fortsetzung 15.10.2026:** [202-V-Puls- und Q301-Thermik-Screening](INPUT_STRESS_GATE_2026-10-15.md) mit reproduzierbarem [Python-Stresscheck](../../../tools/check_trippower_input_stress.py). **R313–315 jetzt als Vishay CRCW25123K30FKEGHP (2512 3,3k AEC-Q200) mit Hersteller-Pulskennlinie konkretisiert, aber noch ohne Heiss-/Wiederhol-/Einzelfehlerfreigabe; STD17NF25 ist bei voller 9-V-Gesamtlast auf kompakter 35-µm-Platine thermisch ungeeignet, solange keine bessere reale Kupfer-/RDS-/SOA-Rechnung vorliegt.** Dieser Check ist **kein** Gate A/B oder Fertigungsnachweis. Reihenfolge unter Punkt 5 bleibt verbindlich, als naechstes RVS-MPN/Pulsdaten und Q301-Alternative qualifizieren. Native ERC/Netlist des alten Run 38636492660 unveraendert, neues CI nach Commit checken.

## 0. Sofortiger Arbeitsauftrag fuer den naechsten Chat

> Arbeite **direkt in GitHub** am eigenstaendigen **TripPower_5V2A** im Repository **GeneralEdelweiss/TripTracer**, Branch **design/solid-state-power-v1**. Lies zunaechst `AGENTS.md`, diese Datei, `module_contract.json`, `lm74930_design_v1.json`, `LM74930_DIMENSIONING_2026-10-14.md`, die beiden KiCad-Schaltplaene sowie den aktuellen KiCad-10-CI-Bericht. **Nicht die Architektur erneut diskutieren oder nur dokumentieren**: verifiziere als naechsten Schritt die kritischen Eingangsschutzbauteile und bringe das eigenstaendige KiCad-Projekt weiter in Richtung PCB-Layout, mit kleinen nachvollziehbaren Commits. Die 5V/2A-Buck-Wahl, LM74930-Controllerwahl und die Entscheidung fuer nur eine externe Hauptsicherung sind fix. **Keine fertigungstauglichen Statusbehauptungen ohne Belege.**

## 1. Repository und echte Arbeitsdateien

- GitHub: https://github.com/GeneralEdelweiss/TripTracer/tree/design/solid-state-power-v1/hardware/modules/TripPower_5V2A
- Geltende Arbeitsregeln: https://github.com/GeneralEdelweiss/TripTracer/blob/design/solid-state-power-v1/AGENTS.md – COTS zuerst, eine Baugruppe bis zu nachvollziehbaren Gates bearbeiten, KiCad 10, niemals ERC/DRC oder reale Automotiv-Tests erfinden.
- Standalone **KiCad-10** Projekt (im ganzen Ordner kopierbar): `TripPower_5V2A.kicad_pro`; Root `TripPower_5V2A.kicad_sch`; Unterseiten `01_Protection_LM74930.kicad_sch` und `02_5V_LMR38020.kicad_sch`.
- Projektlokale Bibliotheken: `sym-lib-table`, `fp-lib-table`, `TripPower_Sym.kicad_sym`, `TripTracer_V1.kicad_sym`, `Tripmaster_Sym.kicad_sym`, `Tripmaster.pretty/`. **Achtung:** vorhanden bedeutet nicht, dass alle MPN/Footprints/3D und Modelle bereits qualifiziert sind.
- Vertrag / Zahlen: `module_contract.json`; `lm74930_design_v1.json`; `LM74930_DIMENSIONING_2026-10-14.md`; `README.md`.
- Pruefung via `.github/workflows/kicad10-checks.yml`, `tools/check_trippower_native_netlist.py`, `tools/check_trippower_lm74930_values.py`. Auch Legacy-TripTracer-Schaltplan/PCB werden noch im selben Workflow geprueft und koennen den Gesamtstatus rot halten.

## 2. Vom Nutzer **fest entschiedene** Architektur

- **Eigenstaendiges, universell verwendbares 12-/24-V-Bordnetzmodul**, kein Umbestuecken fuer 12 gegen 24 V. Arbeits-Eingangsbereich **9–30 V**; Fahrzeugeingang „dreckig“ (Verpolung, Load-Dump, Spannungstransienten), erzeugt **geregelte saubere 5 V bis 2 A**. ISO-/Automotiv-Freigabe ist ein **Testziel**, nicht bestanden.
- Eingangsschutzcontroller **LM74930QRGERQ1**, **nicht LM74800-Q1** fuer das neue Modul; Buck **LMR38020SQDDARQ1** bleibt. Ehemaliger LM74800 in `hardware/kicad/01I_LM74800_INPUT.kicad_sch` gehoert zum **alten, unveraenderten integrierten TripTracer-Projekt** und darf nicht versehentlich als aktueller Modulcontroller eingesetzt werden.
- **Zwei Spannungsausgaenge:** `5V_OUT` 5V/2A sowie `VIN_PROTECTED_UNFUSED` an **J302 Pin1** = **ungeregelter** Roh-Bordnetzabgriff **hinter** LM74930-FETs und gemeinsamem Shunt **R301**, parallel zum Buck-Eingang. Nicht 15V, nicht 5V und nicht selektiv abgesichert.
- **Kein F302, kein separater SMD-/AUX-Schmelzeinsatz, kein Sicherungshalter auf TripPower oder TripTracer.** Die einzige verbindlich erforderliche **austauschbare Hauptsicherung `F_MAIN` ist EXTERN in der FAHRZEUGZULEITUNG, so nah wie praktikabel an der Stromquelle und vor SAEMTLICHER TripTracer-Verkabelung**. `F_MAIN` ist **nicht** auf TripPower und bisher keine 3A-Festlegung.
- **3 A ist nur ein Kandidat**, nicht freigegeben: Bei 9V und 5V/2A mit konservativ angenommener Buck-Effizienz 80% + 1A zusaetzlichem rohem Ausgangsverbrauch ergeben sich ca. **2,39A Quellstrom**. Eine exemplarische 3A-Littelfuse-MINI-58V-Sicherung hat bei 80 Grad C nur ca. **2A** zulaessigen Dauerstrom. **4/5A** ebenfalls nur Kandidaten: Kabel, Steckverbinder und **ALLE Leiterbahnen hinter der Hauptsicherung** nach Nenn-/Ueberlast, realem Kurzschlussstrom, Zeit-Strom-Kurve, **I²t und Fehler „Schutz-FET kurzgeschlossen“** nachweisen. Sicherung ist nicht harte Strombegrenzung auf ihren Nennwert. Ohne diese Koordination keine Fahrzeug-/Fertigungsfreigabe.
- Der LM74930 hat einen **gemeinsamen elektronischen Circuit Breaker (OCP/SCP)**; Fehler am Hilfszweig koennen **5V ebenfalls abschalten**, ein FET-Defekt kann den elektronischen Schutz umgehen.
- `RUN_CMD` fuer die universelle Platine: **3,3V/5V aktiv HIGH** als Entwurfsziel. Externes ACC/ESP32-HOLD bleibt auf TripTracer; keine Einbau-Relaisloesung. Lokale optionale ALWAYS_ON-Bestueckung R319. Sperrdiode **D305** gegen Backfeed in den RUN-Eingang. **12-/24-V-Zuendplus nie direkt an RUN_CMD**. Fail-OFF, 9-V-Start, heisser Ruhestrom und Power-Off-Leckpfad noch pruefen.
- Das **Riverdi-Display** bekommt bevorzugt einen **separaten 5V->~15V /100mA LED-Konstantstrom-Boost** aus `V5_SYS`, Kandidat **TPS61165-Q1** auf der TripTracer-Hauptplatine. Nicht erforderlich, dass TripPower selbst feste 15V liefert. `VIN_PROTECTED_UNFUSED` trotzdem als universeller Rohspannungsausgang vorhanden.

## 3. Auslegungsstand Schutzstufe (nominal, keine ISO-/thermische Freigabe)

| Funktion | Bisher entworfener Wert |
|---|---|
| U301 | **LM74930QRGERQ1** RGE24 + RTN25, RTN **FLOAT**, nicht GND |
| Q301 / Q302 | **STD17NF25** 250V FET als **thermisch/SOA UNFREIGEGEBENER Kandidat**; **BUK7Y4R8-60EX** 60V IDEAL-Diode-FET ebenfalls prüfen |
| R301 gemeinsamer Sense | **5 mΩ**, 1%, 2512, Leistung/MPN/Footprint verifizieren |
| RSET / RILIM / RISCP | **50Ω / 33,2 kΩ / 470Ω** → nominal ca. **3,61A OCP**, **5,03A schnelle SCP**; Toleranzen und Einschaltstrom pruefen |
| CTMR / RTMR | **47 nF / 100 kΩ** → nominell ca. 0,685ms TMR (real mit Parallel-R neu pruefen), **Latch-Off**-Ziel |
| UVLO | nominell Ein **7,52V**, worst-case der bisherigen Rechnung 6,90–8,35V |
| OV | nominell AUS **35,89V**, worst-case bisherigen Rechnung 34,02–38,74V |
| VS-Versorgung | **3×3,32 kΩ** HV-Pulswiderstaende + 56V Zener + **A→VS-Diode** Kandidat **BAV21WQ-7-F**; bei 202V/350ms grob **0,75 J im Serienzweig gesamt**, ca. 0,25J/Resistor: Impulstauglichkeit/Start bei 9V **offen** |
| VIN_PROTECTED_UNFUSED | **1 A zusaetzliche Dauerlast vorlaeufiges Designziel**, nicht freigegebene Stromgrenze; Gesamtstrom und heisse Q301-RDS/SOA pruefen |

## 4. Verifikation und STATUS – **nicht mehr und nicht weniger behaupten**

- **Eigenstaendiges KiCad-10-Schaltplanprojekt existiert** mit zwei echten elektrisch verbundenen Unterseiten, lokalen Sym-/FP-Libraries und aus KiCad exportiertem Netlist + PDF.
- Nach Entfernung von `F302` und Umbenennung `VIN_PROTECTED_UNFUSED` haben die folgenden CI-Ausgaben die **eigenstaendige Schaltung geprueft:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38636492660 – Logdaten: **3 Schaltplanseiten mit je 0 ERC-Verletzungen**, **46 gepruefte native Pin-/Netzzuordnungen**; native Netlist und PDF wurden exportiert. **Gesamt-Workflow-Status nicht automatisch gruen**, weil alte Gesamt-TripTracer-ERC/DRC und weitere Projekt-Gates weiterhin scheitern koennen. CI beim Wiederaufnehmen erneut am aktuellen HEAD laufen lassen und Ausgaben direkt lesen, statt Run-Schritt `success` als Beweis fuer alle Checks zu nehmen.
- **Kein eigenstaendiges fertiges TripPower-PCB**, kein Routing, **kein eigenstaendiger PCB-DRC**, keine thermischen/ISO-/EMV-/Labor-Messungen. Keine Einkauf-/Fertigungs-/Fahrzeugfreigabe.
- Alte Designvergleiche sind **historisch**. Bei Widerspruechen gelten die hier zusammengefassten Nutzerentscheidungen, die tatsaechlichen aktuellen KiCad-Dateien und `module_contract.json`.

## 5. Geordnete naechste Arbeiten – in dieser Reihenfolge

1. **Aktuellen Native-KiCad10-Schaltplan-/Netlist-Test am HEAD checken**, keine stillen F302/LM74800/alten Netznamen. 5V-Ausgang, direkter Rohspannungs-Abgriff, Source `VIN_FUSED`, Schutzcontroller/Rsense, RUN und Pad25 physisch/symbolisch kontrollieren. Eingangsquelle muss extern korrekt `F_MAIN`-gesichert sein.
2. **Sicherheitskritische Eingangsbauteile fertig qualifizieren:** VS-3x3,32k Widerstaende inkl. Hersteller-Impulsdiagrammen und 9V-Chargepump-Start; 202V/350ms Q301 SOA + Dauerverlust **bei 9V und 1A extra Last** heiss; Q302 VDS/VGS; 56V Zener/TVS; OV/UV-Widerstands-Pulsfestigkeit. Verfuegbarkeit/Preis/LCSC/Mouser/PCB bestellbar gegen COTS-Alternativen verifizieren. Nicht ohne Beleg als fix deklarieren.
3. **Hauptsicherung F_MAIN und Leiterbahnauslegung** auf 12/24V-DC-geeignete Sicherungsfamilie, DC-Abschaltvermoegen, Temperatur, Kurve und I²t dimensionieren; 3/4/5A vergleichen. Alle Pfade inkl. TripPower->TripTracer Zwischenverbindung und 5V-Seite auf worst-case sichere Auslegung, insbesondere Fehler „FET shorted“, pruefen. Hohe Sicherungsnennstroeme bedeuten mehr potentielle Energie bis zum Abschalten.
4. **Geometrie/BOM**: alle Herstellerpinouts inkl. LM74930 RGE24/RTN float, Q-HV/IDEAL-Pads und 15µH **FCH0650-150M** Spulen-Footprint (derzeit provisorisch), Geraetebuchsen/Power-Pads/3D und projektrelative Bibliotheken bestaetigen. Ggf. kompakten Stecker ohne neue proprietaere Teile waehlen.
5. **Dann eigenstaendiges PCB** fuer TripPower erzeugen, 2 vs 4 Lagen technisch und kostenmaessig entscheiden, Strom- und transientenarme Rueckstromfuehrung, Kelvin-Rsense, thermal vias/Kupfer, Platzierung. Native KiCad10 ERC/Netlist/PCB-Netzparitaet/DRC **am eigenen Projekt** und Labor-Testplan ausfuehren.
6. Erst nach diesen Gates **Integration** in TripTracer, ACC/HOLD + USB-Speisung inkl. Verpol/USB-Backfeed/USB-Firmwarezugriff, anschliessend Tests 9/12/24/30V, OC/SCP, thermisch, Surge, Fahrzeug.

**Keine neuen Grundsatzfragen noetig.** Wenn ein konkreter technisch notwendiger Grenzwert (z. B. F_MAIN nach I²t) noch offen ist, ihn durch Recherche + Auslegung entscheiden oder als blockiertes Gate belegen, nicht als gefrorenen Wert erfinden.
