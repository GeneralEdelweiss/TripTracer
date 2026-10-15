# TripPower Weg A – Runde 4: Q301 Drain–Source-KURZ und D302-Fail-Short, konstruktives Ergebnis (2026-10-15)

**Branch:** `design/trippower-a`. **Zuerst gelesen:** `docs/TRIPPOWER_A_B_C_REVIEW_ROUND3_2026-10-15.md` auf `design/trippower-review` und `WEG_A_ROUND3_D301_BACKUP_PROTOTYPE_2026-10-15.md`. Anforderungen beibehalten: **9–30 V**, **5 V / 2 A**, RAW bis 1 A als Designziel, **200 V / 350 ms**, **−40…+125 °C**. **Keine Fertigungs-, Fahrzeug-, 9V-Start-, SOA-, Lastdump-, Thermik- oder PCB-Freigabe.** Die REV5-Hauptschaltung und die aktive 57-AUTO/58-RUN-BOM bleiben unverändert; Weg B und C nicht verändert.

## 1. Tatsächlicher Fehlerschaltkreis, KiCad-10-netlistbelegt

Der native KiCad-10-exportierte Schaltplan zeigt:
- Q301 Pin2 = **VIN_FUSED** (D), Pin3 = **SOURCE_A** (S); ein Q301-D-S-Kurz legt SOURCE_A direkt an VIN_FUSED.
- D302 `BAV21WQ-7-F`: **Anode Pin2 = SOURCE_A**, **Kathode Pin1 = VS_CLAMP**. D302 ist bei 200V SOURCE_A und rund 56V VS vorwärts gepolt, **ohne** R313–315.
- VS_CLAMP: D301-Kathode, optional D306-Kathode, **C302 (1uF), C308 (10uF), C312 (10uF)** (alle nominal 100V), U301 **VS pin22**, U302 **VDD pin1**. U301 MODE und Kontrollpins ebenfalls netzlistenbelegt.
- **Zusätzlicher harter Blocker:** U301 **A/Source pins2/15** und Q302 **Source pins1/2/3** liegen **direkt** an SOURCE_A. Selbst bei idealem D302-Strombegrenzer bleibt an U301 A bei ideal 200V-Puls **200V** anstatt des vorgesehenen 4–65V-Betriebsbereichs. Der Q302 ist ein **60V**-MOSFET; tatsächliche `VDS` hängt von Drainspannung ab, ist jedoch unter diesem Einzelfehler nicht nachgewiesen. Eine D302-Fixierung **kann nicht** die Gesamtversorgung für den Q301-DS-Kurz freigeben.

**TI-Herstellerdesign** LM74930-Q1 §8.2.2.1 und SNOAAA1: Der 200-V-Entwurf setzt voraus, dass Q1 abschaltet und **nur VS** via `10kΩ` durch einen Zener versorgt wird; der gezeigte Einzel-FET-Kurz gehört **nicht** zum Herstellerbeispiel. Siehe https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf und https://www.ti.com/document-viewer/lit/html/SNOAAA1/GUID-A29F6540-095F-4408-8FD4-388A1740884B .

## 2. Fehlerstrom, D302 und externe F_MAIN – quantitativ reproduzierbar

`tools/trippower_a_q301short_stress.py` rechnet ein ideal steifes Rechteck `VIN=200V`, `VS=56V`, **illustrierte** `VF_D302=0,7V`, `0,350s` und separate Generator-/Leitungs-Quellimpedanzen. `I_ideal=(200−56−0,7)/Rsrc`. Diese Modellströme sind **keine** realen Hersteller- oder ISO-Testwerte; sobald Dioden versagen, F_MAIN öffnet, der Puls zusammenbricht oder die Zener-Spannung ändert, endet die Annahme.

