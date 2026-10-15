# TripPower Weg C — Round 6: unabhängige COTS-Neuentwicklung, Sicherheits- und Kostenentscheid (15.10.2026)

**Ergebnis: Alle drei vollständig untersuchten Architekturen sind derzeit NO-GO für Platinenbestellung und Fahrzeugeinsatz.** Keine der drei erreicht einen nachgewiesenen 200-V-/350-ms-Schutz samt +125-°C-Dauerlast und sicherer Einzelbauteilfehlerbehandlung. Nicht einfach C1 oder C2 weiterbauen. Ein sinnvoller nächster Prüfpfad ist die vom Hersteller dokumentierte MAX16126-Lastabwurf-Referenz, nicht der ungeprüfte Transfer einer alten Schaltung. Die stärkste neue Erkenntnis: **Weder Lastabwurf-Energie noch sicherer F_MAIN-Auslösestrom lassen sich aus dem Spannungswert 200 V und der Dauer 350 ms allein bestimmen.**

Gelesen: Round-6-Review unter design/trippower-review, POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md, neue PWR-16/34/38–43 und eigene C1/C2-Reports. Keine fremden A/B/D-Schaltpläne gelesen, keine Dateien außerhalb design/trippower-c bearbeitet.

## 1. Anforderungen

Verbindlich bleiben 12/24-V-Fahrzeuge, 9–30 V normal, 5 V/2 A, geschützter RAW-Zweig Ziel 1 A, –40…+125 °C Umgebung für TripPower, 200 V/350 ms ungedämpft, Rückkehr zu 30 V, Verpolung, elektronische Strombegrenzung, austauschbare externe F_MAIN, BAT-OFF-Systemziel unter 100 uA und USB/ACC/RUN ohne Rückspeisung.

**NEU:** TripTracer bekommt eine lokal entkoppelte Knopfzellen-Notdomäne für minimale MCU/FRAM/microSD-Speicherung nach vollständigem M8-Verlust. Normale 5V2A muss bei Überspannung nicht weiterlaufen. Die bestehende RTC-CR1220 reicht für SD-Spitzenstrom nicht erwiesen aus. Primärzellen niemals laden. TripPower stellt Signale und Entkopplung bereit, die Notenergie-Zelle und der kritische Niedervolt-Power-Path liegen auf der Hauptplatine. Die Shutdown-Energiebilanz ist ein getrenntes offenes PWR-41-Gate.

## 2. Drei grundsätzlich verschiedene herstellerbasierte Architekturen

| | R6-T: passiv absorbierender Surge-Shunt | R6-M: dedizierter Load-Dump-ABschalter | R6-L: zeitbegrenzter Hochvolt-Linear-Surge-Stopper |
|---|---|---|---|
| Frontend | Taiwan Semiconductor TLD8S36AH TVS, auslegungsabhängiger Rückpolpfad | Analog Devices MAX16126TCA/V+T, zwei Hochvolt-NMOS, Zener/TVS-Herstellerreferenz | ADI LTC4366HTS8-2#TRMPBF mit Timer, HV-SOA-MOSFET und extra Reverse-Schaltfunktion |
| Versorgungsregler | TI LMR38020SQDDARQ1, 80V, 2A, separate Standardinduktivität | gleicher 80V/2A-Buck als günstiger Vergleich | gleicher 80V/2A-Buck als günstiger Vergleich |
| RAW-Schutz | TI TPS26631PWPR eFuse 60V oper/67V abs, gemeinsames Stromlimit | gleiche 60V-eFuse NACH MOSFET-Block | gleiche eFuse hinter dem Surge-FET |
| Steuerung/Backup | ADC/supervisor auf Backup-Mainboard, LMR PGOOD nur solange korrekt gespeist | MAX FLAG liefert zusätzliche OV-Vorwarnung; M8-Ausfall erfordert lokale Backup-Supervision | timer-Fault allein deckt keinen kompletten Fahrzeugabzug ab |
| 200V/350ms | Shunt nimmt gesamte Lastabwurf-Energie auf, Hot-SOA NICHT belegt | ADI publiziert Tests mit bis zu 202V/400ms, Rsrc 1–8 Ohm, aber anderer Last/Gehäuse/Temperatur | Controller floating VIN bis >500V möglich, externes FET muss 125°C-LIN-SOA bis Timer-Auslösen schaffen |
| schwerster Fehler | TVS kurz/open + F_MAIN-HV-Unterbrechung | Eingang-FET Drain-Source kurz und zweiter MOSFET-Bodydiode -> bis 200V an 67V-eFuse | Leistungs-FET kurz -> 200V am nachfolgenden eFuse trotz TIMER=OFF |
| derzeitige Entscheidung | **NO-GO**, billigste IC-Teilsumme, aber Energie nicht belegt | **NO-GO**, als NÄCHSTE FORSCHUNGSPRIORITÄT, weil Hersteller-Referenzprüfungen veröffentlicht | **NO-GO**, mehr SOA-Aufwand, teurer, 9V gerade Controller-Minimum |

