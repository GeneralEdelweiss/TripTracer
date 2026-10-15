# Weg D Round 6: prüfbarer technischer Entscheid (2026-10-15)

**Management-Entscheid: NO-GO für einen einzigen TVS als vollständigen TripPower-200V-Eingangsschutz.** Ein gewöhnlicher Geräteausfall ist erlaubt, aber Brand, unkontrollierte Fehlerenergie und Rückspeisung nicht. **Bourns SM8S36A-Q** ist der stärkere, beschaffbare TVS-Laborkandidat; **LTC4366-2** ist der funktionell passendste reine Surge-Stopper-IC, aber kein einfacher preisgünstiger 1:1-Ersatz des REV5-Schutzes. **Kein** KiCad-Prototyp, weil die vorgeschriebenen P0-Safety-Gates nicht geschlossen sind.

## Quellen- und Projektbasis

Gelesen: Review Round 6 auf design/trippower-review, Vorgänger-Screen und FINDINGS_LOG, REV5_DESIGN_BASELINE.json, AGENTS.md und POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md. Anforderungen: Normalbetrieb **9–30V**, 5V/2A plus RAW bis 1A, **200V/350ms**, Ta -40..+125°C, 9V-Anlauf/30V-Wiederanlauf, austauschbare externe und DC-taugliche F_MAIN, Entkopplung und frühes PWR_FAIL für separat versorgte kritische TripTracer-Backup-Domain. REV5 bleibt unverändert bei 57 AUTO/58 RUN.

Evidenzklassen: [DATENBLATT] garantierte Angaben nur unter ausdrücklich angegebenen Bedingungen; [AN/OEM] konkretes Herstellerbeispiel/SOA-Diagramm; [RECHNUNG] idealisierte Szenarien; [OFFEN] Herstellerfreigabe oder Messung fehlt. Kein ISO-/Fertigungs-/Fahrzeugnachweis.

Herstellerdaten:
- TSC AN-1003 S.3 https://services.taiwansemi.com/storage/resources/application-note-17/AN-1003_Automotive%20circuit%20protection%20of%20load%20dump%20TVS_A1901.pdf
- TSC TLD8S-Serie E2310 S.1–4 https://services.taiwansemi.com/storage/resources/datasheet/TLD8S10AH%20SERIES_E2310.pdf
- Bourns SM8S-Q (SOA-Diagramm S.4, 10 Pulse) https://www.bourns.com/docs/product-datasheets/sm8s-q.pdf
- LTC4366 Rev F S.1/8/15/20 https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf
- SCHURTER SPT 5x20 https://www.schurter.com/de/datasheet/typ_SPT_5x20.pdf
- SCHURTER FEU (Sicherungshalter) https://www.schurter.com/en/datasheet/typ_feu.pdf

## P1: AN-1003 ausdrücklich widersprüchlich

**[AN] Figure 5 auf PDF-Seite 3:** grüne Kurve 350ms und Vs=202V: **Ri ungefähr 4,5Ω**. Lineare Interpolation auf 200V ergibt ca. 4,45Ω, aber **keinen** qualifizierten Grenzwert. **[AN] Fließtext:** zuerst Beispieleinsatz Ri=4,5Ω, anschließend plötzlich Prüfung für Ri=3,5Ω. **[AN] Tabelle 1 und Scopefoto:** TLD8S36AH, Vs=202V, td=350ms, **Ri=3,5Ω, Ipp=42,8A, Vc=61,2V, Ppeak=2619,36W, Ta=25°C**. **[RECHNUNG]** (202-61,2)/3,5=40,23A, leicht verschieden vom Ipp-Messwert. Quellenimpedanz/Spektrum/Messzeitpunkt erklären die Differenz nicht eindeutig. Dass ein Exemplar mit 3,5Ω gemessen wurde, beweist keine garantierte Serien-SOA bei 3,5Ω und 25°C, erst recht nicht bei 125°C.

