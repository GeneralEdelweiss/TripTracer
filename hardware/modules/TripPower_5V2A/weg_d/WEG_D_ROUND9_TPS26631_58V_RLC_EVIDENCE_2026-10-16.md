# TripPower Weg D – Round 9: TPS26631 bei 58V/350ms, RLC-Modell und Prüfentscheid (16.10.2026)

**ERGEBNIS:** Konditionaler GO für **Weg A als Labor-Prototyp**, jedoch NO-GO für einen garantierten 58V-Serienbetrieb mit der derzeitigen Schaltung. Ursache sind die unbekannten Pinspitzen sowie ein **bereits jetzt rechnerisch identifizierter 58→32V-Wiederanlaufmangel**. Die Sensitivitätsrechnung zeigt 60V- und 67V-Grenzüberschreitungen bei gewissen Eingangs-L/C-Parametern. Das sind **Szenarien – KEINE gemessenen realen Spannungsspitzen**. LTC4368-Schaltung bleibt zurückgestellt. Keine Sicherung auf TripPower.

## 1. Primärbasis und echtes Weg-A-Schema

Gelesen: AGENTS.md, docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md, docs/HARDWARE_REQUIREMENTS.md PWR-44–56, docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md, FINDINGS_LOG.md, Weg-D-Round8 und folgende Dateien direkt auf design/trippower-a:
- hardware/modules/TripPower_REV6_A/01_TPS26631_REV6.kicad_sch (U201 TPS26631PWPR, Q201 SQM100N10-10_GE3 100V reverse MOSFET, Q202 BSS138LT1G, C201/C202, R201–204)
- hardware/modules/TripPower_REV6_A/02_5V_LMR38020_REV6.kicad_sch (U101 Buck, C101/C108, C104..106, PGOOD Q501)
- hardware/modules/TripPower_REV6_A/REV6_A_25_PART_ORDER_BOM_2026-10-15.csv

**Aktuelle A-Werte:** C201 KEMET C1210C105K1RACAUTO **1µF/100V nach Verpol-FET Q201** direkt am TPS-IN_SYS/VIN_FUSED; C202 gleicher Wert hinter U201 am OUT. U101 Eingang C101+C108 KYOCERA AVX 12101C475K4Z2A **2x 4,7µF/100V nominal** plus C107 100nF; echte DC-biased Ceff für alle Kandidaten unbekannt. Kein separat nachgewiesener Shunt-C am vorgeschalteten **Q201-DRAIN**. R204 6,04k (~3A nominell); dVdT-C203 100nF (steuert Ausgangshochlauf, nicht Eingangs-Transienten). SHDN13 offen/floating: **max 5,5V an diesem Pin**, niemals an 58V ziehen.

**KONKRETE QUELLEN-DRIFT:** Im aktuellen A-KiCad-Blatt trägt R202 **12,0kΩ und MPN ERA-8AEB123V**, die aktuelle separat abgefragte A-CSV nennt R202 **12,4kΩ RT1206BRD0712K4L**. Gezeichneter R201=100k (100k precision), R203=4,22k. Eine vollständig native erneute Stücklisten-/Netzlisten-Verifikation auf dem tatsächlichen neuen A-Commit ist vor Fertigung nötig. Der frühere 25-Positionen/ERC0-KiCad10-CI-Run 38814076115 belegt nur damaligen Commit und keine heutige Transienten-/Werte-Validierung.

**Unabhängiger Herstellerkonflikt:** TI TPS2663 Rev G **§9.4 S.36** verlangt bei Verwendung des externen Verpol-FET mindestens **300k zwischen IN_SYS und UVLO**. R201 in der Zeichnung verbindet VIN_FUSED/IN_SYS mit UVLO_SENSE, beträgt aber **100k**. Vendor-Abweichung – nicht stillschweigend freigeben, auch nicht ohne geprüften UV/OV-Teiler blind auf 300k wechseln.

Primärdaten: https://www.ti.com/lit/ds/symlink/tps2663.pdf , TI TPS2663-Produktseite https://www.ti.com/product/TPS2663 mit offizieller **TPS2663 PSpice Transient Model Rev A / SLVMD03A.ZIP**. Nicht mitgeliefert bzw. in diesem Lauf als Hersteller-Makro NICHT ausgeführt.

