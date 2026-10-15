# TripPower Weg D – fortlaufendes Forschungsprotokoll

**Scope:** dedizierter Load-Dump-IC bzw. speziell für 200V/350ms ausgelegter passiver Schutz. Änderungen nur auf design/trippower-d-load-dump.

## 2026-10-15 – Gründung / erstes Screening

**Quelle der Kriterien:** REV5_DESIGN_BASELINE.json auf design/solid-state-power-v1: 9–30V, 5V/2A plus RAW-Aux-Ziel 1A, -40..+125°C, 200V/350ms, F_MAIN austauschbar, Restart bei 30V und sicherer 9V-Start.

**[HERSTELLER + HÄNDLER] D1 TLD8S36AH, Taiwan Semiconductor:** Hersteller-Application-Note AN-1003 weist spezielle Load-Dump-SOA und 202V/350ms bei 25°C aus. TSC-Graph Fig5 fordert bei Vs202V/Td350ms ca. Ri4,5Ω, Text/Tabelle nutzen 3,5Ω und nennen 42,8A / 61,2V; Unstimmigkeit **offen**, nicht übergehen. Reichelt DE TLD8S36AH MAG: 1,85€ brutto bei 1, 1,72€ bei 10, 1,572€ bei 100; Restposten. Quelle https://services.taiwansemi.com/storage/resources/application-note-17/AN-1003_Automotive%20circuit%20protection%20of%20load%20dump%20TVS_A1901.pdf und https://www.reichelt.de/de/de/shop/produkt/tvs-diode_unidirektional_36_v_6600_w_do-218ab-273917 . **[STOP]** wegen Hot-SOA/Gen-Ri/F_MAIN/Einzelfehler.

**[HERSTELLER + HÄNDLER] D2 LTC4366HTS8-2#TRMPBF, ADI:** Dedizierter Hochvolt-Surge-Stopper mit externer MOSFET-Steuerung, 9V..>500V System-Spannungsbereich (NICHT direkt am Pin), einstellbare Clamp/Timer, -2 Auto-Retry nach ~9s, H -40..+125°C; 9V mit hohen Lasten kann den MOSFET ohne Timeout erhitzen (Warnung). DigiKey DE 10,42€/1, 8,174€/10, 6,996€/100 netto (nur IC). Quellen https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf und https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4366HTS8-2-TRMPBF/2825884 . **[STOP]** FET-Hot-SOA, 9V/2A, 30V-Restart, MOSFET D-S short und Zusatzstromschutz unbekannt.

**[HERSTELLER] D3 LTC4380-2, ADI:** Surge-Stopper mit Timer und strombasierter Auslegung. DC2178A-B dokumentiert ISO-Test-A-Anwendung im 28-V-Bereich, aber 0,5A und 250-V-1-ms-Anforderung. 2A + RAW / 200V350ms NICHT erwiesen. Quelle https://www.analog.com/media/en/technical-documentation/user-guides/dc2178af.pdf . **[UNVERIFIZIERT für TripPower]**.

**[HISTORISCHE REFERENZEN]** A LM74930-Q1 (Q301 SHORT → A/SOURCE-Pins/Q302 Hochvolt), B und C AP74502HQ (Eingangs-FET D-S SHORT → zweiter MOSFET Bodydiode → 200V-Ausgang), LTC4364, LTC7860, ST LDP01-35AY; vertiefte Daten/Quellen siehe Hauptscreen und Review-Round4. **[STOP]** Keine Variante derzeit im Fahrzeug freigegeben.

**[KONZEPT]** Bei angenommener konstanter Klemme 61,2V und 200V/3,5Ω entsteht initial ca. 40A TVS-Strom; tatsächliche SOA/Energie muss das 350ms-Zeitprofil berücksichtigen. Zwingend alternative Generator-Ri bis niedrigstem Testwert prüfen. Bei LTC4366 mit 35V Clamp und 1A Last fällt initial (200−35)*1A=165W am Serien-FET an, nicht auf 350ms Dauer ohne SOA-Test zulässig.

### Nächste Schritte / Verantwortlichkeit des jeweiligen nächsten Weg-D-Chats

1. Hersteller wegen 3,5Ω vs 4,5Ω und –40/+125°C-SOA / zulässigen Folgepulsen anfragen bzw. Dokumentation gründlicher auswerten.
2. Reales 200V/350ms-Quellprofil und erwartete Ri_min/Flanken klären. Wenn nicht bekannt, plausible Worst-Cases als **Szenario statt Garantie** berechnen.
3. F_MAIN aus Datenblatt mit möglichem 200-V-DC-Fehlerstrom, Ausschaltvermögen/I²t und Kupfer-/Kabelwärme qualifizieren. Beim TVS-SHORT den 200-V-Puls berücksichtigen.
4. Zwei einfache **volle** Architekturvarianten vergleichen: nur D1-TVS + revisionskonformes regulatorisches Downstream / D2-LTC4366 mit 250/300V-FET und gezielter Frühabschaltung; jeweils 9V-Startup und 30V-Restart messen/simulieren.
5. Nur bei wirtschaftlichem Sicherheitsvorteil KiCad-10-Prototyp mit echtem ERC/DRC und kompletter 1/10/100-Stück-BOM; weder „ein IC löst alles“ noch automatisches Fail-Safe behaupten.

## Schema für spätere Einträge

### YYYY-MM-DD – Thema
- **Status:** HERSTELLER / RECHNUNG / SIMULATION / LABOR / BLOCKED / GO
- **Kandidat / MPN / Variant:** ...
- **Beleg (Datenblattabschnitt/URL/Messdatei):** ...
- **Änderung gegen vorherige Annahme:** ...
- **Fehlerrisiko / F_MAIN / Thermik / 9V / 30V / 200V350ms:** ...
- **Gesamt-BOM-/Kostenwirkung (wenn belegt):** ...
- **Nächstes offenes Gate / Commit:** ...

Hinweis: Dieses Log ist eine Struktur für spätere Arbeitsaufträge. Es aktualisiert sich nicht automatisch zwischen Chats; jeden neuen Befund ausdrücklich committen.
