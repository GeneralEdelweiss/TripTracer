# TripPower A/B – Review-Runde 1 (2026-10-15)

**Stand:** Branch-Vergleich und Berichtsauswertung (keine eigene KiCad-Ausführung oder Laborprüfung). **Keine elektrische oder Fertigungsfreigabe.**

## Geprüfte Änderungen

Gemeinsamer Ausgangscommit: `2cafbf43e24aadc12ede10cd413b962c84579664`.

- **A** `design/trippower-a`: 1 Commit, ausschließlich `hardware/modules/TripPower_5V2A/WEG_A_LMR38020_RELIABILITY_REVIEW_2026-10-15.md` (+95 Zeilen).
- **B** `design/trippower-b`: 1 Commit, ausschließlich `hardware/modules/TripPower_5V2A/weg_b/WEG_B_SCOPE_AND_GATE_REVIEW_2026-10-15.md` (+67 Zeilen).
- Keine Branch-spezifischen KiCad-, BOM-, Script- oder PCB-Änderungen. Aussagen aus den Berichten sind selbstberichtete Ergebnisse, keine unabhängig ausgeführten Tests.
- `REV5_DESIGN_BASELINE.json`: weiterhin 9–30 V, 5 V/2 A, RAW-AUX 1 A, 200 V/350 ms, -40…125 °C, F_MAIN extern, 57 AUTO / 58 RUN. Alle relevanten P01–P10 offen.

## Kritische Befunde Weg A

**A-01 – TVS-Auslegung/250-V-MOSFET:** Die Dokumentation begründet aus Hersteller-V(BR)-Minima 167+36,7=203,7 V, weshalb bei 200 V nicht auf eine garantierte positive TVS-Klemme vertraut werden kann. Die Summe unterschiedlicher Einzel-IPPs bei Clamping-Voltage darf nicht als gemessener gemeinsamer Serien-Clampwert gelten. Der Q301-250-V-Grenzwert liefert nominal 50 V Differenz zu 200 V, **aber** kein garantierter VDS/SOA/Peak-Nachweis. **P03 weiterhin kritisch.** Bei der nächsten Iteration ist eine echte Schaltungs-/Signalpfadanalyse inklusive TVS-Polarität, Worst-Case-Überschwingern und Herstellerpuls/SOA verlangt.

**A-02 – VS/9-V-Gegenläufigkeit:** R313–315=9,9k begrenzen Pulsstrom, liefern für VS≈8 V bei VIN=9 V aber nur ca. 101 µA. 21 µF sind nominal; effektive Kapazität und dynamischer VS-Strom unbekannt. Der Hinweis ist korrekt als unbewiesener Start gekennzeichnet. Mehr allgemeine Prosa hat geringeren Nutzen als ein **reproduzierbares** Best-/Worst-Case-Modell mit Mess-/Testpunkten und eindeutigen Restdaten.

**A-03 – Pulslast/Thermik:** Rechteck-Beispiel 200V→56V, I=14,55mA, je 3,3k 0,698 W/0,244J, Zener 0,815W/0,285J rechnerisch nachvollziehbar, aber **kein** ISO-Profil oder Pulsfreigabe. Hot-FET-SOA und Sicherung fehlen. Induktor-Ripple ideal modelliert, keine Hot-2A-Garantie.

**A-04 – Fortschritt:** Noch kein elektrischer Branch-Commit, keine neue CI-Regression, keine abgeschlossenen Gates; daher Review inhaltlich positiv, Reife unverändert.

## Kritische Befunde Weg B

**B-01 – Eindeutiger Systemengpass:** TPSM33620-Q1 ist 36-V-Betriebsmodul (40 V absolut maximal laut Bericht); 200V/350ms vor der Schutzstufe und OV-Ausschalten lösen noch keinen garantierten dynamischen <36-V-Padwert. Schützende Reaktion muss **am Serienpfad** erfolgen, nicht lediglich via Modul-EN; Power-on/Power-off fail-safe. Ohne belegten Schutz **keine Bestückungsfreigabe**.

**B-02 – Supervisor statisch vielversprechend, aber noch nicht integriert:** TPS3760E012DYYRQ1 ist ein existierender Automotive-Baustein; Hersteller-TI-Bestellseite aktuell als nicht vorrätig gekennzeichnet. Probe mit Rtop=940k/Rbottom=23,2k ergibt ca. 33,21 V rising, nominell 32,55 V falling, Eckwerte im Bericht nur angenommene Fehlermodellierung; kein definierter Freigabe-/Abschaltzustand bei einem nicht versorgten OD-Monitor. Gesamte Fehlerkette unter Berücksichtigung von VIN=0, 9V-Start, 30V-Restart, 200-V-SENSE, VS-VDD, Reset, FET-Gate und Toleranzen ist zu verifizieren. Zusätzlich reale Marktverfügbarkeit klären. Quellen: https://www.ti.com/product/TPS3760-Q1/part-details/TPS3760E012DYYRQ1 und https://www.ti.com/product/TPSM33620-Q1.