**[DATENBLATT] E2310:** TLD8S36AH VWM=36V, VBR=40,0–44,2V bei 5mA, **Vc max58,1V bei 114A / 10/1000µs**, typische RthetaJC=0,8°C/W mit idealem Kühlkörper, maximal Tj175°C, VBR-Tempkoeffizient typisch +0,091%/K. Keine dieser Angaben liefert Vc_max oder Pulsenergie für 350ms bei Ta125°C. Beispielrechnung VBR,max(125)=44,2×1,091≈48,22V; darf NICHT direkt auf Vc übertragen werden. **[OFFEN] Herstellerkontakt**: schriftliche Klärung Fig.5 versus Tabelle, Chargengrenzen, Ri_min/Temperatur, wiederholte Impulse, 350ms-Vc(t) und Setup. Keine Herstellerantwort eingeholt oder behauptet.

**Regel bis zur Klärung:** TSC höchstens mit graphisch ersichtlicher ~4,5Ω bei 25°C als unverbindlicher Laborvergleich; 3,5Ω als Einzelmessung, nicht als garantierter Grenzwert.

## P2: Thermik, Quellimpedanz, integrierte Energie

**[RECHNUNG, nicht ISO-Generator]** Idealisiere TVS mit *konstanten* 61,2V aus einer 25°C-TSC-Tischmessung und einer Thevenin-Quelle mit Ri. TVS ohne Laststromabzweig: i(t)=max(0,(Us(t)-61,2)/Ri), P=61,2i, E=Integral(Pdt), 0..350ms. Zum Zeigen der Pulsform-Sensitivität: CONSTANT=200V für 350ms; LINEAR=200→28V in 350ms; EXP10=28+172×10^(-t/350ms), endet bei45,2V. Die beiden abfallenden Modellwellen sind **keine** behaupteten ISO-16750-2-Wellen. Der konstante Rechteckimpuls ebenfalls nicht.

| Ri Ω | Ipeak A | Ppeak W | E CONSTANT J | E LINEAR J | E EXP10 J |
|---:|---:|---:|---:|---:|---:|
| 1,0 | 138,80 | 8495 | 2973 | 1200 | 783 |
| 3,5 | 39,66 | 2427 | 849 | 343 | 224 |
| 4,5 | 30,84 | 1888 | 661 | 267 | 174 |
| 6,0 | 23,13 | 1416 | 496 | 200 | 131 |

**Reproduzierbar:** load_dump_scenarios.py und test_round6.py im selben Ordner. Numerische Mittelpunktintegration mit 20000 Schritten; isoliert von RLC, Temperatur, TVS-Differentialwiderstand, Serienverdrahtung, realem ISO-Puls und Nachbarknoten. Die Breite der Energiespanne zeigt, warum 200V/350ms *ohne* Us(t), Ri und reale Pulse keine thermische Freigabe erlaubt.

**[DATENBLATT]** TSC E2310 Fig.1: 8W stationär bei Gehäuse25°C linear gegen 0W bei175°C; bei Gehäuse125°C **ungefähr 2,67W stationär**, nicht 350ms-SOA! Fig.2 beschreibt **10ms exponentiell**, Fig.5 typische transiente thermische Impedanz, keine garantierte Tj,max-Vorhersage für unser 350ms-Profil. Alleine die thermische Headroom-Spanne bis Tj175°C sinkt von 150K bei 25°C Start auf **50K bei 125°C Start**. 1/3 Headroom ist **keine** erlaubte lineare Reduktion von Ri oder 350ms-Pulsleistung. **[OFFEN]** Tatsächliche Integration E, Tj(t), Ta125, Gehäuse-Heatsinking, Folgetrigger und 10 Pulse (Hersteller-Intervall!) fehlen.