| Angenommene Rsrc | Ungeschützter rechnerischer Zweigstrom | E an 56V-Zener in 350ms bei nicht auslösendem F_MAIN |
| ---: | ---: | ---: |
| 1 Ω | 143,3 A | 2.809 J |
| 5 Ω | 28,66 A | 562 J |
| 10 Ω | 14,33 A | 281 J |
| 50 Ω | 2,866 A | 56,2 J |

D302 ist eine automotive `BAV21WQ-7-F` mit 400mA durchschnittlichem Gleichstrom-Rating und 200V **Sperrspannung**; die 200V-Sperrzahl verhindert **keinen** Strom bei Vorwärtspolung. Hersteller/Distributor https://www.digikey.com/en/products/detail/diodes-incorporated/BAV21WQ-7-F/16548209 . Das ist ein massiver Gegenbeweis gegen „D301/D306 verträgt 0,3J“ **ohne** RVS unter diesem Fehler. Die Realgefahr kann ein Schmelz-/Brand-/Kurzschluss- oder Leiterbahnversagen sein. D301-/D306-Energie hängt in Wirklichkeit von I-V(T), Dioden-SOA und realem Sicherungsverhalten ab; nicht von 200V-Rechteck allein.

Die **extern zu dimensionierende F_MAIN** hat bislang **keine exakte Sicherungs-MPN, DC-Auslöse-/Abschaltvermögen bei 200V, I²t-/Lichtbogenkurve und Kabeldaten**. Eine Beispielrechnung zeigt: Für eine nur **willkürlich** angenommene 0,3J-Zenerenergie und I_ideal=143,3A bei 1Ω müsste der Gesamtstrom theoretisch nach rund **37µs** weg sein. Für 10Ω sind es rund **374µs**. Die reale Sicherung könnte langsamer, andere Spannungs-/Leitungsströme könnten die Kurve verändern. Die Beispielwerte sind **kein** Nachweis für F_MAIN.

Sind beide Klemmen D301/D306 ausgefallen, kann der direkte D302-Pfad im idealen Extrem VS auf den 200-V-Quellpegel nachladen. Der nominale VS-C-Speicher 21uF enthielte bei 200V **0,420J**, gegenüber rund **0,033J** bei 56V; die 100-V-Caps, U301-VS und TPS38-VDD hätten Grenzverletzungen. Ceff(V,T) und reale Ladezeit bleiben unbekannt. Bei intakter Klemme sind stattdessen **D302/Zener-Leistung** unkontrolliert, solange F_MAIN nicht qualifiziert ist.

## 3. Isolierter konstruktiver Zweig: BSP135 + R342 vor VS, **nur Zwischenstufe**

**Konkreter KiCad-Prototyp:** `hardware/modules/TripPower_5V2A/01_Protection_LM74930_Q301SHORT_CURRENTLIMIT_PROTOTYPE.kicad_sch`. Baut auf dem *D306-only-Prototyp* auf; keinerlei Änderung an `01_Protection_LM74930.kicad_sch` der REV5-Hierarchie.

**Aktive Nachlade-Topologie** im isolierten Blatt:
`SOURCE_A → D302.Anode2 → D302.Kathode1(VS_BOOST_IN) → Q307.Drain2 → Q307.Source3(VS_BOOST_RS) → R342.1→R342.2 → VS_CLAMP`, Q307.Gate1 nach VS_CLAMP. **D306** bleibt als separate 56V-Zenerdiode VS_CLAMP→GND vorhanden.

Hersteller Infineon **BSP135H6327XTSA1**, 600-V-automotive **Depletion** N-MOSFET, Gehäuse SOT-223, Pins 1G/2D/3S/4Tab-D (Footprint **SOT-223-3_TabPin2**), AEC-Q101. Hersteller https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsp135-ds-en.pdf und Hersteller-Applikation https://www.infineon.com/assets/row/public/documents/24/42/infineon-application-note-applications-for-depletion-mosfets-applicationnotes-en.pdf . Die Infineon-Referenz zeigt die Selbststrombegrenzung durch **Gate am unteren Source-Widerstandsanschluss** (bei Stromfluss `Vgs≈−I·R`). Bauteil Q307 mit `600 V` bietet Spannungspuffer gegenüber 200V, **nicht** automatisch eine belastbare Strom-/SOA-Maximalgarantie.

