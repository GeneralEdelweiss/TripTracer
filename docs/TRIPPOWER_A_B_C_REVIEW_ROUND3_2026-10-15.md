# TripPower Projektleitung – A/B/C Review Runde 3 (15.10.2026)

**Keine Fertigungs-, Fahrzeug-, Lastabwurf-, 9-V-Start-, 125-°C-/2-A- oder PCB-DRC-Freigabe.** Dies ist eine dokumentierte Quell-/GitHub-Prüfung. A: `design/trippower-a`, 31 Commits seit `2cafbf43e24aadc12ede10cd413b962c84579664` (+15 seit letztem Manager-Review); B: `design/trippower-b`, 15 (+9); C: `design/trippower-c`, 18 (seit vorheriger C-Kontrolle unverändert). Keine fremden Entwicklungsbranches geändert.

## Kurzentscheidung

- **A** bleibt bevorzugter Hauptpfad und hat als einziger einen *separaten, wirklichen KiCad-Schaltungsprototyp* mit unabhängig verifizierbarem erfolgreichen KiCad-10-CI-Job vorgelegt. Der alternative D306-Zenerpfad ist ein **Kandidat**, noch keine nachgewiesen sichere Lösung.
- **B** hat den dringend zu analysierenden weiteren Einzelfehler **Q301 Drain-Source kurz** erkannt: `VIN_FUSED → SOURCE_A → D302 (vorwärts) → VS_CLAMP`, **unter Umgehung von R313–R315**. Dadurch sind D301 und eventuell D306 trotz intakter TVS nicht notwendig energiebegrenzt; diese Hypothese hat Vorrang vor Freigabe der D306-Prototypverbesserung.
- **C** hat einen ernstzunehmenden unabhängigen Integrationspfad mit **AP74502HQ + 2 HV-MOSFETs + TPS26631 + TPSM33620-Q1** sowie einen separaten KiCad-Entwurf und 28 Draft-BOM-Positionen (inklusive 2 Steckverbindern). Es gibt **keinen neuen Commit** seit letzter C-Kontrolle, keine bestätigte KiCad10-ERC/Netlist oder reale Sicherheitsfreigabe. **Nicht** voreilig verwerfen: Hersteller Diodes zeigt wirklich eine explizite *200V unsuppressed load dump*-Anwendung für AP74502(H)Q, mit externer VIN-Zener-Vorspeisung; dies ersetzt aber nicht die 350ms-/Hot-/Abschalt-/Buck-VIN-Pad-Qualifikation.

## A – Reale Fortschritte und Grenzen

Neue `01_Protection_LM74930_D301_BACKUP_PROTOTYPE.kicad_sch` (nur alternate protection sheet, nicht in aktiver REV5-Hierarchie), `WEG_A_D306_PROTOTYPE_BOM_DELTA_2026-10-15.csv`, Modelle und Regression. Zusätzliche Comchip `ACZRC5370B-G` 56V/SMC als D306 direkt `VS_CLAMP → GND`; Prototyp **58 AUTO / 59 RUN** (+1 zu bestehend 57/58), Mehrkosten vor Montage bei 1 Stück ca 1,23€ gemäß Bericht. Bei D301-OFF besteht topologisch eine zweite Clamp. Kritisch: 56V ±5% bei Prüfstrom ≠ garantierte 65V-Obergrenze bei 200V/350ms/+125°C. 5W-Nennwert ≠ 350ms-Puls-/Lead-Hot-Derating. Auch 9-V-Heißleckage und der Wiederanlauf bleiben offen.

**CI direkt verifiziert:** GitHub Actions runs `38728505510` und `38728846904`, Job `quantitative-and-native`, **conclusion=success**. Die einzelnen Schritte umfassten Modelltests, native KiCad-10-ERC/Netzliste und Validierung des alternativen D306-Blatts. Das ist ein tatsächlich erfolgreicher **Schaltplan-/Netzlistencheck**, **kein** 200V-SOA-/Fertigungsnachweis.

Q301 MOSFET `SQM10250E_GE3` bleibt 250V / 30mΩ, 200V nominal nur 50V Überschwingerreserve. 300V `SQM35N30-97_GE3` hat mehr VDS-Marge, aber ca 97mΩ bei 25C und höheren Gate-Charge-/Leitverlust; Hersteller-Hot-SOA 350ms fehlt. D303/D304 keine garantierte gemeinsame Klemmkennlinie bei 200V und temperaturabhängigem Puls.

