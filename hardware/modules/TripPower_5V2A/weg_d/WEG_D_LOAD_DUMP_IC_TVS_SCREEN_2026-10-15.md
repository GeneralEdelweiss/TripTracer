# TripPower – Weg D: dedizierter Load-Dump-IC / Hochenergie-TVS (2026-10-15)

**Status: Markt-/Hersteller-Screen, NICHT ZUM EINBAU FREIGEGEBEN.** Nur Forschungs-Branch D. Keine Änderung an REV5, A, B, C oder dem Review-Branch. Kein neuer KiCad-Schaltplan und keine simulierte/experimentell validierte Schaltung. Datenblattversprechen sind keine ISO-Freigabe des TripTracer-Geräts.

## 1. Auftrag und feste Systemgrenzen

**Fragestellung:** Gibt es einen fertigen IC bzw. ein einziges Halbleiterbauteil, das sich gezielt um den bisher ungelösten **ungedämpften 200-V-Load-Dump für 350 ms** kümmert, sodass die Schutzstufe weniger komplex und günstiger wird? Zuerst dedizierte Surge-Stopper, zweitens ein dafür gebauter Load-Dump-TVS; keine erneute komplette eFuse/Power-Path-Architektur ohne Mehrwert.

Quelle: hardware/modules/TripPower_5V2A/REV5_DESIGN_BASELINE.json (REV5, 2026-10-15):
- Fahrzeugbetrieb am Eingang 9–30 V; ~9-V-Startziel (darunter Reset zulässig), funktionierender Wiederanlauf bei 30 V.
- Last: geregelte 5 V / 2 A plus RAW-Aux-Konstruktionsziel bis 1 A (gemeinsame Eingangsstrom-/Fehlerbetrachtung erforderlich).
- Eingangs-Sonderimpuls: **200 V Spitze, 350 ms Dauer**; keine stille Erhöhung auf 202 V. Herstellerbeispiele mit 202 V sind nur Referenzmessungen.
- Umgebung -40 bis +125 °C; F_MAIN außerhalb des kleinen Moduls, austauschbar und geeignet für Leitungs-/Leiterbahnschutz; Absicherung von BAT+/ACC und kein Rückspeisen.
- 80-V-Buck LMR38020-Q1 ist derzeit REV5-Basis, 57 AUTO / 58 RUN Bestückpositionen. Änderungen an REV5 unterlassen, solange keine vollwertig nachgewiesene Alternative existiert.
- Ein irreparabler, aber **energetisch sicherer Geräteausfall** bei einem seltenen Einzeldefekt ist akzeptabel; **Brand, heiße Leiterbahnen/Kabel oder gefährlicher Rückstrom** niemals. Ein Chip unterhalb ABS MAX im Normalfall allein genügt nicht.

**Was aus den Angaben nicht folgt:** ISO-konformes Prüfprofil ist mit 200 V und 350 ms noch nicht vollständig spezifiziert. Quellinnenwiderstand Ri, Impulswellenform/Flanken, Impuls-Wiederholanzahl, Bordnetz-/Kabelinduktivität, parasitäre Filterelemente, F_MAIN-Typ einschließlich Ausschaltvermögen und maximale thermische Anfangsbedingungen stehen noch aus.

## 2. Kandidaten / erste Go-No-Go-Matrix

