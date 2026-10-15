# TripPower Weg A – reproduzierbare Schutzpfad- und Startanalyse, Runde 2 (15.10.2026)

**Branch:** design/trippower-a. **Grundlage:** docs/TRIPPOWER_A_B_REVIEW_ROUND1_2026-10-15.md auf design/trippower-review und WEG_A_LMR38020_RELIABILITY_REVIEW_2026-10-15.md auf Weg A.

**Status:** Tatsächlich commitete, ausführbare Modelle + Regressionstests + eigene native KiCad-10-ERC/Netzlisten-CI. Das schließt **keinen** Fahrzeug-, ISO-, 200-V-, 9-V-Start-, SOA-, PCB-/DRC- oder Fertigungsgate. P01–P10 weiterhin offen. Alle elektrischen REV5-KiCad-Dateien und die 57-AUTO/58-RUN-BOM sind bewusst **unverändert**, weil die fehlenden SOA-/Transientengrenzen keinen sicheren Bauteiltausch begründen. Weg B unberührt.

## 1. Ausführen und reproduzieren

Vom Repository-Stammverzeichnis:

```bash
python3 tools/trippower_a_model.py --scenario pulse --pretty
python3 tools/trippower_a_model.py --scenario startup --pretty
python3 tools/trippower_a_model.py --scenario worst_9v --pretty
python3 -m unittest discover -s tools -p 'test_trippower_a_*.py' -v
```

Native KiCad-10-Prüfung (nicht durch die Python-Simulation ersetzbar):

```bash
kicad-cli sch erc --severity-all --exit-code-violations --format json \
  -o trippower-a-erc.json hardware/modules/TripPower_5V2A/TripPower_5V2A.kicad_sch
kicad-cli sch export netlist -o trippower-a.net \
  hardware/modules/TripPower_5V2A/TripPower_5V2A.kicad_sch
python3 tools/check_trippower_native_netlist.py trippower-a.net
python3 tools/check_trippower_a_netlist.py trippower-a.net
```

Der eigene Workflow `.github/workflows/trippower-a-verification.yml` führt diese Schritte im **KiCad-10-Container** auf jedem passenden Push in Weg A aus, legt maschinenlesbare JSON-Ergebnisse und den nativen Netzlistenexport als Action-Artefakte ab. CI-Grün bedeutet **nur** reproduzierbare Arithmetik, korrekte nachgeprüfte Pin-Netze und ERC-Kohärenz. Es kann weder ein fehlendes RC-Minimum noch fehlende Hot-SOA-Kurven ersetzen.

## 2. Tatsächlicher Signal- und Schutzpfad: Netzliste und Polarität

Die Prüfung wird auf der **exportierten KiCad-Hierarchie-Netzliste** durchgeführt, nicht per bloßer Prüfung, ob Netznamen im Schaltplan vorkommen. Der zusätzliche Regressionstest vertauscht bewusst D303.1/.2 bzw. überbrückt R314 und verlangt einen Fehler. PWR_DIODE-Symbol: **Pin 1 = K, Pin 2 = A**.

| Bauteil | Pin-Netze (echter Nettopologie-Sollwert) | Konsequenz |
| --- | --- | --- |
| Q301 SQM10250E_GE3 | G1=HGATE, D2=VIN_FUSED, S3=SOURCE_A | Schaltet den 200-V-Eingang **vor** Q302; OFF-VDS hängt von SOURCE_A und Überschwingern ab |
| D303 SMBJ150A-13-F | K1=VIN_FUSED, A2=TVS_STACK | Bei positivem Impuls **Sperr-/Avalanche-Richtung**, keine Vorwärtsdiode |
| D304 SMBJ33CA-13-F | Pin1=TVS_STACK, Pin2=GND | **Bidirektionale** TVS; bei positivem Eingang in Serie mit D303 |
| D301 1SMB5943BT3G | K1=VS_CLAMP, A2=GND | Positive VS-Zener-Klemme, bei D301-Kurzschluss andere Belastung |
| D302 BAV21WQ-7-F | K1=VS_CLAMP, A2=SOURCE_A | Nachladen von SOURCE_A **erst nach** Eingang-FET-Durchleitung |
| R313 / R314 / R315 | VIN_FUSED → VS_SERIES_A → VS_SERIES_B → VS_CLAMP | 3 × 3,3 kΩ, MPN CRCW25123K30FKEGHP, je 1 % |

