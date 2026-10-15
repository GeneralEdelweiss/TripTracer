# TripPower 9–30-V-Anlauf: VS-Bootstrap-Gate, UVLO, EN, Buck (15.10.2026)

**Status: KEIN nachgewiesenes vollständiges 9–30-V-Kaltstartfenster.** Nicht als SPICE-Simulation, echte Fahrzeugfunktion, ISO-16750-Freigabe, validiertes Bauteil oder fertiges PCB ausgeben. **Schaltplan in dieser Revision absichtlich noch nicht geändert:** Der bestehende 202-V-Schutz ist nicht durch willkürliche Verringerung des VS-Schutzwiderstands zu gefährden. Zahlen in `tools/check_trippower_9_30v_startup.py` auf HEAD als reproduzierbare Rechnung; CI-Erfolg bedeutet nur korrekte Arithmetik.

## 1. Tatsächliche Topologie im eigenständigen KiCad-10-Schaltplan

`VIN_FUSED → R313+R314+R315 = 3×3,3kΩ = 9,9kΩ → VS_CLAMP/U301.22`. An VS: `C302=1µF/100V` nominal, `D301=56V Zener` nach Masse; `D302 = BAV21WQ-7-F` leitet von SOURCE_A (U301.A / U301.OUT = gemeinsamer Source-Knoten hinter Q301) nach VS. Q301 hat Drain an VIN_FUSED, Source an SOURCE_A und ist ohne HGATE **SPERREND**. D302 ist eine notwendige Nachlade- und Stützdiode **NACH** Freigabe von Q301, **keine unabhängige Startstromquelle im vollständig ausgeschalteten Zustand**. Q302 (DGATE) verbindet SOURCE_A mit C_NODE und gemeinsamer `VIN_PROTECTED_UNFUSED`-/Buck-Zuleitung. Kein separater F302, `F_MAIN` muss an der Fahrzeugseite passen.

`R318=100kΩ` von VS zu Auto-EN, `R319=0Ω` für ALWAYS_ON, `R316=100kΩ` Pull-down: im Normalfall näherungsweise `EN ≈ VS/2`. EN-ON-Schwellwert bis 1,05V → Auto-EN-Bedarf VS≈2,1V, also **vor** 4V empfohlener Betriebsspannung und nahe VS-POR 2,4–2,9V. Kein eingeplanter VS-Vorlade-/Bootstrap-Haltezeitmechanismus. Wird R319 nicht bestückt, braucht die kontrollierte RUN_CMD-Schnittstelle ein externes 3,3/5V-High-Signal; nicht mit 12/24-V-ACC direkt verbinden.

## 2. Herstellerquellen und nicht austauschbare Ströme

[TI LM74930-Q1, SNOSDF6, Seiten 6–8 / 15–16 / 25](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf):
- VS **Betriebsversorgung 4–65V**, POR rising **2,4/2,6/2,9V** (min/typ/max).
- `I_Q` **665µA typisch / 780µA maximal**, unter spezifizierter Messbedingung **VS=12V**, `EN=2V`; **dies ist nicht das garantierte I(VS) bei VS=4V oder im Pumpen-Ladetransient**.
- CAP-**Ladestrom** `I(CAP)` **mind. 1,3mA / typisch 2,7mA** bei spezifiziertem CAP–A und **VS≥6V**. **Niemals mit dem am VS-Eingang aufgenommenen Strom gleichsetzen**: Energiewandlung, Eigenverbrauch, Randbedingungen sind verschieden.
- Gate-Enable erst nach `VCAP−VS≥5,4/6,6/7,9V` rising und zugleich EN high, VS-POR, UVLO, kein OV. Für C303=470nF nominal nach TI Gl.(1) **typisch** `175µs + 0,470µF×6,6V/2,7mA = 1,324ms` nach wirksamer Freigabe (VS dabei bereits intakt!). Mit 1,3mA und 7,9V als bloßer Vergleich `3,03ms`, kein echter garantierter Worst Case (nicht spezifiziert für VS=4/5V).
- [TI E2E Entwicklerfall: VS=10kΩ, VS blieb bei ~3V und MOSFET startete nicht](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1524655/lm74930-q1-inrush-current-voltage-instability-during-startup). Anderer [TI-Mitarbeiter bestätigt, dass A→VS-Diode wegen RVS-Strommangel nötig ist](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1411181/lm74930-q1-question-regarding-disabling-reverse-current-blocking-and-it-s-effect-on-the-imon-pin). Kein Beweis, dass **unsere** 9V-Schaltung scheitert; ausreichend zum Blockieren einer ungetesteten Startfreigabe.
- [TI LMR38020-Q1 SNVSBS6B](https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf): Buck VIN braucht **4,2V zum Start**, typisch **4ms Soft-Start**, interne OCP-Blanking 18ms typisch (nicht gleich TripPower-LM74930-Schutz); U101.2 EN ist im Projekt mit `VIN_PROTECTED_UNFUSED` verbunden, daher startfähig **erst nach** Q301/Q302, nicht als VS-Vorladung. Buck-U101 PG ist absichtlich unbeschaltet.

