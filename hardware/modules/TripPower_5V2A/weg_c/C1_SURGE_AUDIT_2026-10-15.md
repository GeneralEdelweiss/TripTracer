# TripPower Weg C — Hersteller-Pin-Audit, 200 V/350 ms, 9 V und Thermik (15.10.2026)

**ENTSCHEID: C1 derzeit NO-GO FUER FERTIGUNG/FAHRZEUGBETRIEB.** Das integrierte COTS-Grundprinzip bleibt interessant; C1 wie verdrahtet ist nicht bewiesen und war bis zur Korrektur von U2 Pin 13 unmittelbar ausserhalb der absoluten Herstellergrenze. Einzelne Fehler sind im nativen Text korrigiert. Erst nach Schliessung untenstehender Gates darf PCB-Layout/Freigabe erfolgen. Kein Rueckgriff auf A/B.

## Quellen und verifizierte Referenzen
1. Diodes AP74502Q/AP74502HQ DS47093 Rev2-2, **S. 2, 4–5, 15–16, 20**: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf
2. TI TPS2663 SLVSE94G, **S. 3–9, 27**: https://www.ti.com/lit/ds/symlink/tps2663.pdf
3. TI TPSM336xx-Q1 SNVSCS7E 09/2026, **S. 5–8, 27–31, RDN0011B**: https://www.ti.com/lit/gpn/tpsm33610-q1
4. Vishay SQM35N30-97, **S. 1–3**: https://www.vishay.com/docs/66742/sqm35n30-97.pdf

## 1. Diodes Herstellerreferenz Seite 15: Pin-fuer-Pin Vergleich

| AP74502HQ SOT28 | Herstellerreferenz 200-V-Surge-Stopper (OV-cutoff) | C1 nach Korrektur | Befund |
|---|---|---|---|
| 1 EN/UVLO | definierter externer EIN/AUS-Pegel, Versorgungs-Transienten beachten | R5=100k von ACC; R7=47k nach GND; D2/R6 fuer RUN_CMD | Funktionelle Pegel bei ACC normal plausibel; **200-V-/negativ-Pulse an ACC, Schutz und USB-only-Leckstrom NICHT qualifiziert** |
| 2 GND | Masse | GND | richtig |
| 3 NC | offen | no-connect | richtig |
| 4 VCAP | C>=0.1uF zum **lokalen IC-VIN**; im Surge-Beispiel 220nF | C2=220nF / 100V AEC-Q200 `C1206C224K1RACAUTO` am AP_VIN (nach Herstellerbeispiel korrigiert, Ceff nicht garantiert) | nominal nun identisch mit Herstellerbeispiel; thermisch/DC-Bias min wirksame C und 200-V-Stress offen |
| 5 VIN | nach R1=10k; bei 200V Zener 60V nach GND; mind. **1uF effektiv** | R1+R2=10.2k; D1=SMCJ56A, C1=1uF/100V nominal | Konzept vergleichbar, **D1 max Vclamp bei ca. 13mA, Ceff bei 60V, R-Pulsenergie NICHT belegt** |
| 6 GATE | beide Gates der antiparallelen Drain-Drain-MOSFETs (physisch gemeinsame Source) | Q1/2 gates verbunden, `AP_GATE` | vom Pinanschluss her richtig; Qg und Gate-Schutz transientsicher pruefen |
| 7 OVLO | Zweig via VIN oder VOUT umsteckbar, fuer **OV cut-off: Roh-VIN**; R2=100k, R3=3.5k | R3=1M von BAT, R4=39k GND | Cutoff-Prinzip richtig, aber Schwellen/Leckstroeme/30-V-Rueckkehr siehe unten |
| 8 SRC | gemeinsamer Source-Knoten zwischen Q1 und Q2 | `FET_SRC` | richtig, sofern physische D-S-Pads kontrolliert |
| MOSFET Q1/Q2 | Q1-Drain an Fahrzeug, Q2-Drain am Ausgang, Sources verbunden | `BAT_FUSED_IN` -> Q1 Drain; Q2 Drain -> `HV_PROTECTED` | richtige Back-to-back-Orientierung, **kein sicheres Hochvolt-Sperren bei Q1 Drain-Source-Kurzschluss**: Q2-Bodydiode speist HV_PROTECTED aus BAT |
| Externer Eingang | CIN=0.1uF an Roh-VIN, Ausgang COUT=220uF (Herstelleraufbau), definierte Schutzdioden fuer -Impulse | vor Q1 kein entsprechendes 200-V-taugliches CIN, nur geringe Kapazitaeten hinter Q2 | Schwingungen/Flanken/L-Induktivitaet unverifiziert, Empfehlung C1-BOM unvollstaendig |

