# TripTracer – Regeln fuer KI/Codex

- Ziel: KiCad 10 und vollstaendig portable lokale Projektbibliotheken.
- **TripTracer V1** in `hardware/kicad/` ist der aktive, noch nicht freigegebene Elektronik-Entwicklungsstand; **V0.3** bleibt historische Referenz. V0.1-Firmware und -Mechanik nur als Prototyp-/Referenzstand behandeln.
- Keine gepruefte PCB-Fertigung, keine bestandenen ERC/DRC, keine Automotive-Sicherheitsfreigabe behaupten.
- Vermeide Vermischung mit SoulTracer (Solar-Schmuck) oder BTN9990LV-Lueftersteuerung.
- Bei Aenderungen so wenige Dateien wie moeglich anfassen; Git-Commit und Aenderungsbericht erstellen.
- Projektlokale Bibliotheken und Modellpfade relativ `${KIPRJMOD}` halten, keine absoluten Windows-Pfade.
- Neue Bauteile mit Hersteller-/Teilenummer, Geometriedatenquelle, Pinout und Geometriepruefung dokumentieren.
- Wiederholte Korrekturen: maximal 3 Versuche pro Fehlergruppe; offene Fehler klar benennen und nicht stillschweigend unterdruecken.
- Erst nach elektrischem Test, KiCad ERC/DRC, manueller Pin- und Footprintpruefung und Automotive-Pruefung fuer Fertigung freigeben.

## KiCad-Projekt als einheitliches, durchblaetterbares Mehrseiten-Schema

**Verbindliche UX- und Projektanforderung:** Alle TripTracer-Baugruppen sind **innerhalb eines einzigen KiCad-10-Schaltplaneditors** über den **Hierarchie-Navigator** und die Funktionen für vorherige/nächste Seite erreichbar. Der Nutzer darf **nicht** gezwungen sein, jede Baugruppen-Datei einzeln zu öffnen.

- **Ein einziger Projekteinstiegspunkt:** `hardware/kicad/TripTracer_V1.kicad_pro` mit der **Root-Schaltplandatei** `TripTracer_V1.kicad_sch` und dem gleichnamigen `TripTracer_V1.kicad_pcb`. Im Editor müssen sich Root-Deckblatt und sämtliche Baugruppenseiten als **ein Schaltplanprojekt** präsentieren.
- **Modular statt monolithisch:** Für jede eigenständige Baugruppe eine korrekt referenzierte **hierarchische Unterseite** (separate `.kicad_sch` mit relativem Dateinamen) verwenden. Mehrere echte KiCad-Seiten gehören in die Hierarchie, **nicht** als unabhängig zu öffnende Einzel-Schaltpläne; auch nicht alle Bauteile auf ein unlesbares Riesenblatt drängen. Eine einzelne physische `.sch`-Datei ist **nicht** das Ziel.
- **Jede neue Baugruppe sofort in die Root-Hierarchie integrieren:** Sheet-Symbol, gültige `Sheetfile`-Referenz, eindeutige Namen/UUIDs und konsistente `instances`-/Seitennummerierung anlegen. Bei Datei-Umbenennung oder Verschiebung alle Referenzen korrekt aktualisieren; keine verwaisten Seiten, mehrfachen Sheet-UUIDs oder gebrochenen relativen Pfade erzeugen.
- **Schnittstellen korrekt über Blattgrenzen:** Signale mit dokumentierten globalen Netzen oder – vorzugsweise bei klaren Schnittstellen – **hierarchischen Labels und zugehörigen Sheet-Pins** verbinden. Lokale Labels allein verbinden keine verschiedenen Blätter. Nur grafische Hierarchie **ohne elektrische Anbindung** niemals als funktionsfähig integriert deklarieren.
- **Prüfung nach jeder Baugruppe:** Root-`.kicad_sch` und **alle** Referenzen/Unterseiten systematisch prüfen. Wenn KiCad 10 ausführbar ist, das gesamte Projekt über `.kicad_pro` öffnen, **Hierarchie-Navigator** einschließlich neuer Seite durchklicken, Vor-/Zurücknavigation verifizieren, projektweiten ERC und nötigenfalls Netlist/BOM aus der Root starten. Wenn keine native KiCad-Prüfung ausgeführt wurde, diese Einschränkung ausdrücklich dokumentieren.
- **Benutzerführung dokumentieren:** In der Projekt-README eindeutig angeben, **welche eine Projektdatei zu öffnen** ist und wie alle Seiten im KiCad-Hierarchie-Navigator erreichbar sind. Den aktuellen Gesamtumfang und offene/validierte Baugruppen auf dem Deckblatt kenntlich machen.