## 3. Konservative Eingangsspannungsmatrix – keine simulierten tatsächlichen VS-Werte

Für die *hypothetische statische* Lastaufnahme I_VS = 665µA oder 780µA rechnen wir `VS=VIN−9,9kΩ×I`. Der Ruhestrom ist bei VS=12V spezifiziert, bei VS≪12V können Strom und Ladungspumpenregime **anders sein**. Die relevantere elektrisch sichere Obergrenze `I_feed,max(VS≥4V)=(VIN−4V)/9,9kΩ` gilt ohne A→VS-Nachladung.

| VIN | VS-Zufluss maximal bei VS=4V | Modell-VS bei 665µA | Modell-VS bei 780µA | 5V/2A+RAW1A VIN-Strom bei angenommener 80%-Buck-Eff. |
|---:|---:|---:|---:|---:|
| 9V | **0,505mA** | **2,42V** | **1,28V** | 2,389A |
| 12V | 0,808mA | 5,42V | 4,28V | 2,042A |
| 13,8V | 0,990mA | 7,22V | 6,08V | 1,906A |
| 24V | 2,020mA | 17,42V | 16,28V | 1,521A |
| 30V | 2,626mA | 23,42V | 22,28V | 1,417A |

**Fazit dieser Matrix:** 9V erste EN-/Pumpenfreigabe **hoch riskant**, weil für VS≥4V höchstens 505µA über R313–315 verfügbar, **weniger als TI 665µA typ unter seinen Messbedingungen**. 12V ebenfalls **knapp** gegen 780µA I_Q und dynamischen Pumpenstart. 13,8V fraglich ohne Spannungsreservoir; 24/30V hätten im gleichen hypothetischen statischen Modell mehr Reserve, aber tatsächliche Pumpeneingangsleistung und Sättigung bleiben unbewertet. **Nichts als als garantierten Startfall markieren**. Mehr C303 verbessert elektrische Stützwirkung nach Start, verlängert aber die anfängliche nötige CAP-Ladungsübertragung.

## 4. UVLO und EN sind nicht die primäre 9V-Grenze, aber knapp

UVLO-Widerstandsteiler `R310+R311=1,5MΩ`, `R312=130kΩ`: rising Schaltschwelle nominal `0,6V×(1,63MΩ)/130kΩ≈7,52V`. Bei 9V liegt UVLO-Pin nominal 0,718V an. Mit **angenommenen jeweils ±1% Widerständen**, ungünstigem Vorzeichen des max. **200nA** Eingangsstroms und TI maximaler rising-Schwelle **0,63V** liegt die geschätzte *ungünstige Rising-VIN-Schwelle* bei **8,35V** (9V Rand etwa 0,65V Eingangsmarge). Das ist ein Worst-Case-Modell unter R-Toleranzannahmen; einzelne Teile sind noch nicht sämtlich als exakte 1%-MPN fixiert und Versorgungseinbruch/Temperatur separat. `R319=0Ω` Auto-EN schaltet *früh*, bei `VS≈2,1V` statt die Pumpe abzuwarten.

OV-Schaltschwelle ca. 35,9V nominal, sodass 30V Normalbetrieb idealerweise unterhalb bleibt; bei Toleranz und Leakage erneut prüfen.


**9V Spannung am Fahrzeuganschluss ≠ 9V am TripPower-Modul:** Bei 5V/2A + 1A RAW ergibt die beispielhafte 80%-Buck-Effizienz ca. 2,389A bei 9V. Mit der pessimistisch errechneten UVLO-rising-Schwelle von ca. 8,35V bleiben nur 0,65V für die komplette M8-Kabel-, F_MAIN-, Stecker- und Zuleitungsimpedanz. Für dauerhaft 9,00V vor dieser Leitung resultiert deshalb **R_total ≤ (9−8,35)/2,389 ≈ 0,272Ω**, ohne Einschaltstromreserve und unter den genannten pessimistisch/angenommenen Schwellwerten. **9V Systemstart muss am VIN_FUSED-Pin unter Last spezifiziert/gemessen werden**, nicht nur an Batteriepolen. Dieser Kabel-Spannungsabfall ist ein unabhängiges UVLO-Budget und löst das VS-Bootstrap-Problem nicht.

## 5. Startverlauf: Blockfolge