| Kandidat | Funktion und belegter Punkt | Externe Hochenergie-Bauteile | 200V/350ms für TripPower? | Vorläufiger Rang |
|---|---|---|---|---|
| **Taiwan Semiconductor TLD8S36AH** (TVS, kein IC) | Spezifische ISO-Test-A-Load-Dump-TVS; AN-1003 zeigt 202 V/350 ms an 25°C mit Ri-abhängiger SOA, ~61,2 V gemessen | Ein DO-218AB-Die als Shunt; **keine Serien-FETs** im Prinzip | Quellimpedanz + 125°C + induktive Nachschwinger + F_MAIN/Fehler thermisch UNBEWIESEN | **D1: günstigste Minimalhardware, Quellenprüfung zuerst** |
| **ADI LTC4366-2, H-Grade** | Dedizierter Hochvolt-Surge-Stopper, 9 V bis >500 V mit schwimmender Architektur, Timeout & 9 s Cooldown, Auto-Retry | 1 externer HV-N-FET, Timer- und Versorgungs-Bauteile, Teiler | 200 V Eingang grundsätzlich möglich; bei 350 ms möglicherweise lineare MOSFET-Hochverlustleistung; 9-V-Einschaltgefahr | **D2: klarster reiner Schutz-IC** |
| **ADI LTC4380-2, H-Grade** | Surge Stopper mit einstellbarer OV-Klemme, Strombegrenzungs-/Timerkonzept; EVM mit ISO-Test-A-Bezug | 1 externer HV-FET, Rsense, Versorgung/Zener, Teiler | EVM 0,5 A; explizite 250-V-Angabe nur für 1 ms, keine Freigabe unserer Last | **D3: hochwertig, mehr Funktionen/Teile** |
| **ST LDP01-35AY** (TVS) | Load-dump-spezifische AEC-Q101-TV S, ca. 30-V-Arbeitsbereich | 1 D2PAK TVS | Die vorliegende Test-A-Grafik belegt nicht 200V/350ms für 24V-Test A | Bedingt/kein 200V-Nachweis |
| TI LM74930-Q1 | Bestehende REV5-Basis (Verpolung, OVP, Überstrom, 200V-Referenz) | mehrere FETs/Versorgung/Detektoren | Vorhandene Einzelfehler A/Q301 short und Widerstands-/Zener-Überlast offen | Vergleich, nicht „nur Load Dump“ |
| Diodes AP74502HQ | Datenblatt mit 200-V-Test-A-Beispiel | zwei FETs, VIN-Zener, Widerstände | Eingangs-FET short → zweite Bodydiode → 200V an nachfolgenden ICs | Vergleich B/C, nicht reiner Schutz |
| ADI LTC4364 | Surge Stopper mit Idealdiode und Strombegrenzung | FETs und Shunt, Beschaltung | kein 200V/350ms-Vollastbeweis | mehr Komplexität |
| ADI LTC7860 | schaltende Surge-Stopper-Architektur | Spule, FET(s), Strommessung, Kondensatoren | 200V+ per Auslegung möglich, aber Hochvolt-Auslegung statt einfaches Bauteil | Priorität niedrig |

**Methodik:** „200 V tolerant“ bedeutet hier NICHT „350 ms +125°C und alle Fehler bestanden“. 6,6-kW-TVS-Datenblattwert bezieht sich auf **10/1000 µs**, NICHT auf 350 ms. Spannungsratings von IC, VS-Pins, externen FETs und nachgeschaltetem 80-V-Buck getrennt behandeln.

## 3. D1 – Spezialisierte Load-Dump-TVS TLD8S36AH

### Harte Herstellerangaben

Taiwan Semiconductor Anwendungshinweis **AN-1003**, Version A1901, S. 3, Fig. 5 und Tab. 1:
- ausdrücklich ISO 16750-2 Test A, 24-V-System und TLD8S36AH als 36-V-TVS.
- Fig. 5 gibt bei Vs = 202 V und Td = 350 ms einen minimalen Ri von ungefähr **4,5 Ω** an.
- Die textliche Beispielrechnung nennt Ri = 4,5 Ω, prüft aber dann mathematisch mit **3,5 Ω** und enthält die Tabelle **Ri=3,5 Ω, Ipp=42,8 A, Vc=61,2 V, P_peak=2619 W, Ta=25 °C**. **Widerspruch: SOA-Grafik 4,5Ω, Tabellen-/Textbeispiel 3,5Ω!** Quelle beim Hersteller klären; weder 3,5Ω noch 4,5Ω als universell garantierten Grenzwert ausgeben.
- Maximale nachgewiesene Dauerklemmspannung für die genannten Randbedingungen aus der Messung ~61,2 V, nicht Worst-Case bei +125°C oder anderem Ri. Die nominelle 36-V-Arbeits-/Standoff-Spannung bedeutet bei 30 V Dauerbetrieb keine wesentliche aktive Shuntlast, aber Leckstrom/Temperatur/Startfolge neu prüfen.
- Qualifikation AEC-Q101, unidirektional, DO-218AB, Tj -55 bis +175°C laut Produktangebot. **Wichtig: 175°C zulässige Tj ≠ 200-V-350-ms-Nachweis bei Ta +125°C.**

