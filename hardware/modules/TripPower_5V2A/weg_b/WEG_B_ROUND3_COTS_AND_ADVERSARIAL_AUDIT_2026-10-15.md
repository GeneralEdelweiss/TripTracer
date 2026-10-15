# TripPower Weg B – unabhängige COTS-Architektursuche und adversarialer Schutzreview, Runde 3

**Datum 2026-10-15, nur Branch \`design/trippower-b\`.** Auftrag: Review \`docs/TRIPPOWER_A_B_REVIEW_ROUND2_2026-10-15.md\` aus \`design/trippower-review\` sowie B-Report Runde 2 gelesen. TPSM33620-1:1-Swap ist abgeschlossenes NO-GO und wurde nicht erneut entwickelt. Alle gemeinsamen REV5-KiCad-/Baseline-Dateien und Weg A unverändert. Diese Untersuchung ist eine **COTS-Machbarkeits-/FMEA-Entscheidung**, keine Bauteil-, SOA-, ERC-/DRC- oder Fahrzeugfreigabe.

## Executive Entscheidung

1. **Kein neues Gesamt-Schutz-IC/Modul erreicht derzeit einen nachgewiesenen Sicherheits- UND Bauteilzahl-/Kosten-/Entwicklungs-Vorteil gegenüber LM74930 + LMR38020-Q1 bei 9–30 V, 5 V/2 A, zusätzlichem RAW-1 A, 200 V/350 ms und −40…+125 °C.** Weg A bleibt Entwicklungs-Hauptpfad – P01–P10 nicht freigegeben.
2. **Unabhängig neu priorisierter Einzelfehler: Q301 D-S-KURZ → SOURCE_A ≈ VIN_FUSED → D302 in Durchlassrichtung → VS_CLAMP.** Dies umgeht R313–R315 (9,9 kΩ) **selbst bei intakter D301-Zener**. Potenziell sicherheitsrelevant: D301 und D302 können weit mehr Fehlerstrom/Impulsenergie sehen als der niederstrombegrenzte RVS-Zweig. Eine fahrzeugseitige 3-/4-/5-A-Sicherung sichert diesen niederohmigen Zwischenzweig **nicht automatisch**.
3. **Zweiter unabhängiger Einzelfehler: D301 OFFEN:** 200-V/350-ms-Lastabwurf kann im idealisierten 21-µF-Null-Lastmodell VS >65 V und 100-V-MLCC-Grenzen überschreiten. Verlust des Geräts ist akzeptabel, **unkontrollierte thermische Energie/Leiterbahnschaden nicht**.
4. **Konkreter, beschaffbarer Alternativvorschlag als Vergleichsarchitektur**, *aber keine Designempfehlung*: Analog Devices **LTC4380HMS-4#WPBF** (AEC-Q100, −40…+125°C, 4–72-V-Betrieb, Retry, einstellbare Überstrom-/Überspannungsfunktion) + **LMR38020SQDDARQ1**, externer HV-MOSFET, reverse/ideal-diode-Block, Fehler-/SENSE-Widerstände, 200V-feste VCC-Vorspeisung/Klemme, lokaler Ein-/Ausgangsschutz und F_MAIN. Diese Architektur ist technisch plausibel, aber teurer und **nicht** als vollständige 200V/350ms-2A/RAW1A-/125°C-Schaltung nachgewiesen. Kein KiCad-Prototyp, da dokumentierte NO-GO-Entscheidung vor teurem Bibliotheksbau.
5. Wesentliche Verbesserung ist **gezielte Einzelfehlerqualifikation bzw. Umkonstruktion der D302-SOURCE_A-Nachladung**, nicht ein beliebiger IC-Tausch. Eine kleine Fehlerpfad-FMEA + echte KiCad-10-Netzlistenregression wurde auf B programmiert.

## 1. Reale beschaffbare Bausteine und referenzierte Herstellerbelege

| Exakte MPN (Stand Preis-/Lagersnapshot 15.10.) | Funktion / Herstellergrenzen | Bestandsbeleg | Systemurteil |
|---|---|---|---|
| **TI LM74930QRGERQ1** | Q1, Ideal-Diode + eFuse/OV/UV; 4–65-V-VS-Betrieb, externe FETs, externe 200-V-taugliche VS-Klemme, Q301/302 SOA | [DigiKey DE](https://www.digikey.de/en/products/detail/texas-instruments/LM74930QRGERQ1/22147207), regionale Snapshots **widersprüchlich: 0 bis 1364**; [TI](https://www.ti.com/product/LM74930-Q1) | Aktive Baseline; **Lager vor Bestellung neu prüfen** |
| **TI LMR38020SQDDARQ1** | Automotive -40…+150°C TJ, 4,2–80V, 5V/2A ausgelegt, externe 15µH Spule und Ausgangsfilter | [DigiKey DE](https://www.digikey.de/de/products/detail/texas-instruments/LMR38020SQDDARQ1/18177286), regional **0 / 522** widersprüchlich | Erhaltenswert wegen größerer VIN-Reserve |
| **ADI LTC4380HMS-4#WPBF** | AEC-Q100, 4–72V OP, −40…+125°C, 8µA Iq, ein externer N-FET, Überstrom, Fault Timer, Auto-Retry; 10-MSOP | [Mouser DE](https://www.mouser.de/ProductDetail/Analog-Devices/LTC4380HMS-4WPBF) **154 Lager**, EUR 9,07 / 7,10 / 6,05 je1/10/100; [ADI](https://www.analog.com/en/products/ltc4380.html) | **Einziger hier deutlich verifizierter alternativ lieferbarer AEC-Kandidat**, aber mehr Sonderrisiko/Kosten. Evaluation board DC2178A nur für kleineren Laststrom, nicht 2A+RAW/350ms/125°C |
| **ADI LTC4364HS-2#PBF** | 4–80V, integrierter Ideal-Diodencontroller, OV/UV/OCP/Retry; 16-SOIC, externe FETs; zur Familie existieren AEC-Q100-Versionen, **bei dieser exakten #PBF-MPN AEC-Zertifizierung nicht bestätigt** | [DigiKey DE](https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4364HS-2-PBF/3507757) 200 Lager, EUR 13,24 / 10,474 / 9,0206 je1/10/100 | **Nicht als Automotive-qualifizierte MPN bewiesen**; höherer Preis, externe HV-VCC-/FET-/SOA-Risiken |
| **ADI LTC4366HTS8-2#TRMPBF** | Floatende >500-V-Surge-Stopper-Architektur, externer HV-FET; keine gleichwertige integrierte Ideal-Dioden-/eFuse-/Rückspeise-Funktion; AEC-#W-Nachweis **nicht** vorgelegt | [DigiKey DE](https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4366HTS8-2-TRMPBF/2825884) 10186 Lager, EUR 10,42 / 8,174 / 6,996 je1/10/100; [ADI](https://www.analog.com/en/products/ltc4366.html) | Spannungsreserve gut, vollständige Automotive- und Schutzkette aber schlechter belegt/teurer |
| **ADI EVAL-ADVTS4152-EBZ** | Hersteller-EVM: 6,5–38V Betrieb, 5V/3A, bis zu 200V Eingangsimpulse, mehrere Controller **LT4356-1 + LT8609A + LTC4040**, Batterie-Backup | [ADI Hersteller](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-advts4152.html) | Sehr guter **Labor-/Referenz-Beleg**, aber keine kostengünstige kompakte Ein-IC-Lösung und **kein expliziter 350ms/125°C-Nachweis** |

**Hinweis zu den Preisen:** Vertriebslistings sind laufend veränderlich, unterschiedliche regionale DigiKey-Seiten widersprechen sich beim TI-Bestand. Stückpreise in **EUR netto**, ohne MWSt., Porto, PCB, Handbestückung und Zölle. Nur MPN, zu dem wirklich spezifische Händlerseiten existieren, wurde als „lieferbar belegt“ beschrieben; eine AEC-Familienangabe beweist **nicht** AEC für jede Modellendnummer.

Hersteller-Unterlagen: [ADI LTC4380 PDF](https://www.analog.com/media/en/technical-documentation/data-sheets/LTC4380.pdf), [ADI LTC4364](https://www.analog.com/en/products/ltc4364.html), [ADI LTC4366](https://www.analog.com/en/products/ltc4366.html), [TI LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), [TI 200-V-Load-Dump-EVM-Guide](https://www.ti.com/lit/pdf/sluucw6), [ADI EVAL-ADVTS4152 Referenz](https://www.analog.com/en/resources/app-notes/an-2083.html).

### COTS ist nicht gleich „externer Schutz entfällt“

Beim LTC4380 bleibt die 200V-feste **VCC-Vorspeisung samt Klemme** zwingend und kann selbst wieder ausfallen; bei 200V würde der Regler ohne diesen Schutz 72-V-Betriebsbereich überschreiten. Die Referenz nutzt eine HV-Vorspeisung und Zener. **Ein offener Zener ist auch dort ein zu untersuchender Einzelfehler** – keine automatische FMEA-Verbesserung. Weiter erforderlich: HV-FET mit heißer Puls-SOA und Verpol-/Rückspeisefähigkeit (evtl. zweiter FET), 5V/2A-Buck/Induktor/Passivteile, RAW-Zweig, F_MAIN, OVP-Schwellen-/Hysterese-Kontrolle und sicheres Wiederanlauf-/Stromlimit. LTC4364 kann Ideal-Diodenfunktion zusammenführen, aber auch er kann eine 200-V-Quelle **nicht** ohne externe FET-/VCC-/SOA-Bauteile direkt aufnehmen. Eine aufwendigere linear **regulierende** Stufe ist bei 200V/350ms und Strom bis3A kritisch: hypothetischer FET-Verlust (200−60)×2A=280W, Energie 98J in 350ms, und bei 3A 420W/147J. Deshalb bevorzugt echte Abschaltung bei Überlast statt langem Linear-SOA-Betrieb.

## 2. Unabhängig geprüfte *tatsächliche* REV5-Netzpfade und FMEA

Weg-A-Protected-Pin-Map wurde aus **\`design/trippower-a/tools/check_trippower_a_netlist.py\`** gegengeprüft, **nicht** aus bloßen Flag-Namen abgeleitet. Der auf Weg B angelegte \`safety_b_fmea.py\` muss den **echten KiCad-10-exportierten .net**-Inhalt einlesen und erwartet folgende Pins:

\`Q301.D2=VIN_FUSED, Q301.S3=SOURCE_A, Q301.G1=HGATE;\`
\`D301.K1=VS_CLAMP, D301.A2=GND;\`
\`D302.K1=VS_CLAMP, D302.A2=SOURCE_A;\`
\`D303.K1=VIN_FUSED, D303.A2=TVS_STACK;\`
\`D304.1=TVS_STACK, D304.2=GND;\`
\`R313→R314→R315 = VIN_FUSED ... VS_CLAMP.\`

**Neue Ableitung, Q301 einziger D-S-KURZ**: ein extern verursachter 200-V-Impuls gelangt über Q301=Kurzschluss an \`SOURCE_A\`, von dort im **Vorwärtsbetrieb** über **D302** zur \`VS_CLAMP\`-Domäne, **OHNE R313–R315**. Der Schutz liegt dann nur noch in nicht garantierten D302-/D301-I/V-/Pulse- und F_MAIN-Charakteristiken, nicht im 9,9k-Zweig. Die daraus folgende Bauteilbelastung kann bei einem 200V-Ereignis gefährlich werden, selbst wenn 5V-Buck/RAW erfolgreich abstürzen dürfen. 
* **Reiner Sensitivitätsstrom 0,10A** in 56-V-D301 während 350ms → Zener-Leistung **5,6W**, Energie **1,96J**; 
* **1,0A** → **56W**, **19,6J**. Keine Angabe behauptet, dass tatsächlich 0,1A oder1A fließen – Source- und Bauteilimpedanz, D301-V(I,T), D302-Kennlinie, Vorimpuls, PCB bestimmen es. Schon 0,1A löst eine nominelle mehr-Ampere-F_MAIN nicht zwingend aus.
* Bei D301 gleichzeitig OFFEN (Doppelfehler): 9,9k noch immer überbrückt, VS-Domäne kann in Richtung VIN steigen, und die Kondensatoren sind nur 100V spezifiziert.
* **Einfache „D302-Serien-R“-Reparatur widersprüchlich:** Um hypothetisch 0,780mA Nachladebedarf bei VIN/SOURCE_A9V, VS8V und D302 Vf0,7V zu liefern, braucht es **R≤0,385kΩ**. Um dagegen bei SOURCE_A200V, VS-Zener56V und Vf0,7V den Fehlerstrom auf höchstens **15mA** zu halten, wäre **R≥9,55kΩ** nötig. Kein einzelner Serien-R erfüllt beide angenommenen Ziele. 0,780mA stammt aus spezifizierten 12V/EN-Bedingungen des LM74930 und **ist keine bewiesene 9V-VS-Last**; die Rechnung ist eine belastbare **konditionale Unvereinbarkeit**, kein absoluter Beweis gegen alle Schaltungsvarianten.

**D301 OFFEN, auch ohne Q301-Kurzschluss**: RVS=9900Ω, VIN=200V, Ceff **angenommene Nennsumme 21µF**, VS0=0, nulllastiger RC-Fehlerfall: VS(350ms)=~**162,9V**, VS65V nach~**81,7ms**; startet VS0=56V → VS65V nach~**13,4ms**. Bei angenommenen 5µF Ceff früher. 65V ist LM74930-VS-Betriebsgrenze, C302/C308/C312 jeweils 100V. **Kein Beweis realer VS-Peakspannung**: unbekannte IC-Ströme und interne ESD können den Wert senken, aber ggf. zu starker eigener Pinüberlast führen; externer F_MAIN kann einen kleinen RVS-Ladestrom nicht notwendigerweise auslösen.

**D303/D304 Stack**: in der realen Polung D303 K=VIN/A=TVS_STACK, D304 bidirektional TVS_STACK↔GND. Spezifische Hersteller-VBR-Untergrenzen 167V und 36,7V unter unterschiedlichen Prüfbedingungen summieren sich auf mindestens 203,7V; **keine garantierte aktive 200V-Klemmung**. Man darf die unterschiedlichen beiden individuellen Peak-Clampingwerte bzw. Stromkennlinien nicht zu einem Serien-IV addieren. Einzelfehler D303-KURZ oder falsch gedreht → D304 allein, hohe Fehlerenergie unbewiesen; D304-KURZ → D303 allein, Clamping und Q301 SOA unbewiesen. Beide Kurz/Gegenfehler müssen über F_MAIN/Zuleitung geprüft werden. Einsparen des Stacks **ohne** bestätigte Q301-Rating-/Ringing-Prüfung ist unzulässig.

**Q301 Vishay SQM10250E_GE3**: 250V abs. VDS, damit **nur 50V nominelle** VDS-Differenz zum 200V-Puls. **Hersteller veröffentlicht tatsächlich ein 25°C-Single-Pulse-SOA-Diagramm** im [Datenblatt](https://www.vishay.com/docs/75035/sqm10250e.pdf) (Seite 5); eine 350ms/125°C-/repetitive-Freigabe folgt daraus nicht. Die EAS-Avalanche-Prüfung ist kein Ersatz für Drain-Gate-Überschwingen, Hot-Linear-SOA und PCB-Thermik. Beim Einzelfehler Q301 D-S-KURZ kann außerdem **Q302 mit nur 60V absolutem VDS** nachfolgend ungünstige Differenzpotentiale sehen. Bei Q301 und Q302 beide kurz droht die 200V-Versorgung auch auf RAW und den 80V-Buck. Q301 D-S kurz allein genügt für den neuen D302-Fehlerpfad.

| Fehlfall | Einzelfehler/Doppelfehler | Primäre Konsequenz | Einstufung |
|---|---|---|---|
| D301 OFFEN | Einzel | VS >65V/100V möglich, thermische Pin-/MLCC-Überlast | **kritisch** |
| Q301 D-S KURZ | Einzel | SOURCE_A→D302→VS ohne RVS-Kontrolle, Q302 60V gefährdet | **kritisch** |
| D302 KURZ | Einzel | verliert gerichtete Isolation; mit Q301 Kurz schlimmer | gefährlich in Kombination; Einzel-Thermik prüfen |
| D303/D304 einzeln kurz | Einzel | die jeweils andere TVS trägt Surge; keine SOA belegt | **kritisch** |
| Q301+Q302 D-S kurz | Doppel | RAW/Buck am hohen VIN, kein elektronischer Breaker | **kritisch** |
| D301+ein RVS kurz | Doppel | verbleibende Widerstände Energie~1J | thermisch kritisch |
| RUN bleibt LOW / D302 OFFEN | Einzel | keinen Start/Reset; Datenverlust möglich | **akzeptabel**, soweit keine Gefahr |
| USB RUN HIGH / VIN0 | Zustand | möglicher Rückspeisepfad und undefinierter EN | **offenes Funktions-/Safety-Gate** |

## 3. Was wirklich eine robustere Architektur begründen würde

**Vorrangige konkrete Verbesserung – projektspezifisch und ohne Reglerwechsel:**
* VS darf bei jeder plausiblen einzelnen hochspannungsführenden Fehlfunktion (D301 offen, Q301 kurz, D302-Langschluss) **nicht unkontrolliert auf den 200-V-Eingang geladen werden**. Eine robuste Lösung benötigt **nachgewiesene Trennung/Strombegrenzung jeder VS-Speisung**, nicht nur der VIN→RVS-Linie, inklusive SOURCE_A→D302. Ein zweiter Zener parallel zu D301 ist **keine vollständige Lösung**, weil bei Q301-Kurzschluss der D302-Bypasspfad viel höhere Ströme als RVS liefern kann.
* Nur wenn der Hersteller eine **zweigunabhängige, 200V-Einzelfehler-tolerante, startfähige** IC-Versorgung mit überschaubarem Aufwand und 9V Startreserve belegt, soll Weg A einen reproduzierbaren Revisionsvorschlag übernehmen. Im jetzigen Design ist ein sicherer Aus- oder Reset-Zustand zulässig; gefährliche Kurzschluss- oder thermische Wirkungen sind es nicht.
* F_MAIN mit realer Kennlinie/DC-Abschaltvermögen, Leitungsquerschnitt, I²t und Dauerfehlstrom koordinieren. Kein nennwertbasierter Beweis.
* Gesamter 200V-Prüfpuls muss über konkrete Quelle/Flanke/Quellimpedanz/Leitung-L und wiederholte thermische Limits spezifiziert werden. Auch ein 350ms-Rectangular-Rechenfall ist keine ISO-16750-Prüfsignatur.

## 4. Kosten/Bestückung/Montage – kein unvollständiger Gesamtpreis als Tatsache

Reproduzierbar aus [\`cots_b_compare.py\`](cots_b_compare.py), **nur tatsächlich preisbelegte Regler-IC-Teilmengen** bei Mengen 1/10/100 (EUR netto/Stück; Quellen oben):

| Menge | A: LM74930 + LMR38020 | B: LTC4380 + LMR38020 | B Mehrpreis je Platine |
|---:|---:|---:|---:|
| 1 | 8,3300 | 12,9800 | **+4,6500** |
| 10 | 6,3340 | 10,0650 | **+3,7310** |
| 100 | 5,2878 | 8,5203 | **+3,2325** |

Alternative LTC4366+LMR IC-Subset bereits bei 1 Stück **14,33€** (+6,00 € gegenüber A), ist zusätzlich im Schutzniveau nicht AEC-/Rückspeise-gleichwertig. Die aktuell im REV5 tatsächlich gezählten Bestückpositionen bleiben **57 AUTO / 58 RUN**. **Für vollständige LTC4380/LTC4364/4366-Architekturen ist weder eine validierte Pin-für-Pin-Schaltung noch eine echte End-BOM vorhanden.** Deshalb sind vollständiger neuer Stücklisten-Count und die 1/10/100-EUR-Gesamtkosten **unbestimmt**, ausdrücklich nicht „0 €“ oder automatisch 57. Die architektonisch erforderlichen Baugruppen bleiben: 5V-Buck U/L/C/R, HV-FET, Rückspeise-/Verpolungsschutz, VCC/HV-Zener- und Filter, Strom-Sense, OV/UV/Timer, RAW, F_MAIN extern und passendes PCB; ohne Eingabe/PCB-Lösung kann man ihre genaue Stückzahl nicht als technische Tatsache behaupten.

**Montage/Thermik:** LTC4380 im MSOP10 ist besser zugänglich als LM74930 VQFN24, aber die nötigen externen HV-Leistungstransistoren/TVS, Handbestückung und ggf. vierlagiger Kupferaufbau bleiben. TLC/LTC4380-Timer + gewolltes lineares Clamping bei hohen Pulsen erhöht die thermisch/energetische Entwicklungskomplexität. Dass 5V/2A bei TA125C und RAW1A klappt, ist weder für A noch für B nachgewiesen. Dazu unabhängigen Hot-Thermik- und 200V-Transientennachweis führen.

## 5. Reproduzierbare technische Artefakte und GitHub-Actions-Wahrheitsstatus

Unter \`hardware/modules/TripPower_5V2A/weg_b/\` ausschließlich neue Dateien:
* \`safety_b_fmea.py\` – hergeleitete VS- und D302-Faultpfade; echte native KiCad-Netzlisten-Pinprüfung; explicit single/double FMEA; Ein-Serien-R-Widerspruch.
* \`test_safety_b_fmea.py\` – Regression inkl. synthetischer Netzlisten-Mutationsfälle für D302-Polarität/R314-Bypass, Fault-VS/Energie und NO-release.
* \`cots_b_compare.py\` und \`test_cots_b_compare.py\` – mit konkreten URLs belegte IC-Kosten, Vorratsstatus, 1/10/100, absichtlich kein erfundener Systempreis.
* \`.github/workflows/trippower-b-independent-audit.yml\` – separater Branch-Workflow im KiCad10-Container: Python-Regression, native KiCad-ERC, **native** Netlist+FMEA und Artefakt-Upload. Ein grüner Lauf belegt Netzstruktur/Konsistenz und die Modellrechnung, **niemals 200V-/Hot-SOA-/Automotive-Freigabe**.

Schnellprüfung vom Repo-Root:
\`\`\`shell
python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_b -p 'test_safety_b_fmea.py' -v
python3 -m unittest discover -s hardware/modules/TripPower_5V2A/weg_b -p 'test_cots_b_compare.py' -v
python3 hardware/modules/TripPower_5V2A/weg_b/safety_b_fmea.py
python3 hardware/modules/TripPower_5V2A/weg_b/cots_b_compare.py
kicad-cli sch export netlist -o /tmp/trippower-b.net hardware/modules/TripPower_5V2A/TripPower_5V2A.kicad_sch
python3 hardware/modules/TripPower_5V2A/weg_b/safety_b_fmea.py --netlist /tmp/trippower-b.net
\`\`\`

**CI-Beweisstand bei Verfassen:** Für geprüften B-Commit \`989e02c3fda5e3e8c3110dc9f175f3dfbd50b5e7\` gab GitHub-Commit-Combined-Status \`statuses=[]\`; der für PR-getriggerte Runs zuständige GitHub-Connector meldete \`workflow_runs=[]\`. **Das ist weder ein bestätigter PASS noch ein FAIL des Push-Workflows.** Eine verifizierte Workflow-Run-URL konnte über die verfügbaren APIs nicht ermittelt werden; **keine URL erfinden**, keine behauptete native KiCad10/ERC-PASS. Der Workflow ist zum Nachprüfen vorbereitet und speichert bei echter Ausführung Run-Logs und native Netlist.

**Weg B Exit:** Keine neue KiCad-Schaltung beginnen, bis ein tatsächlicher COTS-IC die harten 200V/D301/Q301/D302-/9V-Sicherheitsgates plus mindestens einen belegten Preis-/BOM-/Entwicklungsaufwandsvorteil löst. Die neue Q301→D302→VS-Fehlerkopplung und der passive Serien-R-Gegennachweis sind die wesentlichsten konkreten unabhängigen Ergebnisse und sollten im Weg-A-Review als neue Gefahren-Hypothese untersucht werden. **KEINE Fertigungs- oder Straßenfreigabe.**
