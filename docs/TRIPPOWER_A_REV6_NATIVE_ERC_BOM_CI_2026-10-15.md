# TripPower REV6 Weg A — nativer KiCad-10-CI-Qualitätsnachweis 2026-10-15

**Branch `design/trippower-a`**, separat vom unveränderten historischen TripPower-REV5.

## Echte verifizierte, erfolgreiche Actions-Läufe
- **Später erfolgreicher Lauf** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38814076115 , getesteter Commit `48433b193c9c5d96a1253be65abe7876aea2ba8d`, Job **116694234743**. GitHub Jobs API status **completed/success** und vollständigen Log gelesen:
  - **9 Python-Regressionstests bestanden** (`Ran 9 tests in 0.001s`).
  - **Native KiCad 10.0.6 ERC: `Found 0 violations`** für Root-Projekt mit beiden Seiten.
  - `native_REV6_protection_pinout_correct: true` (eFuse PWP20, 100V-B-GATE/Q202-DRV, UVLO/OVP, SHDN13 NC, ILIM6.04k).
  - `native_PGOOD_external_fail_high_no_main_backfeed: true`.
  - `root_populated_count_derived_from_native_instance_refs: 25`.
  - **Nativer BOM-Export erfolgreich** (`Wrote bill of materials to 'reports/rev6-a-entire-native-bom.csv'`), enthält genau 25 tatsächlich bestückte Positionen.
  - GitHub Actions-Artefakte enthalten Model, ERC-JSON, native Netzliste, Pin-Checker-Ausgabe und native BOM.
- Erster bestandener Lauf dieser Schaltung: https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38813768801 , SHA `17318999a066a2ac511f59eaf256ce154045157b`, Job **116693210258**; ebenfalls 9/9, ERC0, nativer Prüfer25/25 und BOM-Export.

## Was ein grüner Test ausdrücklich NICHT beweist

Native ERC0 und richtige Pinnetze beweisen **keine** Qualifikation für 58V/350ms am Kabel, −20..+70°C, +60°C bei 5V2A, sichere Geräteabschaltung bei +85°C, Schutz unter FET-Short/RAW0.5A, USB-Rückspeisung, +32..36V Wiederanlauf, F_MAIN-I²t, BAT+-OFF<1mA oder realen M8/Stecker/Kabellayout.

Der TPS26631 ist **Industrie-eFuse**, nicht für AEC-Q100 als echter Q1-Typ belegt. **58V am IC bedeutet lediglich +2V zur empfohlenen 60V-Obergrenze, +9V zur 67V-Absolutgrenze; Ringing und Kabelinduktivität müssen vor Qualifikation gemessen werden.** SHDN13 ist nach TI-Hersteller-Funktion bei interner Pull-up-Beschaltung **floating**, keinesfalls VIN_FUSED (Absolute max5.5V).

**Verbindlicher offener +85°C-Stop:** Die U201-Tj-Notabschaltung bei typisch~165°C ist **kein** gemessener/garantierter Abschaltpunkt bei 85°C Geräte-Umgebung. Der Prototyp besitzt noch keine separate qualifizierte Temperaturschaltung. Vor Fertigung müssen Ambient-T-Sense/Derating-Pfad, Ceff/Isat, 5V/2A+60C Last, eFuse-PWP20-/L101-Hersteller-Landpattern, Leitungs-/RAW-Absicherung, Modulsteckverbinder, USB-Host und externe BAT/ACC Sicherung komplettiert werden. **PCB existiert nicht**, PCB-DRC weder möglich noch behauptet.

**BOM- und Preiswarnung:** `REV6_A_25_PART_ORDER_BOM_2026-10-15.csv` enthält 25 exakte MPNs; nach verifizierten Teilquotes 14 von25 preisbelegt, **11 unbepreist**. Bekannte TEILSUMME EUR netto je Gerät **15,789 / 10,632 / 8,4331** bei Stückzahl 1/10/100 – *keine vollständige einkaufbare BOM*. Vor allem ist die Murata `GRM32ER71E226KE15L` 3×22uF **EOL und bei Mouser DE Bestand0**, daher ein qualifizierter Ersatz Pflicht. Nicht ergänzte eFuse-/Buck-Komponenten und Kabel/Halter/thermische Zusatzteile haben noch keinen endgültigen Herstellerwarenkorb.

**Ergebnis:** erfolgreich geprüfter **isolierter KiCad10-Schaltplan-Prototyp**, bewusst **keine Fertigungs-, Sicherheits-, Fahrzeug- oder SD-Backup-Freigabe**.
