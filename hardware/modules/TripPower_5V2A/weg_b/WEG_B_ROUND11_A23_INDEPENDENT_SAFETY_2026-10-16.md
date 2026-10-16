# TripPower Weg B – Round 11: unabhängige A23-Sicherheitsqualifikation (16.10.2026)

**Entscheidung: A23-NATIVE-SCHALTPLAN PASS; ELEKTRISCHE SYSTEM-/LABORFREIGABE NEIN.**
MODE=GND/PGTH=GND ist als Hauptvariante für einen strom- und energiebegrenzten Laborprototyp vertretbar, jedoch nicht als qualifizierter Kurzschluss- und Temperaturschutz. **NO FAB / NO VEHICLE / NO PRODUCTION**. A/C/D bleiben unverändert; dieser Bericht und zugehörige neue Prüfdateien liegen ausschließlich auf design/trippower-b.

## 1. Geprüfte aktuelle Quellen statt historischer A25-Annahmen

Direkt auf GitHub gelesen: AGENTS.md; docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md; docs/HARDWARE_REQUIREMENTS.md, PWR-44 bis PWR-56; docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md; hardware/modules/TripPower_5V2A/POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md; B Round10 WEG_B_ROUND10_TI_300K_FACTORY_OVP_UVLO_INDEPENDENT_DECISION_2026-10-16.md.

A23: design/trippower-a bei Commit **f30f35d404e6ba549ee6202c46d660f498c36545**, neueste Round5-Dokumentation REV6_A_ROUND5_MODE_PGTH_A23_HOST_GATE_2026-10-16.md. Elektrischer A23-Stand seit Commit **3f3dd727452d61aa894ad2f03be03af10174eeec** unverändert. Wirklich vorhandene Projektwurzel hardware/modules/TripPower_REV6_A/TripPower_REV6_A_FACTORY_OVP.kicad_pro mit Root .kicad_sch, 01_TPS26631_REV6_FACTORY_OVP.kicad_sch, 02_5V_LMR38020_FACTORY_OVP.kicad_sch und 23er Bestell-BOM REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv (Blob ea8cf61eef9f18f5585581a9a9ea67abb47951c8). Historischer A25-Root wurde **nicht** als aktuelle Basis benutzt.

D neuester Round11: design/trippower-d-load-dump Commit **7d3f53b8c6c517aeb4d258fe2b1c783b63098a57**, hardware/modules/TripPower_5V2A/weg_d/WEG_D_ROUND11_A23_AFTER_M8_SPICE_BLOCKER_LAB_PLAN_2026-10-16.md. C neuester Round11: design/trippower-c Commit **bab593fdac16ac68f8c9e58e47df577fd7f9fe4e**, weg_c/REV6_ROUND11_A23_Q201_MLCC_BUCK_PROCUREMENT_2026-10-16.md. Der B-Round10-Nachweis bezog sich noch auf A25 und ist deshalb nicht in einen A23-Nachweis umbenannt worden.