Das sind **drei physikalisch verschiedene Strategien**: TVS-Energieabsorption, vollständige aktive Sperre, zeitbegrenzte lineare Spannungsregulierung/Abschaltung. 80V-Buck ist hier lediglich derselbe vergleichbare Lastwandler, keine Fortsetzung der C2-HV-Frontend-Konstruktion.

## 3. 200V Energie / Quellimpedanz: harte P0-Sperre

TSC AN-1003 nennt für TLD8S36AH in der 25°C-Anwendung 202V/350ms, Ri etwa 3.5Ohm in der Ergebnistabelle, aber 4.5Ohm im erläuternden SOA-Teil. Bei 125°C kein aus diesen Daten belastbarer Load-Dump-Nachweis. 58.1V bei 114A als 10/1000us-Datenblatt-Clamp ist kein 350ms/125°C-Ceiling. Ein 61.2V-Clamp aus dem 25°C-Anwendungsbeispiel ist nur eine **Rechenannahme**.

Für Rechteckspannung 200V/350ms und idealisierten 61.2V TVS-Clamp folgt I=(200−61.2)/Rsrc und E=61.2*I*0.35:

| Rsource | Spitzen-I | Spitzen-P | Rechteck-E | nur mathematisch angenommene 350ms-Exponentialzeitkonstante, E |
|---|---:|---:|---:|---:|
| 1 Ω | 138.8 A | 8495 W | 2973 J | 1840 J |
| 3.5 Ω | 39.66 A | 2427 W | 849 J | 526 J |
| 4.5 Ω | 30.84 A | 1888 W | 661 J | 409 J |
| 8 Ω | 17.35 A | 1062 W | 372 J | 230 J |

Die 350ms-Exponentialzeitkonstante ist frei gewählt und **kein ISO-Profilbeweis**. Fehlt eine untere Schranke für Rsource, wird E im Modell unbeschränkt. Bei defekter offener TVS folgen 200V bis zu eFuse (67V abs) und Buck (80V Betrieb). Bei TVS-Kurzschluss muss die externe F_MAIN **unter dem möglichen 200V-DC-Fehler** normgerecht abschalten. Gängige 32V-ATO-Sicherungen haben nicht automatisch 200V DC-Abschaltvermögen; Strom unter dem Auslösebereich kann ein PCB-Teil dauerhaft thermisch schädigen. Zusätzlich muss eine unidirektionale TVS vor einem Rückpolschutz auf mögliche Vorwärtsleitung bei -30V geprüft werden.