## 2. Datenblattgrenzen und Verzögerungen

TPS26631 regulär **bis60V**, ABS für den relevanten längeren Zeitraum **67V**. Die zusätzliche 75V-Angabe ist **nur10ms/25°C**, nicht350ms. B_GATE-GND≤81V und B_GATE−IN_SYS≤14V; DRV-GND≤72V und DRV−IN_SYS≤20V; empfindliche OVP/SHDN/ILIM/dVdT etc haben niedrige GND-relative absolute Limits (z.B. 5,5V). U201 OUT/IN-/UVLO/FLT-/PGOOD-spezifische Grenzen einzeln nach TI Pin-Tabelle; Q201 VDS/VGS und Q202 VDS/VGS unabhängig prüfen. 80V empfohlener Buck-Eingang und eigener LMR38020-SW-Knoten sind nicht durch den 67V-Wert der eFuse beschrieben.

**TI Rev G §7.6:** OVP_tOFF(dly) **8,5–14µs** ist unter Testbedingungen die Verzögerung vom OVP-Pin 20mV über Rising-Schwelle bis **FLT↓**, **nicht** ein universell garantiertes vollständiges MOSFET-Gate-AUS. Kurzschluss Fasttrip um 1µs typisch (testabhängig), Softshort2,2–4,5µs in Datenblatt-Testbedingung; die relative Stromabschaltzeit, GATE-/DRV-Dynamik und LMR-Bootstrap-/EMV-Spikes erfordern Makromodell und Labor.

**TI §9.5.1 S.36/37:** Hersteller nennt ausdrücklich Quelle/Kabelinduktivität und positives INPUT-Ringing nach Stromabbruch; empfiehlt niedrige Loopinduktivität, ausreichend Input-C (1µF bei Surge), kurze Masseführung, ggf. speziell dimensionierte TVS und Ausgangsnegative-Spitzen-Schottky. TVS-Beschaffung erst NACH Quantifizierung, keine unbewiesene SMBJ58A-Klemmung unter67V.

## 3. Reproduzierbares Modell und Annahmen

**Ausführbares reduziertes Mehrzustands-Netzwerk:** tps26631_58v_network.py, Tests test_tps26631_58v_network.py, dazu tps26631_input_sensitivity_unvalidated.cir mit realen separaten ESR-/ESL-Netzwerkzweigen als **unverifizierte ngspice-Schablone**.

Quelle Vs(t) – Rsource – Kabel R/L – Connector R/L – Q201 reverse ON Rds/L – TPS-IN_SYS mit C201 wirksam – angenäherte interne eFuse (RON31mΩ + tanh-current-limit~3A, OVP OFF timing) – C202 an OUT und RAW bis0,5A – LMR VIN mit C101+C108 wirksam und angenäherter Buck-10W-Konstantleistungsaufnahme. **Vier** dynamische Zustände: Strom des Eingangs, V(IN_SYS), V(OUT), V(LMR-VIN). Q201 Drain wird aus I*R+Ldi/dt geschätzt, nicht als separat vollständig gekoppelter Eigenresonanzknoten simuliert. Eingang-C-ESR/ESL in Python im Leitungsäquivalent **lumped**, im SPICE-Netzwerk explicit in Reihe als R/L/C – beide sind NICHT vendor-verified.

