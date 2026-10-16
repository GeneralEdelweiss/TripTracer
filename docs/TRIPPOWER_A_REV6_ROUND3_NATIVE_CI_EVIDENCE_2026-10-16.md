# TripPower Weg A — REV6 Round3 Native KiCad10 / BOM / CI-Nachweis (16.10.2026)

**Verifiziert aus echten GitHub-Actions-Jobs und heruntergeladenen Logzeilen, keine lokale KiCad-Lauffähigkeit behauptet.**

**Letzter geprüfter Schaltungs-/README-Commit:** `715b143f139c38c396ca74e00166f5007c05c5ea`. Der native [GitHub-Actions-Lauf 38864912564](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38864912564) mit **Job 116855394381** ist durch GitHub Jobs API **completed / success** und durch die originalen Job-Logs verifiziert.

**Beobachtete technische Evidenz:**
- **19/19 Python-Unittest** bestanden, `Ran 19 tests in 0.001s`: feste TI Factory UV/OV NO-GO, 32V programmierte rising/falling, 10V Start, 58V-Pinringing-Beispiel, 15uH-10/32V-Spulen-Sättigung/IRMS und +60°C Thermal-Open Gate.
- Drei separate **native KiCad 10 Schaltplan-ERC**: Original REV6 A (25 Plätze), isolierte +1 Sensata-67F080-Temperatur-Forschungsvariante (26 Plätze), isolierte +1 Bourns-72V-RAW-PPTC-Forschungsvariante (26 Plätze). Im Log **dreimal `Found 0 violations`**.
- Native KiCad 10 S-Expression-Netzliste, Pin- und Schutz-FET-Orientierung `native_REV6_protection_pinout_correct:true`, `root_populated_count_derived_from_native_instance_refs:25`, `no_replaceable_or_one_shot_fuse_or_holder_on_tripPower:true`.
- Native getrennte Forschungs-Netzlistendifferenzen `native_thermal_delta_only_T201_1_2_and_SHDN13:true` und `PPTC_ONLY_RAW_BRANCH_NATIVE_NETLIST_VALID:true`, jeweils lediglich eine Position, **nicht in die 25er-Referenz übernommen**.
- Native KiCad 10 BOM Exporte nach erfolgreichem Netlist/IRC für **alle drei Varianten** in `reports/rev6-a-entire-native-bom.csv`, `reports/rev6-67F080-native-bom.csv` und `reports/rev6-RAW-PPTC-native-bom.csv`. 25er Haupt-Export **25 relevante bestückte, exakt aus Modul-BOM übereinstimmende Hersteller-MPNs**, Preis-Regression `native_KiCad_refs_equal_MPN_rows:true`, `all_25_real_MPNs_and_supplier_EUR_price_rows_present:true`. Lieferanten-EUR-Summen **20.7630 /13.9910 /11.0217€ netto pro Modul** bei1/10/100 bestellten Stückzahlen (Herstellerteile, ohne MwSt, Versand, Board, externe/Host-Funktionsblöcke).
- Erfolgreich hochgeladenes CI-Archiv `tripPower-A-REV6-native`, Artefakt-ID `12031075653`, Download [über diesen Lauf](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38864912564/artifacts/12031075653).
- **Kein** KiCad-Board vorhanden, **kein** PCB-DRC ausgeführt. Testerfolg kann nicht als EMV-, 58V/350ms-, 36V/400ms-, +85°C-Safe-Off-, 5V/2A@60°C-, RAW0.5A-, ACC-/USB-/Backup- oder Fahrzeug-Testfreigabe interpretiert werden.

Die fehlenden Hersteller-/Prototypnachweise sind in [REV6_A_ROUND3_FIXED_OVP_25MPN_COMPLETE_2026-10-16.md](../hardware/modules/TripPower_REV6_A/REV6_A_ROUND3_FIXED_OVP_25MPN_COMPLETE_2026-10-16.md) konkret mit benötigten Messpunkten aufgelistet. **Status: NO FAB / NO VEHICLE.**