**R342: Yageo `AC1206FR-071K5L`** 1,5 kΩ, 1%, ±100ppm/°C, 1206, AEC-Q200, 250mW @70°C, 200V continuous; bestellbar. Hersteller/Lieferant https://www.mouser.de/de/ProductDetail/YAGEO/AC1206FR-071K5L . Die neue R/Hot-Toleranz ist **für den Gesamtstrom noch nicht** als garantierte Imax gerechnet, weil die Gate-Transferkurve `Id(Vgs,Vds,T)` nicht als absolute Grenze verfügbar ist.

**Mouser-DE-Snapshots**, vor Steuer/Versand: BSP135 €1,43 / 0,912 / 0,633 bei 1/10/100; R342 €0,086 / 0,027 / 0,021. D306 zusätzlich €1,23 / 0,776 / 0,5138 laut DigiKey. Damit **+3 bestückte Positionen ggü. REV5**, insgesamt 60 AUTO / 61 RUN, nicht die aktive BOM. Gesamtteilepreisdelta gegenüber REV5 ca **+2,746 / +1,715 / +1,168€ je PCB** bei 1/10/100 vor Steuern/Versand/PCB. Keine live garantierten Bestände; Infineon/Mouser Bestellstatus vor Muster neu prüfen. Maschinenlesbar `WEG_A_Q301SHORT_D302_LIMITER_BOM_DELTA_2026-10-15.csv`.

**Hersteller-Gate, kein fiktiver Maximalstrom:** Das BSP135-Datenblatt gibt `VGS(th)=−2,1..−1V` bei **VDS=3V, ID=94µA**, `IDSS_min=20mA` bei VGS0 (kein IDSS_max), `RDS(on)_max=60Ω` bei 10mA/25°C an, aber keinen garantierten **0..200V, −40..125°C, 350ms** Stromlimitwert der Gate-R-Schaltung. Die Rechnung `2,1V/(1,5k·0,99)≈1,414mA` ist **nur heuristische Quelle für einen Sensitivitätsfall**, *kein* Hersteller-Imax. Als Beispiel bei **angenommenen** 1,4mA und SOURCE_A200 / VS56 / VF0,7 liegt Q307 bei etwa `~141V·1,4mA≈0,197W /0,069J in 350ms`, D306/D301 bei `~0,078W /0,027J`. Bei angenommenen **5mA** liegt Q307 bei >0,6W, ist heiß kritisch. Alle diese Werte sind parametrisierbare Szenarien, keine Schaltungsfreigaben.

Infineon gibt für BSP135 maximale `RθJA` **115K/W minimal footprint** und **70K/W auf Hersteller-6cm²/70µm-FR4**. Bei TA125/Tjmax150 ergeben sich rein stationär **0,217W** bzw. **0,357W** Restbudget – ohne zusätzliche Hotspots. Die letzte Kurve `SOA(TA25)` ist **kein** Beleg für 350ms bei125°C; `ZθJA(350ms)` muss am realen PCB mit Sicherheitsmarge und dem tatsächlichen Id(T) überprüft werden. Datenblatt Fig.3/4, Seiten2/4.

## 4. Kritischer 9-V-Start: dieser Prototyp ist **kein Drop-in**

