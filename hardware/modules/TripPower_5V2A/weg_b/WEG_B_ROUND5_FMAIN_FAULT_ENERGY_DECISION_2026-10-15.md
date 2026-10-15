# TripPower Weg B – Runde 5: F_MAIN/I²t/Single-Fault-Gefahrenenergie und sichere Gerätezerstörung

**Datum 2026-10-15. Branch \`design/trippower-b\`; Änderungen nur unter \`weg_b/\` und am eigenen B-Workflow.** Zuerst gelesen: \`docs/TRIPPOWER_A_B_C_REVIEW_ROUND4_2026-10-15.md\` (Review-Branch) und bereits akzeptierter B4-/TPSM-No-Go. **Keine neue generische IC-Suche, keine Änderung von Weg A, REV5 oder Weg C.** Prüfziel: Ein zulässiger **sicherer Totalausfall** muss gegen **gefährliche Fehlerenergie** unterschieden werden. Ergebnisse sind Schaltungs-/Datenblatt-/Grenzfallanalysen, keine realen SOA-, Zerstörungs-, ISO-, Kabel-/Brandschutz- oder Fertigungsprüfungen.

## Entscheidung und notwendige Beweisschwelle

**Eine zusätzliche HV-Abschaltstufe ist NICHT logisch zwingend**, wenn ein sorgfältig nachgewiesener Mechanismus aus (a) tatsächlich im Fehlfall ausreichend begrenzter Energie, (b) korrekter HV-DC-F_MAIN samt Halter und (c) nachweislich nicht zündendem IC-/MOSFET-/PCB-Fehlerverhalten gefährliche Folgeschäden ausschließt. **Aber auch eine richtig spannungsfeste F_MAIN ist bisher KEIN Ersatzbeweis:** In realistischen Fehlerfamilien kann das defekte Silizium Strom **unter dem 5-A-Sicherungsnennstrom** ziehen und sich trotzdem bei 200V gefährlich erwärmen. Beschädigung der 5V-/RAW-Ausgänge ist nur dann akzeptabel, wenn das Gerät sicher ausgeht und extern keine schädliche Rückspeisung / anhaltende Stromversorgung / Leiterbahnbrand entsteht.

**Konsequenz:** Weg A und die AP74502HQ-Referenz sind **nicht** unter Verwendung *irgendeiner beliebigen* Sicherung freigegeben; es existiert aber **kein Beweis**, dass eine weitere vollwertige HV-Abschaltung die einzige zulässige Abhilfemaßnahme ist. Zuerst muss die *tatsächliche Ausfallenergie* gegen freigegebene Bauteil-, PCB-, Gehäuse- und Leitungsgrenzen überprüft werden. Q307+D306 bleibt ausdrücklich Forschungsprototyp, ohne ihn weiter aufzublähen.

## 1. Physikalisch unterschiedliche Strompfade

### A – einzelner Q301 D-S-Kurzschluss

Die KiCad-10-Protektionstopologie wurde in [Weg A Runde 4](../WEG_A_ROUND4_Q301_SHORT_FAILSAFE_PROTOTYPE_2026-10-15.md) mit nativer Netzliste und Prüfschema belegt; wir verändern sie nicht:

\`\`\`text
200 V / 350ms -> externe F_MAIN -> VIN_FUSED -> Q301[D-S Kurz]
                                                |
                                            SOURCE_A -------- U301.A pins 2/15 (abs +70V to GND)
                                                |----------- Q302 source pins 1/2/3
                                                |           (Q302 VDS abs 60V, nur falls andere Seite entsprechend niedrig)
                                                +-- D302[Anode -> Kathode] --> VS_CLAMP
                                                    | D301 56V Zener nach GND
                                                    | 100V MLCC, LM74930 VS<=65V
                                                +-- übrige RAW-/Buck-Leistungspfade (Zustands-/Lastabhängig)
\`\`\`

**Herstellerfest:** TI [LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf) 6.1 / 6.3: A zur Masse abs +70V, normal +65V; weitere VS/CS-Grenzen dürfen nicht überschritten werden. [Vishay SQM10250E](https://www.vishay.com/docs/75035/sqm10250e.pdf): Q301 250V VDS/±20V VGS, SOA-Kurven bei TA25°C nicht geeignet als heiße 350-ms-Garantie. Q302 = 60V VDS-Abs.-Max **zwischen Drain/Source**, nicht pauschal 60V gegen GND! Bei SOURCE_A=200V und Q302-Drain hypothetisch 0V ergäben sich 200V VDS; bei Drain ebenfalls 200V dagegen ungefähr 0V VDS. Seine tatsächliche Fehlerbelastung ist wegen nicht vorgegebener Knotenpotentiale unqualifiziert.

**NEUER SICHHERHEITSUNTERSCHIED:** U301.A 200V statt ABS70V ist **sicher eine Grenzverletzung**, aber **kein** Beweis von 200V an jedem anderen Pin oder eines Brandes. Ob der A-Pin offen, niederohmig zur Masse/Versorgung/OUT, leitend oder durchschlagend versagt, **ist keine garantierte TI-Fail-Mode-Spezifikation**. Die elektrische thermische Fehlenergie ist deshalb zu prüfen, bevor Geräteverlust als ungefährlich eingestuft wird.

**D302 [BAV21WQ-7-F](https://www.digikey.com/en/products/detail/diodes-incorporated/BAV21WQ-7-F/16548209):** 200V sind **Sperrspannungs**-Rating; vorwärts beträgt die durchschnittliche Stromangabe nur **0.4A** (kein 350ms/125°C-Hot-SOA-Beleg). Mit Q301 kurz und D301 intakt gelangt SOURCE_A vorwärts über D302 zur 56V-Zener **ohne** die 3×3.3k-Begrenzung. Der D306/Q307/R342-Prototyp begrenzt bei FET-Fehler **nicht** die bereits direkt an SOURCE_A angeschlossenen Pins. D301 OFFEN über 9.9k bleibt unabhängiger Einzelfehler (ideales 21uF-Null-Lastmodell ~163V bei 350ms; 65V VS und 100V C überschritten), der nominelle Gesamtfusenstrom ist dabei milliamperig.

### B/C – einzelner Eingangsmosfet Q1 D-S-Kurz in AP74502HQ common-source

\`\`\`text
VIN_FUSED -> [Q1 Kurz] -> MID_SOURCE -> Q2 BODY DIODE (MID -> VOUT) -> nachfolgende
                                                          60V/80V IC-/RAW-Domain
\`\`\`

**Die verbleibende Bodydiode ist kein zweiter positiver Sperrschalter.** Der in B4 gespeicherte gerichtete MOSFET-Faultgraph prüft Q1-Kurz = Durchgang, Q2-Kurz allein = Eingang gesperrt, beide gesund = gesperrt. Auch hier ist **das Gerät selbst verloren** zunächst akzeptabel – nicht aber ein unkontrollierter niederohmiger oder mehrsekündiger Überlastpfad, Rückspeisung in externe Leitungen oder Brand. F_MAIN kann nur dann an Stelle eines zweiten Blocks dienen, wenn **alle zu betrachtenden Fehlerströme** innerhalb ihrer passenden DC-Öffnungs-/Zeit-/Energie-Kennlinien liegen oder die **nicht auslösenden Fehler** nachweislich harmlos bleiben.

## 2. MPN- und Herstellerbelege: Nennstrom ≠ DC-Abschaltvermögen ≠ Zeit-SOA

| Exakter Kandidat | Hersteller-Spannung / Wärme | DC-Interrupt / Min.-Brechstrom | Kosten/Lieferstatus 15.10.2026 | Urteil |
|---|---|---|---|---|
| Littelfuse MINI/ATOF gewöhnliche Kfz-Sicherung | **32VDC** (andere Automotive-Familien bis58V) | Nenndaten bei32/58V, KEIN 200VDC-Brechnachweis | bewusst keine fiktive konkrete MPN | **AUSSCHLUSS** als 200V-DC-unterbrechender Schutz |
| **Weidmüller GZ5.0A/F \`1460620000\`** | 5A, 500V laut Hersteller-Nennspannung / DigiKey ausdrücklich AC/DC, **Hersteller-Umgebung −5…+40°C** (!) | DigiKey 50kA ohne passende DC-Zeitkennlinie | 20 auf Lager, €3.080/2.361/1.8065 bei1/10/100, [DigiKey](https://www.digikey.de/de/products/detail/weidm%C3%BCller/1460620000/22132585); [Weidmüller](https://eshop.weidmueller.com/en/gz-5-0af/p/1460620000) | Bei −40…+125°C ohne andere qualifizierte Einbaustelle **AUSSCHLUSS**, trotz attraktivem Preis |
| **Eaton Bussmann \`FWC-4A10F\`** | 4A, konservativ 500VDC laut [Eaton](https://www.eaton.com/us/en-us/skuPage.FWC-4A10F.html); Temperatur-Rating für Zielumgebung offen | Eaton gibt **10kA DC**, pre-arcing **5.2 A²s**, total clearing **32 A²s** als Tabellenindizes; Klasse **aR, nur Teilbereichsschutz** | Original-MPN aktiv; verifizierter DE-Bestand und €-1/10/100 nicht vorhanden | Potenzieller echter DC-Schutz bei hohem Kurzschlussstrom, aber **kein vollständiger 0..5A-Überlastschutz und kein 350ms-Clearing-Beweis** |
| **Mersen \`MEV55C5\` (externe Clip-Fuse)** | **550VDC, 5A, −40…+125°C**, automotive ISO8820-8, Hersteller [Datenblatt 2025 S.1–2](https://de.mersen.com/sites/default/files/medias/PIM/files/DS-EVpack-fuse-MEV55C-MEV50A-500VDC-max-L-R-less-than-2-5ms-5-800A-EN.pdf) | **20kA bei550VDC**, L/R≤1ms; **Mindest-Brechstrom 10A**, **Max.-Clear-Zeit bei 10A: 10s** | [Mersen MPN](https://www.mersen.com/en/products/evpack-fuse-mev55-550-vdc-max-l-r-less-or-equal-1ms-5-50a/mev55c5). [Sekundär-Händler EU](https://eu.raptorsupplies.com/c/electrical/p/mersen-ferraz-ev-pack-fuses) führt ca **€46.24 für 1**, RFQ/Bestand und 10/100 unbestätigt | **Beste nachgewiesene Hersteller-Temperatur-/HV-Passung**, aber für **350ms bei 10A nicht garantiert**, bei <10A kein garantierter DC-Break; teuer und spez. Halter nötig |

**WICHTIGE Datenblattabweichung:** Mersen Tabellenzeile \`MEV55C5-P\` (PCB-Mount) listet 10 **ms** Max.-Clear bei MBC, während \`MEV55C5\` (Clip) und \`MEV55C5-S\` 10 **s** zeigen; ein älterer Herstellerkatalog listet auch für \`-P\` 10s. Dies kann ein Tabellenfehler sein: **keine 10ms-Garantie behaupten, Hersteller schriftlich aufklären.** Außerdem erfordert das System ausdrücklich **austauschbare externe** F_MAIN; PCB-\`-P\` wäre dazu ungeeignet. Sicherungshalter, Anschlussklemmung, DC-Kriechstrecke bei 200V, -40..+125°C und montierte Baugruppen müssen separat ausgewählt/qualifiziert sein.

## 3. Reproduzierbares 200-V-/350-ms-Gegenbeispiel: gefährliche Leistung bei *nicht auslösendem* F_MAIN

**Nur mathematische Szenarien, NICHT der reale ISO-Generator:** steifes Rechteck 200V/350ms am Eingang, Quellimpedanz \`Rsrc\`, modellierte Fehlerpfadimpedanz \`Rfault\`; für D301 **fiktiv** konstanter 56V-Klemmwert und D302 **fiktiv** 0.7V Vorwärtsspannung. In Wirklichkeit können D301/D302 zuerst durchgehen/aufreißen, Spannung ansteigen, Leiterbahnen schmelzen etc. Gerade dieses **ungeklärte Fail-Mode-Verhalten** ist der Grund für die P0-Einstufung.

\`I=(200−56−0.7)/(Rsrc+Rfault);\` \`E_Z=56·I·0.35;\` \`I²t=I²·0.35.\`

| Rsrc | Rfault | ideal I | I²t bei350ms | hypothetisch E_D301 | Konsequenz |
|---:|---:|---:|---:|---:|---|
| 5Ω | 0Ω | 28.66A | 287.49A²s | 561.74J | Große Energie; reale F_MAIN t_clear und DC-Arc entscheidend |
| 20Ω | 0Ω | 7.165A | 17.97A²s | 140.43J | Selbst bei >5A kann die Sicherung mehrere 350ms brauchen |
| **5Ω** | **50Ω** | **2.605A** | **2.376A²s** | **51.07J** | **Unter 5A Sicherungsnennstrom; kein Sicherungs-Clearing nachgewiesen!** |
| 5Ω | 150Ω | 0.925A | 0.299A²s | 18.12J | Auch weniger als 1A kann in 350ms hohe Zenerenergie aufbauen |

**Völlig ohne Zener:** Ein geschädigter 100Ω-IC-/PCB-Leck-Kurzschlusspfad mit \`Rsrc=5Ω\` sieht \`I=200/105=1.905A\`; die hypothetische Verlustenergie am Fehlerbauteil ist **~126.98J** in 350ms (\`I² Rfault t\`). **5A F_MAIN muss diesen Strom nicht abschalten.** Dies ist keine Behauptung, dass genau der LM74930 real als 100Ω versagt; es ist der erforderliche *Evidenzgegenbeweis* gegen „ein zerstörter IC öffnet bestimmt sicher“.

**Kabelbeispiel (ebenfalls rein hypothetisch):** \`Rsrc=5Ω\` liefert einen verfügbaren Vollkurzschlussstrom von \`40A\`. Bei \`Rwire=0.1Ω\` wären unter dem willkürlichen 350ms-Dauerrechteck \`Ewire=I²Rwire t=56J\`; \`I²t=560A²s\`. Bei \`Rsrc=0.5Ω\` wären es 400A und 5600J im identischen angenommenen Draht. Ohne **vollständige** DC-Ausschaltzeit inklusive Lichtbogen, Leitungsquerschnitt/Isolierung, Umgebung, Temperaturreserve und Stecker-/Kupfer-Kennlinie **keine** Behauptung eines Kabelbrands oder eines Kabelschutz-Passes.

**Warum reine I²t-Grenzen nicht reichen:** Die Eaton \`FWC-4A10F\` Tabellenwerte 5.2A²s (prearc) / 32A²s (clearing) haben definierte Hochstrom-Prüfbedingungen; sie berechtigen **nicht** zur Formel \`t_clear=32/I²\` bei 3A, 5A, 10A oder einer anderen Spannung/L/R. Eine Schmelz-I²t ohne **DC-Lichtbogenlöschzeit** ist kein Gesamtunterbrechungsnachweis. Umgekehrt zeigt die echte Mersen-Kennzahl am **Mindest-Ausschaltstrom 10A eine Maximalzeit von 10s** – daher bei 350ms keine hinreichend schnelle Garantie am 10A-Punkt.

## 4. Q301- und Serien-TVS-SOA bleibt eigenständig offen

* Q301 **SQM10250E_GE3** VDS abs250V; bei 200V gegen SOURCE_A≈0 ist nominell **50V Überschwingermarge** vorhanden, bei angenommen +51V überschreitet VDS die absolute Grenze. Bei Q301-D-S-Kurz ist VDS≈0, dennoch ist die **restliche Schaltung unmittelbar 200V ausgesetzt**. Transientes Gate-/MOSFET-Versagen darf nicht als definierter hochohmiger Sicherungsmechanismus angenommen werden.
* D303 SMBJ150A-13-F + D304 SMBJ33CA-13-F haben summierte VBR-Minima **203.7V an unterschiedlichen DC-Prüfstrombedingungen**. Damit ist kein garantierter gemeinsamer Serien-Clamp bei 200V belegt; unabhängige Hersteller-Vc bei verschiedenen IPP dürfen nicht als gemeinsame Kennlinie addiert werden. Kurzschluss einer der TVS verlagert die Fehlerenergie auf die andere und F_MAIN, auch diese Ausfallart testen.
* D301 OFFEN führt über R313–R315 zu kleinem Fehlerstrom. **Eine 3A/5A-F_MAIN beseitigt einen 20mA-Ladezweig nicht**, auch nicht wenn sie 550VDC Unterbrechungsvermögen hat. Die 100V-Caps, LM74930-VS und TPS38-VDD können nach dem Null-Last-Modell überlastet werden.
* Die Zener-/RVS-Einzelpulsgrenzen bei TA125°C, wiederholte Pulse, auf Wärme leitfähiges PCB, BAV21WQ \`I_F(avg)=0.4A\`, Hot-Q301-SOA und die 200V-Testflanke/Induktivität bleiben Hersteller-/Hardware-Stopps.

## 5. Empfehlung nach minimaler Teilezahl und System-Sicherheit (keine naive Redundanz)

**Pfad 1 – Weiteres HV-Schaltglied vermeiden, sicheren Totalausfall zulassen (bevorzugt als erste *Prüfhypothese*, derzeit NICHT nachgewiesen):**
1. Externe F_MAIN ausschließlich als **hersteller- und halterqualifizierte 200V-DC-Unterbrechung** dimensionieren, bevorzugt automotive Mersen \`MEV55C5\` zum Datenvergleich, falls echte Lager-/Halter-/Temperatur-/Kostenbedingungen akzeptabel; nicht als automatisch fertige 5A-Lösung. Stromnennwert 5A gegenüber modellierten 9V/Eta75–90%+RAW1A \(2.23–2.48A\) gibt nominell eine Betriebsreserve; reale Derating-/Inrush-/Blockadebedingungen müssen qualifiziert werden. Die noch preiswertere Weidmüller 1460620000 ist bei 125°C und -40°C **ausgeschlossen**.
2. Definiere für **jedes** Einzelfehlerbild zwei mögliche sichere Endzustände: a) F_MAIN öffnet unter realem Source-I(t) *vor* lokalem E-/T-/I²t-Grenzschaden einschließlich Lichtbogen; **oder** b) Bauteile/PCB/Enclosure gehen bei geringer Energie kontrolliert **hochohmig/offen** mit nachgewiesener Temperatur- und Flammfreiheit aus. Nichts davon bislang garantiert. Im Modell speziell SOURCE_A→U301.A, SOURCE_A→Q302, SOURCE_A→D302→D301 sowie AP-Q1short→Q2 bodydiode→5V-Buck getrennt messen. Äußerlich sicherer Geräte-Totalausfall und kein unzulässiger Kabelstrom sind Pflicht; interne 5V/RAW-ICs dürfen sterben.
3. Falls z.B. 1–3A über 350ms an einer beschädigten IC-Stelle weiterfließt, obwohl die Sicherung unberührt bleibt und keine belastbare Safe-Open-/Brand-Prüfung vorliegt: **Pfad 1 verwerfen**, nicht durch mehr unspezifizierte Dioden/Widerstände kaschieren.

**Pfad 2 – Nur lokale, begrenzte Fehlerenergie**: Eine einzelne 200V-/pulsfest **wirklich strombegrenzende** fertig erhältliche Nachladebaugruppe könnte *nur* den D302/VS-Zweig entschärfen. A’s \`Q307 BSP135H6327XTSA1 + R342 1.5k + D306\` hat jedoch **kein über Temperatur garantiertes Stromlimit**, verschlechtert potenziell 9V-Start und schützt **U301.A/Q302-Source NICHT**. Auch bloßer D306-/Zener-Paralleltausch und einfacher D302-Serienwiderstand sind nicht hinreichend. **Keine Freigabe/kein neuer KiCad-Prototyp** dieses Teilpfads, solange direkter U301.A-Pfad besteht.

**Pfad 3 – unabhängige Hochvolt-Isolation**: Wenn Pfad 1 durch echte Fehlerenergie- und Dauerstrommessungen fällt, benötigt man ein **eigenständig gegen positive VIN sperrendes** HV-Leistungselement **vor** ungeschützten A-/Q302-/RAW-Knoten oder eine integrierte gleichwertige Lösung. Bei AP-common-source kann man nicht bloß „zwei MOSFETs vorhanden“ als Redundanz zählen: eine eingangsseitige Drain-Source-Brücke lässt die Bodydiode des zweiten MOSFETs weiterleiten. Diese Variante hat Kosten/Platz/Steuersignal/SOA-Risiken und darf erst nach Hersteller-SOA und Pin-Netzlistennachweis zu KiCad weitergehen. **Das ist eine konditionale Architekturentscheidung, kein abstraktes Gebot nach jedem IC-Defekt einen zweiten Schalter zu kaufen.**

## 6. Konkrete Prüfplanung, Verifikation und Nachweiskette

**Zuerst beim zuständigen Generator-/Fahrzeugprüfer erfragen:** 200V-Lastabwurf ist eine **offene** Quelle oder ein **unter definierter Last** gemessener Verlauf? \`V(t)\`, rise/fall in us/ms, \`Rsrc(V,t)\`, Harness-L (L/R), initial battery-voltage/-state, parallele 24V-Bordnetzquelle, wiederholte Pulszahl/-abstände, zulässige 125°C Hot-Start-Umgebung. Ohne diese Parameter ist jede F_MAIN-Auswahl bloß relativ zur Szenarioquelle, keine Endfreigabe.

**Bench (nur geeignete HV-/ISO-geschützte Prüfeinrichtung, strombegrenzt und in Brandschutz-Testumgebung):**
1. Gute und einzeln gezielt **gebrückte Q301** / gebrückte AP-Q1, D301 offen/kurz, D303/D304 jeweils kurz/offen; relevante Q301+D301-, AP-Q1+AP-Q2-Doppelfehler. Realen Quellenwiderstand und verfügbare Leistung überwachen.
2. Differential-HV messen: VIN_FUSED, SOURCE_A, U301 A2/A15, CS/VS, D301, D302, Q302 D/S/G, OUT/RAW, beide AP-FETs, plus *gleichzeitig* I_MAIN vor/nach Sicherung, I_D302, RVS, Spannungsabfall F_MAIN und Kabeltemperatur. Bei Q301-D-S-Kurz Q302 Drain ausdrücklich messen: VDS hängt von beiden Potentialen ab.
3. Mit 9/12/24/30V funktionierend und insbesondere 9V Kaltstart nach 200V, TA −40/+25/+125°C: 5V 0…2A, RAW0…1A, Halbleiter-Wärme, Widerstandspulse, Zener/Zth, Ceff/Leckströme. F_MAIN namentlich, Halter, DC-Rating, min breaking, maximum t_clear(I), Max-I²t (prearc + DC clearing) samt Lichtbogen unter eigener Quelle belegen.
4. **Akzeptanzbedingungen vor Boardbestellung:** Schlimmster Einzel-/Doppelfehler gefährdet kein Kabel, Stecker, PCB oder Gehäuse über zulässige thermische/smoke-/flame-Grenzen; keinerlei dauerhaftes 200V-Potenzial auf externen 5V/RAW-Anschlussflächen; sicherer Aus- und Nicht-Rückspeisezustand. Konkrete thermische Zeit-/Energiegrenzen nur aus Herstellern, PCB-/Kupfer-/Leitungsherstellern oder vom Prüflabor, nicht erfundenen Joule-Limits. Ohne solche Grenzwerte **STOP**.

### Neue ausführbare Artefakte in Weg B

- \`fault_energy_fuse_gate.py\`: unabhängiger DC-Fuse-MPN-Vergleich, 200V/350ms \`I²t\`, Zener-/Diode-/Fehlerwiderstandsenergie, QS 9V-Betriebsstrom, Kabel-I²t, Hersteller-Temperaturecken, TI U301.A max70V, conditional Q302 VDS, priorisierte JSON-FMEA; ausdrückliche FAIL/STOP-Gates.
- \`test_fault_energy_fuse_gate.py\`: Regressionen auf reale Herstellerangaben und Gegenbeispiele, **keine unbelegte Ableitung der Abschaltzeit aus Tabellen-I²t**.
- \`FMEA_ROUND5_PRIORITIZED_2026-10-15.csv\`: P0/P1-Reihung mit konkreten Mess-/Akzeptanzkriterien, getrennt nach Einzelfehler, Doppelfehler und zulässiger kontrollierter Ausfall.
- \`.github/workflows/trippower-b-independent-audit.yml\`: neuer Prüfblock mit Python-Regressionen und JSON-Reports. Workflow jetzt mit \`set -euo pipefail\` in den Test-Pipelines, um verdeckte Testfehler durch \`| tee\` zu verhindern; zusätzlich vorhandene native KiCad-10-Baseline-Netzlisten-/ERC-Screens.

**CI-Status-Wahrheit:** Ein Workflow-Commit ist **kein** verifizierter GitHub-Actions-PASS. Bei erfolgreicher Workflow-Ausführung sind Run-ID, Run-URL und Testlogs nachzureichen. Keine native KiCad-10-, 200V-, 125°C-, SOA- oder Fahrzeugfreigabe aus bloßen Modell-PASS.