**Basishypothesen – keine Hersteller-/Fahrzeugwerte:**
- Rsrc0,25Ω, Rcable0,10Ω, Rconnector0,015Ω, RPCB0,010Ω, Lcable0,8µH, Lconnector0,02µH, LPCB0,01µH, Q201-RdsON0,010Ω plus L0,02µH.
- C201 **1µF nominal aber Ceff0,5µF** als Probestufe; Sweep **0,2/0,5/1µF**, C202eff0,5µF, Buck-C101+C108eff3µF (nominal9,4µF!). Temperatur, Toleranz, Alterung und tatsächliche DCbias-Ceff fehlen.
- ESR in Leitungs-R zusammen 18mΩ, ESL in Leitung 3nH: **keine** genaue 100MHz Pin-Prognose. Q201 Coss/Bodydiode/GATE, eFuse-FET-Interne/B_GATE/DRV-/OVP/GND-Ringing und LMR-SW sind nicht modelliert.
- Vs 32→58V in20µs, 58V **350ms** konstant (nur Laborszenario, nicht echte Test-B-Kurve), in20µs zurück nach32; OVP aus beispielhafter *idealer SOURCE*-Schwelle34,2V mit Delay14µs und Fallzeit2µs. Dadurch wird in der Rechnung die wirkliche dynamische IN_SYS-/OVP-Ansprechzeit **nicht** exakt nachgebildet. Sensitivität off-delay 2/14/100µs (100µs ist **nicht** Vendor-Max!).
- Buck5/10W@η85%, RAW0/0,5A; Gehäuse-/Heiß-SOA wird nicht simuliert. 10V Start als kleiner Softswitch; OUT-Short mit0,5Ω Rload, Q201 KurzRds0,001Ω, U201 interne FET-Kurzschluss-Sonderuntersuchung.

**Warum keine echte SPICE-Freigabe:** TI stellt Hersteller-PSpice-SLVMD03A bereit, aber in dieser Sitzung ist **ngspice nicht installiert**, das Makromodell wurde nicht integriert/ausgeführt. Der beigefügte .cir-Netzplan ist bewusst nur ein ngspice-Syntax-Target mit idealisierter Verhaltensstromquelle und müsste zunächst vom SPICE-Simulator ausgeführt und mit dem Original-TI-Makro ersetzt/gegengeprüft werden. Es gibt **keine native KiCad10 ERC/Netzlisten- oder PCB-DRC-Prüfung** für Weg D, kein eigenes PCB.

## 4. Neun Pflichtfälle, modellhaft / Messung noch ausstehend

| Szenario | Reduziertes Modell (aufgerundete Modellwerte bei Basishypothesen) | Wesentliche Grenze / Aussage |
|---|---|---|
| 10V Start, 10W-Buck +0,5A RAW | max IN_SYS ca10,1V, Buck VIN ca9,3V | simuliert **NICHT** korrekt den internen LMR 5V/2A-Regelstart, tatsächlichen η, Spitzenstrom |
| 32→36V 20µs | IN_SYS ca36,6V | 36V/400ms/OFF/ON und Tj offen |
| 32→58V 20µs, 350ms | IN_SYS ca**59,1V**, OUT ca40,9V, Buck VIN ca40,9V kurz vor OFF | bei Base-RLC **unter60V**, aber **nur ~0,9V Modellszenario-Marge** |
| 58→32V nach350ms | INPUT zurück32V, angenommene Gate-Fraction OFF | **Wiederanlauf bei exakt32V nicht garantiert**, siehe §5 |
| OUT-Kurz bei10V | IN_SYS ca12,1V | Q-FET SOA, ILIM-Fasttrip/SLB und schadhafter Kurzschlussstoff **nicht** verifiziert |
| OUT-Kurz bei32V | IN_SYS ca34,3V | Kurzschluss-Strom-/AutoRetry-Energie nicht qualifiziert |
| OUT-Kurz während58V | IN_SYS ca58,6V | bei58V OV-Zustand zuvor bereits **OFF**; anderer Fehlermodus als Kurz aus ON |
| schnelles M8-Abziehen aus32V | Modell input ~32V ohne kritischen positiven Overshoot | **kein** realistischer M8-Lichtbogen, Reverse-Diode oder GND-/USB-Backfeed-Test |
| Q201 D-S-SHORT | Modell ähnlicher OVP-Verlauf, Q201-Verpolsperre physisch entfällt | No Return-Current/Backup-FMEA ohne vollständige Körperdioden-/MCU-I/O-Netzliste |

Zusätzlich: U201 interne FET-D-S-SHORT => gesamte 58V können auch im OVP-Fall durch defekten Switch zur Buck-/RAW-Schiene; Buck-Eingang grundsätzlich80V-fähig **nur bei lokalen Pin-Limits**, RAW/Kurzschluss/Backfeed gefährlich bei unqualifizierter Zusatzlast.