R6-M: Der Hersteller publiziert ein getestetes MAX16126-Referenzboard mit 202V/400ms, Ri 1–8Ω, 1A und 330uF/35V COUT, OV ca.28V; er berichtet TVS-Aufnahme 35.74J anstatt 160J bei anderem rein passivem Verfahren. Das ist eine wertvolle COTS-Referenz, **kein** eigener 200V/350ms/+125°C/5V2A+RAW1A-Test und kein Nachweis für Einzelfehler. Beim kurzgeschlossenen eingangsseitigen 300V-FET kann eine zweite MOSFET-Bodydiode die nachgeschalteten 67V/80V-ICs gefährden. Zener-OPEN/KURZ, Kondensatorfehlversagen und F_MAIN-Rsrc-Koordination bleiben P0.

R6-L: Beispielhafte hypothetische Linearbelastung für 2.4A, 200V-Input, 43V-Clamp: (200−43)*2.4 = **376.8W** und bei ausbleibender Abschaltung über 350ms **131.9J**. Ein korrekt dimensionierter LTC4366-TIMER würde früh abwerfen; echte 125°C-SOA, Sperrspannung, Wiederanlauf bei 30V und MOSFET-D/S-Kurz-Fail-Close sind aber nicht nachgewiesen. VDD-Mindestwert LTC4366 ist 9V, Reverse-Drop/Versorgungsstart-Risiko.

## 4. 9V vs 10V/11V und 125°C

Vergleichs-Sensitivität (nicht Architekturvorgabe): 2 Hochvolt-MOSFETs mit je 214mΩ @125°C und 10V VGS, 53mΩ eFuse, η90% Buck, 5V/2A=10W plus RAW1A. Selbstkonsistenter Eingangsstrom mit Spannungsabfall:

| Vin | Strom gemeinsamer Pfad | Spannung am Buck | 2-FET-Heizleistung | eFuse-Heizleistung |
|---:|---:|---:|---:|---:|
| 9 V | 2.418 A | 7.837 V | 2.502 W | 0.310 W |
| 10 V | 2.246 A | 8.920 V | 2.158 W | 0.267 W |
| 11 V | 2.113 A | 9.984 V | 1.911 W | 0.237 W |

11V statt 9V spart im Modell etwa 0.59W an zwei heißen HV-FETs, **aber noch keine belegbar entfallende Bestückposition, keinen 200V-Schutz und keinen Nachweis bei +125°C**. 9V bleibt verbindlich; 10/11V nur Sensitivitätsstudien. LTC4366 bei 9V genau am Eingangslimit besonders kritisch.

Regler-Hot-Screening: 10W Ausgang bei angenommenem η90% -> 1.111W Gesamtkonversionsverlust. Bei Ta125°C und gewünschtem TJ≤150°C müsste eine 100% im IC anfallende Verlustleistung einen effektiven θJA höchstens **22.5 K/W** haben; bei 30K/W rechnerisch 158.3°C. Dies sind bewusst konservative Screeningzahlen, **weder** garantierter LMR38020-Wirkungsgrad **noch** tatsächlich gemessener Wärmewiderstand oder Verlustverteilung (Spule!). Physische Gehäuse-, PCB-Kupfer- und hohe-Vin-Tests unverzichtbar.

Gegenprobe Modul: RECOM **RPH-3.0-CT**, 4.5–55V 3A, integrierte Induktivität, QFN 10×12mm =120mm², Preis 7.89 / 7.76 / 7.06 EUR für 1/10/100 laut Mouser DE. Derating bei 125°C ist nicht als 5V2A im kompletten 9–30V-Bereich belegt, so dass es **noch keine kostengünstige Sicherheitslösung** ist. RECOM R-78K5.0-2.0L nur ~+90°C, ausgeschlossen.

## 5. Keine fingierten Vollkosten / Bestückpositionen