**Dokumentationsfehler gefunden:** C1 hat **kein** nach Hersteller geregeltes COUT=220uF hinter den Back-to-back-FETs. Die vorhandenen C3=1u, C4=4.7u, C5=0.1u, C9=0.1u und C10=4.7u sind nominell 10.6u, unter DC-Bias weniger. Die Diodes-Wellenformen von S.16 stammen von einem **anderen Ausgangskondensator** und duerfen nicht als C1-Verifikation gelten.

## 2. U2 TPS26631-Pin-Korrektur

- Original Pin 13 (SHDN) lag direkt auf `HV_PROTECTED`, also 9..30V — **Absolutmaximum 5.5V verletzt!**
- **Tatsaechlich in .kicad_sch korrigiert:** Pin 13 ist nun elektrisch offen und mit No-Connect gekennzeichnet. TI spezifiziert offenen SHDN-Pin mit intern typischer Vorspannung **2.48 bis 3.3V**, die Einschaltschwelle ist 2V; externe Verbindung fuer dauernd EIN entfaellt. Temperature/Leakage pruefen.
- Pin 7 UVLO direkt HV_PROTECTED: liegt im spezifizierten Hochvolt-Bereich des Pins, aber die Anwendung als Direktanschluss ist gegen die UVLO-Funktion und +125C zu pruefen. Pin 8 OVP direkt GND waehlt interne Default-OVP und **keine** 36-V-taugliche Schwelle: eigenstaendiger U3-Schutz ist so NICHT vorhanden. 2x/3x Fehlerstrom beachten.
- Pin 1/2/3 IN an HV_PROTECTED; Pin 6 IN_SYS ebenfalls dort; Pin 4 B_GATE und Pin 5 DRV offen (kein zusaetzlicher Reverse-FET nach vorgeschaltetem AP); OUT Pin 18/19/20 an RAW_PROTECTED; Pin 9 und EP an GND.
- U2 Stromlimit mit R8=5.6k: ca. 3.21A Nenn-Strombegrenzung (TI 9k=>2A, 3k=>6A), **2x Puls** ca. 6.43A bis 31ms, Fast-Trip circa **3x** ca. 9.64A. Gesamtstromschutz ist nicht ein eigener 1-A-RAW-Schutz. F_MAIN 3A ist noch NICHT begruendet.
- 67V absoluter U2-Eingangsgrenzwert und 60V Betriebsgrenze: zu keinem Zeitpunkt aus der Datenblattanwendung des AP allein als 200-V-sicher abgeleitet.

## 3. Rechenbarer 30-V-Wiederanlauf-/Buck-36V-Widerspruch

C1-OVLO-Teiler `R3=1000000Ω, R4=39000Ω` ergibt beta = 39/1039 = **0.0375361**.

Diodes OVLO-Schwellen ueber Temperatur: **steigend 1.165 / 1.250 / 1.333 V** (min/typ/max), **fallend 1.063 / 1.143 / 1.222 V**.

