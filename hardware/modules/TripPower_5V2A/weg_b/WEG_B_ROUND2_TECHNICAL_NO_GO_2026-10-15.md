# TripPower Weg B – Review Runde 2: quantitatives NO-GO als **einfacherer** REV5-Ersatz

Datum 2026-10-15. Branch **`design/trippower-b`**. Nur `weg_b/` und neuer isolierter CI-Workflow geaendert. Ausdruecklich **KEINE** Aenderung der gemeinsamen REV5-Baseline oder Weg A. Basisreview: `docs/TRIPPOWER_A_B_REVIEW_ROUND1_2026-10-15.md` auf `design/trippower-review`.

## Entscheidung vor weiterem KiCad-Aufwand

**NO-GO fuer einen TPSM33620S5QRDNRQ1 als einfachere, bereits sicher qualifizierbare 9–30-V/5-V-2-A-/200-V-350-ms-Alternative zum LMR38020-Q1.** Der IC selbst ist verfuegbar und gut; der benoetigte **garantierte** VIN-Pad-Schutz ist mit lediglich einem praezisen OV-Supervisor nicht beweisbar. Eine ausreichend schnelle, energie- und temperaturfeste zusaetzliche VIN-Klemme/zweiter schaltender HV-Schutzpfad + Default-OFF-Interlock kann prinzipiell untersucht werden, macht den Ersatz aber komplexer als Weg A und neutralisiert dessen minimale Teilezahlersparnis. Deshalb **kein** provisorisches KiCad-10-Schema, unvalidierter Footprint oder Pseudo-DRC. No-Go ist eine **Systemkosten-/Nachweissentscheidung**, kein physikalischer Beweis, dass irgendeine aufwendigere 36V-Architektur unmoeglich waere.

**Nachweise im Branch:** Ausfuehrbares Rechenmodell `verify_b_feasibility.py`, sieben reproduzierbare Regressionsgruppen `test_verify_b_feasibility.py`, isolierter GitHub-Workflow `.github/workflows/trippower-weg-b-feasibility.yml`, positionsgenaues `BOM_DELTA_TPSM_CANDIDATE_2026-10-15.csv`. Python-stdlib ohne Drittanbieter. Tests koennen `PASS` fuer korrekt erkannte **NO-GO-Gates** melden, nicht eine positive Hardwarefreigabe. Native KiCad-10/ERC/DRC und physische Tests **nicht ausgefuehrt**.

## Verwendete aktuelle Datenblaetter / Parameter