Beim aktiven Start bei VIN_FUSED=9V und angenommenem VS≈8V bleiben für D302/FET/R342 nur rund **1V Spannungshub**. Bei willkürlich angenommener 0,7-V-D302-Flussspannung und 60Ω BSP135 erreicht der Ohm-Sensitivitätswert über 1,5k nur **0,192mA**; R313–315 speisen zusätzlich rund **0,101mA**. Summe **0,293mA**. Der TI-LM74930-Aktivstrom **780µA max** gilt zwar bei **VS12V/EN2V**, ist *kein* echter 9V-VS-Laststrom, zeigt jedoch, dass der 9V-Nachladestrom nicht garantiert ist. Der BSP135-Rds-Wert ist bei anderen Testbedingungen ermittelt; das 0,293mA-Ergebnis ist **kein harter Strom-Maximalwert**. **P01/P06/P10 offen** – Ceff, dynamischer CAP/VS-Strom, TPS38-Reset und C311-Restladung noch separat zu qualifizieren.

## 5. D306-Bewertung nach Comchip-Herstellerdaten

**Comchip ACZRC5370B-G 56V ±5% SMC** hat 5W **nur bei TL=75°C**, laut Comchip RevD Seite1, auf 5mm/1oz-Kupferlötflächen; die Derating-Kurve geht ungefähr linear auf 0W bei TL150°C. Bei einer tatsächlich **auf TL125°C gehaltenen** Anschlussleitung ist nominell noch **~1,67W Dauerbudget**. Für RVS-versorgte D306 allein bei VIN200, VS56, RVS worst ca **0,83W** ist die Bedingung aus dieser *einfachen linearen* Herstellerkurve `TL < ~137,5°C`. Bei Umgebung **125°C** sind das nur **~12,5K Bleierzungsreserve** – die tatsächliche Anschlussleitung kann wegen Verlustwärme wärmer sein. Das aus dieser Rechnung folgende `D306_SAFE=TRUE` **darf nicht** behauptet werden. Das Herstellerschaubild `ZθJL(t,D)` enthält zusätzliche Angaben zur transienten Pulsbelastung, aber ohne tatsächliches PCB/thermische Montage und Vz_max(I,T) besteht keine nachgewiesene Grenze. Quelle Comchip https://www.comchiptech.com/admin/files/product/ACZRC53xxB-G%20Series%20RevD.pdf (Hersteller-Link leitet teils um; Spiegel der RevD-Daten: https://pdf.elecfans.com/COMCHIP/ACZRC5341B-G.html ).

Der zusätzliche D306 hat **keinen belegten** IRmax bei 8–9V /125°C. Die Hersteller-IR-Grenze **0,5µA @42,6V** gilt nicht automatisch für die 9V-Heißleckage. D306 ist **gegen D301 OFFEN strukturell sinnvoll**, aber bei **Q301-KURZ ohne zusätzliche Begrenzung nicht** sinnvoll als vermeintlich sicherer Energiespeicher. **D306 weiter nur als isolierter Prototyp, KEINE Aufnahme in Haupt-BOM**, bis TL/Tj/Schutz-Einzelausfall und 9V-Nachweis erfüllt.

## 6. Zwingende Architekturentscheidung für echte Q301-Single-Fault-Abdeckung

**Dieser D302-Limiter löst nur einen von mehreren Q301-short-Schäden. Auch mit idealem Q307 tritt 200V unmittelbar an U301 A und Q302-SOURCE auf.** Eine belastbare Architektur muss eine **zweite unabhängige Serienabschaltstufe vor Q301** oder ein gleichwertiges für 200V/350ms und F_MAIN/I²t nachgewiesenes Schutzsystem enthalten. Reine 5W-Zenererweiterung oder zusätzliche Sicherung ohne 200V-DC-Abschaltvermögen genügt nicht. Vorschlag (noch nicht im A-Hauptschaltplan implementiert):