| Messgroesse (ohne zusaetzliche Widerstandstoleranz/Leakage) | Min | Typ | Max |
|---|---:|---:|---:|
| Eingang Cutoff steigend | **31.04V** | 33.30V | **35.51V** |
| Eingang Wiederein unterhalb | **28.32V** | 30.45V | 32.56V |

Bei strengem spezifiziertem Wiederanlauf bei 30V ist der Worst-Case **NO-GO**: untere Abschalt-Schwelle 28.32V bedeutet bei rueckgekehrten 30V keine Freigabe.

Es existiert **kein** passiver AP-Teiler mit einem beta, der gleichzeitig folgendes ueber die vollen AP-Schwellentoleranzen garantiert:

1. Reset/erneutes EIN bei 30V: beta < 1.063/30 = **0.0354333**.
2. Abschalten spaetestens bei 36V: beta > 1.333/36 = **0.0370278**.

Die Anforderungen sind widerspruechlich (zusaetzliche 1%-R-Toleranzen und I_OVLO fehlen sogar noch). Fuer den nur auf **40V absolute maximum** begrenzten Buck kann beta zwischen 0.033325 und 0.03543 sein, jedoch nahezu ohne Sicherheitsabstand zu 40V und ohne Schaltflankenreserve. **TPSM33620S5 kann mit dem AP74502HQ als EINZIGER Schutzschwelle 30V reenable und nie >36V bei beliebigen schnellen Spitzen nicht gleichzeitig garantiert bekommen.**

## 4. 200-V-Flanke: Hersteller-Abschaltzeit und reale Gates

AP74502HQ OVLO->GATE <1V: **typ 0.6us, max 1us nur fuer CGATE-SRC = 4.7nF** unter TI/Diodes spezifizierten Testbedingungen. Vishay SQM35N30-97: Qg typ86nC, max130nC pro Stueck @10V VGS, VDS150V, ID9A; 2 Stueck bis **260nC**, Ciss max5650pF je FET. Die Summe ist nicht durch den 4.7nF-Standardfall fuer garantierte 1us abgedeckt. 260nC/(4.7nF*10V)=5.53 ist ein **grober Belastungsvergleich**, KEINE neue garantierte Zeit; die Entladezeit haengt nicht linear von Qg ab.

Konservative illustrative Flankenrechnung mit *bereits optimistisch angenommener* 1us-Abschaltung und Cutoff max35.51V, ohne Ueberschwinger:

| 30->200V Anstieg | Eingangsslew | rechnerische Spannung zusaetzlich in 1us | Moeglicher Input vor Trennung |
|---|---:|---:|---:|
| 10us | 17V/us | 17V | **52.51V >40V ABS MAX** |
| 100us | 1.7V/us | 1.7V | 37.21V (bereits >36V Betriebsgrenze) |
| 1000us | 0.17V/us | 0.17V | 35.68V vor Toleranz-/ESL-Spitzen |
| 10us / illustrative 5.53us | 17V/us | 94V | **129.5V (nicht nachgewiesen, nur Stressbeispiel)** |

**Keine dieser Modellwerte ist eine nachgewiesene reale V(HV_PROTECTED)-Wellenform.** Leitungsimpedanz/Kapazitaet koennen Flanken verformen; niedrige Quellimpedanz, Schwingkreise, Miller-Effekt und ESL koennen viel hoehere Peaks verursachen. TI-TPS26631 OVP-Abschaltverzoegerung **max 14us** (OVP->FLT) ist keine ausreichend schnelle alleinige Absicherung der 40-V-Pins. ISO-16750-2-Lastabwurf-Rampen koennen langsamer als obige Beispiele ausfallen; ISO-7637-2-Schnelltransienten sind trotzdem eigenstaendig zu qualifizieren.

