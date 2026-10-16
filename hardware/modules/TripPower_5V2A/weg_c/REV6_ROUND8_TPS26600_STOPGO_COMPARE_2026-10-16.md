> **ERRATUM (16.10.2026, REV6 ROUND9): DIE IN DIESEM HISTORISCHEN ROUND8-TEXT VERMUTETE 32V-HYSTERESE IST FALSCH BEWERTET.** Richtig ist: zum Neustart bei fallendem Eingang32V muss **MIN(OVLO_FALL)>32V** gelten. Die TI TPS26600 1.085V falling MIN/1.225V rising MAX verlangen einen unmöglichen Teiler G>29.493 und G<=29.388. Die untenstehenden <32V-Fallingschwellen sind **FAIL** für Neustart32V, nicht PASS. Maßgeblich [aktuelle definitive NO-GO Entscheidung](REV6_ROUND9_C_NO_GO_AND_A_OPTIMIZATION_2026-10-16.md). Keine alte TPS26600-Designfreigabe mehr verwenden.

# TripPower Weg C – REV6 Round 8 TPS26600 vs TPS26631, 16.10.2026

**ENTSCHEIDUNG:** TPS26600PWPR ist die beste aktuelle Teilezahl-/Halbleiterkosten-Alternative, aber NICHT als komplette, qualifizierte V1 freigegeben. Bis der 62V-Absolutwert bei 58V Eingang auf dem realen PCB nachgewiesen wird, bleibt der mit nativer KiCad10-CI geprüfte, aber ebenfalls unvollständige **Weg A** der bessere derzeit vorhandene Entwicklungsprototyp. C wird bewusst nicht nur wegen möglicher Ersparnis zur Fertigung freigegeben. Keine fremden Branches geändert. Verbindliche REV6-Spezifikation, AGENTS, PWR44–56, FUSE_PLACEMENT_DECISION, Backup und letzte gemeinsame REV6 Review gelesen.

## 1. Herstellerseitig verifizierte TPS26600 Fakten

Original TI TPS2660 SLVSDG2G Rev.G Seiten 6–8, 28–29, 37–38: https://www.ti.com/lit/ds/symlink/tps2660.pdf

- 4.2–60V recommended VIN, **62V absolute** IN / IN-OUT für dauerhafte Ratingbetrachtung. Die **70V nur für 10ms bei Ta25C** sind NICHT auf 58V/350ms anwendbar. Integrierte Rückpolsperre bis −60V, Rückstromsperre, zwei Leistungsmosfets ohne externe Schottky, RON typ150mΩ, über Temp max250mΩ.
- TPS26600 **5.36k ILIM** liefert laut Datenblatt **2.11/2.23/2.35A MIN/TYP/MAX**. Normaler 10V-Eingang, 5V2A plus RAW0.5A, Eta85% angenommen, 250mΩ Max-ON-Widerstand: Gesamtstrom **1.730A**, am Buck ca **9.568V**, EFuse-Hitze **0.748W**. TI-PWP16 JEDEC thetaJA38.6K/W ergibt bei Ta60C Tj-Proxy **88.9C**. Es verbleiben nur0.380A bis zur minimalen Überstromgrenze, Inrush/Kabel/Start müssen getestet werden; keine Buck+60C- oder eFuse-Produkttemperaturzusage daraus.
- TPS26600 UVLO-Werkseinstellung 14.25V MIN Einschalten: 10V-Ziel würde verfehlt. TPS26600 OVP-Werkseinstellung 31V MIN Rising: 32V-Dauerbetrieb nicht garantiert. Ein echtes externes UVLO+OVP-Netz ist zwingend.
- TI Fig50 und Gleichungen 10/11: **Drei gemeinsame Sensewiderstände in Folge IN→R1→UVLO→R2→OVP→R3→RTN**, nicht nur ein OVP-Zweier-Teiler. **RTN darf NICHT fest auf GND gelegt werden: TI Kapitel 10.4 sagt, das deaktiviert den Verpolschutz.** Alle relevanten Schutzpassive/Exposed Pad auf RTN beziehen; GND ist ein eigener Power-Pin. Das verhindert voreilig falsch verdrahtete KiCad-Projekte.
- TPS26600 SHDN 0..4V empfohlener Betriebsbereich gegenüber RTN. Hoher Grenzwert einzelner Absmax-Differenzen berechtigt NICHT zum direkten Verbinden von Fahrzeug-ACC mit SHDN; Pegelanpassung und Rückspeisung sind separate Gates.
- TPS26631 dagegen 60V recommended/67V ABS, 31mΩ typ/53mΩ Max hot, aber braucht externen N-MOSFET + kleinen N-MOSFET-DRV im Hersteller-Verpolpfad. Beide Industriekatalogteile, keine beanspruchte AEC-Q1-EFuse-Zulassung.

