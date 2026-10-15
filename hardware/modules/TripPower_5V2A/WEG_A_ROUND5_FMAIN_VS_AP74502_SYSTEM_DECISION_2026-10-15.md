# TripPower Weg A — Runde 5: F_MAIN-Fehlerenergie oder unabhängige Hochvolt-Trennung (15.10.2026)

**Basis:** Management-Review `docs/TRIPPOWER_A_B_C_REVIEW_ROUND4_2026-10-15.md` aus `design/trippower-review`, A-Bericht `WEG_A_ROUND4_Q301_SHORT_FAILSAFE_PROTOTYPE_2026-10-15.md`, REV5 mit 57 AUTO / 58 RUN bestückten Positionen. **Aktive REV5-Schaltung bleibt elektrisch unverändert.** Q307/R342/D306 aus Runde 4 werden **nicht** als Lösung fortgeführt. Ziel: sicherer Geräteausfall zulässig, aber kein Kabel-, PCB- oder Fahrzeugbrand. `200V/350ms` ist **kein** vollständiges Quellprofil (R, L, Flanke, Wiederholung fehlen). Keine Fahrzeug-, Fertigungs- oder Einsatzfreigabe.

## 1. Zwei gesamtheitliche Lösungswege

### A — externe, wirklich DC-abgeschaltete F_MAIN und akzeptierter Totalausfall