**DRINGEND**: Q301-DS-Kurz + D302-Anodenpfad separat am realen Schema/netlist und im Fehlerstrom-/Zener-/Leitungs-/Sicherungsbudget untersuchen. Das neue D306-Parallelbauteil *verdoppelt* Topologie, **nicht** notwendigerweise Fehlerenergie-Festigkeit. Die bereits verfügbare aktive A-Konstruktion enthält D302 K=VS / A=SOURCE_A, womit der B-Befund elektrischer Orientierung nach plausibel ist.

## B – Erkenntnisse und Grenzen

Neue `WEG_B_ROUND3_COTS_AND_ADVERSARIAL_AUDIT_2026-10-15.md`, `safety_b_fmea.py`, `test_safety_b_fmea.py`, `cots_b_compare.py` und Workflow. No-Go für simplen TPSM33620-Q1-Tausch bleibt richtig. Neuer **Single-Point-Fault** Q301 D-S-KURZ plus vorhandenes D302-Forward ist ein Sicherheitsgate (nicht mit D301-offenem Doppelfehler verwechseln). Eine reine Serien-R-Sicherung der SOURCE_A→VS-Nachladeleitung zeigt im *angenommenen* 9V-Pumpenstrom- und 200V-Zenerstrom-Modell widerstreitende R-Grenzen (~385Ω vs 9,55kΩ); das ist kein mathematischer Beweis gegen integrierte Schalter/Limiter, aber ein guter Hinweis gegen einen simplen Widerstandstausch.

LTC4380HMS-4#WPBF als teuer zu qualifizierender Vergleich (Hersteller 4–72V, benötigt HV-VCC-/MOSFET-/Reverse-Pfad); andere ADI-Optionen wurden angemessen als ungeeignet/unqualifiziert dargestellt. B-Workflow existiert, aber **kein erfolgreicher Actions-Run unabhängig bestätigt**. Nicht aus der Existenz von Python-Tests auf elektrischen oder nativen CI-Pass schließen.

**Nächster B-Auftrag**: Fehlerpfade priorisieren und für Q301 short + D302 + D301 + F_MAIN ein beschaffbares **fail-safe** Nachlade-/Strombegrenzungskonzept mit 9-V-Startbewertung nach Herstellerreferenzen finden; gegen A-D306-Topologie unabhängig validieren. Kein generisches IC-Markt-Screening wiederholen.

## C – Hoher Nutzen möglich, aber hartes Funktionsgate

**C1-Draft:** `AP74502HQTA8-7` (AEC-Q100, Hersteller-Normalbetrieb 4–75V), zwei 300V Back-to-back FETs, `TPS26631PWPR` (TI 4,5–60V Industrial/Catalog eFuse, nicht pauschal AEC), `TPSM33620S5QRDNRQ1` (Automotive 3–36V recommended, 40V ABS, integrierte Spule), CSV-BOM mit 28 Positionen inklusive J1/J2. `TripPower_C.kicad_sch`, `TripPowerC.pretty` enthalten einen noch **provisorischen** RDN11-Footprint; BOM sagt `FOOTPRINT_MISSING`, die Datei existiert jedoch – **Status inkonsistent**, Herstellergeometrie nicht verifiziert.

**Hersteller-COTS-Beleg:** Diodes `AP74502Q_AP74502HQ.pdf`, Seite 15: explizit 200V ungedämpfter Load-Dump als **Topologiebeispiel** mit R+60V-Zener für AP-VIN, zweifach externem FET, und Umschaltung zwischen OV cutoff / OV clamp. Es handelt sich **nicht** um eine Zusicherung, dass exakt C1 mit 200V/350ms, Q/FET/PCB/50V Kondensatoren und 125C qualifiziert ist. Diodes spezifiziert VIN bis 75V empfohlen und 80V ABS. Besonders nötig: richtige VCAP/GATE/SRC/EN/OVLO-Beschaltung, OV-Cutoff statt linearem 350ms-Clamp, Hersteller-Timing, AP-VIN 56/60V-Zener-Hot-Pulslast, 200V-Slew und FET heißes Gate-/SOA-/VDS-Ringing.