## 2. Echte UVLO/OVP-Hysterese mit allen 3 Widerständen und Eingangslecks

Einfache neue Herstellerreferenzwerte TPS26600 (je 0.1%, 1206, konkrete Liefer-MPNs noch offen): **R1=86.6k, R2=9.65k, R3=3.57k Ohm**. ±100nA UVLO- und OVP-Pinleck, beide Richtungen unabhängig, Hersteller VR_OV=1.170..1.225V, VF_OV=1.085..1.125V, VR_UV=1.175..1.225V, VF_UV=1.080..1.125V.

| Senseband am TPS26600-IN | 0.1%-R min..max | 1%-R min..max |
|---|---:|---:|
| OVLO EIN→AUS bei steigendem Vin | **32.633..34.336V** | 32.071..34.938V |
| OVLO AUS→EIN bei fallendem Vin | **30.261..31.535V** | 29.740..32.087V |
| UVLO AUS→EIN bei steigendem Vin | **8.846..9.277V** | 8.709..9.423V |
| UVLO EIN→AUS bei fallendem Vin | **8.130..8.520V** | 8.004..8.655V |

Mit 0.1%-R passt der **rein statische** 32V-ON-/OV-Abschaltung unter36V-/32V-Recovery-/10V-Start-Fall. Mit 1% kann OVLO-Wiederanlauf oberhalb32V liegen -> NO-GO. Der früher genannte Zweier-Teiler 100k/3.74k war eine OVP-Isolatrechnung, noch keine herstellerkonforme UVLO+OVP-Gesamtbeschaltung.

Der Teiler zieht bei VIN12V **120µA**, VIN24V **240µA**, VIN32V **321µA**, dazu eFuse I_OFF bis33µA und ACC/RUN/Mainboard-Pegel. REV6 BAT OFF <1mA (Ziel <0.5mA) könnte erreichbar sein, benötigt aber eine echte elektrische Gesamtrechnung/Messung.

**C31 + Schottky** aus der vorigen eigenständigen Weg-C-Studie: 100k/3.78k, 0.1% R, Worst OV-falling **31.649V am eFuse-Eingang**. Bei Vin_connector32V muss die Schottky beim fast stromlosen Neustart **Vf ≤0.351V** garantieren. Kein verbindlicher Vf-Min-/Max-Nachweis vorliegend. **Weg A hat jedoch einen externen MOSFET anstelle unserer Schottky:** dessen Spannungsabfall/RDSON ist anders und die eigene A-3R-OVLO-Hysterese muss separat berechnet werden. Die Schottky-Rechnung ist NICHT automatisch ein A-Fehler.

## 3. 58V/350ms und eingebettete Kurzschluss-Flanken: harter TPS26600-Stop

TI **SLVSDG2G S.38** weist ausdrücklich auf positive Eingangsüberschwinger durch Leitung-L beim Überstrom-Abschalten hin. Einfache Hersteller-Schätzwertgleichung für ungedämpften Fall: Vpin≈Vin+Iload*sqrt(Lin/Cin_effective). Hier kein Test, kein Worst-Ringing-Proof. Bei nom58V und I_max2.35A:

| L / wirklich bei58V wirksames C | Schätzwert VIN-Pad | Prüfung |
|---|---:|---|
| 1µH / 0.47µF | **61.428V** | >60V recommended, <62V abs |
| 2µH / 0.47µF | **62.848V** | **>62V ABS NO-GO** |
| 1µH / 1µF | **60.350V** | >60V recommended, fast keine Reserve |
| 2µH / 1µF | **61.323V** | >60V recommended |

Ohne reale Dämpfung/ESL/Temperatureffekte, idealisiertes gleichzeitig leitendes Abwerfen bei VIN58. Bei langsamem Lastabwurfanstieg schaltet OVP möglicherweise schon unter35V aus, was diesen worst load case entschärft; schnelle Kanten und Kurzschluss-Unterbrechungen bleiben trotzdem separate mögliche Randbedingungen.

Theoretische L-Grenzen bei Ceff1µF,2.35A und 58V **ohne Sicherheitsreserve**: TPS26600 <**0.724µH** für max60V recommended und <**2.897µH** für max62V ABS; TPS26631 hat gleiche 60V-oper Grenze, aber für67V-ABS <**14.669µH**. Eine 100V X7R 1µF Nennbeschriftung ist bei58V nicht automatisch Ceff1µF. Deshalb weder 62V noch60V bei allen Pads ohne Quelle/Kabel/PCB-Test garantiert. TI-70V 10ms bei25C ist nicht die 350ms Freigabe. Einfach eine TVS ohne Energie-/Clamp-Qualifikation dazu zu nehmen widerspricht COTS-/Kosten-Ziel.

Einzelfehler: integrierter eFuse-Leistungspfad intern Kurzschluss -> bis 58V plus Ringing an RAW und am 80V-Buck; Schutz der RAW-Verbraucher/Leitung muss daher qualifiziert oder eigene 0.5A-Branch-eFuse eingesetzt werden. 32V/36V/58V Einbau-F_MAIN muss extern passende Leitungen schützen. PWR55/PWR56: **Keine Schmelz-/Einmal-SMD-Thermosicherung und kein Sicherungshalter auf TripPower.** Keine PPTC ohne wirklich passenden 58V+Transiente/Ihold(60C) Hersteller- und Fehlernachweis. F_MAIN im Fahrzeug-Harness, ggf. zusätzlich zugängliche Sicherung auf TripTracer (ersetzt Fahrzeugleitungsschutz nicht).

## 4. Thermik, Backup, ACC/RUN und echte Funktionsgrenzen

LMR38020SQDDARQ1 ist Automotive-AEC-Q100/80V/2A, aber auf TripPower müssen dessen eigene Kupfer- und 15µH-DC/DC-Verluste, 25/32V+60C/2A und Ceff-Bias nachgewiesen werden. **+85°C Ambient safe OFF** ist nicht mit TPS26600 ~157°C Tj-Thermal-Shutdown gleichbedeutend. TI **TMP302-Q1** Automotive-Temperaturschalter (Setpoint 80°C plus Toleranz, Versorgung 1.4–3.6V) wäre ein COTS-Kandidat, aber ein vom abzuschaltenden 5V abhängiger Sensor kann nach dessen Wegfall erneut einschalten und heißes Flattern verursachen. Versorgung/Latch/Temperaturgradient oder mechanischer auto-reset Thermoschalter nach Hersteller zu qualifizieren und fair bei A wie C einzupreisen.

RAW0.5A ist beim gemeinsamen 2.11..2.35A-ILIM nur Nennlast, **keine selektive 0.5A-Kurzschlussbegrenzung**. Beide Konzepte benötigen entweder Leitungs-/Stecker-Faultbudget für vollen gemeinsamen Strom oder zusätzliche kleine elektronische RAW-Stufe, einschließlich ihrer echten MPNs/Footprints/Preise. Die A25-Funktion ist ebenfalls unvollständig. Das gilt auch für ACC/MCU-RUN-Selbsthaltung, M8/USB-Prio/Backfeed und vollständig isolierten FRAM-first-PWR_FAIL. Der Verlust des M8 kann ohne Vorwarnzeit erfolgen, FRAM muss vorher atomar gespeichert sein, Primär-RTC-Zelle darf nie den 5V/2A-Hauptpfad versorgen oder geladen werden.

