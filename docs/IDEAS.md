# TripTracer – Ideen, Wünsche und Funktionen

Diese Datei ist dein **freier Ideenspeicher** für TripTracer. Schreibe hier jederzeit etwas hinein – auch unfertige Gedanken, spontane Einfälle und Wünsche ohne technische Details.

**Wichtig:** Ein Eintrag ist **keine automatische Umsetzungsfreigabe**. Bei Entwicklungsaufträgen sollen ChatGPT und Codex die Ideen lesen, berücksichtigen und mögliche Konflikte mit dem aktuellen Projektstand benennen. Die konkrete Umsetzung erfolgt erst auf deine Anweisung.

## Neue Ideen / Wunschliste


## Themenbereiche (optional)

### Bedienung & Anzeige

- Alle Funktionen eines typischen Tripmasters sollten vorhanden sein (Teilstrecken, Gesamtstrecken, korrektur etc).
- Anzeige der Anzahl der verbundenen Satteliten auf dem Display.
- Piepser bei Tastendruck (ein/ausschaltbar über ein Menü)
- Automatische Helligkeitseinstellung des Displays (ein/ausschaltbar über Menü)

### GPS, Streckenmessung & Navigation

- Aufzeichnung von Strecken und Export in typischen formaten soll möglich sein (SD-Karte?)

### Firmware, Schnittstellen & Extras

- **USB-C:** Firmwareupdates/Flashen und alternative Stromversorgung mit **5 V** (z. B. vom PC oder über einen externen 12-V-Zigarettenanzünder-auf-5-V-USB-C-Adapter); keine direkte 12-V- oder 24-V-Einspeisung über USB-C.
- **Hauptversorgung:** separate **M8-A-codierte, 3-polige Schraubsteckverbindung** für den normalen 12-/24-V-Fahrzeugbetrieb anstelle einer DC-Hohlbuchse. Der Geräteanschluss wird mechanisch im Gehäuse montiert.
- **Fahrzeugwechsel:** TripTracer soll einfach zwischen mehreren Fahrzeugen umgesteckt werden können. Pro Fahrzeug ein selbst angefertigtes, unkompliziertes M8-Kabel ohne zusätzlichen gerätespezifischen Sicherungshalter. Anschluss an einen bereits abgesicherten Fahrzeugstromkreis; bei direkter Batterieverbindung muss die Zuleitung separat nahe der Batterie abgesichert werden.
- **Versorgungsschutz:** **Selbstrückstellende SMD-eFuse als primärer Geräteschutz auf der Trägerplatine**. Gewählter eFuse-Typ muss einen wirksamen Verpolschutz besitzen oder dieser wird separat ergänzt; 12-/24-V-Fahrzeugtransienten/Load Dump separat absichern. **Das einfache M8-Fahrzeugkabel wird fahrzeugseitig abgesichert.** USB-5-V- und Bordnetzeingang sicher entkoppeln; keine Rückspeisung zu PC/USB oder ins Fahrzeug.
- **Geplante M8-Belegung:** Pin 1 = abgesichertes +12/24 V, Pin 3 = Masse, Pin 4 = Reserve (vorerst unbeschaltet); endgültige Kontaktansicht und Belegung vor der PCB-Freigabe am Steckerdatenblatt prüfen.

### Gehäuse & Mechanik

- **Schnellwechsel-Halterung:** pro Fahrzeug eine feste Halterung, TripTracer selbst werkzeuglos einschieben/ausrasten; zusätzlich nur den M8-Stecker lösen.

## Später prüfen / offene Entscheidungen

- _(Optionen, Vor- und Nachteile, technische Machbarkeit oder Kosten.)_

## Zur Umsetzung freigegeben

Nur Wünsche hier aufnehmen, wenn du ausdrücklich entschieden hast, dass sie umgesetzt werden sollen. Ein Eintrag allein startet keine Arbeit.

- _(Noch keine Einträge.)_

## Umgesetzt

Hier umgesetzte Punkte mit Commit, PR oder Versionsstand dokumentieren.

- _(Noch keine Einträge.)_

---

### Einfache Schreibweise

Du kannst auch nur eine Zeile schreiben, z. B.:

`- [ ] Wunsch: ...`

Optional dazu `Priorität: hoch/mittel/niedrig`, Rahmenbedingungen oder Bilder/Links ergänzen. Struktur ist **keine Pflicht**.

**Hardware-Anforderungsliste:** Bestätigte Vorgaben und offene Entscheidungen werden in [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md) gesammelt.

**Abgrenzung:** Verbindliche technische Vorgaben bleiben in den bestehenden Anforderungs-/Architekturdateien und in `AGENTS.md`. Ideen dürfen diesen Vorgaben nicht stillschweigend widersprechen oder sie ersetzen.
