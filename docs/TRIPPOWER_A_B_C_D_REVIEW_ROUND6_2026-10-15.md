# TripPower Round 6 – Status und zielgerichtete Arbeitsaufträge (15.10.2026)

## Verifizierter Aktualitätsstatus

GitHub-Compare mit den **exakten** im vorigen All-Branch-Review erfassten SHAs liefert **identical, ahead_by=0** für:
- A `2f5469131f4cf16f1c5515a9a2c5e04c2719f8b0`
- B `7b6228a1a2b8b68e4b1d5135b5bb9473d92222d4`
- C `bb7cd43c79e42d1c60848da2b06c1e6b6c6a7f53`
- D `0b3bf1bf52cee54f84a0ae9b0fbe0b754c89cb6e`.
- Vorheriger Review `949f20a343bb63bc8af786605b570dde98e4fd0c` ebenfalls unverändert.

GitHub-Suche listet weiter **12 Repository-Branches**. Legacy `design/trippower-80v` hat noch separate echte KiCad-MPNs für `L101=Bourns SRP7050TA-150M` und `C306=Panasonic EEHZC1J470P`, mit 30V/2A-Buck-Peak-Reserve *nicht* sicher nachgewiesen. Legacy-36V hat seit Basispunkt nur Dokumentationsänderungen. Alte `snapshot/*` und `design/01d-input-protection-review-20261013` sind Archiv. `main` und `design/solid-state-power-v1` sind nicht identisch, da main separat weiterentwickelt wurde.

Diese neue Review-Datei ist ein *Management-Dokument*, keine neue elektrische oder thermische Evidenz. Keine Hersteller-, KiCad- oder 200V-Laborexperimente im neuen Turn. **Kein Branch A-D/Legacy wurde geändert oder zusammengeführt.**

## Unveränderte technische Voraussetzungen

- 12/24V-Fahrzeug, regulär **9–30V**, geregelte 5V/2A, geschützter RAW-Aux bis 1A, 200V/350ms unsuppressed Lastabwurf, -40…+125°C, externe austauschbare und passend DC-spezifizierte `F_MAIN`, AUTO/RUN/ACC und USB-Rückspeisesperre.
- **9V bleibt verbindlich**. 10V und 11V nur Sensitivitätsvergleich auf klare reale Positionen-/Thermik-/Kosten-Vorteile, erst nach ausdrücklicher Managementänderung erlaubte Mindesteingangsspannung umsetzen.
- Neue **TripTracer-Knopfzellen-Backupfunktion**, PWR-38–43: Bei plötzlichem Verlust von BAT+/M8 sollen kritische MCU/FRAM/microSD-Schienen mit lokaler Notenergie Daten konsistent sichern und herunterfahren. **Die aktuelle RTC-CR1220 ist kein belegter Stromspeicher dafür.** Backup-Versorgung, SD-Pulsstrom und Flush-Worst-Case sind TripTracer-Aufgaben; TripPower stellt frühzeitigen `PWR_FAIL`/Power-Good, Entkopplung, Fail-Off, sicheren Quellenwechsel und keine Rückspeisung. Zeitpuffer ist auch bei unerwarteter kompletter Trennung erforderlich; bloßes `PWR_FAIL`-Flag ohne Energiepuffer sichert keine SD.
- Ein nicht gefährlicher Geräteverlust kann bei schweren externen Fehlern akzeptabel sein. Keine Annahme, dass jeder MOSFET/TVS/Zener bei 200V Einzelkurzschluss geordnet hochohmig versagt. **F_MAIN DC-Unterbrechung/I²t, Rsrc, Ta, Kabel/L und Pulsform** sind offene Entscheidungsdaten.
- Die Baseline `REV5_DESIGN_BASELINE.json` und das aktive KiCad-REV5 wurden in diesem Turn nicht angefasst.

## Priorisierte nächste Gates / eigenständige Chats