## 5. Fairer A25 gegen ungebauten C23 (NUR Modulplatine, keine Harness-Fuse)

A-Quelle: tatsächlich 25 im Branch design/trippower-a bestückte Referenzen, native KiCad10 ERC/Netlist bereits vom A-Team. Matched row-by-row Kostenliste dieses Branches: **REV6_ROUND8_MATCHED_BOARD_BOM_A25_VS_C23_DRAFT.csv**.

| Vergleichsmaß | A native TPS26631/extern Reverse | C TPS26600 (rein provisorischer Schaltungsumfang) |
|---|---:|---:|
| wirklich bereits in KiCad bestückte TripPower-Positionen | **25** | **keine neue REV6-C-Schaltung gebaut** |
| Buck+PG gemeinsamer Vergleich | 15 | 15 vorläufig 1:1 übernommen NUR für Kosten-Scope |
| Eingangsschutz-R-/C-/U-Bauteile | 10 | 8 **prognostiziert** (1U, 3R Sense, R ILIM, CIN, COUT, Cdvdt) |
| projizierte gleiche, noch unvollständige Funktion | 25 | **23 hypothetisch**, nicht 23 real überprüft |
| mit irgendeinem Betrag gepreiste Positionen | **14/25** | **11/23**, davon Murata EOL |
| Summe der aktuell als Zahl im CSV stehenden Preise netto 1/10/100 | **16.305 / 10.998 / 8.7721 EUR** | **11.677 / 7.953 / 6.5491 EUR** |

**Nicht echte Gesamtpreise, nicht vollständige BOM.** 11 A- und 12 C-Positionen ohne Preis, die neue 0.1%-R-Verfügbarkeit noch offen, bei beiden fehlen weitere notwendige Gesamtschutz-/Temperatur-/RAW-/Steckverbinder- und ACC-Funktionen. C verwendet für einen sauberen Gleichvergleich nur die 15 A-Buck-/PG-Reihen, obwohl die existierende Murata C104..106-MPN **GRM32ER71E226KE15L** EOL ist; darf vor Einkauf nicht übernommen werden.

**Neuer Preisregister-Befund:** A-BOM-Zeilen geben C104,C105,C106 inzwischen je **0.843/0.445/0.405 EUR** an, während alte A-CSV-SUMMARY noch **15.789/10.632/8.4331 EUR** summiert (ältere 0.671/0.323/0.292 je C). Neu korrekt Zeilensumme **16.305/10.998/8.7721**, Differenz **+0.516/+0.366/+0.339 EUR**. Nur auf C-Branch als unabhängiger Hinweis festgehalten, keine A-Datei editiert.

**Ehrlich sichere preisliche Teil-Differenz:** Ein TPS26600 kostet aktuell bei Mouser 3.42/2.56/2.12 EUR statt A TPS26631 3.89/2.96/2.46 + Vishay 100V Reverse FET 3.78/2.49/1.75 + onsemi DRV-NMOS 0.292/0.129/0.113. Eingesparte aktive Teilegruppe **4.542/3.019/2.203 EUR** bei 1/10/100; Preispräzision-Sense-Netz, Fehlerschutz, Kondensatoren, Thermosensor und seriell testbarer PCB-Aufwand NICHT damit bezahlt.