Dateien:
- R6_VENDOR_PRICE_SNAPSHOT_2026-10-15.csv: echte aktuelle verlinkte EU-MPN-/Liefer-/Preisangaben, EUR netto, 1/10/100, keine unbekannten Preise erfunden.
- R6_ARCHITECTURE_POSITION_SCOPE_UNRELEASED.csv: **jede bekannte notwendige Bauteilkategorie** der drei Kandidaten, einschließlich Buck-Induktivität, Kondensatoren, eFuse-R's, OV/UV, VIN/ACC, RUN, PWR_FAIL, beiden Steckern, externer F_MAIN samt Halter, USB-Entkopplung **und** Backup-Zelle/Halter/Powerpath/Puffer. **TBD-Positionen sind nur Scope-Planung, keine freigegebenen MPN- oder vollständige bestückbare BOM.** Gerade der sicherheitskritische zusätzliche Schutz ist noch unbestimmt.

| Architektur | bisher nur sicher bepreiste Bauteil-Positionen | **Teilkosten** EUR netto je Gerät bei 1 / 10 / 100 St. | erforderliche Scope-Platzhalterpositionen, NICHT tatsächlich endgültige Bestückpositionen | davon MPN/Thermik/Auslegung offen |
|---|---:|---|---:|---:|
| R6-T | 3 | 11.29 / 8.22 / 6.54 | 39 | 36 |
| R6-M | 5 | 21.75 / 15.67 / 12.34 | 49 | 44 |
| R6-L | 4 | 22.03 / 16.53 / 13.56 | 46 | 42 |

**Keine dieser Teilsummen ist ein Komplettpreis.** Teile für sicherheitskritischen Schutz, Stecker, 250V-Keramik, externe auswechselbare HV-DC-fähige F_MAIN und lokale Backup-Hardware sind nicht final spezifiziert/bepreist, und könnten die Zahl ändern. TPS26631 hat laut Mouser-DE-Snapshot nur 57 Stück sofort verfügbar (für 100 Stück nicht komplett). Die bisherige existierende C1-KiCad-BOM mit 28 Bestückpositionen ist ein *anderer, gesperrter* elektrischer Stand, nicht diese Round-6-BOM.

PCB-Fläche ist ohne qualifiziertes Layout NICHT messbar. Bekannte Körper: MAX16126 QFN3×3mm, LMR38020 HSOIC4.9×6mm, TPS26631 HTSSOP4.4×6.5mm und RECOM RPH 10×12mm. Leistungstransienten (DO-218AB-TVS), Kupferkühlung, Abstand bei 200V und F_MAIN-Halter bestimmen tatsächliche Fläche. Keine künstlichen cm²-Vollflächen erfinden. Eine Kostenbehauptung mit unbekannten Preisen als Null wäre gefährlich.

## 6. PWR_FAIL und rückspeisefreie Not-Domäne

Ein funktionierendes PWR_FAIL bei OVLO und bei **abgezogenem M8** lässt sich nicht allein mit einem ungespeisten MAX16126-FLAG oder einem Buck-PGOOD garantieren: nach vollständigem Verlust des Fahrzeug-GND/BAT kann der Ausgabepin floating sein. Die sichere Quelle für Verlustmeldung ist ein **aus der isolierten Backup-Schiene versorgter lokaler Supervisor auf der TripTracer-Hauptplatine**, der die **nicht** durch Akku/USB gebackupte TripPower-5V-Quelle erkennt. Bei fehlender Quelle wird PWR_FAIL=1 (Fehler) im Backup-Logikbereich; ein optionales MAX16126-FLAG zeigt bei versorgtem Frontend Überspannung frühzeitig an. Test gegen Rückspeisung über Power-Good-/GPIO-/ESD-Dioden in TripPower, BAT, ACC, RAW, USB; Backupzelle lädt keinesfalls. PWR_FAIL-Erkennungszeit, Quell-Umschaltzeit und minimaler 3V3-SD-Pulsboden sind Mess-Gates. Kein 5V/2A-Hauptbetrieb aus CR-Zelle.

RAW1A ist **nur ein Verbrauchsziel**: bei gemeinsamem >2A-eFuse-Überstromwert sehen Stecker/Kabel/Leiterbahnen höhere Fehlerströme, wenn nicht eine zusätzliche echte 1A-Strombegrenzung eingebaut wird. Diese Position ist sicherheitsrelevant und bleibt TBD.