### A – Stop/Go statt Aufbau weiterer Schutz-Passive
AP74502HQ single-FET-HV-Guard aus `WEG_A_ROUND5_FMAIN_VS_AP74502_SYSTEM_DECISION_2026-10-15.md`: 69 AUTO/70 RUN (+12); nativer CI-Pass https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38749865263. Vor weiterer KiCad-Bestückung ***zuerst*** abs.-max. SRC≤VIN bei 9V/30V/OVLO und Versorgung 9.9k; Q401 Bodydiode und 250V VDS, D401 Zener-OPEN/SOA, 125C 2A. Falls Fail oder Hersteller nicht qualifiziert: Guard als NO-GO und **kompakteren Herstellerpfad** gegen D-TVS/anderen vorqualifizierten Sperrblock vergleichen. Zusätzlich minimal rückspeisefreies PWR_FAIL-Ausgangskonzept und Dokumentation des Erkennungszeit-/Energieübergabebudgets. Legacy-80v L101/C306 nur nach explizitem Werterating/Peak-I_limit/BOM-Differenz als möglicher Transfer; **keine automatische Übernahme**.

### B – gefährliche Fehlerenergie und Backup-Zeitbudget unabhängig prüfen
`weg_b/WEG_B_ROUND5_FMAIN_FAULT_ENERGY_DECISION_2026-10-15.md`: konkrete Failure-Matrix von A guard Q301/401 shorts, D-TVS short/open, AP Q1short+Q2-Bodydiode und VS-/Zener-Einzelfehlern. Hersteller F_MAIN min-break/current/time/DC-Arc und Kabel-Thermal **statt I²t-Tabellen-Extrapolation**. Neue PWR_FAIL/RTC-/USB-Backup-Einzelfehler FMEA: Detect absent/late, Zellenspannungseinbruch bei SD-write, Power return/flapping, latch, RUN/VIN0. Unterscheide simulierte fault energy von gemessenem Schaden. Reproduzierbares Code-/CI-Resultat auf B; klare Testpunkte/-signale/Pass-Fail-Limits.

### C – COTS-Neubeginn, nachdem C1 UND C2 als Gesamtlösung NO-GO sind
`weg_c/C2_HV_SAFETY_COST_DECISION_2026-10-15.md`: Kein weiteres AP74502+2FET+TPS26631+LM70840 als die vermeintlich sichere Komplettlösung. Stattdessen drei herstellerbasierte Architekturen mit *allen* Frontend-/5V-/RAW-/EN-/PWR_FAIL-Positionen, echter Lieferfähigkeit und -40..125C, 9V/10V/11V Vergleichen. Eine Option soll einen dedizierten TVS-/Surge-Stopper mit wählbarem simplen 80V-Buck prüfen, ohne D's SOA als bewiesen zu übernehmen. Vergleiche echten Komplettpreis 1/10/100, Montagezeit, Positionen, Verfügbarkeit mit REV5 57/58 sowie A 69/70. Bevor neuer KiCad: fuses, source/hot/dynamic VIN/pins und Fehlerenergie-Gates. Green CI für C2 war reines Python, kein native C2-ERC.

### D – TVS-Entscheidung dokumentiert mit belastbarer OEM-Puls-Energie
`weg_d/WEG_D_LOAD_DUMP_IC_TVS_SCREEN_2026-10-15.md`: TLD8S36AH Hersteller AN-1003 widerspricht sich zwischen SOA-Fig (Ri~4.5Ω) und Tab (3.5Ω) für 202V/350ms @25C. Sicheres 200V/350ms bei **125°C** aus dieser Grafik nicht ableitbar. Herstellerkurve/limits, Zeitintegral E_TVS, I_peak, Vclamp max local pads inkl ringing, alternative MPN (verfügbare 10/100 Stück) und TVS-OPEN/SHORT + wirklich qualifiziertes `F_MAIN` vor KiCad; Ergebnis konditionales Go/No-Go bei expliziter Ri/L-/Ta-Konfiguration. Bei NO-GO LTC4366-2 mit FET-Timer/Hot-SOA und 9/30V untersuchen. Vorläufige Kosten D1 Reichelt 1.85€ **brutto** sind keine Systemstückliste, Restpostenrisiko; D2 LTC4366 ca10.42€ **netto** nur IC, nicht gesamtes Modul. Backup-PWR_FAIL-Signal muss auch bei TVS-Kurz und M8-Abtrennung ausreichende Erkennungs-/Überbrückungszeit zulassen.

## Review-Exit

Von jedem Team **eine klare technische Entscheidung, die neu gegenüber dem bisherigen Bericht ist**, ein reproduzierbarer Beleg (konkrete Herstellerklausel, Signal-/Fallmatrix/Unit-Tests/Netzliste) sowie GitHub-Commit. Keinen weiteren großen Marktbericht oder schematischen Symbolfriedhof ohne geschlossenes P0-Gate. **Keine Fertigungs- oder Fahrzeugfreigabe.**