**Parameter-Matrix:** 4 L-Harness (0,2/1/3/5µH) ×3 C201eff (0,2/0,5/1µF) ×3 OFF-Delay (2/14/100µs) ×2 Buck (5/10W) ×2 RAW (0/0,5A) = **144 einzelne Szenarien**. Beim lokal ausgeführten rechnerischen Vorlauf des äquivalenten Modells: **60/144 überschreiten60V am IN_SYS; 2/144 erreichen ≥67V**. Das ist kein statistischer Fahrzeugfehleranteil! Ein Sensitivitätsfall L=5µH, Ceff=0,5µF, Delay14µs, 10W+RAW0,5A erreicht rechnerisch **~67,26V**, damit sogar die ABS-Grenze. Außerhalb des Sweeps (L=5µH, Ceff=0,1µF) rechnerisch >70V möglich. Reale Kabel-L und 58V-Ramping können völlig andere Ergebnisse ergeben. Auch höherer Ceff-Wert verbessert MAX im schwingungsfähigen Kreis **nicht monoton**.

**Ausführung, nach Installation von Python3 numpy+scipy:** 
- python3 hardware/modules/TripPower_5V2A/weg_d/tps26631_58v_network.py --scenario cases
- python3 hardware/modules/TripPower_5V2A/weg_d/tps26631_58v_network.py --scenario matrix > tps26631_matrix.json
- python3 hardware/modules/TripPower_5V2A/weg_d/tps26631_58v_network.py --scenario 32_to_58_350ms --full
- python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_d -p test_tps26631_58v_network.py -v

In .github/workflows/trippower-d-rev6-analysis.yml werden explizit numpy/scipy und neun Netzwerk-Regressionstests hinzugefügt sowie Matrix JSON als **MODELL**-Artefakt erzeugt; grüner CI belegt **nur Rechenlogik**, keine elektrische Bauteil-/PIN-Stress-/Brandsicherheit. Ein tatsächlich erfolgreicher aktueller Workflow-Run wurde noch nicht überprüft.

## 5. Separater, harter analoger P0-Fehler: 58→32V Recovery mit Weg-A-Teiler

TI TPS2663 Rev G: V_OVP rising 1,176..1,224V, falling 1,09..1,15V, typischer ±150nA Sense-Leak. Gezeichneter R201100k/R202**12,0k**/R2034,22k liefert k≈0,03631:
- rising ohne weitere Fehler: **32,39..33,71V**
- falling ohne weitere Fehler: **30,02..31,67V**.
Nach OVP-Abschaltung an58V und Rückkehr auf32V liegt der Eingang oberhalb der FALLING-Schwelle, daher **kein garantierter automatischer Restart bei stabilen32V** (R6-RESTART-08). BOM-R202 12,4k ist inkonsistent mit KiCad.

Für einen einzigen idealen OV-Teiler und völlig unabhängige Vendor-extremes muss 1.224/k_min≤36 => **k_min≥0,034000**, und 1.09/k_max>32 => **k_max<0,0340625** sein: **nur 0,184% Gesamtfenster** vor Widerstands-/TCR-/Pinleck-/Feuchtigkeits-/Temperatur-Unsicherheit. Selbst unabhängige ±0,1%-R können dies bereits übersteigen. Kein blindes Anheben der Schwelle um1V ohne vollständige Hersteller-Grenzrechnung und 300k-UVLO-Hinweis. Eventuell getrennte niedrigimpedante OV-Netzwerke, präzise matched dividers oder ein anderes Schalt-/Hysterese-Prinzip nötig. Dies betrifft Weg A direkt und ist unabhängig vom Fragezeichen Input-Ringing.

## 6. Kleinstmögliche Maßnahmen, kein extra Bauteil ohne Evidenz