Liefer-/Technologiestand: TPS26600 TI ACTIVE, Mouser Preise wie oben; Momentaufnahmen widersprechen sich zwischen etwa69 und >1000 sofort verfügbaren TPS26600, keine verbindliche Menge bei100 ohne echten Warenkorb. TPS26631 Mouser zuletzt57 lagernd. LMR38020SQDDARQ1 TI ACTIVE (nicht EOL), aber MOU-Snapshots zwischen alter Lagerzahl und angekündigtem Januar2027 uneinheitlich, vor Kauf live prüfen. Bourns SRP7050TA-150M 15µH typ 0.95/0.783/0.6435 EUR, bei DigiKey ca4.6k verfügbar. 100V-Kondensator KYOCERA AVX KAM32LR72A475KU AEC-Q200 X7R 4.7µF/1210, Mouser 0.783/0.495/0.349 EUR und >30k Bestand: nur Ersatzkandidat, keine Ceff-Garantie ohne58V-Kurve.

Module:
- RECOM RPH-3.0-CT 55V input maximum + eigene Thermik/Derating: falls eFuse-Sperrpfad fehlschlägt, sieht Modul bis58V und ist außerhalb Spezifikation.
- TI LMZ36002RVQT mit integrierter Spule, 4.5–60V/2A, 43B-QFN 10×10mm, Catalog, 105C max ambient, ca **9.78/9.61/8.81 EUR** netto 1/10/100 bei Mouser. Nach eFuse und Schutz-Interface teurer als LMR38020+Induktor-Basisteile, gleiche 2V nominale Pad-Betriebsreserve bei FET-short. Kein verifizierter kleinerer Komplett-PCB-/BOM-Vorteil.

Fahrzeugseitige Sicherung/Stecker/Harness sowie Mainboard USB/RTC/PWR_FAIL dürfen NIE zu den bestückten TripPower-Positionen addiert werden. Kandidat Littelfuse MINI 0997004.WXN 4A/58V mit Halter 0FHM0001ZXJ-RED 58V/125C im Fahrzeug-Harness unter DC-Clearing/I²t/Halter-Temperaturvorbehalt. Auf kleiner Platine **0 Sicherungspositionen**.

## 6. Entscheidung / belegbare nächste Gate-Prüfung

**Weg A vorerst als bestehenden KiCad10-Prototyp mit 25 Positionen bevorzugen, nicht fertigen.** C könnte 2 Schutzpositionen und aktive Halbleiterkosten sparen, aber die nur 4V ABS-Reserve zu58V wird beim TI-gemäß kalkulierten 2µH/0.47µF-Beispiel bereits überschritten. Erst harte Grenzen von M8-Rsrc/R-L/Pad-Ringing und wirklich wirksamer Ceff bei58V plus negatives Schwingen und FET-Short, 60C/2A/10V-Strom und 85C-Temperaturabschaltung **belegen**, dann eigenständigen KiCad10-C-REV6 (drei Sensewiderstände, RTN nicht GND) samt vollständiger BOM/Footprints und nativer ERC/Netlist entwickeln. Keine hypothetische „23 Bestückpositionen verifiziert“-Behauptung.

Tatsächlich reproduzierbare Tests (GitHub Actions): rev6_round8_full_ladder_model.py und .github/workflows/trippower-c-rev6-round8.yml. Sie prüfen nur Mathematik, TI-Grenzen und BOM-Zeilen; **nicht** 58V-Pad, ISO/85C, echte KiCad10/ERC/DRC oder Fahrzeug.

## Hersteller-/Preisquellen

- TI TPS26600 Hersteller: https://www.ti.com/lit/ds/symlink/tps2660.pdf
- TI TPS26631 Hersteller: https://www.ti.com/lit/ds/symlink/tps2663.pdf
- TI LMR38020-Q1: https://www.ti.com/product/LMR38020-Q1
- TI LMZ36002: https://www.ti.com/product/LMZ36002
- Mouser TPS26600: https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS26600PWPR
- Mouser TPS26631: https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS26631PWPR
- Mouser LMR38020: https://www.mouser.de/ProductDetail/Texas-Instruments/LMR38020SQDDARQ1
- DigiKey Bourns: https://www.digikey.de/en/products/detail/bourns-inc/SRP7050TA-150M/5429680
- DigiKey automotive MINI 58V: https://www.digikey.de/de/products/detail/littelfuse-inc/0997004-WXN/701056
- Littelfuse holder: https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0001zxj-red
