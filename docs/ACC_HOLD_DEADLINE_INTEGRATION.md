# TripTracer V1 – ACC/HOLD Hardware-Deadline: Integrationsvertrag

Stand 14.10.2026. **Entwurfs-Gate, keine abgeschlossene Schaltung, keine ERC-/DRC-/Fahrzeugfreigabe.** Ergänzt die vorhandenen DC- und Transientenversuche; ersetzt weder KiCad-Design noch Messung.

## Ausgangslage / nachgewiesenes Problem

Die 12 idealisierten Zeitverläufe in `docs/validation/2026-10-14-acc-hold-transients/` zeigen: Bei dauerhaftem MCU_HOLD bleibt die simulierte Fahrzeugversorgung eingeschaltet. Die bisherige ACC-OR-(HOLD UND Fahrzeug-5-V)-Logik besitzt **keine MCU-unabhängige Zeitgrenze**. Der alte TLC555-Relaisentwurf darf nicht als fertiger Ersatz übernommen werden.

## Verbindliche Systemzustände und Signale

- `ACC_PROTECTED`: geschützter, hochohmig ausgewerteter Fahrzeugeingang (M8 Pin 1); Schutz und 6-/9-/30-V-Schaltschwellen noch zu spezifizieren.
- `V5_BUCK_RAW`: ausschließlich vom Fahrzeug-Hauptbuck erzeugte 5 V **vor** USB-Quellenumschaltung; niemals aus USB rückspeisen.
- `MCU_HOLD_REQ`: MCU-Anforderung an ein begrenztes Nachlaufzeitfenster, keine direkte Freigabe des LM74930 ohne Hardware-Qualifikation.
- `HOLD_WINDOW_OK`: nur während des hardwareseitig freigegebenen Nachlauffensters aktiv. Muss nach Ablauf unabhängig vom GPIO auf LOW gehen.
- `MAIN_ENABLE`: Aktivierung des LM74930, logisch aus ACC oder gültiger, fahrzeugqualifizierter Nachlaufanforderung abgeleitet.

Angestrebte Boolesche Funktion (nur logischer Vertrag):
```
MAIN_ENABLE = ACC_VALID OR
              (V5_BUCK_RAW_VALID AND MCU_HOLD_REQ AND HOLD_WINDOW_OK)
```
Vorsicht: die Gleichung ist **keine** geprüfte Beschaltung. Der Hauptbuck muss bei ACC-Einschalten auch mit 0 V `V5_BUCK_RAW` starten können; ein nur von V5_BUCK_RAW gespeister HOLD-Zweig darf Bootstrapping nicht verhindern.

| Situation | Erwartetes Verhalten |
| --- | --- |
| Fahrzeug BAT+ vorhanden, ACC EIN | Hauptbuck startet ohne MCU; HOLD-Timer wird für den nächsten ACC-Abfall vorbereitet |
| ACC AUS, gültiges MCU-HOLD, Zeitfenster läuft | Logik hält Versorgung bis Dateiabschluss oder Deadline |
| ACC AUS, HOLD wird gelöscht | Hauptpfad wird abgeschaltet (Entladezeit separat prüfen) |
| ACC AUS, MCU-HOLD hängt dauerhaft HIGH | Spätestens mit Deadline OFF; kein automatisches Wiederanlaufen nur durch HOLD |
| Nur USB-C angesteckt, BAT+/ACC fehlen | Kein Fahrzeug-Hauptpfad aktiv; Flash-/Service-Versorgung bleibt separat möglich |
| ACC kehrt zurück | Neuer Start/Reset des Timeout-Fensters nur durch echten ACC-Zustandswechsel |
| ACC flattert | Definiertes Debounce/Reset-Verhalten; kein unbegrenztes Verlängern durch Störimpulse |
| BAT+ fällt aus, ACC bleibt aktiv | Kein unzulässiges Rückspeisen aus ACC oder USB; geordneter Reset/Brownout zulässig |
| Unter 6 V | Definierter Reset/Brownout zulässig, kein unkontrollierter MOSFET-Halbleitbetrieb |