Quelle Hersteller: https://services.taiwansemi.com/storage/resources/application-note-17/AN-1003_Automotive%20circuit%20protection%20of%20load%20dump%20TVS_A1901.pdf

Beschaffung 15.10.2026, Reichelt Deutschland, **TLD8S36AH MAG**, Artikelnummer **TLD8S36AH**: 1 St **1,85 €**, 10 St **1,720 €/St**, 100 St **1,572 €/St**, **jeweils inkl. 19% MwSt., ohne Versand**. Als **Restposten, begrenzte Stückzahl** gelistet, 1–2 Werktage; somit Liefer-/Serienrisiko. Keine Aussage zur Menge, die für 100 Geräte tatsächlich verfügbar ist. Link https://www.reichelt.de/de/de/shop/produkt/tvs-diode_unidirektional_36_v_6600_w_do-218ab-273917 . DigiKey als zweiter Distributor vorhanden, Preise netto in anderer Marktregion; nicht mit Reichelt-Bruttopreisen vergleichen.

### Technische Chancen und Stopps

**Idee:** TLD8S36AH direkt am abgesicherten Eingang als Shunt klemmt den Test-A-Impuls bei spezifizierter Generatorimpedanz in Richtung 60–65 V. Ein 80-V-LMR38020-Q1 könnte solche Pegel potenziell aushalten. Sie reduziert die Gefahr, dass 200 V überhaupt über Q301-Short oder FET-Bodydioden-Fehler in den ganzen Schutz-/Buck-Pfad gelangen. **Aber** gemessene 61,2V sind kein garantiertes lokales VIN-Pad-Maximum und auch 60-V-Q302/65-V-LM74930-Pinlimits werden nicht automatisch eingehalten. Kein 1:1-Austausch ohne alle eingebauten Grenzwerte/Resonanzen zu prüfen.

**Wesentliche Nachteile:**
1. Energie wird direkt im Shunt umgesetzt. Bei 202 V, Ri 3,5Ω, angenommener konstanten 61,2V beträgt anfangs I≈40,2A, P≈2,46kW, rein rechnerisch 0,35s konstant ≈861J. **Hypothetische Rechteckrechnung, nicht gemessene Impulsenergie** – reale Load-Dump-Spannung klingt ab; Energieintegration aus tatsächlichem Testgenerator und Pulsform notwendig. Hersteller hat einen raumtemperierten Versuch gezeigt, kein thermisches Worst-Case-Versprechen.
2. Mit Ri=1Ω flössen im rein ohmschen Vergleich (200−61,2)/1≈138,8 A, praktisch andere dynamische Klemmspannung und unbestimmte TVS-SOA; **nicht als zulässig betrachten**.
3. TVS-Single-Fault SHORT: Strom am BAT+-Kabel/F_MAIN mit realem Ri und 200V während Sicherungsöffnung; F_MAIN muss über ausreichend DC-Spannungs-Ausschaltvermögen/I²t und die Leitungen thermisch sicher öffnen. TVS-Single-Fault OPEN: VOLLE 200 V am Modul, dann muss Modulversagen zumindest gefahrlos bleiben; TVS allein kann ohne weitere belegte Energie-/Leitungsbarriere keine Einzelfehler-Sicherheitsgarantie liefern.
4. Bei –40..+125°C Ta, Wiederholimpulsen, Leiterplatten-Kupferfläche, Verpolschutz, Batterie-Mismatch und 80V-Buck/60V-FETs keine Freigabe.
5. Werksfreigabe einer auslaufenden Reichelt-Restposten-SKU nicht als 100-Stück-Beschaffbarkeit darstellen.

**Einordnung:** Billigster und kompaktester Ansatz für die *normale* Impulsbeherrschung, sobald Generator-Ri, Worst-Case-Ta und Klemmenwerte verbindlich und die gefährlichen OPEN/SHORT-Folgefehler beherrscht sind. Noch KEIN Weg-D-Go.

## 4. D2 – Dedizierter Surge-Stopper-IC LTC4366-2

Hersteller ADI „LTC4366 High Voltage Surge Stopper“ Rev F: https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf . Produkt https://www.analog.com/en/products/ltc4366.html .