## 7. Konkrete Entscheidung / nächste Nachweise

1. P0: Anforderung zur **Quellimpedanz Rsource_min/max, Pulsform inkl. 350ms-Definition, Kabel-L, Generator-Nennspannung und Pulswiederholungen, Umgebungstemperatur zum Pulsbeginn** konkretisieren. Gleichzeitig einen austauschbaren Sicherungs-MPN/Halter auswählen, dessen tatsächliches **DC-Unterbrechungsvermögen bei dem Fehlerpuls** und I²t zur Quelle/Kabel/PCB passt.
2. P0: Taiwan Semiconductor nach **TLD8S36AH hot-SOA @125°C und konkretem Rsource** schriftlich befragen; ADI nach der **MAX16126 202V/400ms-Referenz samt Einzelfehler Q-input D/S kurz, Zener OPEN/KURZ, bei 125°C und 2.5A Last**. Keine TVS- oder FET-Ausfallart als garantiert offen unterstellen.
3. P1: Erst nach positivem P0 echte vollständige Hersteller-Stückliste für die favorisierte Schutzarchitektur bis zum letzten MPN/Footprint und preisliche Gesamtrechnung 1/10/100; Temperatur, 9V-Start, 30V-Restart und nachgeschaltete dynamische Maximalwerte elektrisch testen. Lokal echtes PWR_FAIL/Backup-Energiebudget messen.
4. P2: Dann eigener KiCad-10-Round-6-Schaltplan mit portabler Bibliothek, native ERC/Netlist im CI, PCB/DRC und 200V/350ms-Labortest, bevor gefertigt oder im Fahrzeug eingesetzt wird.

**Kein neuer KiCad-Schaltplan heute:** Sämtliche drei Kandidaten scheitern bisher am P0-Gate. Ein scheinbar vollständiger Entwurf mit fehlenden sicherheitswichtigen Schutzteilen würde diese Tatsachen verschleiern. Die reproducible Python-Screens sind Rechentests, keine native ERC-/ISO-/Hot-Testfreigabe.

## Quellen

- Taiwan Semiconductor AN-1003 (25°C, Ri): https://www.mouser.com/pdfDocs/AN-1003_AutomotivecircuitprotectionofloaddumpTVS_A1901.pdf
- ADI MAX16126 Produkt: https://www.analog.com/en/products/max16126.html
- ADI 202V/400ms Hersteller-Referenz: https://www.analog.com/en/resources/technical-articles/loaddump-protection-for-24v-automotive-applications.html
- ADI LTC4366-2 Datenblatt: https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf
- TI LMR38020-Q1: https://www.ti.com/product/LMR38020-Q1
- TI TPS26631: https://www.ti.com/lit/ds/symlink/tps2663.pdf
- RECOM RPH-3.0: https://recom-power.com/en/rec-s-RPH-3.0.html
- R6_VENDOR_PRICE_SNAPSHOT_2026-10-15.csv enthält konkrete Angebots-URLs und Lagerstandsangaben der Distributoren.

## Round-6 CI-Nachweis (tatsächlich ausgeführt)

Eigenständiger GitHub-Actions-Workflow .github/workflows/trippower-c-round6-cots.yml:
https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38792445057

GitHub Job-/Logprüfung vom 15.10.2026: **SUCCESS, 11/11 Python-Regressionstests, BOM-Scope-Abgleich R6-T=39/R6-M=49/R6-L=46 und Preise-Teilsummen reproduziert**. Das ist **nur** ein arithmetischer und dokumentarischer Status, keine KiCad10-ERC-/Netzlisten-/DRC-, reale 200V-/350ms-, thermische oder ISO-Freigabe. Kein qualifizierter neuer Round6-Schaltplan existiert. Sicheres Endergebnis bleibt NO-GO bis P0 abgeschlossen.
