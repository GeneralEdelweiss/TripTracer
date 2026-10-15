# TripPower REV3 – zuverlässiger 12-V-Bordnetzbetrieb; 9-V-Startpfad (15.10.2026)

**Aktiver Schaltplan jetzt REV3-PROTOTYPENVARIANTE, NICHT freigegeben:** R330 von 825 kΩ auf **715 kΩ ±1 %, Vishay CRCW1206715KFKEA (AEC-Q200 / 1206)** geändert. Alle weiteren KiCad-Bauteile, insbesondere R313–315 = 9,9 kΩ, 56-V-Zener, D302 A→VS, C302 1 µF, C308 10 µF, C311 220 nF, U302 TPS3760A012DYYRQ1, REV2 Q303–Q305, Q301 SQM10250E und Buck unverändert. Dieser Wert ist ein **testbarer Startoptimierungsversuch**, keine garantierte Lösung für 9 V oder −40 bis +125 °C.

## Ziel und verbindliche Randbedingungen

- Modulspannung **VIN_FUSED = 9–30 V** unter Last (9 V am Modul, nicht an der Batterie), 12- und 24-V-Systeme.
- 5,0 V/2 A und zusätzliche RAW-Leitung bis 1 A Auslegungsziel, F_MAIN extern und austauschbar. **Unter VIN_FUSED <9 V darf das Gerät definiert resetten/abschalten**; das bedeutet nicht, dass 6-V-Cranking beliebig weiter betrieben werden muss.
- Unverändert separate Schutzanforderung 202 V/350 ms, Verpolung, gemeinsamer elektronischer OCP/SCP, <100 µA Gesamtfahrzeug-Off-Ziel. Keine RVS-1-kΩ-Abkürzung.
- Klare Unterscheidung zwischen *Schaltplan/arithmetisch bestanden*, *Prototyp gemessen* und *Serien-/Fahrzeugfreigabe*.

## TI-Primärreferenz