- **Referenzkandidat Diodes `AP74502HQTA8-7`** AEC-Q100, 3,2–75V Betriebsbereich, 200V-unsuppressed-load-dump Referenzschaltung mit **eigener** HV-VIN-Zener-R-Kette (10k/60V), 2 externen HV-Back-to-back-FETs und OV-CUTOFF, Hersteller DS47093 Rev2 Fig. §Application Information; https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf . Im echten A-Fehlerzweig müsste diese Stufe **vor** Q301 sitzen, ihre Gate-Ansteuerung unabhängig von dessen U301-A-Pin-Überspannungsversagen bleiben und die beiden FETs spannungs-/temperatur-/SOA-/Quellenimpedanz-qualifiziert sein. Damit kann ein einzelner Q301-D-S-Kurz downstream grundsätzlich spannungsisoliert werden, *solange die separate Eingangsstufe tatsächlich fail-off ist*. Ein gemeinsamer Ausgangs- oder Upstream-Schalterfehler wäre eigenständige FMEA. Ein solcher Dual-Controller-/4-MOSFET-Ansatz ist **deutlich komplexer** als eine sofortige Aufrüstung um D306+Q307+R342; vorher Vollsystem-BOM/2A@125°C/9V-Start gegenüber COTS-Alternative vergleichen. **Nicht** aus Hersteller-Referenzgrafik eine geprüfte neue Gesamtarchitektur ableiten.
- Für Endlösung bevorzugt **bestehende A-Architektur erst nach kompletter Q301-short-FMEA freigeben**, oder nach Abgleich mit unabhängigen Pfaden gezielt auf simpler validierbares Controller-/COTS-Konzept wechseln. Ohne Hersteller-Hot-Pad-/FET-SOA nicht blind neue MOSFETs auswählen.

## 7. Tatsächliche Entwicklungsartefakte, Mess-/Stop-Gates

- Neues konkretes, reversibles KiCad-10-Blatt: `01_Protection_LM74930_Q301SHORT_CURRENTLIMIT_PROTOTYPE.kicad_sch`.
- Nativer Netlist-Mutationsprüfer: `tools/check_trippower_a_q301short_prototype.py` bestätigt den **exakten elektrischen Delta-Satz**: D302.K1 net `VS_CLAMP → VS_BOOST_IN`; hinzu Q307.G1 VS, D2 BOOST_IN, S3 BOOST_RS, R342.1 BOOST_RS, R342.2 VS. Zusätzlich U301-A-/Q302-/VS-Kondensator-Pins bei Q301-short; D306 im Prototyp unverändert.
- Parametrischer ausführbarer Fehler-/Quell-/Fuse-/Thermikscreen `tools/trippower_a_q301short_stress.py`, Regression `tools/test_trippower_a_q301short_stress.py`, beide vom eigenen KiCad10 GitHub-Workflow `.github/workflows/trippower-a-verification.yml` erfasst.
- BOM `WEG_A_Q301SHORT_D302_LIMITER_BOM_DELTA_2026-10-15.csv`; allseitige REV5-Stückliste **nicht geändert**.
- Für echte Freigabe fehlen: A/VS/C/GATE/VDS-Pins bis200V/350ms in Q301-short, Source-R/L, Leitungsschutz F_MAIN 200V-DC-I²t und Sicherungsimpedanz, Q307 limitierte **ID(T,VDS,RS)** vs 9V, Q307 Q301 125°C SOA, hot D301/D306/TL, 100V-Ceff, TPS38/RUN/VIN=0, Buck 5V/2A und RAW1A, 30V-Recovery, komplett geroutetes PCB/DRC.

**Entscheidung:** `D302-Q307-R342` als **wertvollen isolierten Machbarkeitsprototyp** behalten, *nicht* als Lösung für Q301-DS-short oder drop-in 9V-Start freigeben. Q301-short bleibt ein **harter System-STOP**. Die neue Netzlistenvalidierung widerlegt jede Behauptung, ein zusätzlicher Zener oder ein D302-Limiter alleine mache diesen Fehler ungefährlich. Eine unabhängige vorgeschaltete Abschaltstufe ist der nächste konstruktive Pfad, falls echte Single-Fault-Sicherheit gefordert wird.
