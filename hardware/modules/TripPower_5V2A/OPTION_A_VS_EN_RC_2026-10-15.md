# TripPower: Ansatz A – passive VS-Vorladung/EN-RC (Entwicklungsprototyp, 15.10.2026)

**Scope:** eigenständiges `TripPower_5V2A`, LM74930QRGERQ1 + Q301 SQM10250E_GE3 + Q302 BUK7Y4R8-60EX + LMR38020SQDDARQ1, 9–30 V, 5 V/2 A und vorläufig 1 A `VIN_PROTECTED_UNFUSED`. **KEINE 9-V-Start-, 202-V-SOA-, PCB-, ISO- oder Fahrzeugfreigabe.** Übergeordnete Sicherheitsregel: Abschalt-/Brandschutz und externe `F_MAIN` dürfen durch das Bootstrap-Netz nicht verschlechtert werden.

## 1. TI-Funktionsabfolge und Entscheidungsgrundlage

[TI LM74930-Q1 Datenblatt](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), Seiten 6–8, 15, 24–25:
- Wenn `EN` niedrig ist, sind **Ladungspumpe und Gate-Treiber abgeschaltet**. Vorladen bei EN=Low kann nur `VS/CVS` speichern, **nicht CAP–VS**. TI spezifiziert `I_SHDN` typisch 2,5µA, maximal 5µA unter Testbedingungen.
- Beim Übergang zu EN=High und verfügbaren VS/UVLO/OV-Bedingungen lädt die Pumpe `C303=470nF` mit typisch 2,7mA am **CAP-Ausgang**, min. 1,3mA bei VS ≥6V und weiteren spezifizierten Randbedingungen. Dieser **CAP-Strom ist NICHT der aufgenommene VS-Versorgungsstrom**. Deshalb ist eine Energie-/Transientenanalyse ohne echte I(VS,t)-Daten lediglich eine Sensitivität.
- `CAP–VS` muss vor Gate-Freigabe zwischen 5,4 und 7,9V rising erreichen, typisch 6,6V. Gate-Freigabeformel typisch **1,324ms** bei 470nF und 6,6V. MAX-Schwelle 7,9V + MIN-CAP-Strom 1,3mA ergibt isoliert rechnerisch **2,86ms Kondensatorladung**, plus 175µs nur **typische** interne Verzögerung – keine garantierte 3,03-ms-Gesamtzeit.
- Der interne `VS`-POR liegt <4V; **4V Mindestbetrieb** und **6V Mindestbedingung für spezifizierten Pumpenstrom** unterscheiden sich. Eine Start-Simulation, die VS unter 6V fallen lässt, darf die 1,3mA-Pumpenangabe nicht weiter verwenden.
- Der bestehende `D302` speist VS von `SOURCE_A`, jedoch erst **nach** aktivem Q301; kann die erste Startanforderung nicht garantieren.
- `R313–R315` jeweils Vishay `CRCW25123K30FKEGHP` (3,3kΩ/2512), insgesamt 9,9kΩ, bleiben wegen Lastabwurf 202V/350ms unverändert. Das 56V-Zener-/202V-/Puls- und F_MAIN-I²t-Gate bleibt offen.

## 2. In KiCad tatsächlich angelegter Option-A-Stand (Kandidaten; noch nicht funktional verifiziert)

**Bestückung und Netzliste (1. Schutzseite):**

| Pos. | Anschluss | Neuer Schaltplanwert / MPN | Status |
|---|---|---|---|
| R313–R315 | VIN_FUSED → VS_CLAMP | 3×3,3kΩ 2512 Vishay PULSE | UNVERÄNDERT; 202V-Puls noch offen |
| C302 | VS_CLAMP → GND | 1µF / 100V MLCC | UNVERÄNDERT; Hersteller/effektives C unter Bias offen |
| **C308 NEU** | **VS_CLAMP → GND, parallel C302** | **Panasonic `EEE-TG2A100P`, 10µF ±20%, 100V SMD Aluminium TG-Serie, 8mm Ø ×10,2mm, -40..+125°C AEC-Q200** | Nur Kandidat, echter Footprint `Capacitor_SMD:CP_Elec_8x10.5` prüfpflichtig; Polung: 1 +VS, 2 GND |
| R318/R319/R316 | VS → 100k → bestückter 0Ω AUTO → EN → 100k GND | unverändert | 9V AUTO-Prototyp; D305 RUN_CMD kann verzögerte Freigabe übergehen |
| **C309 NEU** | **CTRL_EN → GND** | **KYOCERA AVX `12105C106K4T2A`, 10µF ±10%, 50V X7R 1210 AEC-Q200** | Nur Kandidat, Standard-KiCad `Capacitor_SMD:C_1210_3225Metric`; EN kann bei VS56V über 100k/100k ca. 28V erreichen. Tatsächlicher Ceff unter Bias/-40..125°C nicht belegt. |
| C303 | CAP_PUMP → VS_CLAMP | KEMET `C1206C474K1RECAUTO7210`, 470nF/100V | Unverändert. |

