# TripPower Weg A – Runde 6: tatsächlich ausgeführte KiCad-10-/Backup-PG-Verifikation (15.10.2026)

**Branch:** `design/trippower-a`, ausschließlich Forschung / **keine Fertigungs- oder Fahrzeugfreigabe**. Vollständiger technischer Bericht: [WEG_A_ROUND6_AP_SRC_TLD_PGOOD_BACKUP_DECISION_2026-10-15.md](../hardware/modules/TripPower_5V2A/WEG_A_ROUND6_AP_SRC_TLD_PGOOD_BACKUP_DECISION_2026-10-15.md).

## Erfolgreiche tatsächlich kontrollierte GitHub Actions

**Run:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38792761830

- **Git-Commit des getesteten Stands:** `acc6136f32dea2012551447fa547c1ca7a4f6750`
- **Job ID:** `116621262594`, Status per GitHub-Jobs-API direkt gelesen: **completed/success**; Log explizit überprüft.
- **Python:** `Ran 58 tests in 0.200s`, erfolgreich. Einschließlich neun Runde-6-Regressionen AP SRC/VIN, 9/10/11 V, TVS-Quellen-R-Widerspruch und Hot-Stop, PGOOD-Logik, Backup-Isolation und Gesamt-BOM-Zählung.
- **Native KiCad 10 ERC:** Fünfmal `Found 0 violations`: (1) originale unveränderte REV5, (2) alter D306-Research, (3) alter Q307-Research, (4) AP74502HQ-Research (**heute als No-Go klassifiziert**), (5) **neuer isolierter PGOOD-Schnittstellenprototyp**.
- **Native KiCad 10 Netzliste:** Prototyp gegen Original exportiert und verglichen, `PG_only_isolated_netlist_valid: true`, `new_fitted_parts: 3`, `one_nonBOM_signal_pad: TP501 TestPoint_Pad_1.5x1.5mm`. Keine sonstigen U101-Buck-/Fahrzeug-Eingangspins verändert.
- **Native KiCad 10 BOM:** beide `kicad-cli sch export bom` erfolgreich, Logs `Wrote bill of materials to 'reports/a-rev5-all-positions-bom.csv'.` und `Wrote bill of materials to 'reports/a-pgood-all-positions-bom.csv'.` Beides als Actions-Artefakt in `reports/` gespeichert; **BOM-Export ist kein Lieferantenpreis**, die 57/58 AUTO/RUN-Variante muss pro DNP-Konfiguration aufbereitet und vollständig bepreist werden.
- Artefakt-Upload erfolgreich (reports-Ordner), keine PCB erstellt und **kein PCB-DRC ausgeführt**.

**Zusätzlich erster erfolgreicher Run:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38792405202 , Job `116620027140` completed/success, **58 Tests, fünfmal ERC 0** und PG-Netzdifferenz bestanden; ohne den nachträglich ergänzten vollständigen BOM-Export.

## Aussagegrenzen

Die CI sichert Syntax, definierte Regressionen und Netzliste/Pins der *isolierten* Alternative, nicht Nachweise für:
- Hersteller-Absgrenze AP74502HQ `SRC≤VIN`: Guard als gezeichnet **NO-GO**, nicht durch ERC rehabilitiert.
- TLD8S36AH **200V/350ms bei125°C**: Ri3,5/4,5Ω Herstellerwiderspruch, 61,2V **25°C Messwert**, 10/1000µs VCmax nicht auf350ms übertragen; F_MAIN DC-I²t/Leiterbahn unbewiesen.
- PGOOD-**Vorwarnzeit**/SD-Erhaltung: TI PG nach 5V-FB-Abfall und Filter; idealer 66µF/10W-Hold-up bis4,6V rund **12,7µs** versus spezifizierter mindestens40µs PG-Filter. **PG ist ein fail-high Hauptversorgungsstatus, nicht alleine eine rechtzeitige Sicherungs-/Backup-Umschaltung.** TripTracer braucht autonomen Backup-Power-Path und gegebenenfalls schnelleres vorauseilendes VIN-Sense.
- PGOOD-Q501-Hot-Leakage/ESD, 3V3_AON Host-Pullup, TP501-Mechanik/Kabel/Stecker, Exzessruhestrom und Zellenergie; keine Knopfzelle angeschlossen oder ausgewählt, keine BAT/ACC/RAW/USB/normal5V-Rückspeisung zugelassen.
- Original REV5 **57 AUTO/58 RUN**, isolierte PGOOD-Probe **60 AUTO/61 RUN**, nur theoretischer zusätzlicher TLD **61 AUTO/62 RUN**. 100%-EUR-Warenkorb **nicht seriös verfügbar**: in der nativen Komplett-BOM fehlen für Bestandsbauteile verbindliche Einzel-/Mengenpreise, die Sicherung/Halter-, Leiterplatten- und Zellenkosten. Bekannter Delta-Preis PGOOD R501+R502+Q501 **0,552€/1; 0,274€/10; 0,1751€/100 netto**. Preise für vollständige Schaltung vor Bestellung mit exportierter BOM pro AUTO/RUN einholen.

**Fazit:** Ein technisch begründeter, reversibler Schnittstellenprototyp wurde geschaffen und nativ verifiziert; HV-A-Prototyp bleibt No-Go, TLD nur Research, keinerlei Fertigung.
