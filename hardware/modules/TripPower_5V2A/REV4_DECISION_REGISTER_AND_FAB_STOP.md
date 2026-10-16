> **AKTUELLER TRIPPOWER-VERTRAG (Korrektur vom 15.10.2026): 200 V / 350 ms**, nicht 202 V. Maßgeblich ist [`REV5_DESIGN_BASELINE.json`](REV5_DESIGN_BASELINE.json); in älteren REV2–REV4-Dokumenten stehen historische 202-V-TI-Referenzrechnungen, die NICHT die jetzige Vorgabe darstellen. 9–30 V, 5 V/2 A, RAW-AUX 1 A bleiben Entwicklungsziele. SOA/Puls- und PCB-Freigaben weiterhin BLOCKED. REV5-TPS38 ist aktiver Stand.

# TripPower – verbindlicher REV4-Entscheidungsstand & Prototypen-Stoppgates (15.10.2026)

> **WEITERER COTS-MARKTCHECK (15.10.2026):** [Spannungswandler-/RAW-Switch-Alternativen](COTS_REPLACEMENT_SCREEN_P01_P03_P08_P10_2026-10-15.md) sind gegen alle kritischen TripPower-Anforderungen verglichen. **TPSM33620S5QRDNRQ1** = 5V/2A Automotive-Modul mit Drossel, aber 36V max Betrieb vs. **35,9V nominell Schutzabschaltung** → keine sichere Reserve, nur mit nachgewiesener neuer OV-Schwelle. **TPSM65620SVCGR** = 65V/2A komplett, aber TI **Catalog, nicht Automotive**, aktuell DigiKey DE Lager0. **TPS1H200AQDGNRQ1** = 40V-High-Side-Switch mit FET/0,25–5A-Limit zur optionalen unabhängigen RAW-Abschaltung, Spannungsspitzenprüfung noch offen; **TPS1HTC30-Q1** 60V kann RAW nicht auf1A begrenzen (min.2A). **LM74930 und LMR38020 im aktiven REV4-BOM beibehalten**, P02 TPS38 zuerst konsequent zu REV5 ausarbeiten. Keine Architektur-Neuanläufe, solange keine zusätzliche begründende Hersteller-/Mess-Evidenz vorliegt.

> **P02 COTS-KANDIDAT QUALIFIZIERT ZUR WEITEREN ENTWICKLUNG (15.10.2026):** [TPS38A010122DSKRQ1 Zweikanal-65V-Automotive-Supervisor](P02_COTS_TPS38_DUAL_ENABLE_2026-10-15.md) statt TPS3760+Q303/Q304/Q305. Zwei OD-LOW-Ausgänge mit TI `VOL≤0.300V` @5mA/−40…125°C gegenüber LM74930 `EN_OFF≤0.410V`; OH-Vorteil mit VS-Pullup und `IEN≤200nA` modelliert. **COTS-Teilenummer real/lagernd** (Mouser DE ~4.274, 3,25€/1). **Noch kein REV5-BOM-/KiCad-Umbau**: gemeinsame OD-Feedback-Hysterese, RUN_CMD HIGH bei VIN0, Reset/CTR-Restladung, WSON-10-Footprint und 9V-VS-Startup vor Entscheidung nachweisen; 202V-SOA weiter offen. Keine Wiederholung der alten BJT-Dimensionierungszyklen.

> **Dies ist der aktive Einstiegspunkt für weitere TripPower-Entwicklung.** Maschinenlesbare, CI-verbindliche Fakten: [REV4_DESIGN_BASELINE.json](REV4_DESIGN_BASELINE.json). **Verifizierungsskript:** `python3 tools/check_trippower_design_baseline.py`, KiCad 10 native standalone ERC/Netlist zusätzlich. **Ein erfolgreicher Skriptlauf bedeutet NICHT Funktions-/Fertigungs- oder Fahrzeugfreigabe.** Alte REV1/REV2/REV3-Dokumente und lange historische `START_HERE_NEXT_CHAT.md`-Abschnitte gelten nur zur Herleitung, wenn diese Seite und die JSON-Baseline etwas anderes vorsehen.

## 0. Drei verbindliche Arbeitsregeln (gegen Endlosschleifen)