**P03-Ergebnis:** Bei der Hersteller-Prüfstrombedingung erreichen die zwei seriellen TVS die Summe der spezifizierten VBR-Grenzen **203,7–234,7 V**. Aus dem niedrigen Ende >200 V folgt **kein garantierter Avalanche-Klemmstrom am 200-V-Plateau**; Temperatureinfluss und dynamische I-V-Kurve sind zusätzlich offen. Die getrennt spezifizierten VC-Maxima 243 V und 53,3 V haben **verschiedene IPP-Prüfbedingungen** und dürfen nicht als nachgewiesener gemeinsamer Serien-Clamp benutzt werden. 600 W TVS-Peak bei kurzer Normimpulsform darf nicht über 350 ms integriert werden.

**Q301**: 250 V VDS abs. max, ±20 V VGS abs. max. Bei angenommenem SOURCE_A=0: 200 V VDS ohne Überschwingen, also nominell **50 V Überschwinger-Budget**. Bei +51 V ergibt sich 251 V und ein Verstoß gegen den absoluten VDS-Grenzwert. Das Modell betrachtet zusätzlich beispielhaft 2,389 A während 1/100/1000 µs bei ideal 200 V VDS (0,000478 / 0,0478 / 0,478 J). **Dies sind Rechenrechtecke, keine gemessenen Gate-/Drain-Wellenformen oder Vishay-SOA-Zulässigkeit.** Die Vishay-EAS-Avalanche-Kenngröße (84 mJ bei eigener UIS-Prüfbedingung) ist **nicht** die zulässige 350-ms-Hot-Linear-SOA.

**Quellenimpedanz / Überschwingen:** Mit **rein hypothetischer** 220-V-TV-Stack-Konstantklemme, 250-V-Leerlaufspannung, 5 Ω Quellinnenwiderstand und 100 µs Rechteck ergibt sich I=(250−220)/5 = 6 A, P_Stack=1320 W und E_Stack=0,132 J. Bei unzulässig auf 350 ms verlängertem **anderen** 250-V-Rechteck wäre E=462 J. Diese Zahlen sind **nur Sensitivitäten** auf Quellinnenwiderstand, unbekannte Clamp-Kennlinie und Pulsdauer; keine Vorhersage für den vorgegebenen 200-V/350-ms-Prüffall. Aufteilung der Leistung D303/D304 unbekannt.

## 3. 200 V × 350 ms: RVS und Zener einschließlich Einzelfehler

Annahme der folgenden Tabelle: steifer, idealer Eingang, konstanter V_Z ohne dynamischen Widerstand, 350 ms Rechteck, R-Toleranz ±1 % bei Referenzbedingung. Das ist ein **elektrisches Bemessungsscreening** und keine Hersteller-Pulsfreigabe; bei heißem 125-°C-Start und bei Wiederholung kommt zusätzliche Temperatur-/Puls-Deratingprüfung hinzu.

`I=(V_IN−V_Z)/ΣR; P_Ri=I² R_i; E_Ri=P_Ri·0,350 s; P_Z=V_Z I; E_Z=P_Z·0,350 s.`

| Fall | I VS-Zweig | E je vorhandenem R | E D301 |
| --- | ---: | ---: | ---: |
| 3×3,3k, VZ=56 V (Referenz) | 14,545 mA | 0,244 J | 0,285 J |
| Alle R −1 %, angenommen VZ=53,2 V | 14,978 mA | 0,257 J | 0,279 J |
| Alle R −1 %, angenommen VZ=58,8 V | 14,407 mA | 0,237 J | 0,296 J |
| D301 KURZSCHLUSS, alle R −1 % | 20,406 mA | 0,476 J | 0 |
| Ein RVS KURZSCHLUSS, übrige −1 %, VZ=53,2 V | 22,467 mA | 0,577 J pro verbleibendem R | 0,418 J |
| Ein RVS + D301 kurz (Doppelfehler) | 30,609 mA | 1,071 J pro verbleibendem R | 0 |

**Grenzen:** 56 V ±5 % gelten für den Zener bei spezifiziertem Prüfstrom, nicht zwangsläufig beim tatsächlichen 200-V-Pulsstrom und Temperatur. Die 2512-HP-Nennleistung allein ist kein 350-ms-Pulsenergie-/125-°C-/Mehrfachimpuls-Nachweis. Für diesen exakten Vishay-MPN sind die Temperatur-/Pulsentlastungskurven, Layout- und Wiederholungsabstände erforderlich. R-TCR und R-Pulsdrift werden noch **nicht** als nachgewiesene Grenzen eingesetzt.