1. `VIN_FUSED` steigt von 0 auf 9/12/13,8/24/30V. Bei Q301 aus sperrt die Body-Diode in VIN→SOURCE_A-Richtung. **D302 A→VS hat zunächst keine unabhängige Quelle**.
2. `C302/VS` lädt über den **9,9kΩ-Widerstand** (bei nominell 1µF zunächst RC≈9,9ms, nicht Hersteller-kapazitätsgarantiert). R319 populated: EN wird über den Spannungsteiler früh High.
3. Sobald TI-Bedingungen (VS-POR, EN, UVLO und CAP-UVLO 5,4–7,9V) erfüllt sind, darf HGATE Q301 einschalten. Im bisherigen 9/12V Design ist **nicht bewiesen**, dass VS während der C303-Pumpenladung hoch genug bleibt; C302=1µF nominell ist kein gesichertes Reservoir.
4. Wenn Q301 tatsächlich eingeschaltet hat, steigt SOURCE_A, und D302 kann bei passender Vorwärtspolarität den **VS-Nachladestrom** unter Umgehung von R313–315 liefern. Dann Q302-DGATE ermöglicht Schutz-Ausgang `VIN_PROTECTED_UNFUSED`; `U101 EN=VIN` startet mit ~4ms Softstart.
5. Insgesamt simulieren weder 1,324ms noch 4ms eine garantierte `5V_OUT`-Bereitzeit; sie liegen **hinter** dem ungesicherten Bootstrap-Ereignis. In der 9V-Vollastzone bleibt LM74930 OCP nominal 3,61A und SCP nominal 5,03A als gesondertes kombiniertes Last-/Anlaufstrom-Gate.

## 6. Warum „RVS schnell auf 1k verkleinern“ KEINE Freigabe ist

Bei 202V Rechteck-**Worst-Case nur zur Dimensionierung** und 56V VS-Zener:
- `RVS=1kΩ`: `I=(202−56)/1000=146mA`; Widerstandssatz **21,3W** Spitzenverlust / **7,46J** in 350ms, Zener **8,18W / 2,86J**. Ein 1kΩ/kleines SMD- oder 56V-Zener-Element aus bisheriger BOM wäre **ungesichert überlastet**.
- `RVS=9,9kΩ`: nur ~14,75mA in demselben idealisierten Rechteck-Fall (R313–315 zusammen), pro 3,3kΩ ungefähr 0,72W und 0,251J. Auch diese Werte sind noch nicht pulsqualifiziert. Einfacher 1k ohne größere Schutzstufe **gefährdet das 202V-Ziel**.
- Direkte VIN→VS-Diode oder RVS-Überbrückung bei 202V würde den maximalen VS-Betriebs-/Absolute-Rating Bereich von 65/70V überschreiten. Nicht ausprobieren.

## 7. Technische Kandidaten für nächsten Schritt (noch nicht ausgewählt)

A. **Zuerst reproduzierbar messen**: 9/10/12/13,8/18/24/30V, VIN Ramp schnell/langsam, -40/25/85/125°C geeignete Prüfumgebung, C302/C303 tatsächlicher Ceff, EN auto und extern RUN, 0A/1A roh + 0/2A 5V; VS, CAP–VS mit Differentialtastkopf, SOURCE_A, HGATE–OUT, DGATE–A, VIN_PROTECTED_UNFUSED, 5V, Shunt-Strom, Buck PG falls instrumentiert. Auch Einschalt-/Ausschaltzyklen, 9→24, 24→9, kurze Störungen und MCU-RUN.
B. **Preiswertes Bootstrap-Netz** als *erst zu dimensionierende* Alternative: VS bei EN=Low zunächst über 9,9k laden, EN mit definierter VS-Vorladeschwelle und Hysterese verzögern und C302-Ceff bei Ziel-VS und Pumpenstart nachweisen. Das kann zusätzliche RC/Überwachung erfordern; bloß ein größerer Kondensator ohne geregeltes späteres EN ist **kein Beleg**.
C. Falls A/B nicht belastbar: hochspannungsfeste strombegrenzte Start-VS-Quelle oder fertiger Referenz-IC mit 202V/350ms Puls- und OFF-Leckstrom-Bewertung. **Nicht** vorschnell 12/24V-spezifische Versorgung trennen oder billigen Regler statt Schutz hineinbauen; 9–30V plus 202V einhalten.

**Aktuelle Entscheidung:** Kein blindes Umdimensionieren von R313–315, C302, C303 oder F_MAIN. **9–30V-Kaltstart bleibt `BLOCKED_REDESIGN_REQUIRED_OR_BENCH_PROOF`.** Abgekürzt „LM74930 4V Mindestversorgung“ allein beweist keinen 9V-Systemstart am 9,9k-Surgevorwiderstand. Existierender nativer KiCad10-ERC/Netlist-PASS beweist nur Konnektivität, nicht Funktion.