**Exakte Zielvariante:** LTC4366HTS8-2#TRMPBF, H –40..+125°C, 8-Pin TSOT-23. 9 V bis >500 V als *System-/Controller-Topologiebereich*, nicht zulässige direkte 500V an irgendeinem Pin. Ein externer N-MOSFET regelt Ausgang bei Überspannung (FB-Teiler), Timer kann danach abschalten; **-2** startet nach 9 s interner Abkühlzeit automatisch neu, **-1** bleibt verriegelt. Shutdown <14 µA spezifiziert; 100µA gesamtes TripPower-OFF ist damit **noch nicht bewiesen**.

**Nicht so einfach wie „ein IC“:** Externer ≥250/300V-MOSFET samt ernsthafter 200V/350ms linearem SOA, hochspannungsfeste Serienwiderstände, Versorgungs-/Timer-Cs, Feedback-Teiler, Gate-Bauteile. **Keine integrierte, unabhängige F_MAIN-Ersatzfunktion bzw. vollständige Strombegrenzung.** Bei linearer Begrenzung wäre bei Vclamp=35 V, Vin=200 V und Laststrom 1 A P_FET=(200−35)*1=165 W; bei konstant 2 A 330 W. Ein Schutz-Timer kann früh abschalten, statt 350ms alle Energie zu verheizen. Timerfunktion nur mit Hersteller-/Hot-SOA und realem Zeitprofil dimensionieren. 9-V-Start: Datasheet warnt ausdrücklich, dass bei zu geringer Versorgung und hoher Last der MOSFET **ohne Timeout thermisch überlastet werden** kann. Ein selbstentworfener zweiter Kurzschlussschutz könnte Preis- und Teilevorteil aufzehren.

Beschaffungssnapshot 15.10.2026 **DigiKey DE**: LTC4366HTS8-2#TRMPBF **10,42 €/1, 8,174 €/10, 6,996 €/100**, **netto ohne Versand**; listet Lagerbestand >10k beim Abruf, schwankt. https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4366HTS8-2-TRMPBF/2825884 . EVM **DC1850A-B** ist Forschungs-/Evalplatine, keine geprüfte TripPower-Lösung.

**Unabhängiger MOSFET D-S-SHORT:** Einfacher serieller FET lässt 200V vollständig durch. LTC4366-2 hat somit ebenfalls **keine Single-Fault-HV-Trennung**. Im akzeptierten Sicherheitsziel ist dies nur vertretbar, wenn nachfolgende Ausfallenergie/F_MAIN/Leitungen nachgewiesen werden; sonst zusätzlicher Barrierenaufwand. FET-Hot-SOA, 9V-Weichstart, 30V-Recovery, Zuverlässigkeit/Leckstrom und End-BOM vor jeder Verwendung vollständig prüfen.

## 5. D3 – LTC4380-2 und historische Alternativen

ADI LTC4380: https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4380.pdf ; EVM DC2178A-B: https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/dc2178a-b.html ; User Guide https://www.analog.com/media/en/technical-documentation/user-guides/dc2178af.pdf .
- LTC4380 bietet SURGE-Timer und Strommessung, 4–72/80V eigene Pinlimits je Varianten/Datenblatt, **200V extern nur mit Hersteller-HV-Beschaltung/Zener**, nicht direkt am IC.
- Für das EVM wurde 24/28V-System, 0,5 A demonstriert. 250 V ist als **1-ms-Transient** benannt, **nicht** 250V/350ms. Kein 2A-plus-RAW-Validierungsbeleg.
- LTC4380-2 Auto-Retry unter relevanter Datenblatt-Variante/Timing prüfen; kein kategorischer Einzelfehlerschutz bei MOSFET D-S SHORT.
- ST LDP01-35AY: https://www.st.com/resource/en/datasheet/ldp01-35ay.pdf ; AEC-Load-Dump-TVS, vorhandene Herstellerkurven kein belastbarer 200V/350ms-Nachweis im 24V-Fall. Nicht aus der Bezeichnung ISO Test A die konkrete 200V/350ms-Fähigkeit ableiten.
- TI LM74930-Q1: https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf ; https://www.ti.com/document-viewer/lit/html/SNOAAA1/GUID-A29F6540-095F-4408-8FD4-388A1740884B . Kombiniert ideal-diode/OVP/eFuse etc, bereits REV5, COTS-Referenz aber kein reiner Load-Dump-Chip.
- Diodes AP74502HQ: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf . 200-V-Herstellerbeispiel, ohne 350ms/125°C/Single-Fault-Proof. B-Faultgraph: Eingangsfet kurz + andere FET-Bodydiode leitend.
- ADI LTC4364: https://www.analog.com/en/products/ltc4364.html (mehr Funktionen, mehr Beschaltung).
- ADI LTC7860: https://www.analog.com/en/products/ltc7860.html (Schutz durch geregeltes Schalten, aber zusätzliche Spule/Schalt-MOSFETs).
- TI LM74800-Q1 und Diodes AP74502HQ sind keine magischen einteiligen 200V/350ms-Fuse-ICs, sondern Gate-Controller mit HV-Beschaltung; daher nicht priorisiert.

