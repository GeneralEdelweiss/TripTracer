# TripPower Weg A REV6 Round5 – GitHub Actions Native-Evidence (2026-10-16)

**Geprüfte elektrische Revision:** `3f3dd727452d61aa894ad2f03be03af10174eeec` auf `design/trippower-a`; [Commit](https://github.com/GeneralEdelweiss/TripTracer/commit/3f3dd727452d61aa894ad2f03be03af10174eeec). Beide folgenden GitHub-Actions-Läufe wurden über die GitHub-API als `completed/success` geprüft und die **echten Joblogs** vollständig ausgelesen.

## Echter KiCad-10-Build, A23, A25 und isolierte Forschungen

**[Run 38874846021](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38874846021)**, Job `116887297915`, SHA `3f3dd727...`, `completed/success`.

- Native KiCad10 ERC **viermal `Found 0 violations`**: originale A25, Thermostat A26-Forschung, RAW-PPTC A26-Forschung und Factory-OVP A23.
- **Native** A23-Root `TripPower_REV6_A_FACTORY_OVP.kicad_sch` als Netzliste `reports/rev6-a-factory-23.net` exportiert; Pin-/Net-Semantikcheck meldet u.a. `native_factory_OVP_pin8_ground_and_min_300k_UVLO=true`, `native_mode_auto_retry_and_pgth_gnd=true`.
- Nativer Differenzprüfer zu A25 meldet `native_differential_exactly_seven_changed_pin_connections=true`.
- **Native A23-BOM** `reports/rev6-a-factory-23-bom.csv` via `kicad-cli sch export bom` erzeugt und 23 bestückte `Ref↔MPN↔Footprint` mit Bestell-BOM und Euro-Kalkulation konsistent verifiziert.
- 19/19 ursprüngliche REV6-Regressionen, 15/15 Factory-OVP-Regressionen und **10/10 neue Round5-Regressionen** bestanden.
- Als nicht sicherheitsrelevantes Testsauberkeitsdetail meldet Python bei einem der neuen Tests `ResourceWarning: unclosed file`; Test besteht, Test-Ressourcenstil bei späterer Pflege anpassen.

## Zweiter unabhängiger Workflow

**[Run 38874845997](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38874845997)**, Job `116887297538`, SHA `3f3dd727...`, `completed/success`.

- **102/102 Python-Regressionen** `Ran 102 tests ... OK`, darunter Round5-Tests; wegen Überlappung nicht zu 44 addieren.
- Weitere native KiCad-ERC-Berichte mit `Found 0 violations` und Pin-/Netlist-Delta-Prüfungen `...=true`.
- Ältere Architektur-/REV5-Tests im zweiten Workflow sind nicht als neue A23-58V-Qualifikation zu werten.

## Exakte Grenze des Nachweises

Diese Evidence-Datei ist ein **reiner Dokumentations-Folgecommit** und wurde **nicht** rückwirkend als elektrisch neu geprüfter SHA ausgegeben. Die elektrische A23-Schaltung hat sich seit dem obigen geprüften Commit nicht verändert.

**Keine PCB vorhanden – kein PCB-DRC möglich.** Keine 58V/350ms-Lastabwurf-Hersteller-SPICE- oder Messfreigabe, kein Nachweis der +85°C Umgebungshardwareabschaltung, des selektiven RAW0.5A-Schutzes, der 10V/2A-Heiß-/Kaltstartreserve, des 32V-Restarts unter realem Ringing, des +60°C-2A-PCB-Temperaturbetriebs oder der USB/ACC/Host-Backfeed-Isolation.

Ergänzender detaillierter Befund: [Round5 Fehlerpolitik / A23 / Host-Gates](../hardware/modules/TripPower_REV6_A/REV6_A_ROUND5_MODE_PGTH_A23_HOST_GATE_2026-10-16.md).

**STATUS: SCHEMATIC CI GREEN / NO FAB / NO VEHICLE.**
