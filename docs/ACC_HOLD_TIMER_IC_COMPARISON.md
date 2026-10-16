# TripTracer V1 – Zeitgebervergleich für relaislose ACC/HOLD-Deadline

Stand: 14.10.2026. **Datenblatt-/Beschaffungsvergleich, kein elektrisch fertiger oder verifizierter Schaltplan.** Ergaenzt `ACC_HOLD_DEADLINE_INTEGRATION.md` und `ACC_HOLD_TLC555_CANDIDATE.md`. Verbindliche Versorgung: LM74930-Q1 + LMR36520, 9–30 V Dauer, 6 V Start, Fahrzeug-/USB-Strompfade getrennt.

## Vergleich

| Kandidat | Einschätzung | Entscheidende Einschränkung |
| --- | --- | --- |
| TI TLC555-Q1 | günstiger/handlötbarer Altentwurf (SOIC-8), nominell 1,1 RC | TRIG darf nicht dauerhaft LOW bleiben; für sichere Deadline Pulsformung und Sperre nötig |
| ADI **LTC6993-3** | bevorzugter **Laborkandidat**: fallende Triggerflanke, **nicht retriggerbar während laufendem Puls**, 2,25–5,5 V, programmierbare 1 µs bis 33,6 s, TSOT-23-6 | Nicht retriggerbar bedeutet **nicht** dauerhaft gegen spätere neue Trigger gesperrt! Erneute ACC-Flanke nach Ablauf kann neuen Puls auslösen; externer ACC-Zustandsfilter/Arming/Interlock nötig. Datenblatt-Triggerpegel/Timing und maximale Zeit prüfen. Teurer und schwieriger handzulöten. |
| TI SN74LV221A-Q1 | -40..125°C, 2..5,5 V, zwei Monoflops, Schmitt-Trigger, TSSOP-16 | zwei große RC-Timing-Netzwerke möglich, kein automatisch vorhandener Wiederanlaufschutz; Leckstrom-/Toleranzrechnung für Sekunden nötig |
| TI SN74LVC1G123 | kleines Schmitt-Trigger-Monoflop | ausdrücklich **retriggerbar** (langes Störflattern kann Dauerbetrieb bewirken), ungeeignet ohne Verriegelung |
| TI TPS3431-Q1 | Automobil-Watchdog, einstellbare Überwachung | Watchdog prüft Impulse und ersetzt keine garantierte maximale ACC-Off-Nachlaufzeit; kein direkter Kandidat |

**Datenquellen:**
- ADI LTC6993-Familie: https://www.analog.com/media/en/technical-documentation/data-sheets/LTC6993-6993-1-6993-2-6993-3-6993-4.pdf – Tabelle der vier Trigger-/Retrigger-Varianten, Grenzzeiten.
- TI SN74LV221A-Q1: https://www.ti.com/product/SN74LV221A-Q1
- TI SN74LVC1G123: https://www.ti.com/product/SN74LVC1G123
- TI TPS3431: https://www.ti.com/product/TPS3431
- DigiKey DE LTC6993CS6-3#TRMPBF: https://www.digikey.de/de/products/detail/analog-devices-inc/LTC6993CS6-3-TRMPBF/2404472

## Lieferanten-Momentaufnahme (keine Kostenfreigabe)

DigiKey DE listete LTC6993CS6-3#TRMPBF mit 596 Stück lagernd: 4,15 EUR netto / Stück, 3,164 EUR netto ab 10, 2,6426 EUR netto ab 100; 4,9385 EUR inklusive 19 % MwSt. pro Einzelstück, jeweils Versand nicht enthalten (Web-Abfrage am 14.10.2026). Diese Zahl ist **nur der Timer**, nicht Flankenschutz, Sperre, Dioden, Logik, Widerstände, PCB oder Beschaffungsgesamtpreis. Reichelt-Alternativen und vollständiger Korb bleiben zu prüfen. Kein Gesamtkostenvergleich der vollständigen drei Lösungsvarianten möglich; Kostenstatus **NICHT BELASTBAR**.