1. **COTS FIRST + eine konkrete Fehlerhypothese:** Keine weitere willkürliche Änderung an MOSFET, RVS, Supervisor, Gate, Buck, C308/C312 oder Reset-RC, solange keine **neue** Hersteller-Worst-Case-Angabe, ein KiCad-Nachweisfehler oder ein reproduzierbares Messergebnis den Änderungsbedarf beweist. Bei Alternativen dieselben VIN/T/Last/Surge-Kriterien vergleichen. Nicht jede fehlende Garantie automatisch durch den nächsten beliebigen Kondensator ersetzen.
2. **Ein autoritativer Stand, keine alten Behauptungen:** `REV4_DESIGN_BASELINE.json` enthält die aktiven MPN/Footprints und expliziten offenen Stop-Gates; `check_trippower_design_baseline.py` prüft harte Änderungen. Jede absichtliche Änderung braucht eine **Begründung mit Herstellerreferenz oder Messwert**, ein Delta zu REV4, einen Rückfallplan und dieselbe CI-Anpassung; `START_HERE_NEXT_CHAT.md` verweist nur als Kurz-Index auf diese Seite. Ältere Prototypvarianten sind historische Vergleiche, kein Anlass zur Neuentscheidung.
3. **Keine Platinenbestellung vor RELEASE-GATE:** Hersteller-MPN/Package/pin1/Pad- und 3D-Abgleich, festgelegte EN-/9-V-Startarchitektur, kompensierte Worst-Case-Rechnung, standalone KiCad10 ERC/Netlist, vollständiges eigenständiges TripPower-PCB und natives PCB-DRC, überprüfte Pulsenergie/SOA/F_MAIN. Ein nicht verifizierter 202-V-Schutz darf auch nicht als fertigungstaugliches Experiment für den ungeschützten Fahrzeugeinsatz behauptet werden. Limitierte Laborplatinen sind erst nach definierter Safety-Review vertretbar.

## 1. Festgelegte Arbeitspunkte (nicht erneut konzeptionell ändern)

| Gegenstand | Beibehaltener REV4-Stand | Welche Evidenz? |
|---|---|---|
| Anforderungen | `VIN_FUSED` 9–30 V am Modul, V5 5V/2A, RAW/AUX 1A Entwurfsziel, 12/24V, unter9V Reset erlaubt | Projektvertrag; **kein** 9V-Vollast-Garantiebeweis |
| Frontend | TI **LM74930QRGERQ1** + Q301 Vishay **SQM10250E_GE3**, Q302 **BUK7Y4R8-60EX**, externer `F_MAIN` | Hersteller-COTS + Standalone-KiCad; **202-V-SOA/Q302-spike offen** |
| VS-Speisung | R313/R314/R315 3×3,3k 2512 in Reihe, 56V D301, D302 SOURCE_A→VS; **kein** 1k-Experiment | TI 10k/56V/A-VS Referenz; Widerstands- und Zener-Pulskurven offen |
| Vorstart-Puffer | C302 **C1210C105K1RACAUTO** 1uF/100V, C308/C312 2×**KAF55CR72A106KV** 10uF/100V, nominal21uF | Reale Automotive-MPN; **eff. C(V,T,Alterung)/I_leak offen** |
| Chargepump | C303 KEMET C1206C474K1RECAUTO7210 470nF/100V | Ausgelegt für TI min.100nF, tatsächl. Ceff bei CAP-Spannung offen |
| Supervisor | TPS3760A012DYYRQ1, R330 **715k**, C311 KEMET **C1206C334K1RACAUTO** 330nF, CTR-Verzögerung typ.420ms | Hersteller CTR-R-Werte, aber Ceff/Restart und BJT-Schwellwerte **nicht garantiert** |
| EN/AUTO/RUN | Q303 PMBTA92-Q + Q304/Q305 PMBTA42-Q, R319 0R für AUTO, D305 RUN-Sperrdiode | KiCad-Topologie/Pinprüfung, **µA-hFE/125°C leakage/blocking offen** |
| Buck | **LMR38020SQDDARQ1**, L101 15uH, 5V/2A, LMR38020-EVM Referenz | ausgewählt, aber Footprint/Regelung/Thermik real PCB offen |
| OVP-/UVLO-Teiler | R307/R308/R310/R311 750k/1% **AC1206FR-07750KL** | Hersteller **0,25W @70°C, 200V Dauer/400V Über-Spannung, AEC-Q200**, keine Single-Fault-/202V-Layoutfreigabe |
| Schunt R301 | **RLM25FEER005**, 5mΩ/1% **2W**, 2512 | Hersteller-/LCSC-Stückdaten; Kelvin/Temperatur/Puls/Pad offen |
| Eingangs-MLCC | C305 **C1210C104KARACAUTO** 100nF/250V X7R 1210 | Automotive spezifiziert; 202V nominell **nur 48V V-Headroom**, Leitungsinduktivität offen |
| A-Bypass | C304 **C1210C105K1RACAUTO**, 1uF/100V 1210 (Footprint von 1206 angepasst) | Wert/Package jetzt konsistent; 202V-Impuls-Domain und Ceff offen |
| Supervisor-Bypass | C310 **C1206C104K1RACAUTO**, 100nF/100V 1206 | MPN statt `MPN_PENDING`; 125°C/VS max 65V prüfen |

