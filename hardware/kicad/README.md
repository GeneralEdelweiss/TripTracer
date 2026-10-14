# TripTracer - KiCad10

Oeffne **[TripTracer_V1.kicad_pro](TripTracer_V1.kicad_pro)**. Die Rootdatei `TripTracer_V1.kicad_sch` und der Hierarchie-Navigator erschliessen alle **12 aktiven Seiten** in einem Editor.

Der aktuelle **Labor-Entwicklungsstand** verwendet:
- `01G_SIMPLE_INPUT`: S5MC1000V-Verpolschutz und TVS5800-58V-Klemmkandidat; Beschaffung und Fahrzeugpulspruefung offen.
- `01H_ACC_HOLD_GATE` und `01C_HOLD_TIMER`: VIN-gespeister ACC-Start, voraktivierter Timer und optisch entkoppelte MCU-Selbsthaltung.
- `02_5V_Buck`: LMR38020-Q1,5V/2A als Auslegungsziel.
- `03_3V3_USB`: TPS2116-Bordnetz/USB-Prioritaet und MCP1826S-3V3-LDO.
- `04_ESP32_USB`: GPIO21 HOLD, GPIO33 USB-Status, GPIO34 isolierte ACC-Erkennung; weitere Peripheriezuordnung offen.

Normalbereich9-30V, weiches Kaltstartziel etwa9V. Der alte Netzname `HV_PROTECTED_AFTER_EFUSE` ist eine Legacy-Schnittstelle und bedeutet **keine vorhandene eFuse**. Externe BAT-/ACC-Leitungsabsicherung bleibt erforderlich.

[Aktueller Eingangsentwurf, Berechnungen und Nachweise](../../docs/validation/2026-10-14-input-flat-clamp.md). Native KiCad10-Pruefungen laufen in Actions; Schaltplan-PDF, Netzliste, BOM und Berichte werden14Tage archiviert. Bestehende ERC-/DRC-Fehler, reale Thermik/Transienten und TestA202V sind nicht freigegeben. **Kein Fahrzeugbetrieb oder Fertigungsauftrag aus diesem Stand. Keine PCB-Aenderung in diesem Arbeitsblock.**

[TripTracer_V1_README.md](TripTracer_V1_README.md) enthaelt aeltere Zwischenstaende und ist ab dem gekennzeichneten Historienabschnitt **keine aktuelle Schaltungsbeschreibung**. Alte Mikrorelais-, LM74930- und LMR36520-Angaben ersetzen die aktuellen Anforderungen nicht. Die V0.3-Dateien bleiben historische Referenz.


## Kaufteile-Entscheid und Baugruppenstatus (14.10.2026)

[Nachvollziehbarer COTS-Entscheid samt konkreten Stop-Gates](../../docs/COTS_POWER_DECISION_GATE.md) und [maschinenlesbare Ist-Bestueckung](power_selection.json). COTS-first ist verbindlich, bedeutet aber **keinen blinden Austausch** einer bereits verschalteten Reglerstufe durch einen Wandler ohne EN oder mit engerer Spannungsgrenze. Die aktuell verkabelten Daten werden in CI gegen das Auswahlmanifest geprueft. **Eingangsschutz 01G bleibt entwicklungs-/beschaffungskritisch; keine Freigabe.**


### Auswahl fuer den naechsten Schutzprototypen

Der Nutzer hat LM74800-Q1 + STD17NF25 + BUK7Y4R8-60EX und zugehoerige Bauteile fixiert. Die vermeintliche 85V-Zenerdiode ist lt. TI-EVM eine 75V-Schaltdiode von A nach VS: [Entscheid samt BOM und pruefpflichtigen Punkten](../../docs/POWER_FRONTEND_DESIGN_FREEZE_2026-10-14.md), [maschinenlesbare BOM](power_frontend_design_freeze.json). **Noch nicht in der aktiven 01G_Eingangsschutz-KiCad-Schaltung verbaut.**


Die **6 zuvor offenen Standard-SMD-Positionen** der *geplanten* LM74800-BOM haben nun konkrete, beschaffbare MPNs; [DigiKey-Beschaffungscheck](../../docs/POWER_FRONTEND_PASSIVES_SOURCING_2026-10-14.md) sowie [maschinenlesbare Auswahl](power_frontend_design_freeze.json) und [CSV](power_frontend_order_bom.csv). Alle bisherigen Freigabesperren bleiben bestehen.