- [LM74930-Q1 Datenblatt, Abschnitte 8.2.1/8.2.2](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): 10-kΩ-VS-Zweig, 56-/60-V-Klemme und A→VS-Nachladepfad für 200-V-Load-Dump; CCS/VS mindestens 1 µF, VS-Betrieb 4–65 V, CAP-Ausgangsstrom nicht mit VS-Versorgungsaufnahme gleichsetzen.
- [LM74930Q1EVM](https://www.ti.com/lit/pdf/sluucw6): Startup-Beispiel bei 12 V und 10-kΩ-Zuleitung, **keine 9-V-Garantie**.
- [TI E2E, VS-Nachladediode](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1411181/lm74930-q1-question-regarding-disabling-reverse-current-blocking-and-it-s-effect-on-the-imon-pin): TI sagt ausdrücklich, die Diode überbrückt nach Gate-Einschalten den Strommangel durch RVS.
- [TPS3760-Q1 Datenblatt Rev.B, Tabellen 4-1 und 7-1](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf): auswählbare integrierte Hysteresen bis 2,5 V, OD/PP. Die **8-V-EIN/6-V-AUS-Variante als internes 6,0 V + 2,0 V Hysterese** wäre prinzipiell möglich; ein passender tatsächlich veröffentlichter, lieferbarer Automotive-Bestellcode wurde jedoch **NICHT belegt**. Daher nicht ohne Bestands-/MOQ-Nachweis in die BOM übernehmen. Der vorhandene 0,8-V-2%-OD-Typ bleibt aktiv.
- [TI E2E, 10-kΩ-Fremdfall](https://e2e.ti.com/support/power-management-group/power-management/f/p/power-management-forum/1524655/lm74930-q1-inrush-current-voltage-instability-during-startup): weiteres Beispiel für die Notwendigkeit des echten Gate-/Pumpenstarttests; fremder Aufbau hat riesige Ausgangskapazitäten, darf nicht auf unser Gerät extrapoliert werden.

## Was R330 = 715 kΩ ändert

Vollständige Modellierung: `python3 tools/check_trippower_rev3_12v_startup.py`, Basis `tools/check_trippower_reset_worst_case.py`. Berücksichtigt RESET-Feedback **und** Q304-Basisbelastung; 1%-Widerstände, TPS3760 0,792–0,808 V und hypothetisches VBE 0,55–0,95 V, 100-nA-SENSE-Bias und 300-nA-RESET-Leck.

| Modellgröße | Bisher R330 = 825 kΩ | REV3 715 kΩ | Bedeutung |
|---|---:|---:|---|
| VS_READY ON nominal | 8,221 V | **7,234 V** | Frühere Freigabebedingung |
| VS_READY OFF nominal | 5,998 V | **5,438 V** | Hysterese nominell 1,796 V |
| VS_READY ON oberes Szenario | 8,539 V | **7,510 V** | Kein garantiertes Worst Case |
| VS_READY ON unteres Szenario | 7,669 V | **6,754 V** | >6 V in diesem Modell, kein Temperaturbeweis |
| VS_READY OFF Szenarioband | 5,646–6,336 V | **5,124–5,740 V** | Bleibt im Modell oberhalb VS-Betriebsminimum 4 V |
| RVS-Zufluss bei VIN=9 V und oberem ON-Szenario | **46,6 µA** | **150,5 µA** | 3,23× statischer Strom direkt an modellierter READY-Schwelle |
| RVS-Zufluss bei VIN=12 V und oberem ON-Szenario | 349,6 µA | 453,5 µA | +103,9 µA, nicht dynamischer VS-Pumpenstrom |

**Wesentlicher Zusammenhang:** Niedrigeres READY allein würde die bei EN-Start gespeicherte C308-Energie reduzieren. Im vorliegenden TripPower ist aber **C311=220 nF am TPS3760 CTR** eingebaut, entsprechend nominell etwa **280 ms RESET-Freigabeverzögerung**, währenddessen VS über 9,9 kΩ weiter geladen wird.

**Illustration, KEIN garantierter Startup:** Bei VIN_FUSED=9 V, konstanter fiktiver OFF-Last 34,6 µA, nominal C302+C308=11 µF, RVS=9,9 kΩ, CTR-Verzögerung 280 ms: `VS_eq≈8,657V`, `τ≈108,9ms`. Im neuen Modell wird VS=7,234 V nach ~197 ms erreicht; nach weiteren 280 ms bei weiter ausgeschalteter Last `VS≈8,549V`. Altes nominelles ON=8,221 V wird nach ~325 ms erreicht und nach Delay `VS≈8,624V`. Damit lässt die neue Variante im idealisierten verzögerten Start lediglich **~75 mV weniger** Startreserve, erweitert aber die rechnerische Reichbarkeit der READY-Schwelle um 1,0 V.

**Einschränkungen, die eine Funktion weiterhin verhindern können:** Die 34,6 µA sind kein Hersteller-Temperaturmax, 11 µF sind nicht minimal garantiert, die 280 ms gelten nicht automatisch bei −40/125 °C und ±C-Toleranz. Q303/Q304-BJT-µA-hFE ist ungebunden; RESET kann vorzeitig entlassen, VS unter CAP-Quellstrombedingung **VS≥6 V** fallen, bevor A→VS-D302 nachlädt. Ein höherer RVS-Zufluss beim Schwellenübertritt garantiert **keinen** HGATE-Start. Bei unzureichender Freigabeverzögerung könnte REV3 *schlechter* sein als REV2.

## Diagnostischer Prüfstand: messbare Akzeptanzkriterien

A/B nur R330 825 kΩ ↔ 715 kΩ; U302/C311/C308 und alle übrigen Teile identisch. **Kein 202-V-Puls an ungeschützter EVM-/Bastelhardware.**

1. Kalt mit VS/CAP vollständig entladen: 9,0 / 10 / 11 / 12 / 13,8 V **direkt an J301/VIN_FUSED**, plus 24/30 V; je schnelles Anlegen und VIN-Ramp (100ms/1s/10s), RUN_AUTO und RUN_CMD.
2. Differential messen: **VIN_FUSED, VS_CLAMP, CAP−VS, HGATE−SOURCE_A, SOURCE_A, VS_READY_RESET_OD_PRELIM, CTRL_EN, VIN_PROTECTED_UNFUSED, 5V_OUT**; Q301 Strom, Pumpenstarts, Gate-/OCP-Retries und Batterierückspeisung.
3. Je Stufe 5-V-Last 0 / 0,5 / 2 A und RAW 0 / 1 A; zum Schluss Ein-/Ausschalten und Brownout 13,8→9→13,8 V; R319 AUTO / RUN_CMD HIGH+VIN0.
4. Temperatur −40/25/85/125 °C in geeigneter Kammer, insbesondere C308 ESR/Ceff/Leck, RESET-C311-Effektivkapazität, BJT Q303 I_CEO und Mikroampere-hFE, Q301-/LMR38020-Junctions. **EN_LOW ≤0,41 V, EN_HIGH ≥1,05 V**, kein unkontrolliertes Gate-Chattering, reproduzierbarer START wenn VIN≥9V.
5. Systemnachweis separat: 202-V-Load-Dump/MOSFET-SOA, F_MAIN-I²t/fail-short und 2-A-Last/PCB-Kühlung.

**Bedingtes Ergebnis:** R330715k nur behalten, wenn der Aufbau bei 9 V die CAN/RAW-Startlasten reproduzierbar trägt, RESET-Abschaltlogik über Temperatur fail-safe bleibt und C311-Mindestverzögerung den CAP-Pumpenstrom abpuffert. **Kein RELEASE vor Messung**. Alternative vor PCB: COTS-Supervisor mit **garantiertem integriertem 6/8-V-Schmitt und geeignetem Ausgang** (nur wenn reale lieferbare MPN vorhanden); oder gezielt hochspannungsfeste, strombegrenzte VS-Startquelle, dimensioniert auf 202 V.