## Minimale Funktionsarchitektur für die nächste KiCad-Unterseite

```text
ACC (geschützt, entprellt) ---+----> MAIN_ENABLE via ACC-Zweig
                              +----> ARM / Flankendetektion
                                          |
                                          v
                         LTC6993-3 FALLING EDGE / t_MAX
                                          |
                    V5_BUCK_RAW_VALID AND MCU_HOLD_REQ
                                          |
                                          v
                              HOLD_GRANTED (mit Sperre)
                                          |
                                          v
                           OR --> LM74930_ENABLE
```

- Anfang bei ACC-EIN: Fahrzeugversorgung muss **ohne** Fahrzeug-5-V- oder MCU-HOLD-Qualifikation anlaufen können.
- Bei ACC-AUS: timergetriggerte Freigabe nur bei zuvor erkanntem gültigem ACC-EIN. Versorgung des LTC6993 aus **V5_BUCK_RAW vor USB-Mux**.
- Beim Ablauf: HOLD_GRANTED fällt unabhängig vom festhängenden MCU-HOLD; Main-Enable wird LOW. Der nachfolgende Spannungszusammenbruch darf weder das Fahrzeug-5-V-HOLD-Netz noch ein erneutes Timingfenster selbst starten.
- Bei ACC-Kontaktprellen/Störimpulsen: validierte Debounce-Schwellen und **kein** erneutes Nachlaufen nach bereits abgelaufener Deadline, ohne definierten echten ACC-Neustart. Nicht-Re-Triggerbarkeit des Timer-IC allein genügt ausdrücklich nicht.
- USB-only: V5_BUCK_RAW bleibt 0, Hold nicht aktiv und kein Fahrzeug-Enable; USB kann unabhängig MCU/Service versorgen.
- Timing noch **nicht auf 24 Sekunden festgelegt**: reale maximale SD-Abschlusszeit, Temperatur, Timerextremwerte und Softwareabschaltung erfassen.

## Offene Gates vor Integration / ERC

1. Aus konkretem LTC6993-3-Datenblatt SET-/DIV-Widerstandsnetz, OUT-POLARITY, Trigger-Pulsbreite, Spannungsschwellen, Fehlerzustände, Temperaturklasse und Nachlauf-Maximalzeit berechnen; Hersteller-MPN/Footprint/Pinout nativ prüfen.
2. Arming/Sperre/ACC-Entprellung als **wirkliche Schaltung**, nicht bloß Boolesche Funktion, festlegen. Insbesondere Re-Arm nach Timerablauf, bei schwebendem MCU-Pin und bei brownout testen.
3. Validieren, wie V5_BUCK_RAW während des gesamten Nachlaufs verfügbar ist; eine Abschaltlogik darf keinen gefährlichen positiven Feedback-Loop erzeugen.
4. 6-V-Start, 9–30-V-Normalbetrieb und Pulse/ESD am ACC-Zweig sowie fehlerhafte USB-Rückspeisung mit echten MPNs, Leckstrom-/Temperaturwerten und Fault Injection prüfen.
5. Reale Komplett-BOM für TLC555-Q1 gegen LTC6993-3 vs. SN74LV221A-Q1 mit Reichelt/anderen deutschen Händlern, Porto, Eigenbestückung und 2/10/100 Stück berechnen.
6. Erst danach sichere KiCad-Hierarchie, Footprints, KiCad-10-ERC/DRC und Laboraufbau. **Der alte Relais-/AUX-/TPS26631-Entwurf bleibt bis zum vollständigen Ersatz unangetastet.**

**Vorläufiges Fazit:** LTC6993-3 ist der beste Kandidat zum Erproben eines definierten fallenden Einmaltriggers. Er **ersetzt keine ACC-Sperre** und muss wegen des hohen Einzelpreises noch gegen den TLC555-Altentwurf mit vollständiger externer Beschaltung wirtschaftlich bestehen. Keine neue Serien-BOM, Freigabe oder Teilebestellung.