- Konkreter **Sicherungskandidat**, nicht gewählt: **Mersen A6Y3-1, 3 A, 500 V DC**. Hersteller [A6Y3-1](https://www.mersen.com/en/products/a6y/a6y3-1). Eine 500-V-DC-Nennspannung ist bei 200 V prinzipiell passender als normale 32/58/125/150-V-Autofuses; Mersen muss aber für **200-V-DC-Interrupt, Quell-L/R, 125°C, passenden Sicherungshalter und pulsierende Quellen** die spezifische Charakteristik nachweisen. Der externe Einbauplatz und seine DC-Kontakt-/Kriechstrecken gehören zur TripTracer-Trägerplatine, nicht zum kleinen TripPower-Modul.
- Bei **9 V VIN_FUSED**, 5V×2A bei nur **angenommenen** 80% Buck-Wirkungsgrad plus RAW1 A ergibt sich `I_in ≈ 10W/(9V×0,8)+1A=2,389A`. Das liegt nah an 3 A. Der Sicherungs-Deratingfaktor bei 125°C, Abschaltverhalten unter Start-Inrush und Leitung I²t sind **offen**. Ein 3-A-Fuse allein wurde **nicht** als belastbare Stückliste freigegeben.
- **Gegenbeispiel zum Sicherheitsnachweis:** 200 V können bei einem Einzeldefekt hohe Spannung an eine nur 50 mA aufnehmende angeschlossene IC-/Leiterbahnlast liefern. Bei 350 ms = **3,5 J** mögliche Energie in einem lokalen, thermisch unbekannten Fehlerelement, aber 50 mA sind **weit unter dem 3-A-Sicherungsnennstrom**. Es gibt **keine garantierte F_MAIN-Abschaltung**. Ebenso unbekannt: sicherer Ausfall eines 60-V-MOSFET, freigrenzende Carbonisierung, sekundäre DC-Lichtbögen, Überlast auf einem 100-V-MLCC, RAW-Kabel-/Steckerbrand. Andere Fehler bei 5Ω-Quellwiderstand könnten **28,66A** oder mehr über den D302-Zener-Zweig schicken (vereinfachter fester 56-V-Clamp), was zwar möglicherweise eine Sicherung auslöst, aber weder rechtzeitige I²t-Auslösung noch sichere zerstörte Elektronik garantiert.
- Das vollständig parametrierbare Skript `tools/trippower_a_architecture_decision.py` enthält diese zwei **separaten** Gegenbeispiele, außerdem R_source=1/5/8/20/50 Ω. Die Energie in der beschädigten Elektronik ist nicht gleich der Energie der Quellenimpulsprüfung; nur Sensitivitätsmodelle.
- **Entscheid A:** Als ergänzender **Kabel-/Hartkurzschluss-Schutz unbedingt erforderlich**, aber **F_MAIN ALLEIN = NO-GO** für garantierte gefährdungsfreie Q301-DS-Kurz-200V-Einzelfehler. Ein „sicherer Totalausfall“ ist erst ein Nachweis, wenn elektrisch/thermisch gezeigt wurde, dass die tatsächlichen Versagensarten nicht zu Brand oder Fahrzeugrückspeisung führen.

### B — unabhängig gesteuerte Hochvolt-Abschaltung VOR Q301

- **Konkreter 12-Positionen-Kandidat** als **isolierter KiCad-10-Prototyp**, nicht in aktive REV5-Hierarchie aufgenommen:
  `01_Protection_LM74930_INDEPENDENT_AP74502_GUARD_PROTOTYPE.kicad_sch`.
- Controller **Diodes AP74502HQTA8-7**, AEC-Q100, TSOT-23-8. Hersteller [Datenblatt DS47093](https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf) **Single external MOSFET application (S.2)**, **200-V-unsuppressed-load-dump-HV-feed/reference (S.15)**. Ein zusätzlicher **Q401 = Vishay SQM10250E_GE3** 250V AEC-Q101 TO-263: **D2=VIN_FUSED**, **S3=VIN_A_GUARD_OUT**, **G1=AP_HVGATE**. Die OFF-Bodydiode leitet von Source nach Drain und sperrt daher positive VIN_FUSED→Q301-Richtung. Anders als ein nur zweiter FET einer common-source-B2B-Stufe wird er mit eigener U401-Überwachung **unabhängig abgeschaltet**. Original-Q301-D2 hängt nun an `VIN_A_GUARD_OUT`, übrige REV5-Netze/Pins unverändert.
- U401 **EN/UVLO1 AP_VIN_CLAMP**, GND2, NC3 unbeschaltet, **VCAP4 AP_VCAP**, VIN5 AP_VIN_CLAMP, GATE6 AP_HVGATE, OVLO7 AP_OV_SENSE, SRC8 VIN_A_GUARD_OUT. Separate **R401-403 je 3,3kΩ/2512** HV-Zuführung, D401 **56-V-Zener 1SMB5943BT3G** an AP_VIN_CLAMP, C401 **1µF100V** an GND, C402 **220nF100V** VCAP→VIN, OVLO **R404–406 je 100kΩ**, **R407=10kΩ** nach GND. Embedded exakter AP-Pinout plus tragbare `TripPower_AP74502.kicad_sym`-Bibliothek; `#FLG401` ist nur KiCad-ERC-Versorgungserklärung, **kein bestücktes oder elektrisch begrenzendes Bauteil**.
- **Fehlerpfad Q301 D-S KURZ:** Im Hochvolt-OFF bleibt VIN_FUSED durch Q401 gesperrt, selbst wenn Q301-D2 und S3 kurz sind; U301-A-/Q302-/D302-Pfad ist damit **topologisch separat abschaltbar**. Für **Q401 D-S KURZ** steht alternativ die bestehende unabhängige LM74930-Q301-OV-Abschaltung bereit, vorausgesetzt Q301 bleibt gesund und sein eigenes 200-V-SOA/Timing funktioniert. Bei mehreren fehlerhaften Schaltern, D401 offen oder gemeinsamen Versorgungsfehlern gilt keine solche Aussage.
- **Risiken dieser Architektur:** Dies ist keine bewiesene Einzelfehlerfunktion in Hardware. Q401 besitzt nur nominal **50V** Reserve über 200V vor Induktivitätsüberschwingern und bisher keine 125°C-Hot-SOA-Zusage. Hersteller-**t_off max1µs** wird bei **V_IN12V / C_G=4,7nF** spezifiziert und **gilt nicht** als gesicherter Q401-HV-FET-Gesamtabschaltwert. D401 ist neuer potentieller Einzelfehler: OPEN mit ideal 1µF/9,9k/200V ohne Last → AP-VIN überschreitet 80V absolut nach **5,06ms** (Ceff unbekannt). D401 und R401–403 tragen bei fest angenommenen 56V jeweils ~**0,291J** bzw **0,259J** in 350ms, bei 125°C keine freigegebene Temperatur-SOA. Zusätzlicher UVLO-/OVLO-/RUN-/USB-Rückspeisungspfad bleibt zu prüfen.
- **Kritisch für 9V-Start:** AP74502 spezifiziert bei **VIN>0: SRC ≤ VIN** als Absolute-Maximum. Mit vorgeschalteten 9,9k und bei rein **hypothetischen** 84+5µA Controller/EN-Strom (Datenblatt-Test **bei VIN=12V**, nicht garantiere Pumpenstrom am 9-V-Start), errechnet sich AP_VIN_pin≈**8,119V**; Q401 SRC bei Laststrom 2,389A und angenommener FET-Rds30mΩ≈**8,928V**. Das kann AP-SRC-gegen-VIN-Absolute-Maximum **verletzen**, obgleich das Referenzblatt eine ähnliche 10k+Zener-Speisung zeigt. **STOP:** Hersteller muss die tatsächlichen Test-/Intern-Clamp-/Gate-Zustände bei 9V/30V/RVS bestätigen oder es bedarf einer neuen, geprüften Speisung und Abschalt-Integration. Diese Unsicherheit verhindert eine 9-V-Start-/Fertigungsfreigabe.
- **OVLO-Schwellen** aus Hersteller-Prüfparametern: rising 1,165–1,333V, falling 1,063–1,222V, angenommene I_OV-Leck ±110nA; mit Widerstand 1% und ±100ppm/K auf 125°C statisch **Rise etwa 34,71…42,99V**, **Fall etwa 31,67…39,41V**. Nominal rise 38,75V, fall 35,43V; **30V liegt selbst unter min Fall**, daher statisch günstige Wiederanlaufreserve. Die echten Reaktionszeiten/Source-Flanken und Unterspannung/Kaltstart werden damit ausdrücklich **nicht** bescheinigt. Bei VIN=200V je OV-100kΩ im idealen rechteckigen Modell ~0,0416W/0,0146J, 125°C-/Puls-Derating ohne Hersteller-Befund offen.
- **Bestückpositionen:** REV5 unverändert **57 AUTO /58 RUN**. Neue Guard-Variante **69 AUTO /70 RUN**; **+12 Positionen**, keinerlei Übernahme der alten D306/Q307/R342. Controller AP Mouser EU als Snapshot ca **0,636€/1, 0,450€/10, 0,352€/100** (505 Stk.); Q401 Mouser DE ca **3,85€/1, 1,98€/10, 1,80€/100** (13.730 Stk.). Plus zehn weitere neue bestückte passive/Zener-Positionen **nicht vollständig preisbelegt**; also **keinen Gesamtpreis erfinden**. Exaktes CSV `WEG_A_ROUND5_FUSE_AP74502_ARCHITECTURE_BOM_2026-10-15.csv`. KiCad TSOT-23-8 Hersteller-Landpattern und 3D/PCB noch nicht unabhängig nachgewiesen.

## 2. Vergleich und Entscheidung

| Kriterium | A: externe F_MAIN allein | B: AP74502-Single-FET plus bestehende LM74930 |
| --- | --- | --- |
| Aktive zusätzliche PCB-Teile | 0 (F_MAIN und DC-Halter auf der Trägerplatine) | 12, AUTO69/RUN70, + eigenes VS-Limit |
| Einkauf | Sicherung/Halter/Kabelquerschnitt noch zu kalkulieren | AP/Q401 als reale MPNs; Teilsumme ab ~4,49€ bei1 Stück + weitere 10 Teile |
| 9V Start / 30V Restart | Ohne neue Hauptschaltung; REV5-9V selbst weiter offen; F_MAIN 3A bei heiß kritisch | 30V statisch ja; **9V AP VIN/SRC absoluter Grenzwert ungeklärt** |
| 200V/350ms | Abschalten bei kleinen Strömen nicht garantiert, lokales Gerät kann unkontrolliert versagen | Topologisch Q301-Kurz von Quelle trennbar; Q401-OV-Slew, SOA, D401 HOT unbewiesen |
| +125°C | Sicherung/Holder/R/Copp thermisch unbewiesen | Q401 Hot-/Thermik, neue HV-Zener/OV 125°C unbewiesen |
| Einzeldefekt Q301 D-S kurz | weiterhin bis 200V an SOURCE_A und U301-A/Q302/5V-Pins | **neue unabhängige, richtig orientierte HV-Trennstelle** vor defektem Q301, sofern AP & Q401 tatsächlich rechtzeitig ausschalten |
| Bewertung | **NO-GO als alleiniger Sicherheitsnachweis**, F_MAIN für Hartkurzschluss notwendig | **Bevorzugter Konstruktionspfad, aber NUR isolierter Forschungsprototyp**; Hersteller-9V-SRC-Kriterium und 200V-Grenzen verhindern Produktfreigabe |

**Management-Empfehlung:** Die zweifache unabhängige HV-Abschaltarchitektur ist bezüglich des expliziten Q301-single-short konstruktiv robuster als „F_MAIN löst schon aus“. Sie wird aber **nicht automatisch einfach oder günstig**; +12 Plätze und eine neue HV-Klemmen-FMEA sind wesentliche Nachteile. Wenn ein realer ISO-Generator und unabhängige Sicherungs-/Thermalnachweise zeigen, dass ein zerstörtes Modul deterministisch sicher ausfällt, kann Option A trotz ihres aktuellen No-Go neu evaluiert werden. F_MAIN bleibt in jedem Fall externer Leitungsschutz.

**Nächster Nachweis:** Offizielles Diodes-Support-Statement (VIN/SRC-Versorgung 9V; OV-fail-OFF und Fehlerfall Q301 short), t_OFF mit tatsächlich bestücktem Q401/Ceff bei 200V/125°C; Q401-SOA und 250V-Ringing, 200V-Generator R/L, D401/R401–403 pulse hot; echte 9V- und 30V-Bench-Wellenformen unter passender HV-Prüfausrüstung und kontrollierter F_MAIN; KiCad-10-Netzliste/ERC sind **nur Topologievalidierung**, keine Hardware-Sicherheit.

## 3. Reproduzierbarkeit

Vom Repository-Stamm:

```bash
python3 tools/trippower_a_architecture_decision.py
python3 -m unittest discover -s tools -p 'test_trippower_a_*.py' -v
# GitHub Actions: .github/workflows/trippower-a-verification.yml
# native protection-sheet alternative: reports/TripPower_A_AP74502_Guard_Build/
```

Die CI verifiziert die **echten** Schaltplan-Pinnetze gegen die Original-REV5-Netzliste (einschließlich FET-Bodydiode D2/S3), nicht nur die bloße Existenz von Labels, sowie ERC und Regressionsläufe. `TripPower_AP74502.kicad_sym` und `sym-lib-table` sind transportabel. Gegenüber Original sind **ausschließlich** Q301.D2 umgehängt und 12 neue Bauteile mit genau angegebenen Pins enthalten; `#FLG401` ist nicht bestückt. Kein PCB-Layout / DRC, keine Freigabe.

**Relevante Herstellerquellen:**
- [Diodes AP74502HQ](https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf) p2 Single-FET OV-cutoff, p3 Absolute SRC/VIN, p15 200V unsuppressed load dump mit anderer Referenzkonfiguration.
- [Vishay SQM10250E](https://www.vishay.com/docs/75035/sqm10250e.pdf) 250V NMOS D2/S3, fehlender HOT-SOA.
- [Mersen A6Y3-1](https://www.mersen.com/en/products/a6y/a6y3-1), externe 3A/500VDC-Vorsicherung (alle I²t-/Halterbedingungen im Fahrzeug offen).
- [onsemi 1SMB5943BT3G](https://www.onsemi.com/pdf/datasheet/1smb5913bt3-d.pdf) D401-Zener, hot derating.
- [Yageo AC1206](https://www.mouser.de/de/ProductDetail/YAGEO/AC1206FR-07100KL) Pulse derating muss pro MPN geprüft werden.
