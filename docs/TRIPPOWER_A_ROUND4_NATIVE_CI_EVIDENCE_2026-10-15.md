# TripPower Weg A – belegter nativer CI-Abschluss Runde 4 (2026-10-15)

**Geprüfter HEAD:** `9ec5fc90325b2c58cdff1b979bc5a80b1f1c5973` auf `design/trippower-a`.

**Original-GitHub-Actions-Run:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38742729871

**Job:** `quantitative-and-native`, Job-ID `116448323659`, GitHub-Endergebnis `completed / success`. Der Joblog wurde über die GitHub-Schnittstelle tatsächlich eingesehen, nicht nur aus dem Vorhandensein des Workflows erschlossen.

## Aus dem Joblog verifizierte Zahlen

- Python `unittest`: **41 Tests ausgeführt**, **41 erfolgreich** (`Ran 41 tests in 0.155s`; Exitcode 0).
- Native KiCad 10 (Basis REV5, D306-Ersatzblatt, Q301-Kurz/D302-Strombegrenzungs-Forschungsblatt): **dreimal `Found 0 violations`** im ERC.
- Native KiCad-Netzlisten/Differenzen: `native_kicad10_netlist_candidate_delta_pass: true` mit allein neuem D306 im ersten Prototyp; `native_10_pin_delta_pass: true` für den zweiten Prototyp mit D302-Netzwechsel, Q307 und R342.
- Die Actions-Stufen zum Netlist-Export, zum Erzeugen der Skriptberichte und zum Sichern der Artefakte waren jeweils `success`.

## Technische Bedeutung und Stop

**Erfolgreich:** Reproduzierbare Rechnung, ERC und konkrete Verdrahtung zweier isolierter KiCad-Varianten; der Original-REV5-Schaltplan wurde nicht geändert.

**Nicht nachgewiesen:** Q301-Kurzschluss-Gesamtsicherheit, da U301-A-Pins und Q302-Sources weiterhin direkt SOURCE_A folgen; BSP135 `Id(VGS,VDS,T)`-Obergrenze/125-°C-SOA; D301/D306 350-ms-Hot-Klemmen; VS-9-V-Anlauf mit realen Hersteller-Ceff-/Pumpenströmen; F_MAIN-Ausschaltvermögen/Ansprechzeit bei 200 V; eine vollständige geroutete PCB, DRC und externe EMV-/Fahrzeugprüfungen.

**Abnahmeentscheidung:** `Q307+R342` ist nur ein **experimenteller D302-Nachladezweig**, keine einzelfehlersichere Schutzarchitektur und keine freigegebene Bestückung. Für den direkten 200-V-Pfad über U301 A/Q302 ist eine unabhängig vorgeschaltete, herstellerqualifizierte Abschaltstufe bzw. ein anderes ganzheitliches COTS-Schutzkonzept notwendig. Eine zusätzliche D306 ohne Nachladestrombegrenzung schützt nicht gegen Q301 D-S kurz. Alle P01–P10 bleiben BLOCKED.

**Verweise:** [technischer Bericht Runde 4](https://github.com/GeneralEdelweiss/TripTracer/blob/design/trippower-a/hardware/modules/TripPower_5V2A/WEG_A_ROUND4_Q301_SHORT_FAILSAFE_PROTOTYPE_2026-10-15.md), [KiCad-Prototyp](https://github.com/GeneralEdelweiss/TripTracer/blob/design/trippower-a/hardware/modules/TripPower_5V2A/01_Protection_LM74930_Q301SHORT_CURRENTLIMIT_PROTOTYPE.kicad_sch), [BOM-Delta](https://github.com/GeneralEdelweiss/TripTracer/blob/design/trippower-a/hardware/modules/TripPower_5V2A/WEG_A_Q301SHORT_D302_LIMITER_BOM_DELTA_2026-10-15.csv), [Q301-Kurzschlussmodell](https://github.com/GeneralEdelweiss/TripTracer/blob/design/trippower-a/tools/trippower_a_q301short_stress.py).