## 2. Hersteller-Grenzwerte vs. ausdrücklich modellierte Szenarien

**Aus Herstellerdaten ableitbar, sofern ihre Bedingungen am jeweiligen Bauteil erfüllt sind:**

- [Yageo AC1206FR-07750KL](https://yageogroup.com/component-documentation/download/specsheet/AC1206FR-07750KL): 750k 1%, 1206, AEC-Q200, 200V max **kontinuierlich**, 400V angegebene max Overvoltage, 250mW bei70°C, −55..155°C. Im **idealen 202V-Fall mit zwei oberen 750k** und je 25,5k/130k nach GND fallen pro oberem Widerstand lediglich etwa **99,3V (OV)** bzw. **93,0V (UVLO)** ab. Das belegt nicht die Spannung beim offenen unteren Widerstand, Leiterplatten-Verschmutzung oder andere Fehler.
- [TA-I Tech RLM25FEER005](https://www.lcsc.com/de/product-detail/C185817.html): 5mΩ, 1%, 2W, 2512. Bei 4A sind nominal **80mW**; Temperaturdrift/Kelvin/Anlauf-Stromspitzen und tatsächliche max Verlustleistung nicht damit bewiesen.
- [KEMET 1uF 100V Automotive](https://search.kemet.com/component-documentation/download/specsheet/C1210C105K1RACAUTO); [KEMET 250V Automotive](https://www.mouser.de/de/ProductDetail/KEMET/C1210C104KARACAUTO); [KEMET 100nF 100V Automotive](https://www.digikey.de/de/products/detail/kemet/C1206C104K1RACAUTO/3314516). AEC-Q200 und Typisierung **nicht** gleich Mindestkapazität bei DC-Bias/Alterung/T.
- [KYOCERA AVX KAF55CR72A106KV](https://spicat.kyocera-avx.com/product/KAF55CR72A106KV) X7R100V 2220 Flexiterm: die beiden zusammen mit C302 sind **nominal 21µF, nicht garantiert 21µF effektiv**.
- [LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), [TI 202V-App-Note](https://www.ti.com/document-viewer/lit/html/SNOAAA1/GUID-A29F6540-095F-4408-8FD4-388A1740884B): Bei VIN202V und `VS_ZEN_NOM=56V` sind rein arithmetisch **I_RVS≈14,75mA**, **P_R313/14/15≈0,718W pro Widerstand**, **E≈0,251J je 350ms** bei konstant angenommener Rechteckspannung, **P_D301≈0,826W/E≈0,289J**. **Keine Pulsfreigabe:** voller realer ISO-Puls, Heißleiterplatte, wiederholte Pulse, VS-Zener-Toleranz und Single Fault separat qualifizieren.
- [TPS3760-Q1](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf): RCTR 877/1000/1147k, mit 330nF **typ.420ms**. Unter einer *nicht herstellergarantierechten* ±10% C-Toleranz × ±15% X7R-Temperatur rechnerisch ungefähr **259–664ms**. DC-Bias, Alterung und unvollständig entladener CTR verkürzen/ändern die wirksame Verzögerung.

**Nur Hypothesen, ohne Hersteller-Obergrenze oder Prototyp-Messung:**

- `VIN=9V`, modellierte höchste REV4-READY-Einschaltschwelle7,510V → RVS statisch rund150,5µA. Die bisher angenommenen OFF-Verbrauchsanteile34,6µA sind kein garantiertes Worst-Case-Budget und enthalten **keinen** echten dynamischen Pumpenstrom.
- `I_VS(t)`, C308/C312 Ceff(min) bei−40/125°C, Q303 I_CE(off,max) und min. Q303/Q304 hFE im µA-Bereich sind **unbekannt**. Keine postulierte Wahrscheinlichkeit oder 9V-Startgarantie.
- Q301 250V VDS hat bei nominal 202V **48V statische Reserve**; Q302 nur 60V und lokale VS-Klemme56V bedeuten **keinen** automatischen Q302-VDS-Nachweis. `C306` 47µF/63V ist bis zur konkreten MPN-/Transientenprüfung **offen**. Stress über den realen FET-/Cap-Pins messen oder per verifiziertem Modell qualifizieren.
- 5V/2A + RAW1A bei9V und hypothetischen 80% Buck-Wirkungsgrad zieht rechnerisch **2,389A** am Eingang. 3A `F_MAIN` kann heiß bis unter diesen Betriebsstrom deraten: konkrete Sicherung/Wiring/I²t nötig.

## 3. Verbindliche Reihenfolge ab jetzt – maximal ein Mal pro Fragestellung

1. **P02: Temperaturfeste EN-Freigabe**: Eine lieferbare Automotive-COTS Lösung mit **garantiertem** Pull-Up/Down-/Leckbereich über −40..125°C und VS bis56..65V prüfen (Supervisor-Ausgangstyp/Levelshift mit definierter Off-Klemme). Keine weitere Änderung der diskreten Transistoren ohne Daten. Falls es keine passende COTS-Anbindung gibt, den alten REV4-Zweig erst auf Labor-Testboard *messbar* machen.
2. **P01: 9V-Startpumpe**: Exakte TI-EVM mit unserer 9,9k-D302-C308/C312-C311-RESET-Sequenz vergleichen; ohne VS-I(t)-Bound kein Silizium-Funktionsbeweis. **Startphasen 9,0V/12V/13,8V am Moduleingang**, schnell/langsam, Restladung, Auto/Run.
3. **P03/P04/P05/P07: 202V und Fehler-Sicherheit**: Hersteller SOA+RVS-Impulskurve+Zener/TVS/Q302/C306+externe `F_MAIN` neu zusammenfassen, *nur* physikalisch notwendige Teile ändern. Der unter Last zu trennende 250V-FET ist primärer Stressfall. Widersprüche sicherheitskritisch vor PCB lösen.
4. **P06/P08/P09/P10: vor Erstbestellung**: effektive MLCC-Kurven, 5V-PCB-Thermik, reale Footprint-Abmessungen und fertig geroutetes 2-/4-Lagen-KiCad10-PCB mit vollständigem DRC + gut messbaren Testpunkten; Ruhe- und Rückspeiseströme im Labor.

**Keine Punkte als „gelöst“ markieren, solange kein Hersteller-Worst-Case oder gemessener Nachweis angehängt ist.** Zu jedem offenen Punkt gehören Eigentümer/Nächstes Artefakt/Grenzwert und Status. Für die Maschinenprüfung gelten die GATES P01–P10 aus `REV4_DESIGN_BASELINE.json`.

## 4. Freigabelogik

- **LOCKED**: Wert/Teilenummer/Footprint im KiCad durch Skript und natives Netlist/ERC synchronisiert; nicht gegen Wissen oder aus Routine verändern.
- **CONDITIONAL**: Rechnung auf tatsächlich spezifizierten Teilen mit zusätzlichen Annahmen; nur als Modell-Sensitivität zitieren.
- **BLOCKED**: Funktionen mit fehlender Hersteller-/Messgarantie, besonders Start, EN, SOA, Puls, reale PCB- und thermische Grenzen.
- **RELEASED**: erst nach einem separaten expliziten Release-Prozess, der alle entsprechenden STOP-GATES schließt. **Aktuell gibt es kein RELEASED.**

Der historische TripTracer-Hauptprojekt-CI (33 Root-ERC + 5 PCB-DRC) ist separat von eigenständigem TripPower-ERC und nativer Netzliste zu halten; keine global „grüne“ Freigabe aus einem Teil-Check ableiten.