**B-03 – Echte Teilezahl:** B rechnet 12 (alter Buck) vs 6 (TPSM mit fünf diskreten Caps) = 6 Bruttoeinsparungen; neuer Supervisor +3R+C=5 => **höchstens 1 netto**, noch ohne OVP-Interlock/Pullups/Damping. TI bewirbt zugleich 4 externe Teile für 5-V-Fixed-Minimaldesign; Datenblattvarianten, tatsächlich nötige Ceff/EMV und Zählweise abgleichen, bevor die Bruttozahl verbindlich wird. Auch Bestück-/PCB-/Beschaffungskosten noch unbekannt.

**B-04 – Fortschritt:** Kein eigenständiges KiCad-Schema, kein Pin/Footprint-Modell, keine dynamischen Nachweise. Der bisherige Bericht ist **Vorkonzept**, nicht qualifizierte Alternative.

## Vorläufige Projektleitungsentscheidung

- **A als Entwicklungs-Hauptpfad bevorzugen** (80-V-VIN-Reserve; weniger neue offene Schnittstellen und bessere Nähe zur eingefrorenen REV5-Baseline). Dies ist keine technische Freigabe.
- **B als begrenzte Machbarkeitsprüfung** weiterführen. Vor umfangreichem Routing/Bibliotheksaufwand erst beweisen, dass eine sichere dynamische 36-V-Schnittstelle samt 30-V-Restart und realem Netto-Kosten-/Teilevorteil möglich ist. Bei unlösbarem Gate: sauberer begründeter STOP statt weiterer Prosa/Blindkonstruktion.
- Keine Behauptung eines bestandenen 9-V-, Temperatur-, 200-V-, ERC-/DRC-, ISO- oder Hardwaretests.

## Verbindliche nächste Arbeitsaufträge

### A: Vom Problembericht zu einem verifizierbaren technischen Artefakt
1. Einen reproduzierbaren quantitativen Q301/TVS/RVS/Zener-200V-Worst-Case-Test und die 9-V-VS/EN-Start-/Restladungseckfälle als Skripte/Tests mit Herstellergrenzen (nicht erfundene garantierte Werte) im **A-Branch** implementieren. Fehlende Puls-SOA-Herstellerkurven explizit STOPPEN.
2. Konkrete kritische Netzpfade durch KiCad/Netlist auf echte Polarität und Signalwirkung verifizieren; klare Testpunkte, Messaufbau und Kriterien.
3. Wo eine Verbesserung elektrisch hergeleitet ist: **einen** gezielten, isolierten, reversiblen Schaltungs-Prototyp mit Symbol/Footprint/BOM und Regression (keine ungeprüfte Änderung an A-Baseline); andernfalls eindeutige Bemessungs- und Messanforderung statt fiktiver Lösung.
4. Commit mit tatsächlichen Artefakten plus kurzer Ergebnis-/Blockerliste.

### B: Machbarkeitsentscheid statt bloßer Einzel-IC-Recherche
1. Mit Datenblattgrenzwerten und einem expliziten zeit-/zustandsabhängigen Modell die vollständige Kette Supervisor-VDD/POR → OD/LM74930-EN → Q301-off → TPSM-VIN-Pad bei 9/30/200V untersuchen.
2. **No-Go** falls ein <36V Betriebs- und <40V-ABS-Pad-Gate + Wiederfreigabe bei 30V und fail-off ohne unverhältnismäßige Zusatzteile nicht plausibel belegbar ist; kein unnötiger KiCad-Bibliotheksbau bei diesem Ergebnis.
3. Bei plausibler Lösung: eigenes KiCad-10-Standalone-Teilschema/BOM, Herstellerpinmap, quantitative dynamische Testpunkte und native CI-Checks soweit möglich; vollständige MPN-/Lieferbarkeitserfassung.
4. Vollsystem-Teilezahl/Kosten 1/10/100 und Netto-Nutzen gegenüber A; Commit mit Ergebnis oder dokumentiertem No-Go.

### Exit für nächste Projektmanager-Runde
Ein Branch zählt als technischer Fortschritt, wenn er **mindestens ein konkretes elektrisches/prüfbares Artefakt** (Schaltplan-Änderung, ausführbares Grenzwertmodell mit Regression, nachvollziehbaren Hersteller-SOA-Beleg oder reproduzierbaren Test) neu committed hat. Ein zweiter allgemeiner Review-Bericht allein ist kein Gate-Fortschritt.