**Lastabwurf-Pulsleistung:** angenommen 200V fuer 0.350s und 60V lineare Zener-Klemmung am AP VIN mit 10.2k Ohm: I=(200−60)/10200=13.73mA, P_R=1.922W, E_R=0.673J gesamt; je 5.1k-Widerstand ~0.337J. P_Z=0.824W, E_Z=0.288J. Der gewaehlte D1 `SMCJ56A` ist TVS, **nicht** eine ideal geregelte 60-V-Zener; seine realen Spannungen und Pulsenergie sind erst zu pruefen. 200V/350ms mit Quellimpedanz 0.5–8Ω plus F_MAIN/Leitungsinduktivitaet gesondert.

Einzeldefektbeispiel **Q1 D-S-KURZ**: 200V BAT -> kurz Q1 -> FET_SRC -> Q2 intrinsische Bodydiode -> HV_PROTECTED -> TPS26631 IN/IN_SYS (67V ABS MAX). Ohne zusaetzliche Massnahme ist das nicht beherrscht. Gleicher Gefahrenbezug bei TVS offener Ausfall, U1 Fehlabschaltung, Klemmwiderstand open/short.

## 5. 9V und Hot-Temperatur (explizit keine Freigabe)

- Normalbetrieb 9V, 5Vx2A=10W, angenommene 90% Buck-Effizienz, +1A RAW: I_FET = 10/(9x0.90)+1 = **2.235A** ohne Leitungsverluste.
- AP EN bei ACC=9V, R5=100k, R7=47k, max I_EN-Sink5uA: EN ca. 9*47/147 - (100k||47k)*5uA = **2.718V**, ueber maximaler EIN-Schwelle 1.32V. Startup bei Kaltzustand bleibt von Qg, Ceff und Buck-Laufstart abhaengig.
- Vishay RDSon max @ VGS=10V, TJ25C **97mOhm** und TJ125C **214mOhm** (gueltige Herstellerbedingung ID10A). Bei konstant 2.235A und **125C RDSon**: P fuer 2 FETs **2.137W** (je 1.069W) und mit herstellerseitiger *40K/W nur am spezifizierten PCB* ca. TJ=**167.7C**. MaxTJ175C -> wenig Spielraum. Die extra ~1V FET-Spannungsabfall erhoeht Buck-Eingangsstrom weiter; bei <10V Gate ist RDSon unzureichend begrenzt. PCB, Einbau und heisse Nachbarteile verschlechtern den Fall.
- TPSM33620-Q1: bei eta=90% und 10W: P_loss=1.111W. Bei EVM-aehnlicher effektiver thetaJA=22K/W: TJ ~**149.4C** bei 125C Umgebung (0.6K unter 150C). Bei JEDEC 54.1K/W: TJ ~**185.1C** (Fehler!). Eta85% und 22K/W -> TJ~163.8C. **+125C/5V2A NICHT qualifiziert**, auch wenn TI das Teil als -40..125C Ambient Automotive listet. Nur EVM-optimiertes Board/realer Thermiknachweis koennte das verbessern; keine heimliche Lastreduktion.
- Fuenf Bauteile mit temperaturkritischer Bilanz: HV-FETs, U2, U3, R1/R2 und D1. RAW-1A ist hinter gemeinsamer eFuse nach wie vor nicht unabhaengig auf 1A geschuetzt.

## 6. KiCad / Libraries / BOM / Messstatus