Original-Herstellerinformationen: [TI TPS2663 Datenblatt Rev G](https://www.ti.com/lit/ds/symlink/tps2663.pdf), besonders §6, §8.3.2–8.3.7, §8.4, §9.4–9.6; [TI LMR38020-Q1](https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf); [Vishay SQM100N10](https://www.vishay.com/docs/67027/sqm100n1.pdf); [TI TMP390-Q1 Rev B](https://www.ti.com/lit/ds/symlink/tmp390-q1.pdf); [TI TPS2660 Rev G](https://www.ti.com/lit/ds/symlink/tps2660.pdf). Datenblatt-Min/Max ist keine erfolgreiche Hardwaremessung.

## 2. Eigenständiger NATIVER KiCad-10-Check des tatsächlich gezeichneten A23

**Ausgeführt, nicht nur von A übernommen:** GitHub Actions [B Run 38881195864](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38881195864), Job **116908064982**, B-Prüfcommit **00bfdb6c8ccdcd4d2eb076c2ab79c6879c77a68c**, Status laut GitHub **completed/success**, vollständiges Joblog tatsächlich gelesen. Workflow .github/workflows/trippower-b-round11-a23-native.yml checkt den A23-Quell-Commit f30f35d404e6ba549ee6202c46d660f498c36545 separat nach audit-A23 aus und führt aus:

1. Native **KiCad 10.0.6** ERC auf echtem A23-Root mit allen Schweregraden, Exitcode bei Fehlern: **Found 0 violations**.
2. Echter KiCad-10-Netzlistenexport als XML über die komplette A23-Hierarchie; dazu tatsächlicher nativer KiCad-BOM-CSV-Export.
3. **Eigenes Weg-B-Prüfskript** hardware/modules/TripPower_5V2A/weg_b/rev6_round11_a23_independent_native.py ohne Import von A-Verifikationscode: **44/44 erwartete elektrische Pin-Net-Zuordnungen, 7/7 nominelle Widerstandswerte direkt aus nativem KiCad-XML, 23/23 bestückte Referenzen, 23/23 Hersteller-MPN und Footprints sowohl gegen platzierte KiCad-Instanzen als auch gegen Bestellliste**, vollständige native BOM-Referenzmenge, keine bestückte Sicherung auf TripPower.
4. Preise unabhängig aus CSV addiert: **20,2570 / 13,5610 / 10,6266 EUR netto je Modul** bei Stückzahlen 1/10/100 (nur diese 23 Bauteile; nicht Kosten für PCB, Montage, Stecker, Host, externe Fahrzeugfuse oder Labor).
5. Vollständiges [A23-Evidenzartefakt ID 12037905992](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38881195864/artifacts/12037905992): ERC-JSON, native XML-Netzliste, native BOM, Pin-/MPN-Prüf-JSON, Quelle und KiCad-Version. **Kein A23-PCB, deshalb kein PCB-DRC oder optischer Pad-/EP-Nachweis**.

Fehlertransparenz: [erster B Run 38879738015](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38879738015) hatte bereits native ERC0, Netzliste und BOM exportiert, scheiterte aber an einem **B-Parserfehler**: KiCads mit unconnected- beginnende Pseudo-Netze wurden fälschlich als echte SHDN-/Diagnose-Leitungen interpretiert. Der B-eigene Parser ignoriert nun ausschließlich solche NC-Pseudo-Netze. Schaltung und KiCad-ERC-Regeln wurden dabei **nicht** verändert. Danach oben genannter unabhängiger Run erfolgreich.

### Elektrischer Original-TI-Pin-/Netzvergleich

| Position und geprüftes Signal | Native A23-Netzbeobachtung | Ergebnis / noch offene Grenze |
|---|---|---|
| U201 TPS26631PWPR IN1, IN2, IN3 | EFUSE_IN **vor** Q201 | PASS Net; vor Q201 separat messen |
| U201 IN_SYS6 | VIN_FUSED **nach** Q201 | PASS Net; C201 direkt hier, ≠ EFUSE_IN |
| U201 OVP8 | GND | PASS TI Factory OVP Rising **33,2–35,4V**, Falling **32,7–35,0V** bei IN_SYS |
| U201 UVLO7 / R201 | IN_SYS → AC1206FR-07330KL 330kΩ → UVLO | PASS TI ≥300k bei externem Reverse-FET: Rmin **324,720kΩ** (1% + 100ppm/K × 60K bis +85°C) |
| U201 MODE12 | GND | PASS Schaltung / Auto-Retry bei Überstrom/TSD; Temperaturenergie OFFEN |
| U201 PGTH16 | GND | PASS Schaltung / TPS-PGOOD17 bleibt LOW, **kein 2×IOL-Pulsmodus nach PGOOD HIGH** |
| U201 SHDN13 | NC (interne Pullup-Enable) | PASS bewusste NC, aber **FAIL +85°C-Interlock als vorhandene Funktion** |
| U201 ILIM11/R204 | CRCW12066K04FKEAHP, 6,04kΩ nach GND | PASS Net, Hauptlimit ca. 3A nominal; RAW 0,5A nicht selektiv |
| U201 dVdT10/C203 | 100nF nach GND | PASS Softstartnetz; keine bewiesene 10V-Inrushfunktion |
| Q201 / Q202 | Q201 D=EFUSE_IN, S=VIN_FUSED, G=R6_B_GATE; Q202 DRV/IN_SYS/BGATE | PASS TI-Rückwärtsschutz-Netzkonzept, MOSFET-Gate-SOA bei 58V OFFEN |
| C201/C202/Buck | C201 VIN_FUSED; C202 und Buck-CIN erst nach U201-OUT | PASS Knotenlage; C202 kein direkt paralleler Eingangs-Pulsdämpfer |
| PWR_FAIL | U101 Buck PG6 über Q501 zu PWR_OK_SINK_FAIL_RELEASE | Buck-PG **nicht** U201-PGOOD; Host-Pullup/FRAM-Fail-high OFFEN |

**Herstellerverdrahtungsurteil:** Die vorliegenden TPS26631-Referenzvorgaben zu externer Q201/Q202-Verpoltopologie, 330k zwischen IN_SYS und UVLO, Factory OVP, MODE, PGTH, ILIM und dVdT sind an der **wirklichen A23-KiCad-Schaltung** syntaktisch/elektrisch nachvollzogen. Die absolute Behauptung einer vollständig TI-qualifizierten Anwendung wäre dennoch falsch: Gate-Transienten, DC-Bias-Kapazität, MOSFET-Belastung, reale Wiederholungstemperaturen, IC-Fault-Corners und HF-Layout sind **nicht** geprüft.

**Statische UV/OV-Herstellerrechnung:** 32V am IN_SYS ist 0,7V unter minimaler Factory-OVP-Fallgrenze; damit ist die statische Restart-Logik richtigherum. Um bei 36V an M8 den höchsten Abschaltpunkt 35,4V an IN_SYS sicher zu erreichen, darf der gesamte Momentandrop höchstens **0,6V** sein (einschließlich Q201 und Host). 330k ist **keine** programmierte 10V-Brownout-Schwelle. 10V an M8 und 5V/2A+RAW0,5A sind noch nicht garantiert.

## 3. MODE=GND / PGTH=GND – Auto-Retry gegen Latch

**Entscheidung B:** MODE=GND/PGTH=GND im isolierten, strom- und energiebegrenzten **ersten Laborprototyp beibehalten**, **KEINE Fehler-/Temperatur-/Fahrzeugfreigabe**. Ein MODE=OPEN-Latch reduziert wiederholte Energieeinträge, benötigt nach OCP/TSD aber eine sichere Hardware-Entriegelung (SHDN low→high, qualifizierter UVLO-Zyklus oder Eingangs-Neustart). Dieser Resetpfad existiert noch nicht nachgewiesen im A23/Host. Für rein OVP 58→32V ist nicht MODE, sondern die Factory-OVP-Falling-Logik maßgeblich.

**Permanent RAW-Hardshort:** Hauptlimit nominell ca. 3A, normale Last0A bzw. bei Teilkurzschluss unterhalb Hauptlimitation möglicherweise dauerhaft eingeschaltet. Die TI-Typzeiten um 162ms OCP vor OFF und etwa 648ms typische thermische Retry-Verzögerung (500–800ms spezifizierte Delay-Bandbreite, abhängig vom Fault-Verlauf) sind **nicht** ein garantierter thermischer Puls-Energie-Budget. Als ausschließlich rechnerische Extremhypothese bei konstant 3A, VOUT=0, 162ms: 10V→**4,86J**, 32V→**15,55J** in der internen Serienfunktion je On-Phase. **Weder gemessene Energie noch Worst-Case-Obergrenze:** tatsächliche Leistungsbegrenzung, Thermoregulation, VDS- und I(t)-Verlauf, Verkabelung und Tj-Schwelle verändern alles. Prüfen: Ecycle = Integral[VDS(t) × I(t) dt], Duty Cycle, Pmean und Hotspot Tj/PCB/Copper/Stecker bei +60/+70°C und wiederholtem Test.

**PGTH=GND:** TPS-eigenes PGOOD LOW; nach TI §8.3.7.1.2 ist der optionale **2×IOL-Lastpuls nur nach PGOOD HIGH** nutzbar. Da PGOOD nie HIGH ist, ist er in A23 nicht scharf. Schnelle Short-Spikes sind dadurch **nicht** auf nominell 3A begrenzt. Der unabhängige LMR38020-Buck-PG-Pfad ist nicht dasselbe Signal.

**10V/2A Start:** bei angenommener Wirkungsgradzahl η80%, RAW0,5A fließen stationär ungefähr **1,75A** aus 10V; Start-/CIN-/COUT-Spitzen kommen hinzu. Gate-/Steckerdrop, +60°C, temporäre Brownout-Reset-Schleifen und Buck-PG gemessen testen. Kein per UVLO330k garantiertes geordnetes Abschalten bei <10V.

**OVP 32→36→58→32V:** Nach Rückkehr darf Auto-ON erst bei stabilem IN_SYS <32,7V plus korrektem dvdt/OVP-Ramp erfolgen. Mindestens ein Test mit wiederholten Überschwing-/Unterspannungseinbrüchen und Lastinrush; unter Fault darf keine thermisch gefährliche Restart-Schleife entstehen.

**Geschädigte externe RAW-Last / Teilkurzschluss:** 32V×0,5A = **16W** dauerhafte Leistungsaufnahme sind bei einer äußerlich defekten Last elektrisch nicht von legitimen 0,5A zu unterscheiden. Strombegrenzung selbst bei exakt0,5A verhindert **nicht** beliebige externe Wärme, solange die Last diesen Strom akzeptiert. Es braucht definierte abgesicherte Anschluss-/Leitungslängen und Verbraucher-Wärmeverträglichkeit, ggf. begrenzte Einschaltzeit oder Lasttemperaturüberwachung. Main-TPS ist kein universeller Schutz beschädigter Außengeräte.

**Entscheidungsgate zum Latch:** Wenn OCP-Wiederholversuche heiß werden, auf dem RAW-Abzweig **Latch-off mit definiertem Hardware-Reset nach ACC-OFF→ON** bevorzugen. Haupt-TPS MODE=OPEN erst dann, wenn hardwareseitiger definierter Restart nach bereinigtem Fehler ohne MCU-Hänger/Temperatur-Flattern nachgewiesen wird. Einfach MODE umklemmen würde die REV6-Auto-Recovery-Pflicht ohne Resetvertrag verletzen.

## 4. +85°C Umgebung: kleinstes konkret überprüfbares COTS-Konzept

**VORHANDENE A23-FUNKTION: FAIL** – TPS-Tj-TSD ist keine zuverlässige +85°C-Umgebungsabschaltung. U201 SHDN13 ist offen/enable. Keine nachweislich bestehende Temperatur-Hardware auf TripTracer; altes K101-Relais ist keine Bestückannahme.

**B-Host-Forschungsarchitektur, noch NICHT gezeichnet oder elektrisch freigegeben:** **TI TMP390-Q1**, eine integrierte automotive Temperatur-Schwellwert-IC-Schaltung nahe kritischem Thermikpunkt der tatsächlichen TripTracer-Hauptplatine, statt externer NTC-Leitung. Laut TI-Datenblatt SETA **38,3kΩ / 1% nach GND** = Kanal-A HOT **80°C nominal**, SETB **GND** = **20°C-Hysterese** und deaktivierter Cold-Kanal (nominaler Rückgang ca.60°C). OUTA ist **Open-Drain, aktiv LOW bei HOT**; Pullup z.B. **10kΩ** an gültige Sensor-VDD, 100nF VDD-Abblockung dicht am IC. 1,62–5,5V Sensor-VDD. TI max Schwellengenauigkeit außerhalb0..70°C ±3°C, also nominell höchstmögliche HOT-Schwelle ca.83°C, **2°C Abstand bis85°C ist noch KEINE gesicherte Reserve gegen Leiterplatten-Temperaturgradienten, Gehäuselag und zeitliche Verzögerung**; Ta am richtigen Sensorort und frühere Abschalttemperatur bei Bedarf messen/ändern. Kein voll belastbarer Final-BOM-Zähler vor Host-Auslegung.

**Abschaltlogik auf Host statt MCU-Wunschsignal:** Hardware-RUN_SAFE = (ACC_RUN oder zeitlich begrenzter HOLD) UND SUPPLY_VALID UND TEMP_OK. Ein **dauerhaft versorgter, tatsächlich vorhandener/zu entwickelnder Versorgungsgültigkeits-Wächter** und *definierte Pull-down-/Ansteuerlogik*, welche ohne VDD/Leitungssignal den VIN-Gatepfad sperrt und U201 **SHDN aktiv LOW** hält (SHDN max5,5V, nie direkt Fahrzeug-VIN!), sind erforderlich. **TMP390 OUTA allein direkt an SHDN genügt nicht**: wenn Sensorversorgung ausfällt, wird Open-Drain hochohmig und interner TPS-Pullup aktiviert. Bei gesperrtem Hauptpfad muss die Sensor-/Überwachungshilfsdomäne weiter wirksam bleiben, solange Fahrzeug-BAT verfügbar ist, ohne OFF<1mA zu verletzen. Bei USB-only darf USB nicht BAT/RAW/SHDN unkontrolliert rückspeisen; falls USB-System Wärme erzeugen kann, gehört der Interlock auch in dessen Lastabschaltung.

**Fehlerfälle:** SETA offen/kurz bei **POR** kann nach TI die HOT-Ausgangsleitung LOW festhalten; SETA-/Sensorfehler im laufenden Betrieb sind ohne dokumentierte kontinuierliche Self-Test-Diagnose **nicht** sicher detektierbar. Ein Ausgang OUTA stuck-high/stuck-release ist durch einen einzelnen IC nicht robust erkennbar, unabhängig davon, ob MCU läuft. MCU-Hänger = hardwarezeitbegrenztes HOLD; fehlende Sensor-VDD = V_MON_VALID LOW; Q201 oder Host-MOSFET stuck-on sowie U201-internes Serien-FET-stuck-on jeweils getrennte Einzelfehler: mindestens **zwei verschiedene tatsächlich physische bestehende Abschaltbarrieren** benutzen, sofern geforderte FMEA dies zum Schutz gefährlicher Wärme benötigt, z.B. Host-BAT-Gate und TPS-SHDN; **kein zusätzlicher zweiter Hochvolt-FET als ungeprüfte Pflicht**. Sensor an sinnvollster Hotspot-Position wählen, Temperaturgradienten und Kabel-/USB-Domänen messen. Ein TOT-Ausfall der zweifach vorhandenen Abschaltung bleibt gesonderte FMEA-Bedingung.

**Positionen:** Ein TMP390-IC, 38,3k SETA, 100nF VDD, 10k OUTA, SETB direkt GND; zusätzlich nur die nach **echtem Host-Schaltplan** notwendigen Gültigkeitswächter-/Enable-Gatter. Diese liegen **auf TripTracer-Hauptplatine**, nicht als fiktive Teile in A23 (weiter23). Keine Einmal-Thermosicherung, keine K101-Annahme.

## 5. RAW 0,5A: minimale selektive Absicherung plus Fehlerschutzgrenze

**A23 aktuell FAIL als RAW-Schutz:** VIN_PROTECTED_UNFUSED (U201 OUT) speist sowohl Buck als auch Testpad TP202; **kein eigener RAW0,5A-Limiter, kein qualifizierter Stecker/Leiterbahn-Branch**. Haupt-eFuse ~3A schützt nur gemeinsamen Ausgang auf seiner Schwelle.

**Minimaler Ansatz auf Host/RAW-Port:** **ein separater integrierter High-Side-eFuse/Lastschalter mit einstellbarem Stromlimit** unmittelbar im RAW-Abzweig **nach** dem Haupt-TPS und **vor** dem separaten RAW-Anschluss, mit kurzschlussgeeignetem selbstlimitierendem FET und **hardwaredefiniertem Latch-/Resetpfad**. 0,5A Dauerlast muss unter allen Toleranzen funktionieren; Startzielbeispiel Limit **0,65–0,8A** ist **noch keine freigegebene R_ILIM-BOM**. Strombegrenzung und Abschaltzeit samt Aufbau, Hot-Kupferfläche, Lastinrush und Wiederholungswärme müssen aus echten TI-Min/Max und Messungen abgeleitet werden. TI-TPS2660 ist ein zu prüfender COTS-Kandidat (Stromgrenze 0,1–2,23A), **keine freigegebene Wahl**: recommended bis60V, ABS62V – bei U201-internem FET-SHORT und lokalem Überschwingen nach 58V kann dessen eigener Pin die ABS-Grenze verletzen. TPS2660 hinter U201 OUT darf nicht einfach mit TPS26631-vor-Q201 67V-ABS gleichgesetzt werden. Vorrang: Gate-/Branch-Fehleranalyse, ggf. ein robusterer Baustein oder schützender gesteuerter Host-RAW-Pfad.

**Dauer-Teilkurzschluss unter Limitschwellwert** ist auch mit zweiter eFuse nicht garantiert thermisch harmlos: 0,5A normal und 0,5A fehlbelastet sehen für einen Stromlimiter identisch aus. Maximal zugelassene RAW-Last, Versorgungsspannung, Kabelquerschnitt, Temperatur und zulässige Energie müssen einen sicheren Dauerbetrieb auch bei anormalem Verbraucher ermöglichen; sonst Hardware-Lastzeitbegrenzung oder direkte Lasttemperaturmessung notwendig. Die externe Quell-Sicherung deckt nicht alle 0,5A-Faults ab.

SMD-PPTC wäre nur alternativ/ergänzend nach Beweis von **Vpad inkl. 58V plus Ringing, I_hold@+60°C, I_trip, hot resistance, trip time und Reststrom**, Alterung sowie vollständigem Recovery; ein früher untersuchtes 72V-PPTC mit I_hold ca.0,5A bei60°C und ca.0,44A bei70°C ist keine sicher allgemein passende Lösung. **Nie konventionelle Schmelzsicherung, Halter oder Einmal-Thermosicherung auf TripPower.** Fahrzeugzuleitung ACC/BAT+ nahe Quelle zusätzlich separat fachgerecht absichern; optionaler zugänglicher Host-Gerätesicherungsplatz ist kein Ersatz für Quellkabelschutz.

## 6. Weg Ds 58V-Modell und Messplan: unabhängige Plausibilität

Physikalische Topologie der D-Round11-Analyse **PASS als sinnvolle Fehler-Sensitivitätsstruktur**, nicht als Bauteilqualifikation: M8 ist die 58V-**Geräteeingangsgrenze inklusive HF-Ringing**; die lokale induktive Strecke nach M8 zu EFUSE_IN (U201 IN1–3) darf nicht nochmals dieselbe davorliegende Fahrzeugkabel-L enthalten. Q201 trennt den Eingang EFUSE_IN von IN_SYS6/VIN_FUSED, **C201 liegt direkt an IN_SYS**, C202 plus Buck-CIN erst nach eFuse OUT. Die zwingende Trennung beider TPS-Padspannungen ist korrekt.

D hat **tatsächlich ein lineares Drei-Knoten-Python/SciPy-Modell** mit angenommenem LpostM8=50nH, R=80mΩ, C201eff=0,5µF, Cpre2nF, Vishay-Coss konstant 655pF und ideal konstanter Q201-Leitfähigkeit gerechnet: bei Rise1µs ca. **59,987V** an TPS-IN, bei Rise0,2µs hypothetisch ca. **72,725V** und unplausibel große ~61,44A Spitzenstrom. 14/27 frei gewählte Variationen >60V, 10/27 ≥67V. **Weder reale Fahrzeughäufigkeit, Hardwaremessung noch TI-PSpice**, keine Statistik und kein konkretes Ausfallurteil. Unbekannt: tatsächlich dynamische Quellenimpedanz, C201-Ceff(V,T), ESR/ESL, nichtlineare Coss(VDS,T) (die 655pF sind Vishay Typ bei VDS25V), Gate-Treiber, Q202-Timing, Kontaktparasiten und Stromlimit. 58V am M8 schließt >58V lokal nicht aus. **TPS IN/IN_SYS empfohlen 60V, ABS67V; 67V ist kein erlaubter repetitiver Dauer-/Surge-Sollwert.** Auch DRV, BGATE-gegen-IN_SYS, Q201 VGS, Q202 VDS 50V und LMR-SW/BOOT haben separate Grenzen.

**D-Messplan bestätigt mit B-Ergänzung:** erstes Qualification-DUT ausschließlich an **strom- und energiebegrenztem Laborprüfplatz**, keine Fahrzeuginstallation. Synchrone differenzielle M8-BAT-GND, externe Quelle vor Harness, Q201 D/S/G+VGS/VDS, U201 IN1–3 **und** IN_SYS6, C201 positive/negative Pads, OUT/C202, DRV/BGATE/UVLO/OVP/ILIM/MODE/PGTH/SHDN/PGOOD, LMR VIN/SW/BOOT/PG/5V, RAW und Host 3V3/USB/PWR_FAIL. DC- und schnelle Transientenmessung mit definiertem kalibriertem Probe-Loop/Bandbreite/Strombegrenzung; 10V-Anlauf und -20/+60/+70/+85°C, 32→36V/400ms, 32→58V/350ms und 58→32 Recovery; verschiedene Kabel/Stecker, Last 0/2A+RAW0/0,5A, min/max Ceff, dynamische Q201-Knoten und sichere Dauer-/Teilkurzschlussversuche. Unabhängige Q201-D-S-SHORT und U201-Serien-FET-SHORT, gesperrte Fehlerrückspeisung in USB/BAT/RTC. **Neu für B:** E_retry-Integral und Temperatur pro Wiederholversuch, Hotspot-Leitung bei nominal0,5A-Fehler, MCU-stuck/SHDN-supply-fault und USB-only. Hersteller-SPICE-Modell SLVMD03A wurde von D **nicht ausführbar heruntergeladen**, ist weiterhin OFFEN; keine behauptete ngspice-Inkompatibilität ohne Original-Parserlog.

**Erster Layout-/Laborprototyp bedingt sinnvoll:** post-M8-/Q201-/TPS-Schleife minimal, sehr nahe C201-GND-Low-ESL-Kelvin, breite Kupfer-/Thermal-Pads für Q201/TPS/Buck, DNP-Testpads/optional RC-Snubber **erst nach gemessener Overshoot-Ursache**, keine blind erhöhte Serien-R (0,65Ω bei10V/1,75A ≈1,14V Drop und ~2W), keine beliebig dimensionierte TVS als <60V-Garantie. Abbruch bei nach Unsicherheit nachgewiesenen TPS-Spitzen oberhalb60V als wiederholter REV6-Betriebspunkt, >67V absolut als definitiv unzulässiger Pin-Stress sowie jedem anderen Pin-ABS und Hot-Repeated-Retry. 60V ist Grenze, nicht Ziel. Der D-Laborplan ist eine **gute Ausgangsbasis, keine bereits absolvierte Messung**.

## 7. System-Freigabematrix anhand der tatsächlichen Host-Hierarchie

Der **aktive** Host-Root hardware/kicad/TripTracer_V1.kicad_sch enthält 01_Eingangsschutz / 01I_LM74800_INPUT, 01H_ACC_HOLD_GATE, 01C_HOLD_TIMER sowie 02_5V_Buck, 03_3V3_USB, 07_Speicher_RTC. Er bindet den **isolierten A23-Root aktuell NICHT** ein. Zwei verschiedene Strompfade nicht als integrierte Schaltung oder gemeinsame Serien-BOM deklarieren; ein altes K101-Relais darf nicht vorausgesetzt werden.

| Anforderung | Status | Beleg / konkreter Freigabestopp |
|---|---|---|
| A23 native ERC, Netlist, REF/MPN/BOM | **PASS / SCHEMATIC** | B Run38881195864 KiCad10.0.6, ERC0, 44 Pin-/Netzchecks, 7/7 Widerstandswerte, 23/23 MPN+Footprints, Preisrechnung |
| TI Factory OVP, ≥300k UVLO, MODE/PGTH/ILIM Verdrahtung | **PASS / SCHEMATIC** | U201 OVP8 GND, 330k min324,72k, MODE12/PGTH16 GND, R2046,04k; keine Hardwarefunktion daraus automatisch PASS |
| 32V static OVP-Recovery, 36V OVP | **PASS NUR STATISCH** | 32<32,7V Fallmin; bei36V M8 muss IN_SYS ≥35,4V sein; dynamische Wellenform OFFEN |
| **58V/350ms M8 und ≤60V an allen TPS-IN-Pins** | **OFFEN P0** | Ceff/RLC/Gate/Hersteller-SPICE/Labormessung fehlen |
| **+85°C Ambient Safe OFF, Sensor/MCU/VDD/FET-Faults** | **FAIL vorhanden / P0** | A23 SHDN NC; TMP390+V_MON+Hardwareinterlock auf Host erst zeichnen/prüfen |
| **RAW0,5A selektiver Hard-/Partial-short** | **FAIL vorhanden / P0** | RAW ist gemeinsamer eFuse-OUT; 0,5A-Hülle und selektiver Lastschalter fehlen |
| MODE=GND wiederholter Kurzschluss thermisch sicher | **OFFEN P0** | Strom-/Energie-/Temperaturzyklen bei Hot fehlen; PGTH-Burst-Unterdrückung nur Herstellerlogik |
| 10V-Start und 5V/2A bei +60°C / 70°C Derating | **OFFEN P1** | Buck-Hot/Kalt-, Ceff-/Spulen-/Steckerdrop, Inrush-/PCB-Thermikmessung |
| ACC/RUN/HOLD inklusive Hardware-Timeout/MCU-Hänger | **OFFEN P1** | andere Host-Hochvolt-Topologie, A23 noch nicht integriert |
| PWR_FAIL, FRAM-first, SD-close nach ACC-OFF | **OFFEN P1** | Buck PG→Q501 vorhanden, aber MCU/FRAM-/SD-Timing/Host-Pullup/M8-Hartabriss prüfen |
| M8/GND-Abriss | **OFFEN P1** | 0µs garantierte Vorwarnzeit; RTC-Zelle keine ungerechtfertigte SD-Flush-Versorgung |
| USB-only, BAT-/RTC-/RAW-Backfeed | **OFFEN P0/P1** | reale zusammenhängende Host-Netzliste, USB-/BAT-/ACC-Einzelfehler- und Rückstromtests |
| BAT-OFF <1mA, Ziel0,5mA | **OFFEN P1** | gesamtes Fahrzeug-Gate-/HOLD-/Sensor-/Temperatur-/USB-Iq messen |
| Externe Fahrzeugleitungssicherung BAT+/ACC | **PASS Regel / Installation OFFEN P0** | quellnah, DC-Interrupt/Cable/Ampacity nachweisen; keine fuse/holder/one-shot auf TripPower |
| A23 PCB / DRC / qualifizierte mechanische Footprints | **OFFEN** | kein qualifiziertes A23-Layout vorhanden; grüne ERC ist kein DRC |
| Serien-, Fahrzeug-, ISO-/58V-Hardwarefreigabe | **FAIL / nicht erteilt** | P0- und P1-Gates nicht geschlossen |

### Priorisierte nächsten technisch kleinen Freigabeschritte

1. **P0 58V:** D-Pad-/M8-Test mit getrennten EFUSE_IN und IN_SYS, Quellen-R/L und Messunsicherheit; nur gezielte parasitäre Layout-/Dämpfungskorrektur nach Messung. Nicht sofort auf LTC4368 oder doppelte TVS ausweichen.
2. **P0 +85°C:** ein tatsächlich schaltbarer Host-A23-Interlock um TMP390-Q1 (80°C), VDD_valid und fail-OFF-Enabler in die aktive Host-Hierarchie zeichnen, MCU-Hänger, offen/kurz/UVDS, USB-only und stuck-on-MOSFET unabhängig testen. Eine Sensorposition reicht nur bei belegtem Thermikprofil.
3. **P0 RAW:** 0,5A-continuous plus definierter, Toleranz-sicherer selektiver Hochseiten-Stromlimiter mit hardwareseitigem Latch-Reset; externe 0,5A-Teilkurzschluss-Lasttemperatur/Leitungshülle und eFuse-internal-short-Fault qualifizieren.
4. **P0 Wiederhol-Overcurrent:** Ecycle/Pmean/Tj/Trace/Kabel über viele Zyklen; bei unsicherem Zyklus Latch-Reset für RAW bzw. Haupt-eFuse überprüfen, nie unkontrollierte Restart-Schleifen freigeben.
5. **P1 Host/USB/Data:** eine einzige echte Host-A23-Wurzel, dann native ERC/Net/BOM/PCB-DRC, USB- und Knopfzellen-/FRAM-Backfeed, PWR_FAIL/FRAM/SD, Start +60°C, OFF-Iq und externe Fahrzeug-F_MAIN-Harnessprüfung.

**Belegklassen:** (1) **Native KiCad 10** – jetzt B-seitig tatsächlich ausgeführt und PASS für A23-Schema; (2) **Original-TI-Min/Max und Rechenformeln** – qualifizieren nur statische Parameter oder Sensitivitäten; (3) **D-SciPy-Modell** – tatsächlich gerechnet, aber bewusst hypothetisch und kein TI-SPICE; (4) **Reale Hardwaremessung** – für kritische 58V-/Thermik-/RAW-/Systemfälle **NICHT DURCHGEFÜHRT**. **Keine PCB-/Fertigungs-/Fahrzeugfreigabe.**