**Layout-Gate:** DO-218AB nahe Eingang nach F_MAIN, kurze dicke Hochstromleitung zur Batteriemasse; Spannungs-/GND-Knoten hinter Surge-Abzweig abgreifen, keine 30–50A über RAW-/Buck-/Ground-Signalbahnen. Kupferflächen/thermal Vias, hohe Padabreißkräfte, 125°C/Vibration und dauerhafte Wärmebelastung messen. Layout **verringert** Impedanz, garantiert keine Hot-SOA.

## P3: maximal mögliche Spannung an nachgeschalteten Pads

**61,2V ist OEM-Messwert bei 25°C**, keine Worst-Case-Grenze. Schon dieser Wert überschreitet **60V-Q302-Domäne** und lässt nur **3,8V zu 65V** und **18,8V zum 80V-Buck**. Der Herstellerwert max Vc58,1V bei114A/10/1000µs ist **nicht** in 350ms übertragbar.

**[RECHNUNG]** Induktiver Anteil V_L=L*(di/dt): bei L=1µH, ΔI=42,8A in10µs -> **+4,28V**, beispielhaft 61,2+4,28=65,48V; bei L=0,5µH, ΔI=42,8A in1µs -> **+21,4V**, beispielhaft 61,2+21,4=82,6V. Das Vorzeichen, Überschwingung und reale RLC-Abklingung sind **topologieabhängig**; es sind Sensitivitätsszenarien, keine gemessenen Peaks.

V_PAD,max muss je Q302 Source, LM74930 A/VS, Regler-VIN, C306 und RAW-Connector aus max über t von V_TVS(I,T,Streuung)+I*Rtrace+Ldi/dt+RLC-Ringing bewertet werden. Ohne definierte Quelle/PCB/Vc(I,T) **kein endliches qualifiziertes Maximal-Pad-Ergebnis unter 60/65/80V**. Bei TVS-OPEN liegen **200V plus mögliche lokale Ringing-Spitzen** am Eingang. Weder Q301-Short noch AP74502-Eingangsfet-Short wäre damit als gefährlicher Strompfad ausgeschlossen.

**P3-Entscheidung: NO-GO TVS als einziger Schutz vor der unveränderten REV5-60/65/80V-Kette.**

## P4: TVS SHORT/OPEN, F_MAIN und Schmelzsicherheit

**Einfaches hypothetisches System:** BAT+ -> serviceable **F_MAIN** -> VIN_FUSED; TVS von VIN_FUSED zur Fahrzeugmasse; danach erforderlicher eigenständiger Verpolschutz, sicherer Strompfad, 5V-Buck, RAW-Aux-Leitung und Backup-Isolation. F_MAIN ist kein automatisch separater TVS-Zweigschutz.

**TVS SHORT:** mit reinem Ri=3,5Ω und 200V konstant ergäbe sich I=57,14A, über350ms formal **1143 A²s** wenn KEINE Unterbrechung stattfindet. *Keine* Vorhersage realer Sicherungs-Leitungsenergie. **Schurter SPT 0001.2509 3,15A** ist ein **konkreter F_MAIN-Forschungskandidat** mit **300VDC-Nennspannung, 1500A DC-Ausschaltvermögen laut angegebenen UL-Bedingungen, nominal Schmelz-I²t 33,7 A²s, -55..125°C**; Quelle https://www.digikey.de/de/products/detail/schurter-inc/0001-2509/639709 . Wichtig: nominales **Schmelz**-I²t != gesamt **Abschalt**-I²t mit DC-Lichtbogen, verifiziertem Schutz von PCB/Kabel bei Ta125°C und unbekanntem Ri. Auch bei geringerem Strom, z.B. VIN30V an Rsrc groß, Zeit/Stromkennlinie prüfen. Bei 9V und 5V2A+RAW1A sind ~2,4A Eingang als begründete Wirkungsgradannahme möglich; die 3,15A-Sicherung kann temperatur- und lebensdauerbedingt zu knapp sein. Die 4A-Schurter-Variante ist **nur 150VDC**, keine automatische Lösung.

