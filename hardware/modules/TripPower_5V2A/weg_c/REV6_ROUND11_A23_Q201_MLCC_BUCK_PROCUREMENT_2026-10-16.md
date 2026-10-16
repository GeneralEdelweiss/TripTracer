# TripPower Weg C — Round 11: reale A23-BOM, Q201-Qualifikation, MLCC-/Buck-Beschaffung (2026-10-16)

**Arbeitsbranch:** `design/trippower-c` — **Entscheidung:** A23 in der realen Form beibehalten; Toshiba-Q201 = **NOCH ZU TESTEN**, keine Freigabe; nur exakte bestehende MPNs über den belegten günstigeren Distributor einkaufen. **NO FAB / NO VEHICLE / NO 58-V-QUALIFIKATION.** Dieser Bericht ändert keine KiCad-Leistungsschaltung und erzeugt keine A23-Kopie.

## 0. Nachvollziehbare Eingangsquellen und Grenzen

- Das aktuelle `AGENTS.md` dieses Branches und die verbindliche REV6-V1-Spezifikation `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, `docs/HARDWARE_REQUIREMENTS.md` PWR-44–56, `docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md` wurden direkt gelesen. Verbindlich: 10–32 V Dauer; >32 bis spätestens 36 V OFF, 36 V/400 ms, zentral begrenzte 58 V/350 ms **am M8**, 5 V/2 A bis Ta+60 °C, Ta+85 °C sicher OFF, RAW0,5 A als Entwicklungsziel, BAT-OFF <1 mA, FRAM-first/SD-Recovery und externe quellnahe Zuleitungssicherungen.
- Weg A `design/trippower-a` A23 bei Commit **`f30f35d404e6ba549ee6202c46d660f498c36545`**: tatsächliches `hardware/modules/TripPower_REV6_A/TripPower_REV6_A_FACTORY_OVP.kicad_pro`, eingebundene Blätter `01_TPS26631_REV6_FACTORY_OVP.kicad_sch` und `02_5V_LMR38020_FACTORY_OVP.kicad_sch`, echte `REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv` (Git-Blob **`ea8cf61eef9f18f5585581a9a9ea67abb47951c8`**), A Round5 `REV6_A_ROUND5_MODE_PGTH_A23_HOST_GATE_2026-10-16.md`. **A25 und alte hypothetische A23-Kosten sind keine aktuelle Quelle.**
- Weg D `design/trippower-d-load-dump`: `WEG_D_ROUND11_A23_AFTER_M8_SPICE_BLOCKER_LAB_PLAN_2026-10-16.md`; Weg B `design/trippower-b`: `WEG_B_ROUND10_TI_300K_FACTORY_OVP_UVLO_INDEPENDENT_DECISION_2026-10-16.md` (B hatte damals nur älteres natives A25 untersucht); Weg C eigener Round10 `REV6_ROUND10_A_COMPONENTS_COST_OPTIMIZATION_2026-10-16.md`. Widersprüche werden nach **neuer tatsächlich gezeichneter A23-Schaltung** aufgelöst.
- Die 23 Beschaffungspreise sind die von A übernommene aktuelle **Quotierungs-/Index-Momentaufnahme**, nicht 23/23 live bestätigter Lagerbestand. Neu gegengeprüfte Einzelangebote unten sind als solche bezeichnet. Kein angeblicher Hersteller-Ceff-Wert ohne Kurve, keine erfundene Fertigungskostenquote.

## 1. Die tatsächlich gezeichnete A23-BOM — alle bestückten 23 Referenzpositionen

| Ref | Menge | tatsächliche Hersteller-MPN | € netto/Ref 1 / 10 / 100 (A-Snapshot) |
|---|---:|---|---:|
| U201 | 1 | TI TPS26631PWPR | 3,890 / 2,960 / 2,460 |
| Q201 | 1 | Vishay SQM100N10-10_GE3 | 3,780 / 2,490 / 1,750 |
| Q202 | 1 | onsemi BSS138LT1G | 0,292 / 0,129 / 0,113 |
| R201 | 1 | Yageo AC1206FR-07330KL | 0,086 / 0,026 / 0,016 |
| R204 | 1 | Vishay CRCW12066K04FKEAHP | 0,250 / 0,133 / 0,0807 |
| C201,C202 | je 1 | KEMET C1210C105K1RACAUTO | je 0,585 / 0,391 / 0,267 |
| C203 | 1 | KEMET C1206C104K1RACAUTO | 0,250 / 0,141 / 0,0902 |
| U101 | 1 | TI LMR38020SQDDARQ1 | 3,920 / 2,980 / 2,490 |
| L101 | 1 | Bourns SRP7050TA-150M | 0,980 / 0,809 / 0,6648 |
| C102,C107 | je 1 | KEMET C1206C104K1RACTU | je 0,290 / 0,170 / 0,1088 |
| R101,R501 | je 1 | Yageo RC1206FR-07100KL | je 0,086 / 0,022 / 0,015 |
| R102 | 1 | Yageo RC1206FR-0724K9L | 0,086 / 0,022 / 0,015 |
| R103 | 1 | Yageo RC1206FR-0764K9L | 0,086 / 0,024 / 0,015 |
| C101,C108 | je 1 | KYOCERA AVX 12101C475K4Z2A | je 0,860 / 0,547 / 0,3876 |
| C104,C105,C106 | je 1 | Taiyo Yuden MCAST32MSB7226KPNA01 | je 0,843 / 0,445 / 0,405 |
| R502 | 1 | Yageo RC1206FR-071ML | 0,086 / 0,022 / 0,015 |
| Q501 | 1 | onsemi BVSS123LT1G | 0,380 / 0,230 / 0,1451 |
| **23 tatsächliche Ref-Positionen** | **23 Bauteile** | **alle obigen Zeilen** | **20,2570 / 13,5610 / 10,6266** |

Die Liste umfasst sämtliche **23** einzelnen Refdes, obwohl gleiche MPNs tabellarisch gruppiert sind. Die berechneten Summen sind Stückpreise **pro Modul bei einer Bestellung von 1/10/100 Modulen**, nicht der gesamte Auftragspreis; Gesamtwarenwert 20,2570 / 135,6100 / 1.062,6600 € netto. Noch **kein fertig angeschlossenes TripPower-System**. A23 besitzt laut A Round5 KiCad10-ERC/Netlist-Regressionen auf A; deren grüne Syntaxprüfung ist keine elektrische/thermische Freigabe und dieser C-Branch führt keinen eigenen nativen A23-ERC aus.

## 2. Q201 Toshiba TK11S10N1L,LQ versus Vishay SQM100N10-10_GE3 — **NOCH ZU TESTEN**

| Originaldatenblatt-Eigenschaft | Bisher Vishay | Toshiba-Kandidat | Aussage |
|---|---|---|---|
| VDS / Gate VGS absolut | 100 V / ±20 V | 100 V / ±20 V | Keine höhere nominelle 58-V-Spannungsreserve |
| RDS(on) max bei 10 V | 10,5 mΩ | 28 mΩ | Toshiba max **2,67×** höher; Gate-Hub beweisen |
| RDS(on) max bei 4,5 V | 12 mΩ | 50 mΩ | Toshiba max **4,17×** höher |
| Gate Qg typisch | 122 nC (andere Prüfumgebung) | 15 nC (VDD80 V, ID11 A) | Kein fairer direkter Timing-/Stromvergleich ohne gleiche Prüfbedingungen |
| Coss typisch | 655 pF **bei VDS25 V** | 370 pF **bei VDS10 V** | **Nicht Coss(58 V)**; nichtlinear und Gatezustands-abhängig; Round11-D-Annahmen können nicht ersetzt werden |
| Junction-to-case RthJC max | ~0,4 K/W | ~2,3 K/W | Toshiba 5,75× höher, aber PCB-/Pad-Gesamttemperatur dominiert bei kleiner Last |
| AEC / Gehäuse | AEC-Q101, TO-263/D2PAK | AEC-Q101, TO-252/DPAK+ | Andere Landpattern/Kühlfläche; **kein Footprint-Drop-in** |
| Zusätzliche kritische Bedingung | VGS ±20 V | **V(BR)DSX nur MIN65 V bei VGS=−20 V, ID=10mA** | Nicht normaler VGS=0V-VDS100V-Fall; bei Gate-Ringing/negativem VGS gesonderter STOP-Gate |

**Offizielle Originalquellen:** [Vishay SQM100N10 Datenblatt](https://www.vishay.com/docs/67027/sqm100n1.pdf), [Toshiba TK11S10N1L Originaldatenblatt, Rev4 (2026)](https://toshiba.semicon-storage.com/info/TK11S10N1L_datasheet_en_20200624.pdf?did=30155&prodName=TK11S10N1L), [Toshiba Herstellerprodukt](https://toshiba.semicon-storage.com/us/semiconductor/product/mosfets/12v-300v-mosfets/detail.TK11S10N1L.html). Qg, EAS und Coss nicht als gleichwertige Vergleichsmessungen verkaufen: Teststrom, VDS und VGS verschieden; EAS nur für konkrete Single-Pulse-Testbedingungen. Weder 100-V-Aufdruck noch AEC-Q101 liefert einen vollständigen wiederholten Reverse-SOA-Nachweis bei −20/+60/+85°C.

**Wärmeprüfung als nachvollziehbares Vor-Screening, noch kein PCB-Test:** Bei der als **Annahme** verwendeten kombinierten 10-V-Last 5V·2A / η80% + RAW0,5A ≈ **1,75 A** durch Q201 gilt rein ohmsch P=I²·RDS(on). Vishay max bei angegebenem Gate-/Prüfpunkt ≈0,032 W (10 V), 0,037 W (4,5 V); Toshiba ≈0,086 W (10 V), 0,153 W (4,5 V). Bei beispielhaften 3 A: Vishay ≈0,095/0,108 W, Toshiba ≈0,252/0,450 W. **Diese Datenblatt-RDS-Werte sind kein +60°C-MAX-RDS-Nachweis**: RDS(on) steigt mit heißem Silizium; gemessene Gate-Höhe, Umgebung, Verlustwärme anderer Bauteile, Pad-Kupfer und Derating fehlen. Großes Vishay-Tab ist mechanisch/thermisch günstiger; Toshiba kann unter realer VIN10-Ripple-/Gatebedingung heißer sein. 65-W- und 375-W-PD sind Case-25°C-Grenzfälle und dürfen keinesfalls als 60°C-Board-Reserve interpretiert werden.

**Gate/58-V-Pfad:** Im echten A23: TPS26631 IN1–3 liegt an `EFUSE_IN` **vor** Q201, IN_SYS6 an `VIN_FUSED` **hinter** Q201; Drain von Q201 an EFUSE_IN, Source an VIN_FUSED, Gate an `R6_B_GATE`, Q202 onsemi BSS138LT1G an TPS DRV/BGATE-Steuerung. C201 liegt an VIN_FUSED, **C202 erst nach eFuse OUT**. Weg D modelliert bei post-M8 L=50nH/R=80mΩ und hypothetischem C201eff=0,5µF plus konstant eingeschaltetem Vishay-Q201/RDS=20mΩ **59,987 V @1µs** oder **72,725 V @0,2µs** an IN-Pins; 14/27 selbst gewählte Szenarien >60V und 10/27 ≥67V. **Kein Hersteller-SPICE, keine reale Ausfallwahrscheinlichkeit!** Weder Toshiba-niedrigeres Qg noch die nicht vergleichbare Coss-Angabe garantiert weniger Gate-/LC-Überschwingen. Q202 ist selbst nur 50V-VDS-klassifiziert und braucht Gate-Pin- und Reverse-Fault-Probe.

**Einzelfehler-/SOA-Abgleich erforderlich:** Q201 bei 58V-OVP-Rampe, beim OVP-Öffnen und Restart; Q201 D-S-SHORT (verlorene Reverse-Sperre), Gate OPEN/GND/-Transienten, Q202 OPEN/SHORT, U201-interner FET SHORT getrennt; -Batteriepolung und Rückstrom von OUT/Buck/USB, heißer eFuse-RAW-Hardshort/Auto-Retry, Avalanche nur innerhalb korrekter Herstellerkurven. Vor und nach Q201 synchron messen: VDS, VGS, I_Q, EFUSE_IN, VIN_FUSED, DRV/BGATE und U201-Pinlimits, mit D-Round11 nach-M8-R/L/C und realer 58-V-M8-Flanke. 58-V-Lastabwurf plus Gate-Schwingung darf nicht unkontrolliert an seriennaher Quelle geprüft werden: strom-/energiebegrenzte Laborfixture. **Ohne Coss(V,T), realen TPS-Gate-Verlauf und Q201/VGS-Fault-Test kein Ersatz.**

**Footprint:** Vishay `Package_TO_SOT_SMD:TO-263-3_TabPin2` ist bereits im A23. Toshiba verlangt eigenes **Hersteller-TO-252/DPAK+-Landpattern**, verifizierte Pin1=G, Pin2/Tab=D, Pin3=S und die reale Richtung des Bodydiode-Reverse-Pfads; Netzliste und optische PCB-Padprüfung durch Weg A. Tab-Leiterbahn/ESD/Kupferkühlfläche inklusive +60°C-Messung neu auslegen; gleicher 100-V-MPN ist kein Ersatz ohne Re-Layout.

**Preis/Lieferstatus (EUR netto, Lieferstand nur Abfrage-/Indexmoment, keine Beschaffungszusage):** Vishay original A-Snapshot 3,78 / 2,49 / 1,75; [DigiKey DE gleiches MPN](https://www.digikey.de/de/products/detail/vishay-siliconix/SQM100N10-10-GE3/8556397) **3,7600 /2,4720 /1,7404**, online **3.198** Stück; [DigiKey Toshiba TK11S10N1L,LQ](https://www.digikey.it/de/products/detail/toshiba-semiconductor-and-storage/TK11S10N1L-LQ/12758189) **1,2200 /0,7670 /0,5074**, publizierter Bestand rund **7.713** Stück (Stand/Region/Staffel vor Einkauf erneut prüfen). Daraus Toshiba-Ersparnis gegenüber A-Original **2,560 /1,723 /1,2426 €** pro Modul (1/10/100). Alternative C-Round10-Mouser-EUR-Quote 1,22 /0,574 /0,510 ist *nicht* als aktueller bestätigter deutscher Direktkauf gleichzusetzen; Lieferland/Verpackung/Bestand separat prüfen. **Empfehlung heute: VISHAY BEHALTEN.**

## 3. MLCC Ceff, ESR, ESL: belegbare Daten versus offene Werte

| A23-Position / MPN | Herstellerbelegt | **Nicht belastbar belegt** und Konsequenz |
|---|---|---|
| C201/C202 KEMET **C1210C105K1RACAUTO** | 1210, 1µF nominal, 100V, X7R, Automotive/AEC-Serie; [Original-Bauteildokument](https://search.kemet.com/component-documentation/download/specsheet/C1210C105K1RACAUTO), [KEMET KSIM](https://ksim3.kemet.com/capacitor-simulation) | Kein dokumentierter Original-Ceff(32/58V,−20/+60/+85°C,Alterung/Los), **keine numerische ESR(f,V,T)/ESL samt Montage**, keine belastbare im Szenario eingesetzte 0,5µF-Zahl. C201 auf VIN_FUSED nach Q201; C202 auf eFuse OUT, kein zuschaltbarer Input-Puffer bei OFF. **Beide behalten.** |
| C101/C108 KYOCERA AVX **12101C475K4Z2A** | 1210 4,7µF ±10% 100V X7R **FLEXITERM/Soft-Termination**, AEC-Q200; [DigiKey Original-MPN](https://www.digikey.de/de/products/detail/kyocera-avx/12101C475K4Z2A/9748485) und [Hersteller-Spice-/Bauteilsuche SpiCat](https://spicat.kyocera-avx.com/) | Kein überprüfbares MPN-spezifisches Ceff(32/58V) und ESR/ESL(f,T,V), Buck-U101 liegt hinter eFuse; Bias im normalen 10–32V-Betrieb und U201-SHORT-Fault unterscheiden. **FLEXITERM behalten.** |
| C104–C106 Taiyo Yuden **MCAST32MSB7226KPNA01** | 3×22µF/25V X7R, 1210, AEC-Q200; [TY-SPYCE für genaue MPN](https://spyce.yuden.co.jp/TYSPYCE/or/C/spyce.html?productNo=MCAST32MSB7226KPNA01) | Kein bestätigtes Ceff(5V,+60°C,Lebensalter), ESR(f,T), ESL(montiert) oder Kapazitätsreserve für Loop/5V2A-Lastsprung. **3 Stück behalten.** |

**Physik:** 100-V-Nennspannung ist die dielektrische Spannungsgrenze, **kein** garantierter 58-V-Ceff-Wert. X7R kann unter Bias weit weniger als nominal liefern; Temperaturkoeffizient, ±10%-Anfangstoleranz und logarithmisches Altern separat kombinieren. Der interessierende **differenzielle Ceff=dQ/dV**, ESR(f) und ESL einschließlich Leiterbahnen müssen am tatsächlichen DC-Bias und über mindestens 0,1–100MHz für Gate/Ringing separat bestimmt werden; nicht unkritisch Nenndaten, eine beliebige Dritt-MPN-Kurve oder Hersteller-typische Diagrammablesung als garantierte MIN-Werte deklarieren. In einem nichtlinearen C(V) hängt die Energie von ∫V·C(V)dV ab; statische 1µF-BOM-Werte allein erlauben **keine Verringerung von C201/C202**.

**Reproduzierbarer Nachweisplan:** KEMET K-SIM3, KYOCERA AVX SpiCat und TY-SPYCE nach den **exakten** MPN filtern; Rohdatei/Exportdatum/Toolversion, Messspannung 0/10/24/32/36/58/60V (nur innerhalb MPN-Rating), Temperatur −20/+25/+60/+85°C, Frequenz, Bias-Bedingung, ESR/ESL, DC-Bias- und Alterungsfaktor und Modell-Zuordnungs-IDs als CSV plus Prüf-Hash in Weg C protokollieren. Falls Tool nur nicht numerisch/ohne Daten: Status offen; am bestückten Board mit Bias-fähiger Impedanzanalyse/VNA und unterschiedlichen Losen messen. Für C201 **Ceff an VIN_FUSED**, prä/post-M8-Leitungsinduktivität und Coss(VDS,T) gemeinsam als D-Round11-Modellparameter erfassen. Nach Bauteilfreigabe D-Sweep und reales Scope vergleichen.

**Alternative:** KYOCERA AVX `KAM32LR72A475KU` (standard termination, 4,7µF/100V/1210/AEC) wäre in C-Round10 rechnerisch je **0,783 /0,495 /0,349€** statt **0,860 /0,547 /0,3876€**; für zwei Stück **0,154 /0,104 /0,0772€** gespart. Sie verliert die konkret vorhandene FLEXITERM-Crack-Reserve und besitzt **noch keinen nachgewiesenen gleichwertigen Ceff/ESL- und Vibrations-/Boardflex-Nachweis**, daher **NICHT ERSETZEN**, keine reale Einsparung freigeben. Keine unqualifizierte 63-V-Keramik an 58-V-Eingang, keine Verringerung durch Parallel-Schätzwerte.

## 4. Buck LMR38020-Q1: wirtschaftlich nur identische MPN umbeschaffen

- TI [LMR38020-Q1 Originaldatenblatt](https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf): Automotive 80-V-VIN/2-A-Sync-Buck. A23: U101 LMR38020SQDDARQ1, 400kHz über R103 64,9k; L101 15µH Bourns; C101/C108 2×4,7µF/100V und C107 100nF HF; C102 100nF BOOT; R101 100k / R102 24,9k FB → bei nominal1,000V Referenz ideal 5,016V; C104–C106 **3×22µF/25V** am 5V-Ausgang; R501/R502/Q501 zur Fail-HIGH Statusumsetzung. Referenzprinzip 15µH/3×22µF passt zur TI-400kHz-Anwendung, aber regulatorischer Loop, Ripple, Ceff und LMR-Package-Thermik sind **nicht** ohne Labor-/EVM-Vergleich freigegeben.
- [Bourns Original SRP7050TA](https://bourns.com/docs/product-datasheets/srp7050ta.pdf): **15µH ±20%, DCR 81mΩ typisch/92mΩ max, Irms3,5A (40K Temperaturhub nach Bourns-Definition), Isat6A (−20%-L-Bedingung), AEC-Q200, Gehäuse ca7,3×6,6×5,0mm**. Ideal-L-Ripple bei nominal L15µH/400kHz/5Vout etwa0,417App@VIN10V und0,703App@VIN32V; L-Spitzenstrom bei 2A ~2,35A, bevor Toleranz/Temperatur eingehen. DCR bei 2A maximal 0,368W @Datenblatt-Referenzbedingung, **nicht** inklusive DCR-Anstieg bei +60°C, Kupfer-/Kernverluste oder Verlustspitzen. +60°C-PowerPad/Spule bei 5V2A/RAW0,5A thermografisch und über Temperaturfühler/Scope messen.
- [DigiKey DE exakt gleicher SRP7050TA-150M](https://www.digikey.de/en/products/detail/bourns-inc/SRP7050TA-150M/5429680): 0,9500/0,7830/0,6435 statt A-Quote 0,9800/0,8090/0,6648€; bei Abfrage lagernd (~4.638 Stück). **Klein, aber reeller Beschaffungsvorteil 0,0300/0,0260/0,0213 € ohne elektrischen und Footprint-Eingriff.**
- Alternativer Buck-L101/andere 22µF: **NICHT EMPFOHLEN ohne min-Isat@+60, DCR@Hot, Kernverlust, AEC-Qualifikation, Landpattern, Ceff(5V), Lastsprung und Loop-/EMV-Abgleich**. Der hohe Handbestückungsaufwand liegt eher an großen 1210/1206-Stückpositionen, PowerPad des eFuse/Buck, Kühlflächen und Spule als an einem um Cent günstigeren Induktor. Nutzer fertigt Schablone: Pastenauftrag erleichtert, aber mechanische Positionierung, Vakuum-/Hotair-/Heizplatte und Sichtkontrolle/Heatsink der Thermal Pads bleiben kritisch. **Kein vermeintliches Entfernen von BOOT, HF, Feedback, RT oder einem 22µF ohne belastbare Reserve.**

## 5. Round11-Kostenmatrix — EUR netto **pro komplett mit 23/24 A23-Funktionsteilen bestücktem Modul**, ohne Systemzusätze

| Variante / Quotenbasis | Bestückpositionen | €1 | €10 | €100 | Status |
|---|---:|---:|---:|---:|---:|
| **A23 tatsächlich gezeichnet**, A-Order-CSV | **23** | **20,2570** | **13,5610** | **10,6266** | Echtes KiCad A23, Kosten-Snapshot, keine Hardwarefreigabe |
| A23 Vishay + Bourns **identische MPNs** billiger bei DigiKey | 23 | **20,2070** | **13,5170** | **10,5957** | **EMPFOHLEN** bei Bestands-/Versandcheck, unveränderte Technik |
| A23 mit Toshiba-Q201 statt Vishay (DigiKey) | 23 | **17,6970** | **11,8380** | **9,3840** | **NOCH ZU TESTEN**, Gehäuse/Gate/SOA |
| Toshiba-Q201 + identische Bourns-Quelle | 23 | **17,6670** | **11,8120** | **9,3627** | **NOCH ZU TESTEN** (nur Bourns-Quelle bereits umsetzbar) |
| Toshiba+Bourns+2× standard-KAM-C101/C108 | 23 | **17,5130** | **11,7080** | **9,2855** | **NICHT FREIGEBEN**: Gate- und Ceff/FLEXITERM-Fragen |
| A24 UVLO-Versuchsvariante + 68k (A-Round5-Preis) | **24** | **20,3430** | **13,5830** | **10,6416** | **NICHT UMSETZEN**, kein belegter Bedarf |

**Methodik:** Bestehende A23-Zeilen pro Ref und Staffel übernommen; nur ausdrücklich dokumentierte Ref-/Preis-Overrides. Konkrete DigiKey-Recherche Vishay/Bourns/Toshiba; Toshiba+KAM- und A24-Zeilen sind **Modellkonfigurationen**, keine Bestellfreigabe. Preise dürfen bei unterschiedlichen Distributoren nicht ohne Versand, Verpackungs-/Mindermengen, Reel-Service, aktuelle Steuer-/Währungseinstellung und tatsächliche Bestandsmengen in eine finale Bestellung übernommen werden. Vom günstigsten **freigegebenen** Kaufpfad gegenüber A-Basis sind lediglich **0,0500 /0,0440 /0,0309 € pro Modul** direkt belegt, nicht die hypothetischen Toshiba-Euro. Über 100 Stück können einzelne MPNs, insbesondere TPS26631PWPR (Mouser-Snapshot rund57 Stück), die Bestellung zeitlich blockieren. Keine 23/23 verfügbare Direkt-100er-Bestückung behaupten.

### System-/Gesamtkostengrenze (streng separat, Preis **offen**)

| Ebene | Ist-Bestand / offene Funktion | Stückzahl / Preisstatus |
|---|---|---|
| **Nur TripPower A23** | genau 23 vorhandene Bestückpositionen, kein on-board F_MAIN | beziffert oben |
| **RAW0,5A selektiver Schutz** | A23-Testpad/RAW-Verbindungsnetze ohne geprüften 0,5A-Branch-Limiter | **fehlende System-Hardware, MPN/Position/€ offen**; Platzierung nach realer Branch-Grenze |
| **+85°C Ambient sicher OFF** | TPS interne Tj-TSD ist keine Ambient-Schaltung; offene SHDN-Leitung bedeutet beim TPS default EIN | **Hardware-default-OFF-Pfad/Sensor/Interlock erforderlich, MPN/€ offen** |
| **Verbinder/M8 und TripPower↔TripTracer** | konkrete Stecker, M8-Kontaktpins, Kupfer- und Montagefläche, RAW/PGOD/3V3-Eingang | **nicht in A23 BOM; Preis offen** |
| **TripTracer Hauptplatine/Host** | USB-Powermux, ACC/HOLD, FRAM/SD/RTC, Hauptboard, ggf. zugänglicher Gerätesicherungshalter, keine A23-Einbindung in aktive Host-Hierarchie nachgewiesen | **separate BOM; keine zusätzliche A23-Preisaddition ohne konkrete Ref/Angebot** |
| **Fahrzeugzuleitung** | **quellnah externe BAT- und ACC-Leitungssicherung(en)** mit DC-Ausschaltwert, Haltern/Kabel/Steckern und 58-V-Fault-Eignung | **externer Harness, keine TripPower-Position; Preis offen** |
| **Fertigung** | PCB 2/4 Lagen, Gerber, Kupfer-/Thermikfläche, Stencil, Reflow/Handbestückung, Sichtprüfung, Testfixture, Nacharbeit, Verschnitt, EMV/Labortests | **kein Herstellerangebot: € offen**, keine künstliche Vollkosten-Summe |

**Konsequenz:** Ein endgültiger vollständiger Geräte-/Systemstückpreis ist aktuell **nicht seriös bezifferbar**, selbst wenn die 23 gezeichneten TripPower-Positionen vollständig quotiert sind. 0 Schmelzsicherungen/Halter/Einmal-Thermosicherungen auf TripPower. Eine SMD-PPTC nur optional, falls für realen 58-V-Padstress, Hot-Ihold, Fehlerstrom, Retry und Reset tatsächlich geeignet; keine zusätzliche Sicherheits-Gadget-BOM ohne echten Nutzen.

## 6. Konkrete Übergabe an Weg A — nur nachweisbare Einsparungen

1. **JETZT UMSETZBAR (HERSTELLER-GLEICHE TEILE):** A23-Schaltung unverändert behalten. Für Q201 exakt Vishay SQM100N10-10_GE3 und L101 exakt Bourns SRP7050TA-150M DigiKey-DE-Staffel gegen Bestands- und Versandkosten neu abfragen. EUR/Ref-Vorteile 0,0200/0,0180/0,0096 sowie 0,0300/0,0260/0,0213. Bei Mehrhändler-Versand kann Vorteil wegfallen.
2. **NOCH ZU TESTEN:** optionales Toshiba-Q201-**Testlos** mit herstellerkonformem TO-252/DPAK+-Footprint, korrekter Drain/Source/Bodydiode, Wärmebild bei 10V 5V2A+RAW0,5A Ta+60°C, -20C/32V/58V, VGS-Differenz-Probe, Gate-/Coss(V,T), Rückstrom/Reverse-SOA und D-Labormatrix. Vor diesen Ergebnissen kein serienwirksamer KiCad-/BOM-Wechsel.
3. **NICHT ERSETZEN:** KEMET C201/C202, AVX FLEXITERM C101/C108, Taiyo 3×22µF, Bootstrap/HF/FB/RT und L101-MPN. Kein KAM-Standard-Termination-Swap ohne Gleichwertigkeit bezüglich Boardflex/AEC/Ceff; keine Kondensatorreduktion aufgrund nominal aufgedruckter µF.
4. **A24 UVLO 68k:** nur wenn A/B ein spezifisch gemessenes Flatter-/Brownout-Problem bei stabilem 10V-Start oder mit realer Host-Freigabe nachweisen. TI werkseitige OVP (33,2–35,4 rising; 32,7–35,0 falling) + R201330k hat bereits 0,7V statische 32-V-Recovery-Marge am IN_SYS-Pad; muss dynamisch mit Ripple <32,7V gemessen werden. Mit MODE=GND Auto-Retry nach Kurzschluss/Temperatur und PGTH=GND dauerhaft TPS-eigenes PGOOD LOW (damit kein 2×IOL-Pulsmodus) Fehlerenergie/Inrush testen; kein reiner A24-Preiszuwachs als Verbesserung.
5. **P0 VOR BESTÜCK-/FAHRZEUGFREIGABE:** D-Round11 58V Scope an M8, TPS-IN/IN_SYS, VGS/VDS/DRV/Q202, Vin/U101; Ceff/ESR/ESL und post-M8 L/R gemessen, echte +60°C Volllast, +85°C fail-safe ambient OFF und separater RAW0,5A Fehlerpfad, externe Zuleitungssicherungen und USB/ACC/FRAM-Powerbackfeed und saubere Host-Integration. Keine vollständige A23-Kopie auf C.

## 7. Reproduzierbarkeit / neuer Weg-C-CI (eingeschränkter Beweis)

- Neue Berechnung `hardware/modules/TripPower_5V2A/weg_c/rev6_round11_a23_cost_audit.py`; erwartet explizit **A23-CSV-Blob `ea8cf...`**, MPN-Menge und 23 Refdes, keine F_MAIN-Position und prüft alle 1/10/100-Quoten mit `decimal.Decimal`. Sie exportiert sechs mit Freigabestatus gekennzeichnete Kostenszenarien. Optional werden in beiden KiCad-Blättern die 23 bestückten **Refdes im Quelltext** gefunden; **keine echte Netzliste/Pin-ERC**.
- Neue `.github/workflows/trippower-c-rev6-round11-a23-procurement.yml`: Checkout C für Prüfer, **getrennter read-only Checkout A bei Commit `f30f35d...`** via GitHub Actions, quellengepinntes Cost-Audit und CI-Artefakt `round11-a23-cost-audit.csv`. Änderungen auf A machen die Quelle nicht heimlich anders; A muss bei neuer Revision für den nächsten Bericht neu gepinnt werden. Native A-KiCad ERC/Netlist/PCB-DRC und vollständiger echter Lager-/Preis-API-Check sind **nicht Bestandteil dieses CI**.
- Reproduktion: im Repo-Root `python3 hardware/modules/TripPower_5V2A/weg_c/rev6_round11_a23_cost_audit.py --bom a23-source/hardware/modules/TripPower_REV6_A/REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv --protection a23-source/hardware/modules/TripPower_REV6_A/01_TPS26631_REV6_FACTORY_OVP.kicad_sch --buck a23-source/hardware/modules/TripPower_REV6_A/02_5V_LMR38020_FACTORY_OVP.kicad_sch --output round11-a23-cost-audit.csv`, wobei `a23-source/` dem oben genannten A-Commit entsprechen muss.
- **CI-Lauf/Job/Logstatus bitte nach diesem Commit separat anhand tatsächlicher GitHub-Actions-ID prüfen.** Solange nicht nachgesehen: NICHT als erfolgreichen Lauf ausgeben. Ein grüner BOM-Audit beweist weder Original-Hersteller-SPICE noch 58-V- und Thermal-PASS, noch vollständige Einkaufslieferbarkeit.

**Abschluss Round11:** Derzeit **nur gleiche MPN günstiger kaufen**, **Toshiba nicht einsetzen**, MLCC/Induktor unverändert. Führender A23-Prototyp bleibt **NO FAB / NO VEHICLE**, bis konkrete elektrische und thermische Stop-Gates geschlossen sind.