**Vorsicht bei nachgeschaltetem 36V-TPSM:** Auch diese neue Architektur hat denselben nominalen Modulgrenzwert wie der bei B verworfene *einfache* Swap. AP74502 ist ein anderer, realer Herstelleransatz mit möglichem starken Gate-off, daher *nicht dieselbe No-Go-Entscheidung automatisch übertragen*. Trotzdem ist für C1 **dynamischer VIN-Pad-Maximalwert <=36V im Betrieb und <40V ABS bei jedem transienten Zustand** plus 30V-Restart zu belegen; zusätzlich <=60V für eFuse-VIN im Normalbetrieb, <=67V ABS der TPS2663-Familie. Ein ausgeschalteter Buck ist **kein** Schutz gegen Überspannung an seinem VIN-Pin.

**Thermik/Teilezahl:** Im eigenen 9V/2A + RAW1A-Screen ca 2,235A Eingang bei angenommener η90%; zwei 97mΩ-HV-FETs zusammen ca 0,97W bei 25C, beispielhaft x1,8 hot ca 1,75W ohne eFuse- und Buck-Verluste. TPSM 5V/2A bei 30V, TA125C und kleinem PCB ist **nicht** thermisch freigegeben. Die CSV enthält auch zwei zusätzliche C-Reserve-Positionen, ist keine validierte produktive AUTO/RUN-BOM, kein direkt gleichartiger Count der A-Baseline. RUN-/ACC-/USB-Rückspeisung ist unqualifiziert. `protection_budget.py` enthält nur eigene Sensitivitätstests; kein natives KiCad-ERC/DRC dokumentiert. Kein Layout/3D vollständig.

**Priorität für C**: Hersteller-200V-Topologie zum tatsächlichen KiCad-Pinnetzmodell abgleichen, native KiCad-10 ERC/Netzliste ausführen, offensichtliche Symbol-/Footprint-/BOM-Widersprüche beseitigen, 200V-Ausgangsspitzen und Hot-SOA/9V/30V als auswertbare Gate-Tabelle inkl. starker Quellflanken und Q-Failure untersuchen. Weiterentwicklung nur bei begründeten Grenzen; kein PCB-Bestellgate.

## Übergreifende Prüfpunkte/Entscheidungslogik

- Anforderungen: 9–30V dauernd, 5V/2A, RAW1A Entwurfsziel, 200V/350ms extra ungedämpft, -40…+125°C, extern auswechselbare F_MAIN, AUTO/RUN/ACC/USB ohne Backfeed, OFF<100µA Systemziel.
- Keine implizite Erleichterung beim Lastdump: **200V/350ms** ist eine Peak-/Dauerangabe, noch kein vollständiges Generatorprofil mit Strom-/Flanken-/Energieangaben. Quellimpedanz, Leitung-L, negative Pulse und Wiederholrate sind als Prüfparameter zu bestimmen.
- Gefahrenschutz vor Teilezahl; ein ungefährlicher Neustart ist akzeptabel, Brand/Kabelschaden nicht. Ein selbstberichteter Rechen-/Unit-Test ist keine realweltliche Funktionsgarantie.
- Bis die o.g. Stop-Gates geschlossen sind: **A Hauptpfad, C Forschungs-/Kostenpfad mit realem Herstelleransatz, B unabhängiger Sicherheits-Auditor**. Kein Versuch eines PCB-/Fahrzeug-Releases.
- Nächster Review verlangt: A sichere Q301-short→D302-Pfadantwort, B unabhängige Gegenprobe, C natives Schaltplan-/Pad-/OV-Pad-Gate und belastbare BOM 1/10/100. Von jeder neuen CI einen echten GitHub-Actions-Run und Logs nennen.

### Prüfquellen
- A: `hardware/modules/TripPower_5V2A/WEG_A_ROUND3_D301_BACKUP_PROTOTYPE_2026-10-15.md` und A-D306-Proto/KiCad-10-Workflow.
- B: `hardware/modules/TripPower_5V2A/weg_b/WEG_B_ROUND3_COTS_AND_ADVERSARIAL_AUDIT_2026-10-15.md` und B-FMEA.
- C: `hardware/modules/TripPower_5V2A/weg_c/README.md`, `MARKET_AND_COST_2026-10-15.md`, `BOM_C1_DRAFT.csv`, `TripPower_C.kicad_sch`, `TripPowerC.pretty/TI_RDN11.kicad_mod`.
- Hersteller: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf ; https://www.ti.com/product/TPS2663 ; https://www.ti.com/product/TPSM33620-Q1 ; https://www.vishay.com/en/product/75035/ .