**Halter:** SCHURTER FEU 0031.1751 mit 600VAC/DC nach UL, jedoch Datenblatt Ta nur **-40..+85°C**, also bei 125°C Einbauort STOP. Wenn F_MAIN nachweisbar außerhalb der +125°C-Umgebung montiert ist, separat validieren; keine stille Ausnahme. https://www.schurter.com/en/datasheet/typ_feu.pdf .

**TVS OPEN:** 200V gelangen ohne aktive unabhängige Sperre an 80V-Buck/60V-FET/65V-IC-Domänen. Es ist möglich, dass Bauteile heiß niederohmig statt friedlich offen versagen; die Sicherung ist nicht verpflichtet, bei zerstörerischen Strömen **unterhalb** ihrer Abschaltgrenze auszuschalten. Deshalb nicht behaupten, F_MAIN allein erlaube „sicheren Geräte-Totalausfall“ unter jedem OPEN-Fehler. **No-Go für Single Barrier** bis Messungen/FMEA/Safe-Fail-Zertifikat. Kurzgeschlossene Leiterbahn, Sicherungshalter-/Kontaktwärme, Kabel-L und Spannungs-/Temperaturkoordinierung erfassen.

**F_MAIN-Fazit:** Erste reale spannungsfeste 300VDC-Sicherung ist gefunden, aber Schmelzenergie, Lichtbogen, Holdersystem und eigene heißeste Einzelfehlerkette offen.

## P5: Beschaffbarer Ersatz und LTC4366-2

**Bourns SM8S36A-Q (unidirektional, NICHT CA)**: AEC-Q101, aktive Serie, DO-218AB, VWM36V, VBR40..44,2V, DS Vc58,1V bei 114A 10/1000µs. Bourns DS S.4 zeigt **ISO16750-2 Test A (10 Pulse)** für **SM8S36A** bis Vs202V/350ms, am rechten Diagrammrand liest sich für350ms **Ri ungefähr 2Ω bei UA28V** ab. Das ist eine **OEM-SOA-Performancegrafik**, kein +125°C-/max 350ms-Vc-/Footprintnachweis. DigiKey DE https://www.digikey.de/en/products/detail/bourns-inc/SM8S36A-Q/9922432 : lagernd (Snapshot ~2160), 1/10/100 **3,740/2,453/1,620€ netto**, aktueller „active“ Status. Mouser als zweite Listung https://www.mouser.com/en/ProductDetail/Bourns/SM8S36A-Q . Deutlich besser belegter Wiederholungstest als TSC, **kein** unmittelbarer Hot-Go.

TSC TLD8S36AH bleibt auch bei LCSC und DigiKey als „aktiv“/lagernd auffindbar; Reichelt-Angebot war Restposten beim Einzelhändler, **nicht** erwiesene Hersteller-EOL. TSC-Snapshot Reichelt 1,85/1,72/1,572€ **inkl. 19% MwSt.** für 1/10/100; Umrechnung für Vergleich in Nettowerten im BOM-Bericht. Quellen https://www.reichelt.de/de/de/shop/produkt/tvs-diode_unidirektional_36_v_6600_w_do-218ab-273917 und https://www.lcsc.com/product-detail/C19855393.html .

**ADI LTC4366HTS8-2#TRMPBF:** dedizierter Hochvolt-Serien-Surge-Stopper 9V..>500V Systemtopologie, H -40..125°C, externer Leistungs-NMOS, Timer und Auto-Retry (9s nomineller Cooldown). VDD-/OUT-Pins im **floating** Controller besitzen kleine relative ABS-MAX-Ratings; kein direkter 200V-Silizium-Pin. Herstellerbeispiel DS S.1: 1x IC, **IXTK90N25L2** 250V großer TO-264-MOSFET, 5 Widerstände (324k/10Ω/12,4k/422k/46,4k), 3 Kondensatoren (2nF/0,47µF/1µF), insgesamt **10 elektronische Positionen** ohne F_MAIN/Halter, Verpolung, 5V-Buck, RAW, Power-Fail und Backup-Entkopplung. Das gezeigte 28V/1,5A-**43V-Clamp-Beispiel ist KEINE** fertige 9V-35V-Neuauslegung. ADI zeigt separat eine 9V-Anwendung (DS Low Voltage Application, RSS1,91k) – Pinbudgets und Last neu nachrechnen.

