# TripPower Weg A — REV6 native Round2 Evidenz, 16.10.2026

**Projekt**: `hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_pro` mit unveränderter REV5-Historie außerhalb des Projekts. Fertigung und Straßenfahrzeuge **NICHT** freigegeben.

## Direkt geprüfter GitHub-Actions-Lauf nach OVP-/MLCC-/RAW-/Thermal-Änderungen

- **Erfolgreicher Run**: https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38860188766
- Getestete Revision: `735c39eeee3d682dd7814bfe9e80590277a27499` (seither ggf. Dokumentationsänderungen).
- Jobs API: Job **116840464621**, Status **completed / success**, alle Jobschritte erfolgreich. Raw Logs eingesehen.
- **14/14 Python-Unittest-Regressionen** (`Ran 14 tests in 0.001s`), inkl. OVP RISING/FALLING am 32V-Wiederanlauf, 10V UV, 58V RLC Input-Pin-Ringing, RAW0,5A Eingangslast-Sensitivität und nicht beweisbarer Temperaturfreigabe.
- **KiCad 10.0.6** native Schaltplan-ERC **3× `Found 0 violations`**: (1) 25-positionige neue Hauptschaltung, (2) separate Sensata `67F080` 26-Positionen-Forschungsvariante, (3) separate Bourns `MF-LSMF075/72X-2` RAW-PPTC 26-Positionen-Forschungsvariante.
- Native KiCad10 Netlist-Prüfung: Hauptblatt U201 TPS26631Q-? **TPS26631PWPR** pin- und polaritätsrichtig, `root_populated_count_derived_from_native_instance_refs:25`; Sensata `native_thermal_delta_only_T201_1_2_and_SHDN13:true`; RAW `PPTC_ONLY_RAW_BRANCH_NATIVE_NETLIST_VALID:true`; Ausgang PWR_FAIL Pullup host-seitig, keine Rückspeisung in BAT/RAW/USB.
- Drei native KiCad10 BOM-Exports über die gesamte Root-Hierarchie in CI: `reports/rev6-a-entire-native-bom.csv` (25), `reports/rev6-67F080-native-bom.csv` (26), `reports/rev6-RAW-PPTC-native-bom.csv` (26). Erfolgreiche Export-Logeinträge explizit geprüft. **Alle drei gelten jeweils nur für ihre eigene Variante, die beiden Zusatzoptionen nicht gemeinsam.**
- CI-Artefakt mit JSON/ERC/Netzlisten/BOM/Simulation: https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38860188766 . Kein PCB/DRC, da kein PCB angelegt.

## Späteres erfolgreiches F_MAIN-/PWR55-Regressions-Gate

**Getesteter Commit `a0771bc4c097ee7c28fe469ffd0b78279a0aada9`**, [GitHub Actions Run 38860575434](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38860575434), Job **116841689581**, status `completed/success`; Joblogs geprüft: **14/14 Tests**, **dreimal KiCad10 ERC 0**, nativer Hauptnetzlisten-Guard `no_replaceable_or_one_shot_fuse_or_holder_on_tripPower:true`; Sensata- und RAW-PPTC-Alternativdifferenzen unverändert **true** und **alle drei** native KiCad-Stücklisten erfolgreich exportiert. Der neue Guard prüft **bestückte KiCad-Symbole/Teile**, nicht verbotene Textworte wie `F_MAIN` in der korrekten Beschreibung externer Leitungssicherung. Dies verhindert falsche Freigaben und ebenso Fehlalarme durch die offboard-Pflicht.

## Gesicherte Aussagen und harte Stopps

**Verbessert:** OVP RISING 32,334..33,996V, FALLING29,967..31,943V (Modell ±0,1% 25ppm, ±150nA und TI Sense Ecken). Main-OVP-Wiederanlauf bei **exakten stabilen 32,000V** ohne positive Welligkeit nur **~57mV worst-case** Reserve – **kein garantierter dynamischer Neustart**.

**58-V-Input**: TPS26631 empfohlen max60V, abs67V; Beispiel-Harness/MLCC L/C/Ring übersteigt67V. **Anschluss58V ≠ IC-Pin58V**. Keine ESD-/ISO-/58V-Pulse/SOA-Laborfreigabe.

**+85°C-Safe-OFF**: Sensata `67F080` NO 75..85°C am eigenen Gehäuse, interner eFuse-SHDN ~2,7µA Kontaktstrom; Hersteller prüft Goldkontakt 10mA@5V als Low-Level → nicht als verlässlich klassifiziert. Sensor-zu-Ambient-Temperaturübertragung unbekannt. Kein integrierter Temperatur-Schutzblock in 25er Hauptvariante, **OFFEN**.

**RAW0,5A**: eine Bourns72V-SMD PPTC als eigenständige Forschungsoption, I_hold0,5A@60°C ohne Reserve und0,44A@70°C → keine volle 0,5A-Garantie bis70°C. Kurzschluss-Zeit/PCB-I²t nicht gemessen. Extern F_MAIN fahrzeug-/TripTracer-seitig, **keine** bestückte TripPower-Fuse/-Halter, kein One-Shot. PWR55–56.

**Vollstückliste / 1,10,100 Kostentransparenz:** Hauptvariante 25 reale Plätze, davon **23 mit EUR-Netto-Einzelpreisstaffeln** in `REV6_A_25_PART_ORDER_BOM_2026-10-15.csv`. Teilwarensumme **19,389/12,883/10,1371 EUR** bei1/10/100 **pro Modul**, **exklusive** R202 und L101, Liefergebühren/Steuer, Board/Assembly, 85°C-Qualifikation, RAW-option, Sicherungen/Halter/TripTracer. L101 erhältlich bei LCSC nur quotiert in USD/Mindestabnahme5; R202 Preisland nicht normalisiert. Jede Alternative eigene +1 Positions-/MPN-/Preis-Betrachtung `REV6_A_2026-10-16_BASE_THERMAL_RAW_PROTECTION_COST_CHOICES.csv`. Für eine vollständig bestellbare Serie zuerst Hersteller-fähige Teile inkl. DC-Bias Ceff, L101-Layout/EMV und EUR-Quote 25/25 beschaffen.

**Noch nicht getestet:** reale VOFF-/ON-32V-Wiederstart-Sequenz und Pin-Ringing, 36V/400ms, 58V/350ms, 2A@+60°C Gesamtabwärme inklusive L101, 85°C Ambient-Safe-Off, RAW-Fault-Strom, BAT-off<1mA, USB-M8-/PWR_FAIL-Host Backfeed, FRAM- und SD-Restore, F_MAIN-Harness-I²t, auftragstauglicher TPS26631-EP-Padstack und Spulenlandpattern. **NO FAB / NO VEHICLE**.

**Technischer Änderungsbericht**: [REV6_A_ROUND2_OVP_RIPPLE_TEMP_RAW_2026-10-16.md](../hardware/modules/TripPower_REV6_A/REV6_A_ROUND2_OVP_RIPPLE_TEMP_RAW_2026-10-16.md).
