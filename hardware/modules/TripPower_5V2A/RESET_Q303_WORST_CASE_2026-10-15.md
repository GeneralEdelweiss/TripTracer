# RESET-/Q303-Worst-Case -40…+125 °C — **KEINE FUNKTIONSFREIGABE** (15.10.2026)

**Entscheidung:** Die momentan als physischer KiCad-10-Prototyp gespeicherte `U302(TPS3760A012DYYRQ1) → D306/D308 → Q303(BVSS123LT1G) → U301(EN)`-Schaltung kann mit den Herstellerdaten **weder ein garantiertes AUS bei allen Temperaturen noch ein garantiertes EIN bei 9V** nachweisen. Der 202V/350ms-Lastabwurf und `F_MAIN` bleiben ebenfalls nicht freigegeben. **Dies ist ein Review, keine Simulation, kein Labortest, keine Freigabe für Fertigung/Fahrzeug.** Diese Feststellung ist wesentlich wichtiger als ein erfolgreiches KiCad ERC/Netlist-Ergebnis.

## Herstellerquellen und Gültigkeitsgrenzen

- [TI LM74930-Q1, Kap. 6.5](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): `EN_FALL min = 0.41V` (darunter AUS sicher), `EN_RISE max = 1.05V` (darüber EIN sicher), `I_EN max = 200nA`, `VS` Normalbetrieb 4–65V, Hersteller-Temperatur `-40…+125°C`.
- [TI TPS3760-Q1 Rev.B 2026 Kap. 6.5–6.6](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf): `V_SENSE 0.792…0.808V` bei 0.8V-Variante über Temperatur, `I_SENSE max 100nA`; 2% Hysterese mit ±1.5% **Hysteresewert**-Genauigkeit; `V_RESET_OL max 0.3V` bei `I_RESET=5mA`; `I_RESET_HiZ max=300nA`; interne Reset-Aussage **unter VPOR~1.4V nicht definiert**; `CTR`-Verzögerung streut mit Ceff und intern 877–1147kΩ.
- [onsemi BVSS123LT1G Datenblatt Rev.13 (05/2024), S.1–2](https://www.onsemi.com/pdf/datasheet/bss123lt1-d.pdf): `IDSS max15µA @25°C / max60µA @125°C` **nur bei VGS=0V, VDS=100V**; `VGS(th) 1.6…2.6V` bei 1mA **25°C-Testbedingungen**; `RDS(on)≤6Ω` nur bei `VGS=10V, ID=100mA`; Dauerleistung `225mW @25°C, minus1.8mW/K`, daraus **45mW @TA125°C** auf angegebenem FR-5-Testboard.
- [Vishay BAS70-02V-HG3-08 Rev.1.6, S.1](https://www.vishay.com/docs/85652/bas70-02v.pdf): physisch **Pin1 ANODE, Pin2 CATHODE** (Hersteller-Zeichnung!), `IR(max)=100nA` bei `VR=50V` **nur Tamb25°C und tp<300µs**; `VF(max)=410mV` bei `IF=1mA` ebenfalls **nur 25°C/kurzem Puls**; **kein DC-IR-Maximum bei+125°C oder garantiertes VF bei 50µA/125°C** angegeben. 70V VRRM, max TA +125°C. AEC-Q101 bedeutet NICHT, dass die fehlenden Eckwerte garantiert sind.
- [onsemi SZMMSZ5240BT1G](https://www.onsemi.com/pdf/datasheet/mmsz52xxbt1-d.pdf): nominal 10V Zener (bei spezifiziertem mA-Teststrom), im Design über R334=470kΩ bei 8–65V jedoch **nur einstellige bis ~140µA** verfügbar; Klemmspannung bei diesen Strömen über Temperatur/Alterung **nicht mit garantiertem Maxwert nachgewiesen**.

## 1. Physischer Pin-Fehler aus der Vorgängerrevision bereits berichtigt

**Nicht nur mathematisches Problem:** Vishay BAS70-02V SOD-523 hat in der Herstellerzeichnung **A1/K2**. Der gemeinsame bisherige `TripTracer_V1:PWR_DIODE` benutzt dagegen **K1/A2**. Damit wäre D306/D308 bei ungeprüfter Übernahme in eine Platine **verpolt** worden.

**Elektrisch logisch unveränderte, echte native KiCad-Korrektur:** Projekt-Bibliothek `TripPower_Sym:BAS70_02V_A1_K2`; `D306.2=K=VS_READY_RESET_OD_PRELIM`, `D306.1=A=EN_GATE_DRIVE`, `D308.2=K=VS_READY_RESET_OD_PRELIM`, `D308.1=A=CTRL_EN`. Netzlisten-Regression prüft diese echten Padnummern, nicht bloß Netznamen. D307 ist eine **andere Zenerdiode** und behält getrennt ihre eigene K1/A2-Belegung. Physische KiCad-SOD-523-Landpattern-Orientierung vor PCB-Freigabe zusätzlich mit TI/Vishay-Skizze und Druck überprüfen.

## 2. AUS: <0.41V ist nicht garantiert — schwerster Fehler

**Alte Rechnung** unter der hypothetischen Annahme `VGS(Q303)=0V`:
`I_DSS,125°C × R316 = 60µA × 5.6kΩ = 0.336V`. Dazu `I_EN max0.2µA × 5.6kΩ = 1.12mV`, damit **0.337V theoretisch**. Das wäre nur bei der **exakten onsemi-Testbedingung** ein gebundener Wert.

Die reale Schaltung nimmt bei `RESET=LOW` aus dem Supervisor **bis zu 0.300V** auf; `D306` Schottky leitet erst mit positivem **V_F**, Q303-Gate liegt damit grob bei `V_RESET + V_F` statt an 0V. Q303 `VGS` ist somit nicht garantiert ≤0V. Die onsemi-60µA-Spezifikation ist **hier nicht anwendbar**, ohne dass wir die erhöhte Stromaufnahme unter positiver VGS bei hohen Temperaturen eingrenzen können. `R316=5.6kΩ` allein ist keine Fail-Safe-Auslegung.

**D308 zusätzliche Schottky-Klemme**: TI `V_RESET_OL(max)=0.300V`, Vishay `VF(max)=0.410V @1mA/25°C`; die kombinierte Spannung kann am entsprechenden Prüfpunkt **0.710V > 0.410V** betragen. Dies beweist *nicht*, dass bei 125°C tatsächlich 0.710V anliegen, aber **kein zulässiger oberer Garantiewert** für <0.41V lässt sich daraus ableiten. Bei +125°C fehlt außerdem die garantierte VF(50µA–mA)-Kennlinie. Sicheres Ausschalten **FAIL/UNPROVEN**.

Zusätzlich darf bei `VDD(U302)<VPOR(~1.4V)` die Reset-Open-Drain-Ausgabe beliebig sein; die Logik muss mit `RUN_CMD=5V` und `VIN=0V…3V` trotzdem ohne Fahrzeugrückspeisung AUS bleiben. Nicht untersucht.

## 3. EIN: bei 9V kann Q303 nicht mit garantiertem Strom durchgesteuert werden

Nominell `V_GATE≈VS × 1M/(470k+1M)` ohne Zener-/Diode-Lecks:
- Bei `VS=8V`: Gate≈**5.44V**.
- Beispiel mit **3µA** Leckverlust am Gate (nicht die garantierte Schaltungsvorhersage): Gate≈**4.48V**.
- Ideales AUTO-Ausgangspotenzial bei R318=22k und R316=5.6k: `8 × 5.6/(22+5.6)=1.62V`; dies **ignoriert ausdrücklich Q303**.
- Ideales RUN3.3V mit angenommenem D305 `VF=0.8V`: Ausgang `(3.3−0.8)×5.6/(4.7+5.6)≈1.36V`; ebenfalls kein garantiertes Gate-Verhalten.

Q303 arbeitet als **Source-Follower**, dessen verfügbarer `VGS` am tatsächlichen EN-Pegel nur etwa **3–4V** beträgt. Onsemi garantiert hier aber `RDS(on)≤6Ω` ausschließlich bei **VGS=10V und 100mA**. Selbst eine Schwellspannungsangabe bei 1mA ersetzt keine `I_D,min`-Kurve für 0.2–0.5mA bei −40°C und +125°C. Das geforderte `EN > 1.05V` ist deshalb **nicht garantiert**. Bei 9V Fahrzeugbatterie sinkt VS während CAP-Aufladung und die Gate-Marge weiter.

## 4. Gate-Spannung: 10V-Zener nicht als bewiesener 20V-Schutz behandeln

Ohne nachgewiesene Klemmwirkung ergäbe R334470k/R3351M bei `VS=56V` `V_GATE≈38.1V`, bei `VS=65V` ≈**44.2V** bei Source=0V. `BVSS123LT1G VGS(max) ±20V`. D307 soll das verhindern, aber der 10V-Wert wird bei einem **wesentlich höheren Zener-Teststrom** spezifiziert als unsere max. ca. `(65V−10V)/470kΩ≈117µA`. Ohne garantierte Zener-I(V,T)-Kurve bei diesen Strömen ist `|VGS|<20V` über 202V/350ms, −40…125°C und Restart **nicht nachgewiesen**. Physisch kann die Zener real gut begrenzen; das ist ohne Messung/Limits **keine Garantiezusage**.

## 5. Hysterese 8V/6V – mit tatsächlichen Widerstandstoleranzen

R330=845kΩ, R331=100kΩ, R332=1.91MΩ, R333=1MΩ. Für **±1% alle vier**, `VITN=0.792…0.808V`, interne `VHYS=16mV ±1.5%`, `I_SENSE=±100nA` konservativ, `RESET_OL=0…0.3V`, aber ausdrücklich **ohne externe Schottky-Reverseleckage** und RESET-HI-Z-Variation:

| Schaltpunkt | Nominal (V) | Eckwert min (V) | Eckwert max (V) |
|---|---:|---:|---:|
| RESET freigeben nach stabiler Vorladung | **8.072** | **7.635** | **8.387** |
| RESET LOW nach Versorgungseinbruch | **6.039** | **5.811** | **6.272** |

Bei `VIN=9V` liefert ein *optimistisches* vereinfachtes Kaltstartmodell mit 9.9kΩ RVS und LM74930-OFF5µA, Supervisor2.6µA, C30810µA, R330-SENSE9µA, Reset-1M-Pullup und Gate-470k Zweig `VS_OFF≈8.49V`. Zur pessimistischen idealen 8.387V-Schwelle bleiben nur **~0.10V Modellreserve**, **bevor** 125°C-Leckströme, Zenerabweichung, VS-Schutz-/Diodenleck, Resistor-Temperaturdrift, RESET-Störströme und C302/C308-Derating erfasst wurden. **9V-Einschalten nicht garantiert.**

## 6. 202V/350ms: Korrektur thermischer Bauteilzuordnung

**Der alte Bericht hat ~109mW fälschlich Q303 zugeordnet.** Richtig ist bei VS=56V und hypothetisch EN≈7V:
`P_R318=(56−7)^2/22000≈109mW` – das ist die Verlustleistung **in R318**, nicht automatisch im MOSFET.

Mit nur VS→R318→Q303→R316/Last kann Q303 unter idealisierter ohmscher Quelle maximal
`P_Q303 ≤ VS^2/(4×R318)` aufnehmen, **≈35.6mW bei VS56V** und **≈48.0mW bei VS65V**. Der onsemi-Wert `P_D(125°C)=225−1.8×100=45mW` für das Herstellerboard bedeutet: **bei VS65V würde selbst diese einfache 48mW-Obergrenze oberhalb der DC-125°C-Deratinggrenze liegen**. Bei 56V läge die idealisierte Obergrenze unter45mW; tatsächlicher VDS/ID/zeitlicher Verlauf/zusätzlicher RUN-Pfad/Zth bleiben ungeprüft. Die reale Metall-/Leiterplattenumgebung weicht vom FR-5-Testboard ab.

Für **R318** beträgt die grobe absolute ohmsche Obergrenze `VS²/22k`: **143mW bei56V, 192mW bei65V**. Die bisherige generische 1206-Footprint-Angabe ist **keine Pulsleistungs-/125°C-Rating-MPN**. Dauer-Strompuls sowie 202V-Überspannungs-Profil und Worst-Zener-Voltage müssen mit einer **konkreten widerstandsfesten MPN** bewertet werden.

## 7. RESET-Knoten und Schottky-Reverseleck

`R333=1MΩ` liefert bei VS56V und niedrigem RESET ideal maximal **56µA** Pull-up-Strom. D306 und D308 sind im Freigabezustand gesperrt und können über den RESET-Knoten in Gate- und CTRL_EN-Netze lecken. Die BAS70-Datenblattgrenze `IR≤100nA @50V` gilt **nur bei Tamb25°C und Pulslänge<300µs**, nicht bei +125°C im Dauerbetrieb. Es gibt keinen 125°C-IR-Garantiewert; bereits Leckströme im Bereich einiger µA verschieben die hohen 845k/1.91M/1M-Schwellen deutlich oder verlangsamen/verhindern ein hohes RESET. Die 300nA des TI-RESET-Ausgangs gelten nur für den IC-Ausgang selbst, **nicht** als Garantie für zwei externe BAS70. Damit sind die errechneten 8.072/6.039V nur ideale Vorbemessung.

## −40/25/85/125°C-Prüftabelle

| Temperatur | Q303 IDSS laut Hersteller | BAS70 Reverse Leakage | U302-Freigabe / EN |
|---|---|---|---|
| −40°C | Kein expliziter garantierter Q303-IDSS-Eckwert im angegebenen Testpunkt | Kein IR_max bei −40°C | Nicht freigegeben |
| +25°C | ≤15µA bei VGS0/VDS100, andere VGS nicht spezifiziert | ≤100nA bei VR50 und kurzem Puls | Nicht freigegeben |
| +85°C | Kein expliziter garantierter Q303-IDSS-Eckwert | Kein IR_max bei +85°C | Nicht freigegeben |
| +125°C | ≤60µA bei VGS0/VDS100, **nicht realer VGS** | Kein IR_max bei +125°C | **Nicht freigegeben, kritischer Fall** |

## Entscheidung und nächster Designschritt

**Ich empfehle, diese konkrete Schottky+Q303-Source-Follower-Schaltung nicht für die Fahrzeugplatine freizugeben.** Ohne Spekulationsfaktoren lassen sich weder der garantierte AUS-Pegel noch der garantierte EIN-Pegel beweisen. Das aus TI TPS3760-Q1 ausgesuchte IC bleibt prinzipiell geeignet; das **RESET→EN-Interface muss anders konstruiert** werden:
1. Den **von RESET=LOW aktiv nach GND gezogenen EN** technisch direkt mittels zulässigem Treiber-/Logikpfad realisieren, ohne den ungebundenen BAS70-VF-Anteil und ohne positive nicht spezifizierte MOSFET-VGS im AUS. Bei OFF, VIN=0, extern RUN=HIGH sowie U302 VPOR undefiniert **statisch fail-safe**.
2. Hochohmige Schmitt-Feedback-R333/R332 von Hot-Leckpfaden entkoppeln; dokumentierte I_R(125°C) oder Alternativ-IC mit nativ definierter großer 8/6V-Hysterese prüfen (COTS-first).
3. Gate-VGS-Versorgung und Rücksetzzeit mit konkreten Temperaturkurven und der realen 202V/350ms VS-Zener-Surge begrenzen. AUTO/RUN bleiben in serie nach der Freigabe, keine heimlichen Bypässe.
4. Nach Auswahl: KiCad10-ERC **plus** native Pin/Footprintprüfung, 9V/12V/24V/30V mit Last und −40…125°C, hot restart, Brownout, 202V/350ms/gesicherter VIN samt F_MAIN-I²t.

**Keine versteckte Designfreigabe über grünen Python-Exit:** `tools/check_trippower_reset_worst_case.py` enthält diese Herstellerwerte und publiziert ausdrücklich `"result": "BLOCKED"`, selbst wenn alle Formeln korrekt sind. Der in KiCad vorhandene Q303-Baustein bleibt **nur ein gesperrter Entwicklungsprototyp**, bis eine elektrisch qualifizierbare Verriegelung ersetzt ist.