**D301 OFFEN, neuer harter Prüffall** (ideale Ceff=21 µF, kein VS-Laststrom, SOURCE_A=0, daher D302 reverse, keine weiteren internen Schutzwege angenommen): `VS(t)=200−(200−VS0)exp(−t/(9900·Ceff))`.
- VS0=0 V: nach 350 ms **162,86 V**, VS=65 V bereits nach **81,71 ms**, VS=100 V nach **144,11 ms**.
- VS0=56 V: nach 350 ms **173,26 V**, VS=65 V nach **13,42 ms**, VS=100 V nach **75,81 ms**.
- Mit kleinerem wirksamen Ceff erhöht sich die Anstiegsgeschwindigkeit. Es handelt sich um eine idealisierte **Fehlerfallobergrenze ohne Laststrom**, keine Behauptung, das echte IC würde tatsächlich diese Spannung erreichen: Leckagen, ggf. interne Begrenzung, Zener-Failure-Mode und tatsächliches Ceff sind unbekannt. **Der Einzelfehlerpfad ist jedoch nicht abgesichert nachgewiesen.**

**Weitere Fehler:** D303 kurz → D304 trägt praktisch allein die positive Überspannungsabsorption; D304 kurz → D303 allein. D303 versehentlich gedreht → Vorwärtsrichtung bei positiver VIN und nur D304 als Stack-Begrenzung. Q301 D-S kurz → SOURCE_A kann 200 V sehen; Q302 ist nur 60 V spezifiziert, sein transienter VDS und der 5-V-Zweig sind dann **nicht sicher nachgewiesen**. VS-Clamp offen, Q301-Leckage bei heiß, fehlender F_MAIN und Ausgangskurzschluss sind nicht durch bloßes Bestehen des Modells behoben.

## 4. Ausführbares 9-V-Erststart-/Wiederanlaufmodell

`StartCase` im Skript integriert den precharge/pump/source-**Zustandsautomaten**, den VS-RC-Speiseweg, `Ceff`, Freigabe- und Abschaltschwelle, modellierte Vorstartleckage, beispielhafte aktive VS-Last und zusätzlich **freie Pumpenlast**. Restladung ist in `initial_vs_v`, teilweise geladener Reset-Timer in `initial_timer_fraction` parametrisiert. Die beiden Hersteller-1%-Ecken werden als `r_vs_tolerance_factor=0.99/1.01` untersucht. Nach angenommenem SOURCE_A-Hochlauf darf D302 in der Simulation idealisiert nachspeisen; dies ist ausdrücklich ein **optimistischer Grenzfall**, keine garantierte Stromlieferfähigkeit oder FET-Einschaltzeit.

Für 9 V / drei nominale 3,3-kΩ gilt statisch:
- Bei VS=8 V liefert RVS nur **101 µA** (ohne die tatsächlich abzuziehenden Leckströme).
- Bei modellierten 35 µA Gesamtabzug vor der Freigabe folgt ideal VS∞=**8,6535 V**.
- Bei angenommener ungünstiger REV5-VS_READY-Einschaltschwelle 7,51 V verbleiben ideal ca. **150,5 µA** RVS-Speisestrom. Die Schwelle basiert auf der bisherigen REV5-P02-Toleranzrechnung, **nicht** auf einer vollständig neu nachgerechneten Garantie.
- Bei angenommenen 155 µA Vorstartlast und RVS +1 % kann VS ideal nur bis ca. **7,45 V** laden: das Skript erwartet korrekt **keine Freigabe**. 155 µA ist eine bewusste **hypothetische Testlast**, kein belegter TI-Extremwert.
- Der TI-IQ-Grenzwert 780 µA stammt aus spezifizierten **12-V-/EN=2-V-Bedingungen** und darf nicht als maximale 9-V-/Pumpenlast missverstanden werden. Zusätzliche `additional_pump_ma`/Pumpenzeit sind Sensitivitätsparameter. `Ceff`=21 µF ist Bestückungsnennwert; 4 µF ausdrücklich eine nicht zugesicherte Prüfannahme.
- Ein Grenztest `ready_on_v=8.539` steht **nur** für einen besonders hohen hypothetischen Trip-/historischen REV2-Sensitivitätsfall, **nicht** als aktueller REV5-Sollwert.

Ergebnis ist ausschließlich das modellierte Zeitpunktspaar `first_ctrl_en_model_s` / `first_source_a_model_s`, VS-Minimum während hypothetischer Pumpe und Restart-Zähler. Alle Konfigurationen tragen explizit `guaranteed_9v_start=false`. Der reale TPS38-Reset/CTR-Auf- und Entladevorgang, RUN-SENSE/Feedback-Verkopplung, VIN=0/RUN-HIGH und LM74930-VS-Stromspitzen sind **nicht** durch ein generisches RC-Modell zertifizierbar.

## 5. Nächste technische Stop-/Freigabekriterien