1. Nachgewiesene Quelleninstallation **höchstens58V inkl Ringing am M8**, Kabellänge/Rsrc/L/Quell-Fall/mehrere Temperatur- und Pulskonfigurationen spezifizieren und messen.
2. Vendor-UVLO300k-Hinweis + R202/MPN-Divergenz sowie präzisen 32V-Recovery-Teiler elektrisch schließen **vor Layoutbestellung**.
3. C201eff/C202eff/C101+C108eff vs32/58V und −20..+70°C aus Hersteller-DCbias-/Impedanzkurven oder LCR-Vortest nachweisen. **100V nominal** ersetzt DCbias-Nachweis nicht. Hochstromloop Q201-Drain–Source–IN_SYS–C201–GND und Q202-GATE/Source mit kurzer Rückleitung platzieren; getrennte empfindliche OVP-/ILIM-Masse, PowerPAD und Buck-GND-Kontrolle. Ohne PCB existieren keine genauen L/ESL.
4. Wenn gemessener peak>60V, zuerst Loopverkürzung und gezielt nachgeschaltete **verlustarme RC-Dämpfung** im lokalen Eingangskreis anhand komplettem Source-/Cap-Modell. Ein RC-Snubber muss Spannungs-, Thermik- und Impulsenergie-Leistung sowie Standby-Anforderungen erfüllen; seine Existenz ist noch nicht als zusätzlicher BOM-Posten befohlen.
5. Keine Standard-58V-SMBJ-TVS als vorgeblicher unter67V-IC-Schützer: SMBJ58A VC,max93,6V bei Teststrom (zeitabhängig!), auch TI TVS5800 VC bis75V bei spez. Strom. Kleine TVS **nur** bei belegter VRWM/Tol/VC(I,T)/Fehlerenergie unter allen TPS-Pin-Grenzen; andernfalls TVS=0 bestückt und optionale Testflächen als DNP.
6. Hoher L-/kleiner Ceff-Fault oder tatsächliche Pinspitze >60V (beziehungsweise ≥67V) trotz erfolgreicher Dämpfung => TPS26631 **NO-GO** für diese Installation. Dann allein gezielter LTC4368-2-Vergleich: dessen VIN-Fault100V macht die übrigen **80V-VOUT/SENSE**, externen MOSFET-SOA, OV20V/RETRY5V, Gate/Schutzklemmen und Preis keineswegs automatisch sicher.

## 7. Sicherer tatsächlich ausführbarer Laborprüfplan

**Testquelle:** professionell strom-/energiebegrenzbare programmierbare DC-Transienteinspeisung oder ISO16750-2-Test-B-Generator mit umschaltbarer 10/32/36/58V-Spannung, Fern-AUS/Not-Aus, zuverlässiger mechanischer Berührschutz-Einhausung, separatem Abbruchpfad, dokumentierter Maximalenergie und *externem* DC-zugelassenem quellnahem Leitungsschutz. 58V×5A×0,35s=**101,5J** maximale Rechteckquellenergie, 58V×10A×0,35s=**203J** vor induktiven Spitzen; KEINE direkte ungesicherte 58V-Batterie, kein Handsteck-Brand-/Kontaktlichtbogenversuch im Volllast-Fahrzeug. Qualifizierte Fachkraft bei Impulsen/Kurzschluss mit Energie-/Temperaturbegrenzung. Einzelne zerstörende MOSFET-/IC-Kurzschlüsse erst mit Stromlimit/Schutztrennung und Brandcontainment.

**Kabelsatz:** Kurz (.5m) vs lang (3m) als *beschriftete Messfixtures* mit jeweils wirklich gemessenem RDC/L/Frequenzgang, unterschiedlichem M8-/Ground-Rückleiter; Source-R/L/Generator-Rise/Fall an M8 messen, kein blindes L=µH/m einsetzen. F_MAIN auf Fahrzeug-/TripTracer-Harness, **NICHT** auf TripPower; keine gelöteten Einmalsicherungen, keine PPTC aus Vorsicht.

