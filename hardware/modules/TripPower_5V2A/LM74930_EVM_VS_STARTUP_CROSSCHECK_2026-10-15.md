# TripPower – LM74930Q1EVM-Abgleich für den 9-V-Erststart (15.10.2026)

**Status: Herstellerreferenz abgeglichen; 9-V- und Temperatur-Startnachweis weiterhin OFFEN. Keine Änderung der aktiven BOM oder des KiCad-Schaltplans und keine Fahrzeug-/PCB-Freigabe.** Gültige Basis: `design/solid-state-power-v1`, Revision RESET/EN REV2, `ffcd731c` (vor dieser Notiz), siehe `RESET_EN_REV2_PROOF_GATE_2026-10-15.md`.

## 1. Primärquellen und belastbare Aussage

1. [TI LM74930Q1EVM, SLUUCW6](https://www.ti.com/lit/pdf/sluucw6), Abb. 3-1 auf PDF-Seite 11 (Schaltplan), Tabelle 2-4 und Abschnitt 2.3.1 (Testablauf), Abb. 2-2/2-3 (Startup-Verläufe): **R13=10 kΩ von VIN nach VS**, **D8 von A nach VS (Anode A, Kathode VS)**, **D7 56-V-VS-Zener**, **C18 1 µF an VS**, **EN über J5 standardmäßig mit VREG verbunden**; separate VREG-Erzeugung mit 4,7-V-Zener. Die gezeigte EVM-Startup-Messung erfolgt bei **VIN=12 V**, nicht bei VIN=9 V. Der 10-kΩ-EVM-Wert ist *kein* garantierter 9-V-Startnachweis.
2. [TI LM74930-Q1 Datenblatt, SNOSDF6](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), Tabellen 5-1 und 6.5 sowie Anwendung Abschnitt 8.2: VS-Betrieb 4–65 V, EN darf für Always-On an VS, ON-IQ 665 µA typisch/780 µA max **bei den jeweiligen spezifizierten Datenblattbedingungen (VS=12 V, EN=2 V)**. CAP-Ladestrom ist **nicht** der aus VS aufgenommene dynamische Inputstrom. Die D8-Funktion beweist noch keine eigenständige Vorladung der gemeinsamen FET-Sources.
3. [TI E2E: A→VS-Diode aufgrund unzureichenden Stroms durch RVS](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1411181/lm74930-q1-question-regarding-disabling-reverse-current-blocking-and-it-s-effect-on-the-imon-pin). TI nennt die Nachladediode ausdrücklich notwendig.
4. [TI E2E: reales 10-kΩ-Startup-Problem](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1524655/lm74930-q1-inrush-current-voltage-instability-during-startup): Ein anderer Entwickler berichtet VS ungefähr 3 V und fehlenden Start mit 10 kΩ, 1 kΩ funktionierte in dessen Aufbau. **Anekdotische Problembeobachtung, kein TripPower-Messwert und keine Freigabe für 1 kΩ**.
5. [TI E2E: EN und MODE können an VS angeschlossen werden](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1619173/lm74930-q1-designing-for-202v-load-dump). Das bestätigt, dass die EVM-VREG nicht zwingend für jeden Always-On-Entwurf übernommen werden muss. Für TripPower bleibt die **AUTO/RUN-Abschaltlogik** dennoch erforderlich.

## 2. Tatsächlicher Delta-Abgleich EVM ↔ TripPower

| Funktion | TI-EVM | TripPower REV2 | Konsequenz |
| --- | --- | --- | --- |
| VS-Pulsspeisung | 10 kΩ R13 | 9,90 kΩ aus R313/R314/R315, je 3,3 kΩ/2512 | Praktisch identisches Widerstandsniveau; Puls-Eignung der drei Bauteile separat offen |
| Nachladediode | D8 Anode A, Kathode VS | D302 BAV21WQ-7-F, Anode SOURCE_A, Kathode VS_CLAMP | Funktion bereits im Schaltplan vorgesehen; nicht als unabhängige VIN→VS-Bootstrapquelle ausgeben |
| VS-Klemme | D7 56 V, C18 1 µF | D301 56 V, C302 1 µF + C308 10 µF/100 V | Zusätzliches Reservoir hilft *potenziell* während kurzer Pumpenlast; Leckage/effektive Kapazität und VS-Spitzenspannung offen |
| CAP/VS-Kondensator | separate CAP-/VS-Beschaltung gemäß Abb. 3-1; Bauteilbezeichnungen nicht mit TripPower gleichsetzen | C303 470 nF/100 V zwischen CAP_PUMP und VS_CLAMP | **Nicht** blind EVM-Kondensatoren nach Positionsnummer übertragen; TripPower-C303 ist gegen TI-Regel vorbemessen, Ceff noch offen |
| Enable | J5 standardmäßig an 4,7-V-VREG | U302/TPS3760 mit Q303–Q305 REV2, VS-only | EVM enthält nicht unsere Hysterese, Verzögerung, AUTO/RUN und 125-°C-Leck-/µA-hFE-Probleme |
| Datenblatt/EVM-Test | VIN 12 V, ohne angeschlossenen TripPower-Buck+RAW-Last | VIN **9–30 V**, 5 V/2 A und RAW bis 1 A als Designziel | EVM-Wellenform **nicht** als 9-V-/202-V-/Lastfreigabe werten |

**Wichtige Anlauf-Reihenfolge:** Bei VIN-Einschalten ist Q301 (Drain VIN, Source SOURCE_A) zunächst sperrend. Die D302-Anode an SOURCE_A kann deshalb erst speisen, wenn diese Source durch Gate-Ansteuerung hochkommt. Vorher versorgt nur der 9,9-kΩ-Pfad VS (ggf. aus gespeicherter VS-Ladung bei Neustart). Die zusätzliche U302-VDD-/RESET-/Q304-Last verringert die zunächst verfügbare Reserve.

## 3. Quantitative Grenze bei 9 V (nur Rechnung)

Mit der im REV2-Szenariogate errechneten **oberen modellierten VS_READY-Einschaltschwelle 8,539 V** beträgt der noch verfügbare Speisestrom:

`I_RVS=(9 V−8,539 V)/9.900 Ω=46,57 µA`.

Das bisherige illustrative Vorstart-Lastbudget von 34,6 µA lässt nur **11,97 µA nicht garantierte** Reserve. Beim nominellen Einschaltwert **8,221 V** sind `(9−8,221)/9900=78,69 µA` verfügbar. **Beide Zahlen sind statische Grenzbetrachtungen, kein vorausgesagter VS-Pegel und kein Pumpenstartbeweis.** Sobald der Controller eingeschaltet ist, können die TI-IQ-Messbedingung und die VS-Dynamik völlig andere Ströme erfordern.

Die derzeit eingebaute C308 = 10 µF *nominal* bedeutet auch nicht automatisch 10 µF bei −40 °C / +125 °C und nach Alterung. Für eine illustrative zusätzliche VS-Pumpenlast gilt näherungsweise `ΔVS≈ΔI·Δt/C_eff`, aber I_VS(t), C_eff und die verfügbare RVS-Nachladung sind nicht herstellergarantiert. CAP-Ausgangsstrom nicht als VS-Strom verwenden.

## 4. Konkretes Vergleichs- und Messgate (vor einem neuen Schaltungs-Swap)

**A. EVM / Referenz:** EVM-Schaltung bzw. ein elektrisch identisch abgesicherter Prüfaufbau: 12 V mit standardmäßigem J5=1–2 (EN=VREG), R13=10 kΩ, D8 und VS-Klemme. Erfasse VIN, VS, CAP−VS (**Differenzmessung**), HGATE, SOURCE_A und VOUT. Dann bei 9 V wiederholen: EVM-Spezifikation zeigt nur 12-V-Beispiel, 9 V ist ein zusätzlicher Versuch und **keine pauschale EVM-Garantie**. Keine 202-V-Impulse an unqualifizierter Laborbeschaltung.
**B. Isolierter TripPower-Schutz:** Dieselben Messpunkte und VIN=9/10/12/13,8/24/30 V; zuerst ohne 5-V-Volllast und mit definiertem, für EN zulässigem RUN/Enable-Testsignal, um VS/Chargepump unabhängig von der U302/REV2-Belastung zu charakterisieren. Versuchsbrücken nur auf einer kontrollierten Laborversion, niemals als zulässige Serien-/Fahrzeugbestückung.
**C. TripPower REV2:** AUTO (R319=0 Ω) und RUN (R319 nicht bestückt); RUN HIGH + VIN 0, schnelle Power-Cycles, langsamer VIN-Ramp, C308 frisch entladen und Restladung. Matrix −40/25/85/125 °C × VIN 9/10/12/13,8/24/30 V × 5-V-Last 0/2 A × RAW-Last 0/1 A, thermisch/leistungsgerecht stufenweise. Messen: VIN_FUSED **am Modul**, VS_CLAMP, CAP_PUMP−VS_CLAMP, VS_READY_RESET_OD_PRELIM, CTRL_EN, SOURCE_A, VIN_PROTECTED_UNFUSED, 5V_OUT, Eingangs-/RAW-Strom sowie Q301-/Zener-/R313-315-Temperatur.
**D. Diagnose-Reihenfolge bei Fehlstart:** (1) VS erreicht nicht READY-Schaltschwelle → RVS/Leck-/Resetbudget; (2) READY erreicht, CAP−VS bricht weg oder HGATE bleibt LOW → Ladungspumpe/Versorgung/OCP/FET; (3) HGATE/Source vorhanden, Buck fehlt → 5-V-Regler und dessen Eingang/EN prüfen; (4) 9-V-Start ohne Last ja, unter Last nein → Spannungseinbruch Leitungsweg, OCP, Gate-/Ausgangs-Inrush voneinander trennen.
**E. Release-Kriterien:** reproduzierbarer Start bei **VIN_FUSED=9 V unter den festzulegenden Temperatur-/Lastbedingungen**, kein RUN-backfeed, EN-OFF garantiert unter 0,41 V am heißen Eckpunkt, EN-ON garantiert über 1,05 V am kalten Eckpunkt, definiertes Brownout/Reset statt thermisch gefährlichem Fehlerbetrieb. Messungen alleine ersetzen keine FIT-/Bauteil-Worst-Case-Prüfung; 202 V/350 ms + TVS/VS/RVS/MOSFET-SOA und F_MAIN/I²t bleiben eigenständige Pflicht-Gates.

## 5. Entscheidung und Konsequenz für den aktuellen Branch

- **Keine Änderung an R313–R315, D302, C302, C303, C308, U302 oder REV2** allein aufgrund des 12-V-EVM-Vergleichs. Insbesondere **kein 1-kΩ-Swap**: 202 V, 56-V-Zener, Pulsenergie und OFF-Strom wären neu und teils drastisch zu qualifizieren.
- Die nächste Freigabeentscheidung wird **vom isolierten 9-V-Start-/VS-Strommessprofil** abhängig gemacht, nicht von einem weiteren ungeprüften diskreten Enable-Netz.
- Dieser Abgleich belegt die **funktionell richtige Referenz-Topologie**, nicht den 9-V-Erststart in unserem System; Status **`START_9V_UNPROVEN; 202V_SOA_UNPROVEN; PCB_ABSENT`**.
