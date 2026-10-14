# TripTracer V1 – konkreter TLC555-Q1-Timerkandidat (noch nicht für KiCad-Integration freigegeben)

**14.10.2026. Entwurfsrechnung, kein getestetes Schaltungsmodul.** Bezug: [ACC_HOLD_DEADLINE_INTEGRATION.md](ACC_HOLD_DEADLINE_INTEGRATION.md). Verbindlicher Zielpfad bleibt LM74930-Q1 + LMR36520, relaislos. Die bereits bestehenden 01C-TLC555- und Relaisnetze dürfen **nicht** unverändert übernommen werden.

## Kandidat A: TLC555-Q1 aus Fahrzeug-5-V

TI [TLC555-Q1, Rev. D, Jan. 2026](https://www.ti.com/lit/ds/symlink/tlc555-q1.pdf), Automotive, SOIC-8, –40…125 °C. Pin 1 GND, Pin 2 TRIG, Pin 3 OUT, Pin 4 RESET, Pin 5 CONT, Pin 6 THRES, Pin 7 DISCH, Pin 8 VDD. TI nennt nominell `t = 1.1 × R × C` im Monoflop. **Versorgung ausschließlich V5_BUCK_RAW**; damit kein ständig aktiver Timerverbrauch aus BAT+ bei ausgeschaltetem Hauptbuck. Kein Rückspeisepfad von USB-5-V.

### Netz- und Pinvertrag für einen Schaltplanentwurf

| Pin / Signal | Geplanter Anschluss | Sperrpunkt |
| --- | --- | --- |
| 8 VDD, 1 GND | V5_BUCK_RAW / GND, lokale 100 nF direkt am IC | Regler-Start, Spannungseinbruch und Rückspeisung |
| 4 RESET | definierte Freigabe aus ACC-Logik / V5_BUCK_RAW mit Power-on-Reset; nicht unbeschaltet | RESET bei Boot, ACC-Flattern und Abschaltfall |
| 5 CONT | gemäß Herstellerempfehlung lokal gegen GND abblocken | C/Platzierung und reale Herstellerempfehlung prüfen |
| 6 THRES + 7 DISCH | gemeinsamer RC-Knoten, R nach V5_BUCK_RAW, C gegen GND | Worst-case R/C, Leckstrom, Temperatur, DC-Bias |
| 2 TRIG | **nur kurzer negativer Impuls** nach gültigem ACC-Abfall; davor und nachher HIGH | Flankendetektor, Triggerpulse >= Datasheet-Anforderung, Schutz und Verriegelung |
| 3 OUT | HOLD_WINDOW_RAW; über externe UND-Verknüpfung mit MCU_HOLD_REQ und Fahrzeug-5-V-Qualifikation | OUT niemals alleine LM74930-EN treiben |

**Kritischer Herstellerhinweis:** Das Monoflop endet nach Datenblatt nur zuverlässig, wenn TRIG vor Ende des RC-Intervalls wieder mindestens 10 µs HIGH ist. Daher darf **ACC LOW nicht direkt dauerhaft auf TRIG gelegt werden**; sonst kann die geforderte Hardware-Deadline scheitern. Ein retriggerbarer 74HC123 ist kein automatischer Ersatz: auch dort muss wiederholtes Triggern zuverlässig verhindert werden.

### Vorläufige Zeitrechnung (nur zum Dimensionieren)

Der ältere Ansatz R = 2,2 MΩ / C = 10 µF ergibt t_nom = 24,2 s. Bei bloß angenommenen ±5 % R und ±20 % *effektiver* C sind es rechnerisch 18,39…30,49 s. Diese Spanne ist **keine garantierte Grenze**, da Keramik-DC-Bias, Temperatur, zeitabhängiger Kapazitätsverlust, Kondensatorleckstrom und der TLC555 selbst nicht eingeschlossen sind. 10 µF X7R dürfen nicht einfach mit Nennkapazität bei 5 V eingesetzt werden. Große Widerstände machen den Zeitraum zudem anfällig gegen Leckströme. **Kein R/C/MPN-Freeze ohne Datenblatt-Worst-Case und gemessene SD-Abschlusszeit.**

### Minimale Verriegelungslogik

- `ACC_VALID=1`: MAIN_ENABLE wird durch ACC gesetzt; Timer wird definiert vorbereitet und *kein* Nachlauf ist nötig. MCU setzt HOLD_REQ nach Initialisierung rechtzeitig HIGH.
- Echte, entprellte Flanke `ACC_VALID 1→0`: erzeugt exakt einen negativen TRIG-Puls; die Timer-Versorgung muss dabei aus noch laufender Fahrzeug-5-V-Versorgung bestehen.
- `ACC_VALID=0`: `MAIN_ENABLE = V5_BUCK_RAW_VALID AND MCU_HOLD_REQ AND TIMER_OUT AND NOT TIMEOUT_LATCH`. Das UND-Gatter muss echte Logikpegel und definierte Gate-Treibersicherheit liefern. Kein USB-Durchschalten.
- `TIMER_OUT 1→0`: setzt eine hardwareseitige Zeitablauf-Verriegelung bis zu einem neuen gültigen ACC-EIN. Sie muss verhindern, dass MCU-HOLD, flackernde Trigger oder Wiedereinschalten der eigenen 5-V-Versorgung sofort neu starten.
- Sobald MAIN_ENABLE fällt, wird V5_BUCK_RAW ebenfalls fallen. Power-on-Reset und Entladewerte müssen gewährleisten, dass der Fahrzeug-Hauptpfad **nicht selbstoszillierend** wieder einschaltet.

**Offene Architekturfrage:** Die sichere Verriegelung samt ACC-Entprellung und Reset ohne stets aktive BAT+-Logik ist noch nicht ausgelegt. Ein TLC555 plus UND-Gatter alleine **erfüllt deshalb die Timeout-Forderung nicht**. Eine echte Latch-/Flankenschaltung ist vor Integration notwendig. Sollten deren Zusatzteile den Pareto-Nutzen zunichtemachen, sind geeignete Watchdog-/Timer-ICs in vollständiger BOM zu vergleichen.

### Erforderliche Prüfung vor KiCad-Migration

1. Vollständige Stromversorgung des Timers bei 6 V Motorstart, ACC-Abfall und 5-V-Entladung.
2. Trigger-Puls über Fahrzeugspannung/Temperatur, including ACC permanently LOW und 10/100/1000 ms ACC-Glitches.
3. MCU_HOLD dauerhaft HIGH/LOW/hochohmig; Hard-Off nach Zeitlimit unabhängig vom MCU.
4. Power-on-Reset, Brownout, USB-only, BAT+-Verlust und ACC-Neustart; keine Versorgungsschwingung.
5. Extremwertrechnung mit konkreten MPNs; dann ngspice mit realistischen Modellen und laborgemessene Zeitgrenzen.
6. Kosten und Lieferbarkeit für TLC555-Q1 + Flankendetektor + Verriegelung + Gatter **gegen einfacheres alternatives Timer-IC**, keine neue Baugruppe bloß wegen des vorhandenen TLC555 erfinden.

**Kosten:** Noch kein belastbarer Korb bzw. zusätzlicher Baustein freigegeben. **Status: NICHT BELASTBAR.** Nicht als fertig oder ERC-/DRC-clean markieren.
