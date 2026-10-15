# TripPower Weg B – PWR_FAIL elektrische Schnittstelle R6 (Vorschlag, nicht implementiert)

**Geltung:** Review-Runde 6 und gemeinsame `POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md`; nur Weg B. Diese Signaldefinition ist ein Interface-Kontrakt für die spätere gemeinsame Abstimmung, kein bestückter KiCad-10-Pin, kein zertifiziertes Timing und keine ausgewählte Knopfzelle. Produktions-Baseline bleibt 9–30 V.

## Polarität und fail-safe physikalischer Default

- **Signalname `PWR_FAIL`, aktiv HIGH = Fahrzeugversorgung nicht sicher verfügbar oder Schutzstufe hat abgeschaltet; LOW = nachweisbar Power Good**. Bewusst umgekehrt zu aktiv-low `PWR_FAIL_N`: Vollständiger Ausfall von TripPower muss PASSIV den Fehlerzustand ergeben.
- **Open-Drain NMOS am TripPower-Ausgang**: Source GND, Drain am Signal. Es darf ausschließlich bei bestätigtem Power Good nach GND ziehen; im UV/OV/OFF, VIN=0, PIN unversorgt oder Modul abgesteckt muss der Drain HIGH-Z sein. Kein aktiver HIGH-Treiber und **kein** 5V/VIN-Pull-up in TripPower.
- TripTracer stellt **100 kΩ nominal Pull-up nach `V_BK_3V3`** bereit. Die notversorgte, gegen Batterie/USB/RAW rückspeisegeschützte 3,3V-Domäne muss bei normaler Versorgung ebenfalls vorhanden sein. Vorläufiges Sollfenster `V_BK_3V3=3,0...3,6 V`; Datenblatt-VDDmax des tatsächlichen MCU/FRAM-Pins und Überschwinger nachhalten.
- **Logikpegel als zu erfüllende Schnittstellenziele, nicht als Bauteildaten:** LOW ≤0,30V bei ≤36µA gesenktem Pull-up-Strom; Open-Drain-Leckstrom ≤1,0µA *über −40...+125 °C*, im unversorgten Zustand und bei BAT/USB-Beaufschlagung. Daraus idealisiert HIGH ≥3,0V−(1µA×100kΩ)=2,90V. Tatsächliches Eingang-VIH/VIL und ESD-/Latch-up-Grenzen des TripTracer-Pins prüfen.
- Mit maximal 200pF Signalkapazität ist das rein ohmsche 10→90%-Anstiegszeitbeispiel `ln(9)×100kΩ×200pF = 43,9µs`, ohne Draht-/ESD-/Filter-/Input-Kapazitätsreserve. Maximaler normaler Sinkstrom bei 3,6V=36µA; wenn TripPower aus ist, ist der Pull-up nicht mit einem ständig leitenden MOSFET zu entladen. Kein 100µA-BAT-OFF-Budget als bereits bestanden ausgeben.
- Externe Steckkontaktbelegung, GND-Bezug und Signalrichtung sind **TBD**. Ein ungeeigneter 200-V-Halbleiterausfall in TripPower darf keine 200 V auf den `PWR_FAIL`-Draht und über GPIO-ESD nach `V_BK_3V3` speisen: physikalische Leitungsführung, 200V-HV-Trennung und Einzelkurzschluss-Schutz sind gesonderte P0-Nachweise. Open Drain allein ist **keine galvanische Trennung**.

## Fehlersignale und zeitliche Anforderungen

| Zustand | PWR_FAIL | unabhängige TripTracer-Erkennung | Aktion |
| --- | --- | --- | --- |
| Gesund, 9–30 V und 5V nutzbar | LOW, TripPower sinkt | Lokaler 5V-PG gut | normaler Betrieb |
| TripPower schaltet wegen OVP/UVP ab | HIGH durch Drain-Freigabe | Lokaler 5V-Supervisor bei VMAIN-Abfall | IRQ / Lasten aus / kritische Schienen puffernd |
| M8/BAT+ schlagartig unterbrochen | HIGH sobald Drain hochohmig | Lokale UV + sofort verfügbarer Backuppfad | **0 µs Vorwarnung erlaubt**; Datenenergie bereits auf TripTracer vorhanden |
| PWR_FAIL-Draht durchtrennt / TripPower ausgebaut | HIGH | unabhängige lokale UV | korrektes FAIL, falls Pull-up vorhanden |
| PWR_FAIL dauerhaft LOW kurzgeschlossen | **Falsch GOOD (kritischer Einzelfehler)** | separater lokaler UV-Supervisor mit **anderem IRQ/Hardwarepfad** | Notbetrieb auch ohne TripPower-Signal |
| PWR_FAIL dauerhaft HIGH/Transistor OFF | Falsch FAIL, Verfügbarkeit | 5V-PG gut | keine unkontrollierte Notzellenentladung; Diagnose |
| USB verbunden, VIN=0 | HIGH: Fahrzeug fehlt, obwohl USB 5V bereitsteht | USB-Quelle separat identifizieren | USB/MSC nicht mit Fahrzeug-Good verwechseln |
| Fahrzeug kehrt während SD-Speicherung zurück | LOW nach gefilterter Freigabe | lokaler SAVE-Latch bleibt aktiv | keine zweite Mount-/Dateioperation bis Abschluss |