## 6. Risiko-Matrix: gefährlicher Ausfall vs. tolerierbarer Totalausfall

| Fehlerfall | D1 Shunt TVS | D2 LTC4366-2+FET | Muss vor Freigabe belegt sein |
|---|---|---|---|
| Normale Test-A-200V/350ms | Bei begrenzter Ri ggf. ~61V, Energie im TVS | Gate regelt/Timer schaltet, Energie teils im FET | Gemessene Pulse bis maximal Ta; SOA und V(Pad) |
| 200V mit kleiner Generatorimpedanz | TVS kann durch thermischen Stress ausfallen | FET kann durch SOA-Stress ausfallen | Quellgenerator-MinRi, Ausfalltemperatur |
| Ein Bauteil OPEN | TVS OPEN: 200V ungedämpft | FET OPEN: sichere stromlose Last (ggf. Bodydiode/Reverse untersuchen) | Nachfolgende Fehlerfolge nicht energiereich |
| Ein Bauteil SHORT | TVS SHORT: sehr hoher F_MAIN-Strom | FET D-S SHORT: volle 200V an Ausgang | Echte Sicherungskoordination / Strompfad / Brandschutz |
| 9V Start/30V Restart | TVS üblicherweise passiv, System sonst unverändert | Controller 9V-Untergrenze, 9V hohe Last kritisch | Dynamischer Hot/Cold Start, UVLO/OVP-Toleranz |
| Kabel/Steckverbinder | Hoher TVS-Shuntstrom im Modul | Stromfluss je Versagensart | Leitungs-/Kupfer-/Steckverbinder-Impuls-I²t und F_MAIN-Ausschaltvermögen |

**Sicherung ausdrücklich nicht als Ersatz für den unmittelbaren Spannungsbegrenzer missverstehen.** Eine nominelle Automotive-32V-Sicherung ist nicht automatisch zum **Unterbrechen eines 200V-DC-Fehlerstroms** zugelassen. Maximaler Lichtbogen und Energie bis zur Öffnung müssen nach Herstellerdaten samt Quellwiderstand überprüft werden. Ein ungefährlicher Geräteausfall genügt, aber kein ungeregelt glühender Last-/Shunt-Pfad.

## 7. Wirtschaftlichkeit: bisher nur halbleiterspezifische Teilpreise

**Nicht Gesamtmodulkosten!** Baseline REV5 57/58 aktive Positionen. Weg D wurde noch nicht als echte KiCad-Alternative gezählt; Einsparung wäre verfrüht. Genaue hinzukommende/entfallende VIN-, Filter-, Schutz- und DNP-Bauteile, SOA-gerechter FET, isolierte Sicherung und Layoutflächen sind noch zu ermitteln.

| Bauteil | Distributor / Datum | 1 St | 10 St | 100 St | Steuer-/Bewertungsbasis |
|---|---|---:|---:|---:|---|
| TLD8S36AH MAG | Reichelt DE, 2026-10-15 | 1,850 € | 1,720 € | 1,572 € | **brutto DE inkl. 19% MwSt.**; Restposten |
| LTC4366HTS8-2#TRMPBF | DigiKey DE, 2026-10-15 | 10,420 € | 8,174 € | 6,996 € | **netto**, ohne HV-FET/Passives |