**Physik:** Bei C308 nominal 10µF + C302 nominal 1µF folgt grob `τ_VS = 9,9k×11µF = 109ms` bei EN low und **ohne** Eingangsstrom / EN-Belastung. Mit R318=R316=100k und C309 nominal10µF liegt `τ_EN ≈ (100k || 100k)×10µF = 500ms` bei ***konstanter*** VS; der reale, gekoppelte VS/EN-Ladevorgang lässt sich nicht aus `τ_VS+τ_EN` errechnen. Ohne Pumpe existiert schon ein AUTO-Teilerstrom `VS/200k` ca. **45µA bei 9V**, **150µA bei 30V**: *AUTO_ON ist NICHT ein BAT-OFF-Pfad <100µA*. Der Steuerpfad muss im realen Fahrzeug OFF sein, damit das Gesamt-Batteriestromziel eingehalten werden kann.

### Kosten/Beschaffbarkeit, noch kein freigegebener BOM-Preis

- [Panasonic 10µF/100V EEE-TG2A100P](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-smd/models/EEETG2A100P) Hersteller: -40..125°C, ±20%; [Mouser DE](https://www.mouser.de/de/ProductDetail/Panasonic-Industry/EEE-TG2A100P) angezeigte **1/10/100 St. 1,11/0,678/0,494 EUR netto pro Stück**, beim Check jedoch **0 Lager und 6.499 zur Lieferung 06.11.2026 erwartet**. [DigiKey](https://www.digikey.com/en/products/detail/panasonic-industry/EEE-TG2A100P/817792) listet für seinen regionalen Shop Bestand; **DE-Live-Verfügbarkeit/Preis nicht unabhängig bestätigt**. Nicht als sofort bei Mouser verfügbar markieren. Alternative: größere [22µF/100V EEE-TG2A220P](https://www.digikey.de/de/products/detail/panasonic-industry/EEE-TG2A220P/817794) 10mm Durchmesser, -40..125°C, DigiKey DE ~2.061 auf Lager / 1St. 1,34 EUR netto. Ersatz verändert RC-Timing; kein ungeprüfter Drop-in.
- [KYOCERA AVX `12105C106K4T2A`](https://www.digikey.de/de/products/detail/kyocera-avx/12105C106K4T2A/9374706) 10µF 50V X7R 1210 AEC-Q200, DigiKey DE ~47.094 auf Lager, **1/10/100 Stück 0,83/0,53/0,3751 EUR netto** (Preis-/Bestands-Snapshot). Standardeinbauhöhe 2,79mm. Er muss bei 9V vs EN ca. 4–4,5V ebenso wie EN ca. 15V bei 30V / ca.28V bei VS56V korrekt wirksam bleiben; Hersteller-C(V,T,Alterung) prüfen.
- Weitere **Kondensatorzunahme** ~**1,94 EUR bei Einzel-DigiKey-EUR/C308-Mouser-Preismix** ohne Versand, MwSt, Verfügbarkeit und Montagesummen; solcher Preis-Mix ist **kein realer Warenkorb**. Herstellerpreispunkte bleiben getrennte Indikatoren.

## 3. Rechen-Sensitivität für 9–30 V und Grenzfälle

[Reproduzierbares Python-Skript](../../../tools/check_trippower_option_a_rc_precharge.py) und GitHub-Actions-Report `reports/trippower-option-a-rc.json` integrieren Vorladung über 9,9k, 100k/100k, die beiden Speicher-`C`, `EN≥1,05V`, `I_SHDN(max)=5µA`, beispielhaft 10µA C308-Leckstrom aus Hersteller-Ratings, sowie **mit absichtlich variabler UNSPEZIFIZIERTER Zusatzaufnahme von 2–5mA** für Pumpe während des Gates. TI `IQ(max)=0,78mA` gilt bei anderen Testbedingungen. Die angenommene CAP-Ausgabe 1,3mA bei VS≥6V und 7,9V CAP-UVLO darf nicht als VS-Eingangsstrom betrachtet werden.

Bei 9V, **idealisierten nominalen effektiven** C_VS=11µF / C_EN=10µF, angenommener Pumpeingangs-Zusatzstrom 2mA liefert das diskrete Modell grob **EN-Anstieg um 0,25s**, `VS_EN≈7,5V`, `VS_min≈6,8V` bis zum erst möglichen Gate-Enable, **ohne** Verzögerung für echte MOSFET-Strom- oder Buck-Lasten. Mit **5mA** Pumpen-Zusatz und nominalen Kondensatoren fällt VS-Minimum auf ca. **6,1V**; die Reserve ist schmal.

Bei **ungünstigen, bewusst nur als Beispiel angesetzten effektiven Kapazitäten** C_VS=8,5µF / C_EN=6µF und 5mA extra fällt VS im Modell unter **6V**, womit die TI-Pumpenstrombedingung nicht mehr erfüllt wäre. Damit ist **dieses passive RC-Netz auch rechnerisch noch nicht robust genug qualifiziert**, und es gibt weder eine verifizierte Ceff-Kennlinie noch eine obere Schranke für die Pumpeneingangsaufnahme. Nicht aus einem positiv berechneten Nominalfall auf tatsächlichen 9V-Start schließen.

## 4. Offene Designblocker: Was zuerst nachweisen/ändern?

1. **Rasche Aus-/Ein-Transienten:** C309 EN kann noch geladen sein, wenn C302/C308 VS abgesunken sind; brownout/hot-plug/replug/9→30→9V können die Vorladeverzögerung aushebeln. Eine **rückfallende EN-Überwachung** (z. B. echte VS-Unterspannungserkennung/Schmitt-Trigger, oder gepasste schnelle EN-Entladung mit Diode) wäre bei dieser Variante erforderlich; C309 allein löst das nicht sicher.
2. **Externer RUN_CMD bypass:** `D305/R317` erlaubt eine unabhängige 3,3/5V EN-Anforderung, die das RC überholen kann, wenn RUN schon aktiv ist. Der **kontrollierte Fahrzeugmodus hat damit KEINE gelöste Bootstrap-Freigabe**. Erfordert RUN-UND-VS-gut Verknüpfung oder definierte externe Sequenz; keine MCU/USB-Rückspeisung.
3. **VS-C308 10µF/100V bei -40°C / +125°C, Puls und Leckstrom:** Hersteller-C/ESR bei Kälte, Kondensatorlebensdauer (TG 2000h@125°C), 8mm-KiCad-Landpattern, 56V DC während Load Dump, 202V ESD/ungünstige Schaltung und Verpolschutz prüfen. Nachtrag kein großer BLIND-OUTER Ersatz ohne Geometrie-Prüfung.
4. **Größerer EN-Kondensator kann AUS verzögern:** `EN` ist **kein Ersatz für OV/UVLO/SCP/OCP**, die unabhängig wirken müssen. AUTO und RUN-Aus-Zeitbudget/USB-HOLD und kontrollierte Abschaltung separat prüfen.
5. **F_MAIN / 202V/350ms / Q301 heißer SOA** bleiben ungelöst. Nicht an R313–315 oder Zener-Fail-Safe ändern, bevor Bootstrap wirklich abgesichert ist.

**Schluss:** Dies ist eine bewusst reversible, messbare ***KiCad-Prototypvariante*** auf dem Design-Branch – kein ausgewählter finaler Serien-Schaltplan. Native ERC/Netlist und numerische Regression können Konsistenz prüfen, aber keinen funktionierenden Start zertifizieren. Bei EN-Bypass/Hot-Restart und 9V-Derating sind derzeit **REDESIGN-ODER-HARDWARENACHWEIS** nötig. Die nächste konstruktive Verbesserung ist ein einziges eindeutiges `VS_READY`-Gate mit definiertem Schwellwert/Hysterese, das **beide** AUTO- und RUN-Pfade qualifiziert, statt weitere große RC-Kondensatoren anzusammeln.