**Linearer FET-Puls als Worst-Case-Szenario:** bei Vout-Clamp35V und Vin200V P_FET=(200−35)*I: **165W @1A**, **330W @2A**, **412,5W @2,5A**. Für 350ms linearer Durchlauf ohne nachgewiesene große Hot-SOA/Kühlkörper absurd für kleines Modul. Die LTC4366-2-**frühe Abschaltung** ist dagegen funktionell interessant, da TripPower ausfallen darf: Datenblatt TIMER-Pin offen -> Overvoltage-Timeout ~1µs; mit CT in µF rund311ms/µF, etwa **0,622ms mit 2nF**. Rein fiktiv 330W×0,622ms≈0,205J; Schaltflanken, MOSFET-startup-SOA, Hot-Qg, Last, ESR und Retry nicht enthalten. ADI warnt vor 9V-Startup bei hoher Last und verlangt MOSFET-SOA-Timer-Koordination.

**Kosten:** LTC4366 IC 10,42/8,174/6,996€ netto (1/10/100; DigiKey DE); Herstellerbeispiel IXTK90N25L2 37,57€ netto/1, 23,5625€/100; 10er Staffel unbekannt. **Nur IC+FET = 47,99€ bei 1 St und 30,5585€ bei100**, gegen TVS wenige Euro, **ohne weitere 8 Positionen** und andere Systemschienen. IXTK90N25L2 ist für Kleinplatine auch mechanisch unattraktiv. Kleinerer FET derzeit ohne lineare SOA nicht nachgewiesen. **Fehler FET D-S SHORT:** direkt 200V an nachfolgenden Pins. Bei Eingang=0 darf die FET-Bodydiode je Orientierung Backup OUT→VIN rückspeisen. Daher keine vollständige sichere Alternative für die neue Backup-Anforderung ohne eigenständigen rückstromsperrenden Power-Mux.

**P5-Entscheid:** LTC4366-2 **nur konditionaler Laborpfad**, keine wirtschaftlich oder einzelfehlertechnisch nachgewiesene neue Gesamtschutzlösung.

## Neue PWR_FAIL-/Knopfzellen-Anforderung: Schnittstellen-Gate

TripPower muss bei M8/BAT+-Abtrennung, UV/OV-Schutzabschaltung und nach F_MAIN-Öffnung das Abschalten erkennbar machen. **Konzept, noch nicht elektrisch dimensioniert:** Das Signal muss **POWER_PATH_GOOD** (tatsächlich nutzbarer geschützter Ausgang einschließlich UV-/OV-Abschaltung), nicht nur BAT+ vorhanden / VIN_GOOD, überwachen. Bei einem 200V-Puls kann BAT+ weiter vorhanden sein, während die Lastversorgung längst abgeschaltet ist. Im fahrzeuggespeisten Zustand darf der Pullup nicht ununterbrochen die Primärzelle entladen.  PWR_FAIL als fail-high über Pullup **nur auf TripTracer kritischer Backupdomäne**, während gesunder Fahrzeugversorgung zieht ein Open-Collector-/Open-Drain-Signal aus einer *separaten* VIN_GOOD-Domäne aktiv LOW. Bei Quelle 0V ist der Ausgang hochohmig, IRQ high. Das benötigte Interface, seine off-Leckströme bei125°C und zuverlässige Strom-/Pegel-/Zeitbudgetierung sind **nicht** im aktuellen REV5 vorhanden/qualifiziert. Keine primäre Knopfzelle an +5V_MAIN, RAW, BAT+, ACC, USB oder Schutz-MOSFET-Ausgang direkt anschließen; konsequente doppelseitig rückstromsperrende Energiequellenumschaltung **auf TripTracer**, nur MCU/FRAM/SD bis zur geprüften Shutdown-Energie. Kein Laden einer Primärzelle. Anstieg PWR_FAIL darf im VIN=0-Betrieb keinen IC über seine I/O-Clampdioden speisen. Power-Fail-Puls vor ausgehender 3V3-SD-Schiene testen, USB gleichzeitig, schwache Zelle, wiederkehrende Versorgung. Eine CR1220 ist kein verifizierter SD-Backupakku.