1. **P03/P04 – vor jeder Schutz-Schaltungsänderung:** Quellenprofil 200 V / 350 ms einschließlich Flanken, Innenwiderstand, Leitungsinduktivität, negative Pulse und Wiederholrate spezifizieren. Von Vishay für **SQM10250E** hot-SOA bzw. Transiententhermik einschließlich Gate-Turnoff einholen; 250-V-VDS inkl. Overshoot und ±20-V-VGS am Prüfling durch differentielle HV-Messung prüfen. TVS-Stack D303/D304 bei *gemeinsamem* Strom und Temperatur charakt., nicht zwei spezifizierte IPP-Kennpunkte addieren. R313-315 Einzelpuls-, Dauer-/Heiß- und Wiederhol-Derating plus D301-Puls-Zth belegen. **STOP**, falls Q301 oder Clamp/VS-Grenze nicht sicher eingehaltbar.
2. **D301-offener Einzelfehler:** Nachweisen, was VS bei ausgefallenem TVS/Zener tatsächlich begrenzt und wie F_MAIN diesen Fehler (geringer Strom durch 9,9k!) beherrschen könnte. F_MAIN alleine ist **kein** nachgewiesener Schutz gegen geringe Dauer-Zenerströme. Erst wenn der Fehlerpfad nicht akzeptabel ist, getrennten technischen Änderungsvorschlag mit Hersteller-MPN/BOM/Netzlistentest erstellen; sonst Schutzkonzept revidieren.
3. **P01/P06 – 9-V-Bench-Gate:** VIN_FUSED direkt am Modul 0→9 V, langsame Rampe, Unterbrechung mit 0/4/8 V VS-Restladung und partiell geladenem C311-Timer, AUTO/RUN und RUN_HIGH mit VIN=0, −40/25/85/+125 °C, 5 V Last0/2 A plus RAW0/1 A in Stufen. Zeitgleich VIN_FUSED, VS_CLAMP, CAP_PUMP−VS_CLAMP, CTRL_EN, SOURCE_A, HGATE−SOURCE_A, J302/5V_OUT sowie I_IN messen. Ceff(V,T,Alterung), Leckage, Reset-/Gatezeiten und D302-Strom nach Datenblatt/Prüfaufbau beschaffen.
4. **Prüfgrenzen:** Q301 VDS abs 250 V, VGS ±20 V; Q302 VDS abs 60 V; VS-Betrieb 4–65 V. Zusätzlich strengere tatsächliche Pin-/PCB-/Kondensatorgrenzen, Pulslasten, MOSFET-Tj und EN VIH/VIL anwenden, nicht nur Nennwerte. Ein funktionierender 9-V-Prototyp ist keine Temperatur-/Fehlerfall-Garantie.
5. **Nur bei belastbarer Verbesserung:** Sicheres Hot-SOA-, TVS- und VS-Einzelfehler-Konzept auswählen, dann einen **eigenen reversiblen Schaltplan-Commit** mit zugehörigen Footprints, BOM-Delta, Regression, nativen ERC- und Layout-DRC-Nachweisen; **keine** prophylaktische Entnahme von Schutzbauteilen oder Widerstandsverkleinerung. F_MAIN mit Leitung/Stecker/Kupfer I²t und Q301-stuck-ON separat dimensionieren.

## 6. Quellen und Statusmatrix

- [Vishay SQM10250E](https://www.vishay.com/docs/75035/sqm10250e.pdf): 250-V-VDS, ±20-V-VGS, 84-mJ-UIS ist kein 350-ms-linear-SOA.
- [TI LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): VS-Betriebsgrenzen, Gate- und EN-Logik; keine freigegebene 9-V-Dynamik für diese Platine.
- [TI TPS38-Q1](https://www.ti.com/lit/ds/symlink/tps38-q1.pdf): reale Reset-/OD-Pegel, VDD-/CTR-Grenzen; dynamische Restladung noch offen.
- [Vishay CRCW-HP](https://www.vishay.com/docs/20043/crcwhpe3.pdf): konkreten CRCW25123K30FKEGHP inklusive Puls-/125-°C-/Wiederholbedingungen zur Freigabe heranziehen.
- [onsemi 1SMB5943BT3G](https://www.onsemi.com/pdf/datasheet/1smb5913bt3-d.pdf): VZ 56 V ±5 % bei Prüfstrom, nicht automatisch harte VS-Klemme für alle 200-V-Transienten.
- [Diodes SMBJ150A](https://www.diodes.com/part/view/SMBJ150A), [SMBJ33CA](https://www.diodes.com/part/view/SMBJ33CA): Vergleichs-/Pulsbedingungen getrennt.
- **Neu im Repository:** `tools/trippower_a_model.py`, `tools/test_trippower_a_model.py`, `tools/test_trippower_a_netlist.py`, `tools/check_trippower_a_netlist.py`, `.github/workflows/trippower-a-verification.yml` und dieser Bericht.
- **Gates:** P01/P02/P03/P04/P05/P06/P07/P08/P09/P10 weiterhin **OPEN/BLOCKED**. Native ERC und Netzlistentopologie sind **Teilprüfungen**, nicht die Freigabe.