Diese Mehrseiten-Navigation ist eine **dauerhafte Projektanforderung**, keine optional zu erfüllende Schönheitsmaßnahme. Sie gilt zusätzlich zu den strikten Baugruppen- und Kompatibilitäts-Gates.

## Bauteil-Auswahl: JLCPCB Basic und Handloetbarkeit (TripTracer V1)

**Verbindliche Projektpraeferenz (HW-73 bis HW-76):** Wenn technisch gleichwertig, so viele Komponenten wie moeglich als **JLCPCB Basic Parts** und **von Hand gut loetbare SMD-Pakete** auswaehlen. **Elektrische Funktion und Langzeitzuverlaessigkeit gehen immer vor Basic-Status und Gehaeusegroesse.**

- **Beschaffungs-Reihenfolge:** (1) passendes JLCPCB **Basic**-Teil, (2) JLCPCB **Extended** bzw. bei LCSC verfuegbares Teil, (3) sonstige geeignete Bezugsquelle. Bei technisch besseren Varianten darf der Agent jederzeit von Basic abweichen – die Wahl muss begruendet werden. Basic/Extended ist kein unveraenderliches Bauteilmerkmal; bei der finalen BOM und vor Bestellung aktuell pruefen.
- **Handloeten – Passivbauteile:** Widerstaende und Kondensatoren soweit sinnvoll in **1206 imperial / 3216 metrisch** oder groesser auslegen. **Kein blindes 1206-Dogma**: ausreichend Spannungsfestigkeit, Derating, HF-Verhalten, Ausgangskapazitaet unter DC-Bias, parasitaere Induktivitaet, Strom-/Waermebelastung und Platzbedarf haben Vorrang. Kleinere 0805/0603 oder andere Bauformen bei klaren technischen Vorteilen.
- **Handloeten – Halbleiter/ICs:** Wenn technisch vergleichbar, gut loetbare SOT-23, SOIC, TSSOP, SOT-223 oder vergleichbare gehaeuseseitige Optionen bevorzugen. QFN, DFN, Fine-Pitch, Thermal-Pads und andere schwierige SMD-Formen ausdruecklich **erlaubt**, wenn es deutliche technische/funktionale/thermische Vorteile oder keine sinnvolle Alternative gibt. Dann geeignetes Handloetverfahren oder externe Bestueckung einplanen.
- **Ausnahmen nicht ueberoptimieren:** Insbesondere GNSS/RF, USB-/ESD-Schutz, schnelle Regler-Schaltknoten, Antennen-Bias, Schaltregler-Layout, Thermalpads und spezialisierte Sensor-/Modulbausteine erfordern teils kleine oder spezielle Gehaeuse. **Keine HF-/EMV-/Thermik-Verschlechterung zur Erzielung von 1206/Basic**.
- **Bei JEDER neu konstruierten oder geaenderten Baugruppe** echte Hersteller-Teilenummer, **LCSC-C-Nummer** (soweit vorhanden), aktuelle JLCPCB-Kategorie (Basic/Extended/nicht verfuegbar/**ungeprueft**), exakten Footprint, Handloetbarkeit/Loetmethode und Grund fuer Abweichungen dokumentieren. Nicht verifizierte JLCPCB-Kategorien **niemals als Basic behaupten**.
- **BOM und Design-Gates:** BOM nach Bauteilentscheidung sofort aktualisieren, vor ERC/DRC/Fertigungsfreigabe Package/Pin-Mapping und Loetzugaenglichkeit erneut pruefen; bei Ersatztypen die Kompatibilitaet mit allen frueheren Baugruppen testen. **Eigene Handbestueckung soll moeglich sein**, ohne bestehende separate Entscheidungen zu PCB-/PCBA-Bestellmenge automatisch zu ueberschreiben.
- Bei mehreren geeigneten Alternativen darf der Agent sich bewusst fuer eine teurere/kleinere/nicht-Basic-Variante entscheiden, wenn ein **wesentlicher und dokumentierter** Vorteil fuer Sicherheit, Leistung, Signalqualitaet, Thermik, Kompaktheit oder Ersatzteilverfuegbarkeit entsteht.

## Vorsichtige, baugruppenweise Hardware-Entwicklung (verbindliche Arbeitsweise)

**Grundprinzip: Hardware zuerst korrekt, danach Software daran anpassen.** Eine fehlerhafte, bereits gefertigte Platine ist wesentlich teurer und aufwendiger zu korrigieren als eine Firmware-Anpassung. Deshalb konsequent **schrittweise, risikobewusst und ohne vorschnelle Fertigmeldungen** entwickeln.

### Ablauf für JEDE einzelne Baugruppe

1. **Ausgangslage und Schnittstellen klären.** Vor Änderungen `docs/HARDWARE_REQUIREMENTS.md`, die vorhandenen V1-Schaltplan-/PCB-Blätter, relevante Herstellerdatenblätter und offene Fehler lesen. Zweck, Eingänge, Ausgänge, Spannungen, Grenzwerte, Lasten, Steuersignale und Fehlerszenarien der Baugruppe benennen. Bereits festgelegte Anforderungen nicht eigenmächtig ändern.
2. **Genau eine Baugruppe vollständig elektrisch entwerfen.** Schaltung mit tatsächlich verbundenen Pins/Wires, sinnvoller Versorgung, Schutz-, Entkopplungs-, Pull-up-/Pull-down- und Testbeschaltung fertig ausarbeiten. Keine funktionslosen Platzhaltersymbole, erfundenen Anschlussbelegungen oder reinen Text-Blätter als „fertig“ darstellen. Ein neuer Block darf zunächst als „Entwurf“ entstehen, nicht als validiert.
3. **Bauteile und Footprints gegen Herstellerunterlagen prüfen.** Hersteller-Teilenummer, Pin-1-/Pad-Nummern, elektrische Maximalwerte, Verlustleistung, thermisches Derating, Footprint-Geometrie, Bestückbarkeit und Lieferbarkeit prüfen. Projektspezifische KiCad-10-Symbole, Footprints und 3D-Modelle konsistent und relativ zu `${KIPRJMOD}` pflegen. Vorläufige Werte und abweichende Footprint-Namen ausdrücklich als Sperrpunkt markieren.
4. **Baugruppe für sich validieren.** Datenblattrechnung, Strom-/Spannungs-/Thermikbudget, Bauteilbelastung und einschlägige Fehlerfälle prüfen. **Native KiCad-10-ERC** ausführen, Schaltplan visuell auf Lesbarkeit, Kreuzungen und echte elektrische Verbindung prüfen; wo sinnvoll Simulation oder Labor-/Messprüfung ergänzen. Fehler beheben und relevante Checks nach Änderungen erneut ausführen.
5. **Vor Integration Kompatibilität mit ALLEN bereits vorhandenen Baugruppen prüfen.** Eine neue Baugruppe darf nicht isoliert für korrekt erklärt und unbemerkt integriert werden. Gemeinsame Netznamen und Hierarchie-Pins, Versorgungsreihenfolge, Pegel, Impedanzen, 5-V-/3,3-V-Leistungsbilanz, GPIO-/Strapping-Pins, USB und SD-Zugriffsmodi, I²C-Adressen/Pull-ups, SPI-Chip-Selects, Reset/Enable, Signalrichtungen, Masse-/Rückstromführung, Schutzketten, Rückspeisung, EMV/ESD, Wärme, Steckerbelegung und Mechanik prüfen. Bestehende Baugruppen durch Änderungen **nicht regressieren lassen**.
6. **Erst nach bestandener Integrationsprüfung den nächsten Block beginnen.** Den übergreifenden ERC erneut ausführen; beim PCB-Stand zusätzlich Netze aus dem Schaltplan synchronisieren, reale Pad-/Pin-Zuordnung, Abstände, Kupferstrompfade und DRC prüfen. Falls eine Prüfung technisch hier nicht ausführbar ist, ausdrücklich „NICHT GETESTET / FREIGABE AUSSTEHEND“ schreiben, kein bestandenes Ergebnis behaupten und die fehlende Prüfung als **offenes Gate** festhalten.
7. **Kleiner Commit mit Nachweis.** Pro Baugruppe zusammenhängende Änderungen committen, BOM/Designentscheidungen aktualisieren und eine kurze Prüfliste ablegen: Was wurde geändert? Welche Schnittstellen und früheren Baugruppen wurden überprüft? Welche Tests wurden **tatsächlich** durchgeführt und mit welchem Ergebnis? Was ist noch offen? In nächsten Schritten darauf aufbauen statt dieselben Annahmen stillschweigend erneut zu treffen.

### Verbindliche Qualitäts-Gates

- **Gate A – Baugruppe intern plausibel:** korrekte Hersteller-Pinouts, berechnete Grenzwerte, vollständige Schaltung und Prüfung auf versteckte Annahmen.
- **Gate B – Schnittstellen kompatibel:** systematische Gegenprüfung der neuen Baugruppe mit **allen bereits integrierten Baugruppen** und den verbindlichen Anforderungen; Konflikte vor der nächsten Erweiterung beseitigen.
- **Gate C – KiCad elektrisch geprüft:** natives ERC und visuelle Schaltplanprüfung; kein „ERC bestanden“ ohne ausgeführtes ERC. Fehlendes ERC ist **kein** stillschweigendes Bestehen.
- **Gate D – PCB geprüft, sobald layoutet:** Symbol-Pad-Konsistenz, synchronisierte Netze, Footprint-/3D-Modellprüfung, Layout-Rückstrom- und Thermikreview, natives DRC und Fertigerregeln; kein „DRC bestanden“ ohne ausgeführtes DRC.
- **Gate E – Reales Hardware-Testing vor Fertigungs-/Fahrzeugfreigabe:** Labornetzteil und definierte Messungen, danach relevante Automotive-Schutz-, Transienten-, Temperatur- und Fehlertests. Simulation und ERC/DRC ersetzen keine reale elektrische Erprobung.

**Status immer sauber trennen:** `offen` → `elektrischer Entwurf` → `datenblatt-/schnittstellengeprüft` → `ERC-geprüft` → `PCB/DRC-geprüft` → `am Prototyp gemessen` → `fertigungs-/einsatzfreigegeben`. Die jeweils höhere Stufe darf nur durch tatsächlich vorhandene Nachweise erreicht werden.

### Hardware vor Firmware; keine kaschierten Hardwarefehler

- **Keine fragwürdige Hardware mit späteren Firmware-Workarounds rechtfertigen.** Fehlende Verpol-/Überspannungsabsicherung, thermisch überlastete Bauteile, falsche Versorgung, Boot-Strapping-Probleme, kollidierende Busadressen, instabile Pegel, fehlende Entkopplung oder unzureichende Leitungs-/Pad-Dimensionen müssen auf Schaltplan-/PCB-Ebene gelöst werden.
- Softwareseitig leicht änderbare Entscheidungen (z. B. nicht sicherheitskritische GPIO-Konfiguration, Logging, Anzeige, Timing innerhalb garantierter Hardwaregrenzen) dürfen nachgelagert werden. **Die Hardware muss aber bereits die notwendigen realen Firmware-/Boot-/USB-/Speicherfunktionen elektrisch ermöglichen.** Kritische Timing-, Sicherheits- und Abschaltanforderungen dürfen nicht auf unbelegte spätere Softwareversprechen verschoben werden.
- **Bei Widersprüchen, nicht belastbar belegten Datenblattwerten oder fehlenden Prüfmitteln stoppen und den Sperrpunkt offenlegen**; nicht blind weitere Baugruppen hinzufügen, das Gesamt-PCB routen oder Gerber erzeugen. Gegebenenfalls gezielt eine Entscheidung mit Vor- und Nachteilen einholen.
- **Keine große „alles auf einmal“-Schaltplanaktion**, auch wenn das endgültige Gerät eine einzige Hauptplatine ist. Vollständige Hauptplatine als Ziel bedeutet **nicht**, dass Baugruppen ungeprüft parallel integriert werden dürfen.
- Änderungen an einer bereits geprüften Baugruppe lösen mindestens eine erneute Schnittstellen-/Regressionsprüfung aus. Prüfnachweise und offene Risiken im Repository nachvollziehbar halten.

## Wunschliste und neue Ideen

- Vor jeder **inhaltlichen Weiterentwicklung** (Hardware, Schaltplan, PCB, Firmware, Mechanik oder Funktionen) `docs/IDEAS.md` lesen und relevante Einträge berücksichtigen.
- `docs/IDEAS.md` ist ein Ideenspeicher, **kein automatischer Entwicklungsauftrag**. Ideen nicht allein wegen ihres Eintrags implementieren oder als verbindliche Anforderung behandeln.
- Bei der Planung explizit beauftragter Arbeiten prüfen, welche vorhandenen Ideen dazu passen. Konflikte mit Sicherheitsanforderungen, aktueller Architektur, Bauteilverfügbarkeit oder Aufwand offen benennen.
- Nur ausdrücklich vom Nutzer freigegebene Funktionen umsetzen. Neue spontane Ideen nicht ungefragt in fertige Platinen, Firmware oder Stücklisten übernehmen.
- Bei tatsächlich umgesetzten Ideen den Status in `docs/IDEAS.md` mit Version oder Commit aktualisieren; nur getestete Ergebnisse als getestet kennzeichnen.
- Verbindliche Projektentscheidungen separat in den Anforderungs- und Architekturdateien festhalten. Die Wunschliste ersetzt diese Dokumente nicht.

## Hardware-Anforderungen vor Bauteilauswahl

- Bei Schaltplan-, PCB-, Versorgungs- und Mechanikarbeiten zuerst `docs/HARDWARE_REQUIREMENTS.md` lesen und Anforderungen mit dem aktuellen KiCad-Bestand abgleichen.
- Bei gemeinsam geklaerten Entscheidungen die betroffenen IDs und das Entscheidungsprotokoll in `docs/HARDWARE_REQUIREMENTS.md` aktualisieren; nicht voreilig Bauteile festlegen oder offene Punkte als beschlossen ausgeben.
- **Primaerer Geraete-Ueberstromschutz ist eine selbst rueckstellende SMD-eFuse auf der Platine (PWR-03/PWR-12).** Nicht automatisch annehmen, dass jeder eFuse-Typ Verpolschutz oder Load-Dump-Festigkeit bietet: datenblattbasiert pruefen und ggf. ergaenzen. Eine zusaetzliche unabhaengige Sicherung nur nach Schutz- und Fehleranalyse festlegen.
- **Fahrzeugseitige Kabelabsicherung ist festgelegt (PWR-04/05)**: einfach selbst konfektionierbare M8-Kabel an abgesichertem Abgriff oder mit vorgeschalteter Sicherung nahe der Batterie. Die eFuse sichert das Kabel vor dem Geraet nicht gegen Kurzschluss.
- **M8 hat Versorgungsvorrang (PWR-06/08/13)**: USB-C-5-V versorgt ohne M8 den automatischen microSD-MSC-Datenmodus oder den gesonderten Firmware-Bootmodus, nicht den regulaeren Fahrzeugbetrieb. Bei gleichzeitig verbundenem M8 darf USB die laufende Aufzeichnung nicht automatisch beenden; expliziter MSC-Wechsel erst nach SD-Flush/Unmount. Keine Rueckspeisung zwischen den Quellen.
- Aenderungen an der Hardware-Architektur mit `docs/ARCHITECTURE.md` und der Wunschliste abgleichen. Die Version V0.3 bleibt historischer Bestand.

## KiCad-Schaltplaene: Lesbarkeit fuer Menschen (projektuebergreifende Pflicht)

- Jeder KiCad-Schaltplan muss neben ERC-Konformitaet **fuer Menschen ohne Nachverfolgung unzaehliger Netzlabels lesbar** sein: Funktion und Signalfluss muessen auf den ersten Blick erkennbar sein.
- Schaltung in **klar benannte funktionale Baugruppen/Bloecke** gliedern (z. B. Versorgung/Schutz, MCU, Sensoren, Schnittstellen, Ausgangstreiber). Zusammengehoerende Bauteile raeumlich gruppieren und durch nachvollziehbare, sichtbare Verbindungen vernetzen.
- **Nicht jedes einzelne Bauteil ausschliesslich mit eigenen Labels, Power-Symbolen oder Flags anbinden.** Innerhalb eines Funktionsblocks moeglichst echte, sichtbare Wire-Verbindungen verwenden. Netzlabels sinnvoll nur fuer laengere oder blattuebergreifende Verbindungen einsetzen und eindeutig benennen.
- **Korrekte Power-Symbole und PWR_FLAGs** nach KiCad/ERC-Semantik verwenden: PWR_FLAG nur an tatsaechlich treibenden Versorgungsknoten und nur soweit elektrisch gerechtfertigt, keine dekorativen oder fehlerkaschierenden Flags. Versorgungseingaenge, geregelte Ausgaenge und GND konsistent kennzeichnen.
- **Keine Ueberlappungen oder Beruehrungen von Wires mit Labels/Flags/Texten**, sofern dies nicht der klare gewollte elektrische Anschlusspunkt ist. Keine kreuzenden Leitungen, die Verbindungen vortaeuschen; Verzweigungen und Junction-Dots eindeutig platzieren. Keine Text-/Symbol-/Pin-Ueberlagerungen.
- Einheitliche Leserichtung, gut lesbare Beschriftungen, ausreichende Abstaende, kurze nicht kreuzende Leitungswege und klar strukturierte Blatthierarchie anstreben.
- Vor jeder Schaltplanabgabe **visuelle Kontrolle aller Seiten und Funktionsbloecke** bei normalem Zoom durchfuehren; ERC allein belegt keine menschliche Lesbarkeit. Gefundene Darstellungsmaengel vor Freigabe korrigieren.
- **Diese Regeln gelten fuer saemtliche KiCad-Projekte des Nutzers, nicht nur fuer TripTracer.** In anderen Repository-AGENTS.md ebenfalls festhalten, sobald diese Repositories bearbeitet werden.
