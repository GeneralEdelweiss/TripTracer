# TripTracer ACC-Erkennung U912: Datenblatt-Nachweis, 14.10.2026

**Ergebnis: NICHT NACHGEWIESEN / KEINE SCHALTUNGSFREIGABE.** Dieser Bericht beweist anhand der Herstellergrenzwerte, warum die aktuelle Schaltung NICHT als zuverlässig für 9–30 V und -40 bis +85 °C zugesagt werden kann. Eine positive Funktionsgarantie lässt sich aus den verfügbaren Daten **nicht** ableiten.

## Prüfling und Herstellerdaten

KiCad: `hardware/kicad/01H_ACC_HOLD_GATE.kicad_sch`, U912 Würth 140356145000 (SOP4), R916=6.8 kΩ, R917=47 kΩ nach GND, Optotransistor-Kollektor an V3V3_SYS, Emitter an ACC_DRIVE_5V (Netzname historisch; maximaler Pegel 3.3 V). Herstellerdatenblatt Rev.001.004 vom 22.08.2023, Seiten 1–2: https://www.we-online.com/components/products/datasheet/140356145000.pdf

- Optokoppler-Ambient laut Produktdaten -55…+110 °C: dies ist ein **Betriebs-**, kein garantierter CTR-Arbeitspunkt.
- Maximaler LED-Strom 60 mA; maximale LED-Eingangsverlustleistung 100 mW.
- LED-Durchlassspannung **max. 1.4 V bei 10 mA**; bei 1 mA nicht als harte 1.4-V-Grenze belegt.
- Hersteller-CTR **mindestens 50 % ausschließlich bei IF=5 mA, VCE=5 V**, in der allgemeinen elektrischen Tabelle bei 25 °C. Für **IF~1 mA** und **-40 °C oder +85 °C** ist kein garantierter absoluter CTR-Mindestwert angegeben.
- Max. Collector-Emitter-Spannung 80 V; lokale 24-V-Transienten und >80-V-Fehlpulse gesondert absichern.

## U912-Stromrechnung (nur Indikativrechnung)

Mit angenommenen VF=1.4 V (bei tatsächlichen Strömen nicht herstellerseitig garantiert):

`IF=(V_ACC-1.4V)/6800Ω`

| ACC | IF indikativ | rechnerisch 50%-CTR, **nicht garantiert** | I_R917 bei Vout=2.31V |
|---:|---:|---:|---:|
| 9 V | 1.12 mA | 0.56 mA | 49 µA |
| 12 V | 1.56 mA | 0.78 mA | 49 µA |
| 24 V | 3.32 mA | 1.66 mA | 49 µA |
| 30 V | 4.21 mA | 2.10 mA | 49 µA |

Selbst wenn diese exemplarischen Photoströme weit oberhalb des R917-Laststroms liegen, sind sie **keine belastbare Worst-Case-Garantie**, da die CTR-Mindestangabe bei den tatsächlich vorliegenden IF nicht gilt. Der 555-TRIG hängt zudem von Impulsdauer/Flankenform und Leitungszustand ab.

## Lässt sich das mit einem Widerstandswechsel beheben?

Um unter idealisiertem VF=1.4V bei ACC=9V wenigstens 5 mA zu erreichen, wäre R916 <= (9-1.4)/0.005 = **1.52kΩ** erforderlich. Bei ACC=30V ergäben sich damit ungefähr **18.8 mA** und **0.538 W** Verlust an R916. Das wäre mit einem üblichen 1206-Widerstand ein thermisches Risiko und liegt bereits ohne Temperaturderating weit oberhalb unserer Low-Cost-/Ruhestrom-Orientierung. Mehr noch: Der garantierte minimale CTR-Punkt ist bei **IF=5mA**, nicht für jeden beliebigen höheren Strom oder jede Temperatur; die bloße Verkleinerung von R916 liefert deshalb **auch keinen temperaturweiten Funktionsnachweis**. Bei 30V bliebe LED-P≈26mW unter 100mW (ideal), aber die Widerstandsleistung ist die unmittelbare Schwachstelle.

## Besserer Entwicklungsweg

Für einen wirklich belastbaren ACC-Detektor keine CTR-Annahme außerhalb garantierter Kennlinien verwenden: günstigen Automotive-Hochvolt-Komparator / High-Voltage-Input-Buffer mit ausdrücklichen VIL/VIH- und Leckstrom-Grenzen über Temperatur prüfen und den Eingang über spannungsfeste RC-/TVS-Beschaltung absichern. Alternativ diskreten Transistor/Schmitt-Eingang **nur mit vollständiger Worst-Case-Berechnung** zu Threshold, Leckströmen und Temperatur; die vorhandene optische Trennung bietet keine notwendige galvanische Isolation, da beide Seiten dieselbe Masse besitzen. Eventuell ist eine solche Vereinfachung gleichzeitig günstiger und sparsamer als U912 + R916.

## Reproduzierbare Prüfungen

`python3 tools/prove_acc_opto_limits.py`: prüft, dass R916 und R917 unverändert sind, rechnet 9/12/24/30V und weist fehlende garantierte CTR sowie die Widerstandsverlustleistung aus. **Ein PASS des Prüfskripts bedeutet: die fehlende Garantie wurde korrekt erkannt, NICHT dass U912 bestanden hat.**

System-Nachweis erfordert zusätzlich echte ACC EIN/AUS-Messungen über 9–30V, -40 bis +85°C, 555-Trigger, V3V3-Spannung, MCU stuck-high, Eingangs-Transienten und Ruhestrom. Das Hardwaredesign darf bis dahin nicht in Fahrzeug/Produktion.