**Messtechnik:** Oszilloskop ≥100MHz, ≥500MS/s empfehlenswert, **sichere differenzielle Spannungssonden** ausreichend spannungsfest und ≥100MHz bzw nachweislich gleichwertige isolierte Mehrkanaltechnik; DC-fähige Stromzange mit hoher Bandbreite (Richtwert ≥5MHz) und/oder kalibriertes niederinduktives Kelvin-Shunt mit sicherem getrenntem Auswerter. Relative Sonden-/Masse-/Gate-Antworten zeitkorrelieren, Tastkopfmasse NICHT an Q201-GATE/M8+ legen! Für nanosekundenartige ESD-Ringe höherbandbreitig messen, nicht aus 100MHz-Scope-Einzelfoto fälschlich absolutes Vmax garantieren.

**Messpunkte auf echten Padgeometrien** im Anschlusslayout:
M8+ direkt und M8-GND, vor/nach externer F_MAIN, Q201 D/S/G, U201 **IN(1–3), IN_SYS(6), OUT(18–20), B_GATE(4), DRV(5), OVP(8), UVLO(7), SHDN(13), GND(9)**, C201/C202 direkt an Pads; **BGATE-IN_SYS** und **DRV-IN_SYS** differenziell; LMR U101 VIN/SW/BOOT/GND und Buck-Eingangs-C, RAW0.5A, PG/PWR_FAIL, USB/VBUS, ACC/BAT und Ground-Lift. Step-Replay mit realer Temperatur, 10V Start an voller Last, 32→36 400ms, 32→58 350ms, 58→32 Restart, OUT-Kurz10/32/58V, M8 Hotplug/Unplug *nur mit schützender Testfixture*, Q201-/U201-SHORT als begrenzte destruktive FMEA, USB-only/USB+M8. Bei −20/25/60°C 2A Buck, bei +70°C Derating/OFF, +85°C gefahrloses Abschalten (separate Ambient-Sensorik fehlt noch). RAW0/0.5A und Fehler, 10 Pulswiederholungen/definierter Abstand; FRAM-first/SD-Recovery separat.

**Expliziter PASS**: Bei 58V-Puls *alle* am Bauteil geltenden empfohlenen Betriebsspannungsgrenzen inkl. definierter Oszi-/Bauteiltoleranzmarge einhalten, U201-IN/IN_SYS bei Betrieb ≤60V (67V ABS *niemals* als Wiederholreserve beanspruchen), BGATE/DRV differentiell/GND absolut und OVP/SHDN/LIM-Pins innerhalb ihrer niedrigen Limits, LMR VIN innerhalb80V empfohlen und SW-Gate nach TI Datenblatt; 32V nach58V muss **wirklich automatisch neu starten**; keine Rückspeisung, Brand, Leiterbahn-/FMAIN-/Kabelhitze, RAW-Strang-Teildefekt oder falsche FRAM-/SD-Erfolgsgarantie. **FAIL/NO-GO**, wenn irgendein Pin-Grenzwert verletzt, 32V-Restart ausbleibt, Messung ungeklärt oder Fehlerenergie nicht begrenzt ist. Ein nicht durchgeführter Test ist **OFFEN**, nie PASS.

**Hardwarestand:** keine Messung erfolgt, keine echten SPICE-U201-/LMR-Makro-Simulationen, keine neue native KiCad10-ERC/PCB-DRC in Weg D. Der Weg-A-ERC0-Schaltplan aus einem früheren CI ersetzt weder geänderte BOM-/Schwellwerte noch diese Labortests.

## 8. Schlussentscheidung

**Aktuell**: TPS26631 technisch plausibler als unnötiger LTC4368-Ausbau, aber ohne gemessenes VIN_SYS/IN/Q201-Coss-/Q-Bias-Ringing und mit defektem 32V-OV-Recovery **keine freigegebene REV6-Lösung**. Weg A als kleinster qualifizierbarer Kandidat beibehalten; **keine neuen Fuses/Holder/Thermosicherungen** auf TripPower; keine zusätzliche TVS ohne echten Vc(I,T)-Proof; 200V-Test-A-Modul nur spätere **externe** Erweiterung. **Nächstes P0-Gate:** A-R201/202/203 und 300k-Hersteller-Vorgabe sowie Anschluss-L/C/R mit Referenzmakro und Messung korrigieren; erst dann Entscheidung „Weg A ausreichend“ oder gezielt LTC4368-Vorteil.