**Zeitziele zur Verifikation:** TripPower-Fault-Freigabe des Drains ≤100µs nach *tatsächlich gültigem* internen UV/OV-Pegelerkennen; lokaler unabhängiger UV-Detektor ≤100µs; Backup-Power-Mux ≤100µs; IRQ-Softwarebeginn ≤1ms. Alle Werte sind **Entwicklungsziele**, keine TI/Diodes garantierten Gesamtzeiten, und treffen bei einem sofortigen M8-Abzug keine Zusage auf Vorwarnung. Die notwendige Spannungsschwelle am Fahrzeug- oder 5V-Monitor darf erst nach nachgewiesenem Buck-Droop, Lastwechsel und minimal zulässiger MCU/SD-Spannung bestimmt werden. Ein beispielhaftes `V5_WARN=4,7V` wäre ohne zugehörigen Temperatur-/Rampen-Proof eine frei erfundene Funktionsgarantie.

**Wiederanlauf:** `SAVE_IN_PROGRESS` wird auf TripTracer verriegelt, bis die begonnene FRAM/SD-Transaktion verifiziert beendet oder als unvollständig markiert ist. Stabilitätsfenster als **Testziel 500ms** vor neuem Mount/Logging. Beim Wiederanlauf nach gescheitertem Flush nur Read/Repair-Mount und Transaktionsmarker; nicht stillschweigend 'SD sauber' behaupten. Wiederholtes ON/OFF und MCU-Reset prüfen.

**Wichtig:** `PWR_FAIL` und der lokale UV-Detektor müssen über getrennte IRQ-/Hardwarepfade zur MCU beziehungsweise Backup-State-Machine führen. Zwei parallel geschaltete Open-Drain-Pins mit dieser aktiv-HIGH-/LOW=gesund-Polarität können einen HIGH-Fehler gegenseitig maskieren und sind keine Wired-OR-Fail-Logik.

## Backup-Energie als mathematische Anforderung

TripTracer hält **nur** MCU + FRAM + SD + notwendige Hilfslogik gepuffert; Display, GNSS, Hintergrundbeleuchtung, RAW und 5V/2A-Hauptlast werden abgeschaltet. Vorläufige ~3s aus der Spezifikation sind **keine** gemessene SD-Fertigstellungszeit. Für Hersteller- und Messanforderungen:

- `E_load = Integral(V_critical(t)*I_critical(t) dt)`, inklusive SD-Write-Peaks, Supervisor/Regler und gegebenenfalls Migration der Versorgung.
- `E_backup_usable >= E_load / eta_path × margin`, und zusätzlich **Spannungs-/Impulsstromfenster** an ESP32-S3/FRAM/SD bei −40...+125°C, Zellalterung, Innenwiderstand/ESR; Primärzelle NIE laden.
- Reproduzierbares **nur hypothetisches** Beispiel: `3,3V × 0,1A × 3s = 0,99J`, dazu drei SD-Peaks **zusätzlich 0,2A für je20ms** `0,0396J`; bei angenommenem η=80% und Marge1,25 => **1,60875 J am Backup-Quellfenster**. Ein idealer, ansonsten verlustfreier C von 3,6V auf 2,9V bräuchte `C=2E/(3,6²−2,9²)≈0,707F`; reale Ceff/ESR erhöhen Bedarf. Weder 100mA noch 3s sind gemessen; kein Vorschlag, eine 0,707F-Cap oder RTC-CR1220 ohne weitere Prüfung zu verbauen.
- Reales Zeitbudget als Pass-Gate: `T_hold_measured >= T_detect_max + T_switch_max + T_IRQ_max + T_flush_measured_worst + T_margin`. Ohne **gemessenes** `T_flush_worst` bleibt das Gate explizit FAIL/UNKNOWN, unabhängig davon, ob `PWR_FAIL` elektrisch korrekt ist.

**Prüfplan P0:** VIN0/M8 pull, Q301-/TVS-Kurz, TVS offen, Controller-Versorgungsverlust, GPIO kurz LOW/HIGH, MCU reset während SD-Write, USB-only und Rückkehr/Flattern während SAVE. Jeweils zeitgleich `PWR_FAIL`, lokaler UV-IRQ, `V_BK_3V3`, `V5_MAIN`, Strom zur SD (Peaks), FRAM-Marker, SPI/SD-Linie, F_MAIN/Ladeenergie und Isolationsströme aufnehmen. Schutz bei 200V nur in geschützter HV-Testumgebung. Vergleiche die tatsächlichen Spannungs- und Zeiten mit den ausgewählten IC-Herstellergrenzen; ohne diese keine Freigabe.

**Reproduzierbar:** `round6_safety_backup_gate.py` und `test_round6_safety_backup_gate.py` liefern elektrischen Zielvertrag, Gegenfälle und rechnerisches Hold-Budget; weder symbolische Netznamen noch grüne Unittests belegen physikalisch realisierte Pin-/Backup-Schaltung.