## Wichtige Timer-Architekturentscheidung – noch offen

**Nicht den bestehenden MCU-HOLD-Zustand als Trigger eines erneut anstoßbaren Monoflops verwenden.** Ein dauerhaftes HIGH oder flackerndes Signal darf die Deadline nicht periodisch neu starten. Das Zeitfenster muss durch den echten Übergang `ACC_VALID: EIN → AUS` gestartet werden und entweder *nicht retriggerbar* sein oder mit einer unabhängigen Maximalzeit verriegelt sein. Bei ausgeschalteter Hauptversorgung gibt es keinen Always-on-Zeitgeberbedarf.

Der frühere TLC555 mit 2,2 MΩ / 10 µF war für eine **nominelle** Zeit von 24,2 s dokumentiert; Temperatur, MLCC-DC-Bias, Leckströme, Trigger und Reset sind ungeprüft. Diesen Wert **nicht** als garantierte Maximalzeit verwenden. Vor IC-Festlegung zwei Optionen mit vollständiger BOM und Mess-Gates vergleichen:

1. Einfaches nicht-retriggerbares Monoflop aus ACC-Abfall mit klarer Reset-Logik, niedrigem OFF-Strom und garantiertem Zeitfenster über Temperatur/Toleranzen.
2. Unabhängiger Timeout-/Watchdog-Baustein mit definiertem Enable/Reset, falls Option 1 eine unzuverlässige RC-Extremwertrechnung oder unerwünschte Retriggerbarkeit erfordert.

Eine feste Deadline in Sekunden wird **erst** nach gemessener schlechtester SD-Flush-/FAT32-Abschlusszeit und Bauteiltoleranz definiert. Software muss früher abbrechen bzw. sauber abschließen können. Bei Deadline-Ablauf darf verlorener letzter Datensatz auftreten; Brandschutz/Leitungsschutz haben Vorrang.

## Unabdingbare Integrations- und Prüf-Gates

1. Klären, welcher Versorgungszweig Timer und ACC-Flankendetektor während ACC AUS tatsächlich speist, **ohne** das <100-µA-BAT+-OFF-Ziel zu verletzen. Timerverlust muss sicher OFF ergeben.
2. Der vorhandene LM74930-EN-Eingang braucht nachgewiesene Spannungsschwellen, kalte Startfähigkeit, Schutz bei negativen/positiven Fahrzeugpulsen und kein unzulässiges USB-/ACC-Backfeed.
3. P-MOS-Leckstromproblem aus `ACC_HOLD_VEHICLE_SOURCE_REVIEW.md` bleibt: onsemi-BSS84-Stress führte zum ON-Fehler. Nur konkreten Hersteller-MPN anhand Temperatur-Maximalwerten auslegen.
4. Für 6 V Start, 9/12/24/30 V, heiß/kalt, MCU-GPIO HIGH/LOW/hochohmig, USB-only und ACC-Störpulse eine kombinatorische DC- und zeitabhängige Prüfmatrix erzeugen; besonders **stuck-HOLD über reale Sekunden**, nicht bloß 200 ms.
5. Erst danach KiCad-10-Unterseite mit realen Netzen, Pins, Bibliotheken und Kostenvergleich erstellen; bestehende Relais-/AUX-/TPS26631-Zweige erst nach elektrisch vollständigem Ersatz entfernen.
6. Projektweiten ERC, DRC, Netlist-Parität und die Hardware-/Fehlereinspeiseversuche dokumentieren. Keine simulierte Logic-Funktion als Hardware-Freigabe bezeichnen.

**Kostenstatus:** Kein zusätzlicher Baustein beschlossen, keine neue MPN gewählt, aktuelle Stück-/Warenkorbkosten **NICHT BELASTBAR**. Der Vergleich muss ohne Doppelzählung entfallender Relais-/AUX-Teile erfolgen.
