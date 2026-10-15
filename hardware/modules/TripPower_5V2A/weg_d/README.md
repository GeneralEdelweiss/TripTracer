# TripPower Weg D – dedizierter Load-Dump-Schutz

> **Aktueller technischer Entscheidungspunkt – Round 6 (2026-10-15):** NO-GO, einen einzelnen TLD8S36AH- oder Bourns-SM8S36A-Q-TVS als **vollständigen** 200-V-/350-ms-Eingangsschutz zu benutzen, solange +125°C-Puls-SOA, worst-case Padspannung/60-65-80V-Domänen und TVS-OPEN/SHORT einschließlich F_MAIN-Total-Clearing unbelegt sind. Bourns hat ein ausdrücklich 10-Pulse-Test-A-Performance-Diagramm; Schurter SPT 0001.2509 ist ein 300VDC-Sicherungs-Forschungskandidat. LTC4366-2 bleibt ein nur bedingt laborgeeigneter, teuerer Fallback. **Keine KiCad-/Fahrzeugfreigabe.**
>
> **Jetzt maßgeblich:**
> - [Round-6 technischer Stop/Go-Bericht](WEG_D_ROUND6_CONDITIONAL_STOP_DECISION_2026-10-15.md)
> - [Vollständige Funktions-/Teilpreis-BOM-Matrix 1/10/100](ROUND6_BOM_COST_MATRIX_2026-10-15.md)
> - [Modellrechner](load_dump_scenarios.py) und [Rechentests](test_round6.py)
> - [Chronologisches Findings-Log](FINDINGS_LOG.md)
>
**Separater Forschungszweig:** design/trippower-d-load-dump
**Aufgabe:** möglichst wenige und günstige fertige Bauteile zur Beherrschung eines nicht unterdrückten **200-V-/350-ms-Load-Dump-Pulses** finden, idealerweise *nur* ein dedizierter Schutz-IC oder ein für lange Load-Dump-Pulse qualifizierter Halbleiter. Eine nur für 10/1000 µs spezifizierte TVS gilt **nicht** automatisch als geeignet.

## Hier beginnen

1. [Hersteller- und Marktscreen vom 15.10.2026](WEG_D_LOAD_DUMP_IC_TVS_SCREEN_2026-10-15.md): maßgebliche Anforderungen, Kandidaten, sichere Fehlermodi, echte Herstellerquellen, Kosten und sechs verbindliche Stop-Gates.
2. [Forschungsprotokoll und offene Punkte](FINDINGS_LOG.md): chronologisches Log für alle **künftigen** Recherche-/Mess-/Kosten-/Architektur-Ergebnisse auf diesem Branch.
3. [REV5-Referenz-Baseline](../../REV5_DESIGN_BASELINE.json): **nicht auf Weg D ändern**, sondern nur als gültigen 9–30V/5V2A/200V350ms-Anforderungssatz lesen.

## Momentaner Stand

- **D1 TLD8S36AH:** spezielle Automotive-Load-Dump-TVS, Herstellerbeispiel 202 V/350 ms bei Ta25°C, Reichelt 1,85€ brutto/Einzelstück als Restposten. **STOP** wegen erforderlicher Quellimpedanz, ungeklärter 3,5Ω/4,5Ω-Herstellerdiskrepanz und fehlender +125°C-/Single-Fault-Sicherheitsprüfung.
- **D2 LTC4366-2:** dedizierter Surge-Stopper-IC (9V bis >500V per externer Schwimm-Topologie), zeitgesteuerte Abschaltung/Wiederanlauf; **STOP** wegen großer möglicher linearer MOSFET-Verlustleistung, 9V-Startup, FET-Short und Gesamtstückkosten.
- **D3 LTC4380-2:** schutzfunktionsreicher Alternative; Demo-Platine 0,5A und 250V nur 1ms, **kein** TripPower-2A-/350ms-Nachweis.
- **FMAIN:** externes, austauschbares Sicherungselement obligatorisch. Eine übliche 32V-Automotive-Sicherung darf nicht ohne eigenes DC-Ausschaltvermögen/I²t als 200V-Fehlerabschaltung verbucht werden.

## Abgrenzung zu Weg A/B/C

- Der aktuelle Entwicklungsstand bleibt REV5 auf design/solid-state-power-v1.
- Weg D verändert **keine** KiCad-Dateien, Baseline, Schaltpläne und andere Forschungsbranches ohne ausdrückliche Architekturfreigabe.
- Der Management-Review auf design/trippower-review dokumentiert unter anderem Q301 D-S-Short (Weg A) und AP74502HQ-Eingangsfet-Short mit Durchlass-Bodydiode des zweiten FETs (Weg B/C). Weg D übernimmt dieselben sicherheitsrelevanten Fehlermodelle und legt den Schwerpunkt auf **begrenzte gefährliche Fehlerenergie** statt zwingendem Weiterbetrieb nach Einzeldefekt.

## Regeln für die Fortsetzung

Neue Herstellerdaten, weitere Kandidaten, reale Preissnapshots, Modelle, thermische Prüfungen, FMEA und ggf. später KiCad-Artefakte ausschließlich auf diesem Branch, datiert und mit reproduzierbarem Beleg. **In FINDINGS_LOG.md jeden wesentlichen Befund eintragen** und den Status (UNVERIFIZIERT, HERSTELLER, RECHNUNG, SIMULATION, LABOR, STOP/GO) eindeutig nennen. Bei künftigen GitHub-Arbeiten zuerst dieses README, den aktuellen Screen und REV5/AGENTS.md lesen.

**Wichtig:** Keine vorläufige Marktstudie ist eine Schaltungs-/Fertigungs-/Fahrzeugfreigabe.
