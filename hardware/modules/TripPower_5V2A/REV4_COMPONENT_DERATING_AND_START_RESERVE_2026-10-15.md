# TripPower REV4 – Bauteil-Überdimensionierung gegen 9-V-Kaltstartrisiko (15.10.2026)

**Aktiver Prototypen-KiCad-Stand auf `design/solid-state-power-v1` – NICHT Fertigungs- oder Fahrzeugfreigabe.** Ziel: bereits bekannte 9-V-VS-Haltezeit- und RESET-Zeitrisiken durch reale Automotive-Bauteile verringern. Unverändert: VIN_FUSED 9–30 V am Modul, 5 V/2 A, RAW 1 A Ziel, R313–315 9,9 kΩ + 56-V-Klemme + A→VS D302, TPS3760 mit R330=715k und diskretem Q303–Q305-Enable, Q301 Vishay SQM10250E, 202 V/350 ms nur Designziel.

## 1. Tatsächlich in KiCad geändert

| Referenz | Alt | REV4 gewählt | Hersteller-/Beschaffungsbeleg | Status |
| --- | --- | --- | --- | --- |
| **C311** CTR | 220nF/50V, MPN_PENDING | **KEMET C1206C334K1RACAUTO**, 330nF ±10%, 100V X7R, 1206, AEC-Q200, −55…+125 °C | [Mouser AEC-Auto X7R](https://www.mouser.com/en/c/passive-components/capacitors/ceramic-capacitors/mlccs-multilayer-ceramic-capacitors/multilayer-ceramic-capacitors-mlcc-smd-smt/?height=1.6+mm+%280.063+in%29&length=3.2+mm+%280.126+in%29&product=Automotive+MLCCs&qualification=AEC-Q200&width=1.6+mm+%280.063+in%29) | **Aktiv im KiCad**, Rückstands-/Stückpreis vor Bestellung erneut prüfen |
| **C308** VS | Panasonic EEE-TG2A100P 10µF 100V Aluminium, 8×10.5mm SMD, polar | **KYOCERA AVX KAF55CR72A106KV**, 10µF ±10%/100V X7R, 2220, AEC-Q200, Flexiterm, −55…+125°C | [Mouser DE](https://www.mouser.de/de/ProductDetail/KYOCERA-AVX/KAF55CR72A106KV), typ. Preisindikator Oktober 2026 4,48€/1, 3,40€/10, 2,77€/100 (netto; live prüfen) | **Aktiv KiCad**, jetzt **unpolar** `Tripmaster_Sym:C`, Standardfootprint `Capacitor_SMD:C_2220_5750Metric` |
| **C312** VS | nicht vorhanden | weiterer **KAF55CR72A106KV**, ebenfalls 10µF/100V/X7R/2220/Flexiterm | dieselbe Hersteller-MPN | **Neu aktiv KiCad**, parallel C308 und C302 auf VS_CLAMP↔GND |
| **C302** VS HF | 1µF/100V MLCC | unverändert 1µF/100V | bestehend | 21µF **nominell gesamt**, effektiv nicht garantiert |

Für C308 wurde die **Polar-Cap-Symbolinstanz wirklich durch ein nichtpolares Symbol ersetzt und beide Wire-Endpunkte um 1,27mm neu angeschlossen**; analog für C312 eine zweite nichtpolare Instanz mit getrennten eindeutigen UUIDs und physischen Pinnetzen. Natives ERC/Netlist CI bleibt zwingend; ein fehlerfreier ERC ersetzt Layout-/Fußdruckprüfung nicht.

Die 100V-MLCCs sind bewusst höher spezifiziert als die 56V nominale VS-Zenerklemme, um **Spannungsderating** und Kältestartreserven zu begünstigen. Dennoch **VZ(max)/Transienten** und ESD, effektive DC-Bias-Kapazität bei 8–9V (Start) und 56–65V (Surge), MLCC-Ausfall durch Biegung, Schock, Montage und temperaturabhängiger Isolationswiderstand weiterhin prüfen. `AEC-Q200` ist keine Garantie minimaler Ceff bei VS oder maximaler Leckstrom bei 125°C.

## 2. Rechenbasierter Nutzen beim 9V-Kaltstart

- TPS3760-Q1 internes `RCTR` nach [Datenblatt Rev.B](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf): min/typ/max 877/1000/1147 kΩ und `t=-ln(k) RCTR C311`; für C311330nF **nominal 420ms**.
- **Nicht garantiegebende Zeitspanne** unter *angenommen* ±10%-C-Erstwert und zusätzlichen ±15%-X7R-Temperatur (DC bias/aging nicht enthalten): **259ms früh bis 664ms spät**. Bei nicht vollständig entladenem CTR/C311 kann Neustart wesentlich schneller freigegeben werden!
- Gleiches fiktives 9V-Strombudget wie bisher: RVS9900Ω, I_OFF=34,6µA (nicht Herstellermax), oberes REV3-READY-Szenario 7,510V (nicht garantiert). VS_eq=9V−9,9k·34,6µA≈8,657V. Bei Ceff **NOMINAL** 11µF (REV3) erreicht VS 7,510V nach 220ms; nach hypothetischen 259ms Delay VS≈8,551V; bis 6V gespeicherte Ladung ≈**28,1µC**. REV4 nominal 21µF braucht zuerst 420ms bis 7,510V; nach denselben 259ms Delay VS≈**8,328V**; Ladung bis 6V ≈**48,9µC** (rund **+74 %**). Bei nominaler REV4-Schwelle 7,234V und typ420ms Delay liegt VS≈8,469V, Kaltstartdauer ≈795ms, *vor* unbekannter Pumpen- und Buck-Softstartzeit.
- Die zweite größere Kapazität **verschlechtert vorübergehend die Spannungshöhe und verlängert die Vorladung**, ermöglicht aber mehr gespeicherte Ladung bei pumpenbedingtem Stromimpuls. **Deshalb weder linear höhere Zuverlässigkeitsprozent noch garantierter Start daraus ableiten.**
- `tools/check_trippower_rev3_12v_startup.py` enthält jetzt die tatsächliche REV4-BOM und das RC-Modell; alle Modellparameter und Quell-/Sperrströme bleiben explizit *hypothetisch*.

## 3. Q301: weitere machbare Absicherung, vorerst KEIN Teiletausch

| Alternative | VDS | RDS_on max @25°C/10V | Qg max @10V | Plus | Minus |
| --- | ---: | ---: | ---: | --- | --- |
| Aktiv: Vishay `SQM10250E_GE3` | 250V | 30mΩ | 75nC | geringe Leitverluste bei 2,4A | hohe Pumpen-Gateladung |
| Nur Alternative: Infineon `IPB17N25S3-100` | 250V | 100mΩ | 19nC | **rund 75% weniger maximale Gateladung**, Automotive, D2PAK | ca. 3,3× RDS, höhere PCB-Thermik/5V/2A-Langzeittemperatur |

[Infineon Herstellerangaben](https://www.infineon.com/part/IPB17N25S3-100), [Vishay Herstellerdaten](https://www.vishay.com/en/product/75035/). Die **19nC** gelten für die im Datenblatt festgelegten Gate-/Strom-Messbedingungen; kein garantierter Start-VS-Stromwert. **Vorerst Vishay behalten**, für experimentelles Q301-A/B mit gleicher TO263-D2PAK-Mechanik alternative BOM reservieren, genaue Metall-Tab-/Pad-1/2/3-Gleichheit noch abgleichen. 202V-SOA in beiden Varianten offen.

## 4. Was damit besser wird – und was nicht

**Verbessert/reduziert:** C311-MPN nicht länger offen, längere definierte nominale CTR-Verzögerung, niedrigeres/bei Kälte robusteres VS-ESR (nicht konkret milliohm garantiert), nominal rund 74% mehr gespeicherte Ladung beim modellierten 9V-Startup, kein Elektrolyt-Bauteil im kritischen VS-Vorladezweig, mechanisch flexible Keramik-Endkappen. Alle aktiven FET-/Schutz-/RUN-Bauteile unverändert.

**Noch NICHT gelöst:**
1. TI LM74930 dynamischer **I(VS,t)** bei 9V-CAP-Pumpenstart, keine spezifizierte VS-Strom-Obergrenze; durch Kondensatoren lässt sich kein beliebiges Worst Case „wegdimensionieren“.
2. C308+C312 **effektive** Gesamtkapazität einschließlich DC-Bias bei 9V/56V, Temperatur, Alterung und Isolationswiderstand +125°C; kein numerischer Hersteller-Minimalwert in dieser Revision belegt.
3. Q303/Q304/Q305 **hFE_min bei µA-Strömen/−40 bis +125°C** und **Q303 I_CE_OFF<18,25µA bei125°C** unbekannt; mehr C311 kann die EN-Pegelsicherheit **nicht** lösen. In einem Folge-Design ist ein **qualifizierter integrierter 65V-toleranter Supervisor/Levelshift-Treiber** mit definierter Push-Pull-Logik auf Beschaffbarkeit zu prüfen, statt bloßer BJT-Umbiasierung. TPS3760-OD und vorhandene externe Hysterese bleiben REV4.
4. Q301 hot-VDS-SOA für 202V/350ms, F_MAIN/I²t, interne Zener/TVS-Leck/Impulsfestigkeit, Q302, PCB-Kupfer/Thermik, eigenständiges PCB-DRC, reale Funktion −40/+125°C.
5. Der Gesamtfahrzeug-OFF-Strom **<100µA** ist für die aktuelle BOM nicht gemessen oder nachgewiesen. Zwei große MLCCs sind nicht als Null-Leck anzusetzen.

## 5. Vor dem ersten echten PCB-Auftrag

Native KiCad10 Standalone-ERC und Netzliste mit beiden VS-MLCCs und C311 müssen durchlaufen. Ein Labor-Prüfling braucht **VS_CLAMP, CAP−VS, CTRL_EN, HGATE−SOURCE_A, SOURCE_A, VIN_FUSED, VIN_PROTECTED_UNFUSED, 5V_OUT** zugängliche differentialtaugliche Prüfpunkte und Eingangs-Strombegrenzung. 9/12/13,8V schnell/langsam bei 0/0.5/2A Ausgang, kontrolliertes RUN/AUTO sowie Wiederanläufe mit teilgeladenem CTR. Erst danach thermische und Safety-Gates.

**Urteil:** REV4 ist eine **bewusst teurere, konservativere Prototyp-BOM**, kein Garantiewechsel. Keine Fertigung freigeben, bevor echtes eigenes TripPower-PCB platziert/geroutet/DRC-geprüft und Footprints 2220/Flexiterm physisch verglichen wurden. Kein 202V-Impuls auf unqualifiziertem EVM.
