# TripPower Weg A — eigenständige REV6-Minimalarchitektur (15.10.2026)

## 0. Verbindlichkeit, Bestand, Bedienung

**Autoritativ:** `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, `docs/HARDWARE_REQUIREMENTS.md` PWR-44–54, `AGENTS.md` und aktualisierte Backup-Requirements. **REV5-Vorgaben 9V/200V/125°C und frühere A-Round6-Studien sind ausschließlich historische Vergleichsdaten.**

**Einziges neues KiCad-10-Projekt (separat und portabel):** `hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_pro`; gleichnamiges Root-Schaltblatt `TripPower_REV6_A.kicad_sch`. KiCad-Hierarchien: (1) TPS26631-eFuse mit Verpolschutz/UVLO/OVLO/ILIM, (2) LMR38020-Q1 5V2A mit PGOOD-Puffer. Lokale `TripPower_REV6.kicad_sym`, bestehende portable Buch-/Passiv-Bibliotheken, lokale `Tripmaster.pretty`. Keine REV5-Elektrodatei oder deren 57/58-Bestückliste geändert. **Kein PCB-Layout**, daher kein DRC, Boardpreis oder physische M8-/RAW-/5V-/Status-Steckerfreigabe. Es gibt nur eindeutig beschriftete **nicht bestückte Test-/Übergabepads**; vor Hardware sind echte Strom- und Rückspeise-freigegebene Verbindungen erforderlich.

## 1. Hersteller- und Modulvergleich — COTS zuerst

| Lösung | Bedeutung der REV6-Grenzen | Wertung |
| --- | --- | --- |
| RECOM R-78K5.0-2.0L, 6,5–36V/5V2A SIP3 | Kann **nicht direkt 58V/350ms** sehen; benötigt weiterhin 58V-festen vorgeschalteten OVP-/Reverse-/OC-Pfad. Kein integrierter ACC-/PG-/RAW-Schutz | Kein belegter Gesamtkostenvorteil; Einzelpreis historisch Reichelt **5,35 € inkl. MwSt.**, *nicht* Gesamtpreis |
| TI TPSM33620S5-Q1 36V Buck-Modul | Auch mit integriertem Magnetik nicht für **58V direkt am Eingang**. Der vorgeschaltete eFuse muss bei echtem FET-Kurz die absolute Maximalspannung des 36V-Moduls *nicht* als garantiert geschützt deklarieren | Nicht der kleinste verlässlich qualifizierbare Fehlerfall |
| TI LMR38020SQDDARQ1 Automotive 4,2–80V Buck | **58V direkt am Buck** überschreitet empfohlenes 80V VIN-Max noch nicht, selbst wenn der vorgeschaltete eFuse intern kurzschließt. Aktuelle Reglerfamilie, 5V/2A und PGOOD schon projektiert | **Behalten**, Thermik/USB/Magnetik noch verifizieren |
| TI TPS26631PWPR 4,5–60V Industrial eFuse | OV-/UV-Supervision, MOSFET-OC/Thermal, externes reverse MOSFET (TI Datenblatt Fig 9-2). **67V abs**, daher tatsächlich 58V vor allen lokalen Ringing-/ESD-Spitzen und 350ms-/Tj-Thermik nachweisen | Ausgewähltes **isoliertes** preisgünstigeres Forschungs-Frontend; keine AEC-Automotive-Zulassung dieses eFuse |
| Historischer LM74930/250V/200V-Ansatz | Große Bestückzahl, Hot-SOA-/Zener-/9V-Start-Gates für nicht mehr verlangten ungedämpften 200V-Puls | **Nicht** nach REV6 übernommen |

Quellen: https://www.ti.com/lit/ds/symlink/tps2663.pdf , https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf , https://www.recom-power.com/ .

## 2. Konkrete 2-Blatt-Schaltung

**Eingang:** extern abgesichertes Fahrzeug-BAT/ACC nach TripTracer-Mikrorelais/MCU-HOLD (M8-Fahrzeugkontakt gehört zur Hauptplatine; kein 200V-FET). Externes **F_MAIN** bleibt für jeweils BAT und ACC beim Fahrzeug quellnah verpflichtend. Kein zusätzlich fest eingelötetes Sicherungsteil.

**U201 `TPS26631PWPR`**, Industrie-Qualifikation (nicht Automotive-Q1), HTSSOP/PWP20 Exposed Pad (lokaler KiCad-Padentwurf bis TI-Landpattern-Check **provisorisch**). IN1/2/3 am Q201-Drain, IN_SYS6 am Q201-Source, OUT18/19/20 nach `VIN_PROTECTED_UNFUSED`; B_GATE4 steuert **Q201 `SQM100N10-10_GE3`** 100V automotive reverse FET, DRV5 treibt **Q202 `BSS138LT1G`** Gate-Pulldown; GNDPAD21 und GND9 auf GND. 1µF 100V am IN_SYS; 1µF100V am OUT; C203 100nF100V dVdt. R204 6,04kΩ für ~**2,98A** nominal Overload (TI I_OL=18/Rk), jedoch 2× höhere transiente Current-Limit-Verhaltensmöglichkeit. **RAW0,5A ist NICHT unabhängig selektiv auf0,5A abgesichert**; Leitung/Stecker, Kurzschlussschutz und TripTracer-Aufteilung müssen geprüft werden. IMON/FLT/PGTH/PGOOD nicht benutzt. MODE12 frei = Hersteller-Fault-Mode prüfen.

**Sicherheitsrelevante Korrektur im Entwicklungsverlauf:** TPS26631 `SHDN13` **max5,5V absolut**, deshalb niemals an 10–58V `VIN_FUSED`. **Richtig: SHDN offen/floating**, laut TI E2E Herstellerbestätigung mit internem Pull-up am Eingang; gemessene Freigabeschwelle/Abschalttemperatur bleibt zu qualifizieren. Referenz https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1625619/tps2663-function-of-shdn-pin .

**OV/UV** R201 `AC1206FR-07402KL` 402k, R202 `AC1206FR-0749K9L` 49,9k, R203 `AC1206FR-0716K5L` 16,5k, 1%. Aus TI 1,176/1,20/1,224V Sense-Parameter, ±150nA Pins, Widerstände ±1% plus **angenommene** bis100ppm/K von25→70°C:
- OVP steigt bei **32,337…35,863V**, typisch **34,065V**; erfüllt rein statisch `>32..≤36V`.
- UVLO Freigabe **8,018…8,929V**, typisch **8,465V**; bei `10V` sollten die Pins im **statischen** Modell aus dem UVLO herauskommen. Das beweist weder echten 10V-Kaltstart noch Recovery ohne Flattern; Ti OV-Hysterese und Release-Timing müssen als Herstellergrenzen gesondert qualifiziert werden.
- `36V/400ms` oberhalb OVP; Ausgang darf abschalten, Schutzbauteile müssen überleben. `58V/350ms` bei *wirklich* auf≤58V am Anschluss begrenztem Bordnetz; TPS26631 empfohlen max60V (**nur2V dynamische Reserve!**), abs67V (**9V Reserve!**), Buck max80V operativ. **Leitungsringing + Burst + Temperatur-Peaks dürfen nicht einfach additiv vergessen werden.** Kein neues 200V-Test-A.

**Buck** U101 LMR38020SQDDARQ1, L101 `FCH0650-150M` (Fangcheng 15µH-Isat-Prototyp, **Landpattern und thermische Eigenschaft provisional**), R101/R102 100k/24.9k, R103 64.9k/400kHz, C101/C108 4.7µF 100V, C104–106 3×22µF/25V, C102/C107 HF100nF. **Ausgang 5V/2A durch+60°C ohne PCB und DC-bias-Ceff/Isat/IC-Thermal nicht nachgewiesen.** Q501`BVSS123LT1G` +100k/1Meg als fail-high offener PGOOD-Status: LOW=main5V okay, HIGH/hochohmig=fail mit separatem TripTracer-3.3V-Logikpullup, niemals Primärzelle/Dauerbatterie nach TripPower/RAW/Haupt5V speisen. **PG ist nicht garantiert vorauseilende M8-Warnung.**

**Kritische offene Temperaturschaltung:** Die TPS26631-IC-Übertemperatur-Abschaltung schützt typischerweise den Chip erst bei **Tj~165°C**, **nicht** das gesamte Gerät nach gemessenen **+85°C Umgebung**. **Der neue 25-Positionen-Stand hat noch keinen eigenständig qualifizierten +70-°C-Derating-/+85-°C-Ambient-Abschalter.** Ohne diese Funktion und einen bei 85°C fail-safe messbaren Temperaturpfad besteht **NO-GO**. Eine später echte, spezifizierte Temp-Supervisor-Eingriffslogik ist **nicht** einfach als 0-Euro-/0-Bauteil-Pflichtlösung abzuziehen.

**Standby BAT+-OFF:** kein nachgewiesener <1mA-Modus, denn Haupt-Fahrzeug-Mikrorelais sollte bei OFF trennen, Reststrom hängt vom TripTracer-BAT-/ACC-Relais/Leckpfad ab. Bei U201 aktiv ist 1mA keine zugesagte Eigenschaft. Quell-/Relais-/USB-/RTC-Zustände trennen; nachweispflichtig 12/24V und Temperatur.

## 3. Bewertete Fehlerfälle / No-Go

- **Interner U201-D-S-Kurzschluss:** 58V können bis Buck VIN und geschützten RAW durchschlagen. Buck mit80V empfohlen und 85V absolut kann 58V vor Ringing grundsätzlich verkraften, aber **RAW0,5A / Leitung / Steckverbinder / IN-Rückspeisung weiterhin zu beweisen**; externe F_MAIN löst bei hochohmigen Fehlern nicht zwingend aus.
- **Q201 D-S-Kurz:** Verpol-/Reverse-Sperre fällt aus, eFuse-OCP wirkt weiterhin nur falls korrekt versorgt; gefährliches Backfeed über USB/RAW gesondert untersuchen.
- **Q201 offen, Unterbrechung M8/GND:** ggf. sofortiger Versorgungsausfall, nach REV6 akzeptabel falls vorlaufender FRAM-Commit intakt; SD-Finalisierung nicht zugesagt.
- **OV-Teiler offen/kurz, U201 klemmt ON, max58V und Leitungsspitzen:** UV/OV-Schwellen verlieren Garantie, eFuse maximal67V abs, niemals als 200V-Schutzeinheit markieren. Gegen Fehlschalten/Überstrom braucht externe Fahrzeug-F_MAIN, thermisch sicherer PCB-Aufbau.
- **USB gleichzeitig mit M8 / USB-only:** TripPower hat nur 5V, GND, RAW und fail-high Status; **USB-M8-Priorität, ESD, reverse current blocking des kompletten TripTracer Haupt-5V-Pfads sind allein hier nicht belegt**. 5V-USB darf weder F_MAIN/BAT/ACC/RAW noch VBUS-Host rückspeisen.
- **85°C Umgebung:** spezieller Ambient-Off-Sensor/Regler noch nicht entworfen; das alte +125°C-Volllastziel ist zwar gestrichen, **+85°C safe-off gilt weiterhin**.
- **Kabel/M8/Connector:** neue Testpads sind *keine* für 2A/0,5A mechanisch/electrisch qualifizierte Steckverbinder, Leiterbahnquerschnitt/I²t und Trägermodule schließen.

## 4. BOM / Kostenvergleich: ehrliche Abgrenzung

**Neue bestückte KiCad-Positionen: 25**, 10 eingangsseitig + 15 buck-/PG-seitig, **AUTO/RUN hier gleich** (historisches RUN-Leitungsschema nicht mechanisch übernommen). Mit externem F_MAIN, mikrorelais/Kabel und späterem Temperatur-Sicherheitsblock wird eine **fertige** Kombination teurer und hat mehr als 25 Positionen; diese notwendige Restperipherie nicht in einer falschen „vollständigen 25er Produkt-BOM“ verstecken.

| Kategorie | REV5 AUTO | REV5 RUN | neuer isolierter REV6 A |
| --- | ---: | ---: | ---: |
| Bestückte Teile in jeweiligem KiCad-Schema | **57** | **58** | **25** (−32/−33; kein unterstelltes ausgelagerter Temperaturblock) |
| unabhängige 200V-Zener-/250V-FET-/LM74930-Frontend | ja | ja | **entfallen** |
| Buck-Regler und tatsächliches 5V2A-Ziel | LMR38020 | LMR38020 | **LMR38020 unverändert** |
| RAW | 1A historisches Ziel | 1A historisches Ziel | **0,5A Ziel, zusätzlicher Kabelschutz offen** |
| HV-Test A / Hot125°C | historisch nicht frei | historisch nicht frei | **nicht mehr gefordert** |
| +85°C sicher OFF | offen | offen | **offen, Prototyp noch nicht vollständig** |

Aktuelle recherchierte **Netto-Einzel-/Staffel-Snapshots** auf Bestellung/Priorität, nicht endgültiger Warenkorb: TPS26631PWPR **3,89/2,96/2,46€** bei1/10/100; Q201 Vishay SQM100N10-10_GE3 **3,78/2,49/1,75€**; BUCK LMR38020SQDDARQ1 **3,92/2,98/2,49€**, onsemi Q202 BSS138LT1G **0,292/0,129/0,113€**, 2× KEMET C1210C105K1RACAUTO **2×0,585/0,391/0,267€**, PGOOD Q501/R501/R502 **0,552/0,274/0,1751€**. Insgesamt **nur bisher tatsächlich bepreiste 9 Teile = 13,604 / 9,615 / 7,5221€ pro Gerät**, 1/10/100, **16 von25 ohne kompletten Preis**, Lagerstände/MwSt./Versand nicht als Garantie. Neue `REV6_A_25_PART_ORDER_BOM_2026-10-15.csv` und GitHub-Action `rev6-a-entire-native-bom.csv` zeigen die restlichen exakten MPNs. **Dies ist kein kompletter Einkaufspreis**; zur Fertigung alle25 plus fehlende mechanische/thermische zwingende Teile, Stecker, F_MAIN, Montage, Module-BOM, Porto/Steuer auf einheitlicher Basis bepreisen.

## 5. Regressionen, elektrischer Projektstatus und nächste Entscheidung

`tools/trippower_a_rev6_limits.py`, `tools/test_trippower_a_rev6.py`: Herstellerwerte, kalkulierte 32/36V-Ecken,10V-Neustart-, 58V-Abs- und 2A+RAW-Lasten. `tools/check_trippower_a_rev6_native_netlist.py`: native KiCad10-Netzliste kontrolliert eFuse-Pins und FET-Orientierung, 25 Bauteile und bewusste fehlende 200V-Teile. Neuer eigener Workflow `.github/workflows/trippower-a-rev6.yml` mit eigenem KiCad10-ERC, nativer Netzliste und exportierter Komplett-BOM. **Keine ERC- oder DRC-Behauptung ohne nachgewiesenen erfolgreichen Job/Run**.

**Entscheidung:** COTS-eFuse+80V-Buck ist gegenüber 57/58 Bauteilen der aussichtsreichste REV6-A-Vereinfachungspfad. Gleichzeitig ist eine Version ohne Hersteller-belegtes Temperatur-/RAW-/USB-/Eingangs-58V-Fehlergate und echtes Layout **keine frei verwendbare Schaltung**. Die Leiterplatte noch nicht bestellen; historischer REV5-Baseline-Stand unverändert.