1. [TI TPSM336xx-Q1 Rev.E September 2026](https://www.ti.com/document-viewer/TPSM33620-Q1/datasheet): 3–36 V recommended VIN; 40 V abs max; 5 V/2 A fixed OPN **TPSM33620S5QRDNRQ1**, HotRod 11-pad RDN (4,5 × 3,5 mm), AEC-Q100. TI nennt Laststrom-Derating bei hoher TA, maximal TJ 150 C, empfohlen Layout mit wenigstens einer inneren Masseflaeche und Top/Bottom 2-oz Kupfer. [8.2.2.8 Thermal](https://www.ti.com/document-viewer/TPSM33620-Q1/datasheet/GUID-9A0F9FB2-C8B6-47B9-8D2F-7A0895280F88). [8.2 typical reference values](https://www.ti.com/document-viewer/TPSM33620-Q1/datasheet/GUID-E2EC81F3-EFE3-4E24-8C76-88B8C88E35F0).
2. [TI TPS3760-Q1 SBVS419B Mar 2026](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf) S.3,5,7–10,21–22: tatsaechlich gelistete Automotive **TPS3760E012DYYRQ1**, OV 0,8V 1%-Threshold (0,792/0,800/0,808V), 2%-Hysterese mit +/-1,5%-Genauigkeit auf die Hysterese, OD active LOW, VDD empfohlen 2,7–65V, VDD unter 1,4V Output **undefiniert**. Max Sense Delay 17 us **nur** 20% Overdrive bei 1V/us, Ausgangslast etc; bis 2ms Startup Delay. Die 17us sind **KEIN universeller Maximalwert fuer echte VIN-Steigungen**.
3. [TI LM74930-Q1 SNOSDF6](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): EN low <0,41V disables charge pump und beide Gates; HGATE OV deglitch max7us bei TI-Testbedingungen **ist nicht** maximaler EN→Q301-drain-off. Bestehende REV5-Q301 = Vishay 250V SQM10250E_GE3 nur Kandidat, SOA nicht freigegeben.
4. [REV5 Baseline](../REV5_DESIGN_BASELINE.json): VIN9–30V, VOUT5V/2A, RAW1A Ziel, Lastabwurf exakt **200V/350ms**, -40…+125C, F_MAIN extern, 57 AUTO / 58 RUN.
5. Produktverfuegbarkeit bei Abruf am 15.10.2026: [DigiKey DE TPSM33620S5](https://www.digikey.de/de/products/detail/texas-instruments/TPSM33620S5QRDNRQ1/27687227) 2,100/1,987/1,882 EUR bei 1/10/100; [DigiKey DE TPS3760E012DYYRQ1](https://www.digikey.de/de/products/detail/texas-instruments/TPS3760E012DYYRQ1/16676100) 2,330/1,731/1,418 EUR bei 1/10/100, bei Abruf 2358 lagernd (TI-Shop kann abweichen); [Mouser DE LMR38020SQDDARQ1](https://www.mouser.de/ProductDetail/Texas-Instruments/LMR38020SQDDARQ1) 3,920/2,980/2,490 EUR bei 1/10/100. EUR ohne MwSt. + Transport, unterschiedliche Distributoren. Preise/Lager wechselnd; Checkout nicht erfolgt.

## 1. Vollstaendige angedachte Signal- und Sicherheitskette

Bevor ein B-Schema begonnen werden koennte, muesste **jede** der folgenden Aussagen *elektrisch* zutreffen:

```text
F_MAIN extern -> VIN_FUSED (9..30V normal; 200V/350ms test)
      |           |
      |           +-- 2x470k + 23k2 -> TPS3760E012DYYRQ1 SENSE (0.8V OV)
      |                                        VDD <- VS_CLAMP [nur wenn <=65V]
      |                                        RESET open drain
      v
LM74930-Q1 + Q302/ideal diode + Q301 HV series disconnect + Rsense
     EN <--- wired LOW of TPS38(U302 REV5: VS_READY AND RUN/AUTO)
          + TPS3760 OV low; Pullup from VS_CLAMP
          + independent default-OFF/POR lockout **NOT DESIGNED**
      |
      +-- PROTECTED_RAW_AUX 1A target (still shared circuit breaker)
      +-- TPSM33620 input pad (36V recommended / 40V ABS)
           + CIN (local low-ESL)
           + local energy-rated dynamic clamp **NOT DESIGNED**
           -> fixed 5V output
```

Die OV-Ausgabe muss **den Serienpfad Q301** abschalten (LM74930.EN low), nicht lediglich TPSM.EN: Ein abgeschalteter Buck kann bei 200 V auf VIN trotzdem zerstoert werden. Das offene NOR-/wired-LOW-Interlock benoetigt tatsaechliche MPN-LOW-HIGH-Leck-/Strom-, POR-/VDD-Verlaufs- und Leitungsnachweise. Gemeinsames REV5-TPS38-Feedback haengt vom CTRL_EN-Zustand ab; bei RUN LOW koennen Schmitt-Schwellen interagieren. **Eine Open-Drain-RESET-Stufe kann vor VPOR weder ein definiertes HIGH noch LOW liefern.** Unter 1,4 V VDD gibt TI selbst „output cannot be determined“ an. Ein passiver R_EN-Pulldown allein kann zugleich den 1M-Pull-up und die HIGH≥1,05V bei VS≈8V belasten. Ein anderes Versorgungs-/POR-Interlock oder echter Fail-LOW-Treiber ist deshalb ein zusaetzlicher zu qualifizierender Block, kein unsichtbar vorhandenes Merkmal.

**6 Zustands-Gates, allesamt offen:** 0V VIN mit RUN_HIGH (no backfeed, EN low); 9V Kaltstart bis VS stabil; 30V/2A normal auch bei Heiss; 200V/350ms Q301 off und Buck-Pad unter Grenzwerten; Rueckkehr auf 30V ohne manuelles Reset; ausgefallener/unversorgter OV-Supervisor erhaelt OFF. Die Zustandsliste wird vom Rechenmodell ausgegeben, damit kein Betriebszustand stillschweigend als bestanden gilt.

## 2. Statische Schwellen und Lasten – Teilgate bestanden, Systemgate nicht

TPS3760 Vorschlag **Rtop=940k (2x470k, je1%), Rbottom=23,2k (1%)** direkt an VIN_FUSED. KCL bei Sense-Eingangsstrom `I_S`:

`VIN_trip = VTH * (1 + Rtop/Rbottom) + I_S * Rtop`.

Mit VTH=0,792…0,808V, +/-100nA in beide Richtungen **absichtlich konservatives Leck-Szenario** und +/-1%-Bauteilfehler:

* OV steigende Schwelle: **32,153…34,302 V**, typ **33,214 V**.
* Freigabe nach OV: **31,499…33,628 V**, typ **32,550 V**. Berechnet mit 2%-Hysterese und deren +/-1,5% Genauigkeit. Dies sind rechnerische Bauteilecken, keine gemessene Switching-Hysterese der fertigen Baugruppe.
* 30V ist statisch in beiden Richtungen erlaubt: falling min 31,499 > 30, rising min 32,153 >30.
* Restmarge beim schlechtesten steigenden Grenzwert: **36-34,302 = 1,698 V** Betriebsreserve, **40-34,302=5,698 V** zum ABS-MAX; **vor** irgendeinem Gate-Delay, lokalen Ringing oder MLCC-Leckstrom.
* Spannungsteiler entnimmt bei 30V ideal **31,15uA**: allein etwa **31%** des REV5-System-OFF<100uA-Budgets, vor U301/TPS38/RUN etc.
* Bei VIN200V ideal SENSE≈4,817V (innerhalb 65V-SENSE-Rating), je Top-470k **20,3mW** und **7,1mJ/350ms** (1206 Puls-/Widerstand- und Spannungsspezifikationen noch pruefen). VDD des OV-Supervisors DARF **NICHT** an VIN_FUSED (200V) liegen; VS_CLAMP 56V ist ein noch unqualifizierter Versorgungszweig.

## 3. Zeit-/Spannungskette und Gegenbeispiele – **kritischer No-Go-Befund**

`t_protect = t_TPS3760_detect + t_EN_interlock + t_LM74930_GATE + t_Q301_open`.

Nur `t_TPS3760_detect <=17us` unter spezifizierten Overdrive-/Slew-Testbedingungen bekannt. LM74930 `7us` ist **OV-Pin-De-Glitch**, *nicht* garantierte EN-to-Q301-open-Zeit; Gate-Ladung, C307, R320, Temperatur, VS sowie Q301-Body-Diode/Parasiten sind nicht als garantierte Zeitgrenzen spezifiziert.

**Illustrative (NICHT Hersteller-Worst-Case) Szenariorechnung**: Angenommene in Serie leitende R=0,1Ohm, lokale 4,7uF nominell und VIN(t) als Sprung von 30 auf 200V vor FET-OFF. Dann `Vpad(t)=200+(30-200)*exp(-t/(R*C))`.

* **36V nach nur 0,0169us = 16,9ns**; **40V nach 0,0285us = 28,5ns**. Nach hypothetischen 17us Leitung ≈200V. Ein realer Kabelinduktor aendert diese Werte; das Gegenbeispiel beweist **nicht**, dass exakt diese Waveform nach ISO auftritt. Es zeigt, dass ohne spezifizierten Quellimpedanz-, Leitungs-, t_rise- und Q301-Abschaltvertrag keine obere 36/40-V-Schranke aus der Supervisor-Spezifikation herleitbar ist.
* Unter *alternativer* hypothetischer Rampe bei `t=17us+7us=24us` inklusive unbelegter 7us bis FET-off, 1ms von 30→200V (`dV/dt=0,170V/us`) plus exemplarischem **2V Ldi/dt** (100nH * 2A/100ns) ergibt sich `34,302 + 0,170*24 + 2=40,382V`; sogar ABS MAX verletzt. Bei 10ms Rampe (0,017V/us) +2V ergibt **36,710V**, oberhalb normalen 36V-Limits.
* Ohne jegliches Ringing/Schalt-Delay ueber 24us ist die erlaubte Steigung nur `(36-34,302)/24us = 0,07074V/us`; mit 2V Ringing existiert **kein** positiver erlaubter Slew fuer das 36V-Operating-Ziel.
* Da `t_EN_interlock + t_Q301_open` **nicht** bis 24us garantiert ist und der realen `t_TPS3760_detect`-Grenze ein 20%-Overdrive-Test zugrunde liegt, sind die Beispiele keine Obergrenzen. **Die tatsaechliche maximal moegliche VIN-Pad-Spannung ist mit den verfuegbaren Daten unbestimmt.** In einem nicht oder zu spaet trennenden Pfad kann sie in der Modellierung Richtung 200V streben.
* Selbst eine lange 350ms-Aus-Zeit verhindert nicht, dass **vor** Abschaltung ein destruktiver Peak auftritt. Ein TVS ohne garantierte heiße Clamp-Kurven, Ldi/dt-Verhalten und Pulsenergie ist kein Beweis fuer <36/40V.

**Warum nicht Q301 linear auf 33V klemmen?** Bei 200V und 2A (ohne RAW) wuerde Q301 ideal `(200-33)*2=334W`, bei 350ms **116,9J** abbekommen; mit 1A RAW-Last ideal **501W / 175,35J**. Echte Lasten und Strombegrenzung reduzieren das nicht generell zu einem freigegebenen Hot-SOA-Fall. Linearer Dauerbetrieb ist **kein** einfacher Workaround. Abschalten statt lineares Klemmen hat Vorrang.

**Unveraenderte, ebenfalls offene Gates aus A/REV5:** VS 9-V-Precharge bei R313–315=9,9k; bei VIN9, VS8 nur `(9-8)/9900=101uA`, TI-LM74930-Typ/MAX-Startup-VS-Strom nicht garantiert. 200V/56V-Clamp hypothetisch 14,55mA im VS-Widerstandszweig, je 3,3k ca 0,698W/0,244J und D301 bei56V 0,815W/0,285J – **kein** 125C-/350ms-SOA-Nachweis. Unabhaengig vom Buck-Tausch stehen Q301-SOA, Q302 und F_MAIN offen.

## 4. Thermik und PCB: 125C/2A ist kein herstellerseitiges Freiticket

Bei 5V*2A=10W und maximal 150C TJ bleiben bei TA=125C nur 25K. `P_loss=10*(1/eta-1)` und `theta_max=25/P_loss`; umgestellt `eta_min = 10/(10+25/theta)`.

* **22 K/W** (TI nennt EVM-Effektivwert als Beispiel, nicht unser Board): `eta_min=89,80%`. Bei angenommenen eta90% waeren 1,111W Verluste und ca. 24,44K Temperaturanstieg, also **149,4C TJ** – praktisch keine Reserve.
* **35 K/W** (ausdruecklich nur hypothetisches kleineres PCB) -> erforderliches `eta_min=93,33%`. TI nennt 90% Wirkungsgrad bei VIN24V und 93,2% *Peak* bei VIN12V; kein garantierter eta bei VIN30, 2A und +125C. Damit kein Beweis, dass TJ bleibt unter150C.
* TI empfiehlt mindestens eine Innen-Masseflaeche und Top/Bottom 2oz Cu fuer Waermeleitung/EMV. Kleines TripPower mit 35um-Standardkupfer waere gegen diese Empfehlung und braeuchte eigenstaendigen Thermik-/Layoutnachweis oder teureren PCB-Aufbau. Auch Weg A ist bei 125C/2A noch nicht freigegeben, der TPSM ist aber keine nachgewiesene Vereinfachung.

## 5. **Reale** Stueckzahl und Kondensator-Klarstellung

Aus dem existierenden `02_5V_LMR38020.kicad_sch` wurden **12 echte Referenzen** im Branch per automatischem Textscan gezaehlt: `U101,L101,C101,C102,C104,C105,C106,C107,C108,R101,R102,R103`. REV5 gesamten Fit: **57 AUTO / 58 RUN**.

| Interpretation | TPSM-Reglerteil | extra TPS3760 OV* | B-Gesamt AUTO / RUN | Differenz zu REV5 |
|---|---:|---:|---:|---:|
| TI-Marketing "vier externe Bauteile" = U + 4 Kondensatoren (HF-CIN100nF ausgelassen) | 5 | 5 | **55 / 56** | -2 |
| **TI Tabelle 8-2 fuer 5V/2A**: U + VIN4,7u + VIN0,1u + 2 x COUT22u + CVCC1u | **6** | **5** | **56 / 57** | **-1** |
| 5V/2A TI-Ref + **nur hypothetisch** 2 sichere Interlock- und 1 Clamp/Damping-Position | 6 | 8 | **59 / 60** | **+2** |

\* OV: TPS3760, **zwei** HV-Rtop, ein Rbottom und ein lokaler VDD-Bypass. Die reale Zaehlliste steht in `BOM_DELTA_TPSM_CANDIDATE_2026-10-15.csv`. Der Katalogsatz "nur vier Teile" gilt nicht fuer die **in Tabelle 8-2 gezeigte** Bestueckung mit zusaetzlichem HF-Eingangskondensator. Weder ein ohnehin freier gemeinsamer C noch nicht spezifizierte Zusatz-TVS/Filter/Enable-Pegel duerfen als gratis verifiziert werden. OVP-Interlock, Ldi/dt-Klemme, ggf. schneller Treiber, Fail-POR-Pulldown, 30V-Recovery und Beschleunigung haben aktuell **keine** freigegebene Bauteilzahl.

## 6. Kosten 1 / 10 / 100 – nur tatsaechlich preisbelegte Teilmenge, keine Fantasie-Endsumme

| Menge | A: LMR38020 IC EUR/Stk | B: TPSM + TPS3760 ICs EUR/Stk | B minus A EUR/Stk |
|---:|---:|---:|---:|
| 1 | 3,920 | 4,430 | **+0,510** |
| 10 | 2,980 | 3,718 | **+0,738** |
| 100 | 2,490 | 3,300 | **+0,810** |

Alle Preise Distributor-Snapshots (EUR netto, unterschiedliche Haendler), vor A-Spule/Passivteilen, B-Teiler/Bypass/EMV, externer F_MAIN, Bestueckung, Versand, Steuern und PCB. A hat externe Spule und zusaetzliche Buck-Passive; deren reale Einsparung kann B-IC-Mehrkosten teilweise kompensieren, ist ohne qualifizierte Passiv-MPN/Bestellstaffeln jedoch **nicht belegbar**. B verwendet zusaetzlich kompakten 11-Pad-QFN und 14-Pin-SOT23-THN, beide mit Stencil/Heissluft handbestueckbar, aber nicht so entspannt pruefbar wie diskrete Buck-Drossel/HSOIC. Die fuer 36V benoetigte dynamische HV-Clamp/zweiter Schalter, PCB-EMV und Thermik machen Kosten-/Teile-Gewinn eher schlechter. Kein behaupteter exakter Gesamtpreis.

## 7. Reproduzierbare Ausfuehrung und noch offene Gates

```bash
python3 hardware/modules/TripPower_5V2A/weg_b/verify_b_feasibility.py
python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_b -p 'test_*.py' -v
```

Gleichnamiger **branch-isolierter** GitHub-Workflow startet bei Push nach Weg B und schreibt `trippower-b-gates.json` als Artifact. Ob ein konkreter CI-Run erfolgreich abgeschlossen wurde, **muss explizit anhand Actions verifiziert** werden; ein Commit oder geplanter Workflow allein ist kein Nachweis eines nativen Runs. Die Zahlen wurden unabhaengig mit der angegebenen Rechenformel und den angegebenen Hersteller-Ecken abgeglichen, ohne Hardware-Simulation als Beweis auszugeben.

Zum Neustart von Weg B muesste eine **spezifizierte** hochspannungsfeste mehrstufige Klemme/Schutzschaltung mindestens folgende Nachweise liefern: (1) echte 9/12/24/30V Erstanlauf-/Restart-Zustandsmaschine in AUTO/RUN inkl. VIN0; (2) garantierter Serien-FET-off ab POR- und OV-Fehler, worst-case ueber -40..125C; (3) Hersteller-SOA/F_MAIN/200V-350ms Energiebudget; (4) garantiert VIN-Pad <=36V fuer alle Betriebsprofile und niemals >40V, mit gemessenem kabel-/layoutabhaengigem Peak; (5) effektive CIN/COUT und 125C/2A sowie 4-Lagen-Thermik und Kosten. Das ist **ein neues separates Schutzentwicklungsprojekt**, kein kostensparender Buck-Tausch.

**Projektleitungs-Fazit:** Weg **A/LMR38020-Q1** bleibt der bessere *Entwicklungs-Hauptpfad*, obwohl auch A keineswegs sicherheits- oder fertigungstauglich nachgewiesen ist. Weg B wird mit dokumentiertem NO-GO und testbarer Regression eingefroren, statt ein neues unvalidiertes KiCad-Bibliotheks-/PCB-Risiko zu starten.