- Bestehende native KiCad-`.kicad_sch` **28 positions inklusive C10, C11 (zusaetzliche Bestueckkondensatoren)**; fuer U2 Pin13 `SHDN` ehemals `HV_PROTECTED` nach Herstellerbeschaltung nun **offen/No-connect**, kein weiterer MOSFET/Regler noetig.
- Diodes **SOT28 Seite20 Hersteller-Landpattern**: Pitch 0.65mm, X0.45mm, Y0.90mm, Reihenmitten Y1=3.10mm. Lokaler Footprint `TripPowerC.pretty/SOT28_Diodes.kicad_mod` von falschem Y1=2.20 auf 3.10mm korrigiert.
- **RDN11 ist bereits vorhanden** in `TripPowerC.pretty/TI_RDN11.kicad_mod`. Historische BOM-Behauptung **FOOTPRINT_MISSING** ist falsch und wurde in `BOM_C1_DRAFT.csv` zu `PROVISIONAL_FOOTPRINT_EXISTS_UNVERIFIED` korrigiert. Abweichungen ggü TI RDN0011B Package Outline + Land Pattern Ex. S.46/47 bleiben einzeln zu vermessen; **nicht als verifiziert behaupten**.
- U1/VIN, U2/Pin13 und U3/GND haben vorlaeufige Bibliotheken, alle Pin-zu-Pad-Zuordnungen ausserhalb des Hersteller-Release weiterhin zu kontrollieren. Bei U2 PWP Exposed Pad Kicad Pad21 formaler Platzhalter ohne sichtbare Nummer im TI Top View — Hersteller-Landpattern pruefen.
- In Laufzeitumgebung ist **kein `kicad-cli` installiert**. Daher **keine native KiCad10/ERC/Netlist/DRC durchgefuehrt**. Statischer Textcheck (Parenthesen-Syntax, 28 unikate Ref, 0 doppelte UUID) war erfolgreich, ist KEIN Ersatz.
- Keine BOM-Vollkosten: J1/J2 sind nur provisorische Header mit unbekanntem MPN, + mindestens notwendiges 200-V-CIN, 220-uF-Bulk, Schutz- und EN-Beschaltung fehlen; 28 ist die aktuelle bestueckte **Entwurfspositionenzahl**, nicht die Zielzahl einer fertigen Schaltung.

## 7. Empfohlener Fortgang, ohne unnoetige Eigenentwicklung

**C1-Frontend AP74502HQ alleine + 36V-TPSM: NO-GO ohne nachgewiesene Zusatzmassnahme.** Nichts weiter blind an diesem riskanten Schaltplan routen.

Pruefe zuerst unabhaengig beschaffbaren, temperaturfesten **80V- oder 100V-5V/2A-Buck bzw. Fertigmodul**, das bei 30V Dauerbetrieb und AP OVLO ~37V sicher mehr Spannungsreserve bietet (z.B. TI 80V-Regler mit Herstellerreferenz + separate Standardinduktivitaet). Mit Diodes Herstellerteilen 100k/3.5k waere 30V Auto-Wiederanlauf bei OVLO-FALL min 31.4V plausibel; risikoreiches Buck40V-Grenzspiel entfaellt. 200V-Puls/FET-Fehler bleiben auch dann offene Tore. Alternativ diskrete hochvoltige TVS-Absorption nur mit gepruefter Pulsenergie und externer F_MAIN, nicht ohne Nachweis.

Fuer **echte Einzelbauteilfehlerfestigkeit** der 200-V-Domaene und den 125C/10W-Hotload-Nachweis sind ggf. weitere essentielle COTS-Schutz-/Waermemassnahmen erforderlich. Ohne nachgewiesene Loesung nie Fertigungs-/Fahrzeugfreigabe.


## Nachtrag 15.10.2026: 28 statt 26 positionen und C2 angepasst

Die vorliegende Branch-Version umfasst **28 eindeutig bestueckte Positionen (inklusive C10/C11)**. Vorherige 26-Zaehlungen waren vor dem bereits eingecheckten zusaetzlichen Reserve-Kondensatorpaar entstanden. `PRICED_BOM_C1_PARTIAL_2026-10-15.csv` umfasst alle 28 Referenzen, aber Preise nicht fuer alle Positionen, deshalb **keine ehrliche Vollkostensumme vorhanden**. C2 VCAP wurde auf Diodes-Referenz nominal 220nF/100V KEMET C1206C224K1RACAUTO aktualisiert. Native ERC/Netlist ist noch nicht gelaufen; Shell hier: kein `kicad-cli` vorhanden, und es wurden keine GitHub-Workflow-Laufdaten fuer den Branch gefunden.