## Kostentransparenz, BOM, Test-Gate

Vollständig aufgelistete *zu budgetierende Funktionspositionen* und nach Quellen belegte Teilpreise siehe ROUND6_BOM_COST_MATRIX_2026-10-15.md. Gesamt-BOM im Sinne einer **bestellbaren Schaltung** ist **nicht belastbar**, weil kein sicheres/qualifiziertes Eingangsdesign existiert. Unausgelegte Pflichtteile niemals mit 0€ verstecken. Zahl/Preis der vorhandenen REV5-Stufe darf nicht ohne Netzlisten-Delta gegen TVS als 1:1 ersetzt deklariert werden. Bei einem *zusätzlichen* TVS steigt REV5 zunächst von 57 auf **58 AUTO** bzw. 58 auf **59 RUN** Positionen; **keine** Einsparung. + F_MAIN bleibt fahrzeugseitig.

**Reproduzieren:** Python3-Stdlib: python3 hardware/modules/TripPower_5V2A/weg_d/load_dump_scenarios.py ; Unit-Tests aus weg_d-Ordner python3 -m unittest -v test_round6.py. Script ist bewusst ein idealisiertes RI/VC/E-Modell und **keine** ISO-/Hersteller-/PCB-Simulation. Auf diesem Stand kein KiCad-10-ERC, keine native Netlist, kein PCB/DRC, kein Labor-Nachweis.

## Konditionales Exit-Gate (priorisiert, ohne noch einen allgemeinen Marktvergleich)

1. Lieferant (TSC oder besser Bourns) bestätigt **maximalen 200V/350ms-10-Pulse-Ri_min bei TC/Ta125°C**, Worst-Case Vc(I,T) und erlaubte Kühllösung, inklusive schriftlicher AN-Widerspruchserklärung; ohne das **NO-GO TVS-only**.
2. Testquelle Us(t), Risrc-min, L, Wiederholabstand, Kabel und Gehäusetemperatur definiert; Hot-Energieintegral aus realer Spannung/Strom-Messung und safe failure dokumentiert.
3. Padmaximum für 60/65/80V und TVS OPEN **einschließlich Ringing** nachgewiesen oder nachfolgenden HV-sicheren Abschalter neu auslegen.
4. F_MAIN 300VDC-Kandidat + korrekt temperierter DC-Halter gegen Kurz-/Unterstrom/I²t/Arc nach Hersteller Time-Current/Total clearing und Kabel-/PCB-Temperatur koordinieren.
5. PWR_FAIL plus isolierte TripTracer-Backup-Zelle nach Fail-Off/keiner Rückspeisung dimensionieren; 9V/30V/VIN0/USB-Tests.
6. **Erst wenn 1–5 positiv:** kleine KiCad-10-Prototypstufe, Schaltplan-Hierarchie/Footprint/3D/BOM, nativer ERC und Netlist, Layout/DRC und danach echte ISO-/Temperaturprüfung.

**Endurteil:** TSC als komplette Minimalarchitektur **NO-GO**; Bourns als Datenblatt-klarerer TVS **Laborforschung ja, Produktions-Gesamtlösung nein**; LTC4366-2 **Forschungsfallback, noch kein belegter Sicherheits-/Preisvorteil**. Keine Änderung an A/B/C/REV5.