**Die 1,85 € sind für die konkrete Diode, nicht die komplette technische Schutzarchitektur.** Ein korrekt nachgewiesener TVS kann ggf. sämtliche aktiven Load-Dump-Zusatzteile vermeiden; es fehlen dafür die Schutz- und HOT-Proofs.

## 8. Weg-D-Arbeitsgates und Entscheidung

**D-01 [BLOCKED]** Testquelle als Ersatzschaltbild mit Ri_min/max, Wellenform, Anstiegszeit, Kabellänge/-induktivität und Wiederholimpuls definieren. Erst danach D1-AN-1003-SOA gegen Quelle legen.

**D-02 [BLOCKED]** Taiwan Semiconductor zu Fig.5 (Ri=4,5 Ω) vs. Tab.1 (Ri=3,5 Ω) schriftlich befragen und vollständige SOA-Daten bei Ta +125°C für 200V/350ms + Wiederholungen und Einzelteil-Toleranz verlangen.

**D-03 [BLOCKED]** TVS-Failure OPEN/SHORT an nicht mehr schützender Eingangskette / echte F_MAIN-DC-Unterbrechbarkeit 200V und sichere thermische Wirkung berechnen/testen.

**D-04 [BLOCKED]** Maximalen Eingangs-Pad-Peak und Ringing für 80V-Buck, 60V-Q302, 65V-VS und 250V-Q301 ermitteln; entweder komplette REV5-MOSFET-Stufe vereinfachen oder TVS nur als ergänzendes Gegenmittel mit **vollen** Bauteilkosten ausweisen.

**D-05 [BLOCKED]** LTC4366-2 Timer/Hot-SOA/9V Start bei schlechtester Last, 30V-Erholung und Single-Fault-FET-Short prüfen; ggf. gegen D1 und Ausgangssicherung vergleichen.

**D-06 [BLOCKED]** Vollständige vergleichbare BOM (IC/FET/Diode/R/C/Inductor; Reichelt/DigiKey, Preise 1/10/100 netto/brutto trennen; PCB-Fläche und Handbestückung) sowie KiCad-10 ERC/Netlist, echte PCB-DRC, Labor-Test A/EMV erst beim gewählten Entwurf.

### Managementempfehlung 15.10.2026

**Zwei parallele kurze Prüfpfade, kein neuer langwieriger Schaltplan:**
1. **Kosten-/Teilezahl-Leitkandidat TLD8S36AH** als einzelnes explizit Load-Dump-kompetentes Schutzbauteil. Pro: Reichelt, günstig, AN-1003 auf fast unserem 200V/350ms-Profil. Contra: Quellen-Ri und Ta+125°C-SOA, F_MAIN bei SHORT, Restposten.
2. **Reiner IC-Leitkandidat LTC4366-2**, wenn D1 am Quellen-/Temperatur-Gate scheitert. Pro: 9V..>500V mit HV-Schalter-Architektur/Timer und Auto-Retry. Contra: großer FET/lineare Hitze/9V-Startup, Kosten, keine eigenständige Strombegrenzung.

Keiner wird vor Abschluss D-01 bis D-06 produktiv integriert. **Gefährliche Energie kontrollieren, nicht bloß 200V für jedes IC ohne Schaden überstehen.**

## 9. Quellenlage und Review-Referenzen

- REV5: hardware/modules/TripPower_5V2A/REV5_DESIGN_BASELINE.json und REV5_OPTIMIZATION_IMPLEMENTATION_2026-10-15.md, Branch design/solid-state-power-v1.
- A/B/C unabhängiger Management-Review: docs/TRIPPOWER_A_B_C_REVIEW_ROUND4_2026-10-15.md, Branch design/trippower-review.
- Herstellerquellen direkt in den vorstehenden Kandidatenabschnitten. Die Markt-/Preissnapshots sind ausdrücklich zeitgebunden; kein Preis bedeutet nicht „0€“.
- **Dokumentationspflicht für Folgearbeiten auf Weg D:** Jede wesentliche Datenblattkorrektur, Alternativ-MPN, geprüfte Grenze, Händlerpreisänderung, FMEA und Simulation/Labortest als datierten Commit auf **design/trippower-d-load-dump** plus Eintrag in FINDINGS_LOG.md. Erst nach Managemententscheidung Änderungen an Baseline/A/B/C erwägen.
