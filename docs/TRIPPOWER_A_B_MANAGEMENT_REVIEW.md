# TripPower – Projektleitung / unabhängiger A–B-Review

Stand: 2026-10-15. **Engineering-Review, keine Fertigungs-, PCB-, ISO- oder Fahrzeugfreigabe.**

## Arbeitsaufteilung und Quellstand

- Gemeinsame Ausgangsbasis: `design/solid-state-power-v1`, Commit `2cafbf43e24aadc12ede10cd413b962c84579664`.
- Weg A: `design/trippower-a` – bestehender LMR38020-Q1, 80 V, optimieren.
- Weg B: `design/trippower-b` – 36-V-Modul TPSM33620S5QRDNRQ1 mit eigenständig begründeter Schutzarchitektur prüfen.
- Review: `design/trippower-review` – nur Befunde, Quervergleiche, Freigabegates und Empfehlungen. **Keine ungeprüften Änderungen an A oder B.**
- Erstaufnahme: A und B waren zum Zeitpunkt des Vergleichs mit der Ausgangsbasis identisch (0 Commits voraus/zurück). Das ist **kein** Entwicklungs- oder Testergebnis. Fortschrittswerte müssen bei jeder Kontrolle neu abgefragt werden.

### Autoritative Unterlagen

1. `AGENTS.md`, insbesondere oberste REV5-Korrekturen.
2. `hardware/modules/TripPower_5V2A/REV5_DESIGN_BASELINE.json`.
3. `hardware/modules/TripPower_5V2A/START_HERE_NEXT_CHAT.md` (neue REV5-Abschnitte haben Vorrang vor historischen REV2–4-Aussagen).
4. `hardware/modules/TripPower_5V2A/OVP_36V_MODULE_TRADEOFF_2026-10-15.md`.
5. `hardware/modules/TripPower_5V2A/MPM3551_SWAP_DEEP_DIVE_2026-10-15.md`.

## Unverhandelbare Prüfkriterien

| Bereich | Entwicklungsziel | Prüfnachweis / offene Einschränkung |
|---|---|---|
| Dauerbetrieb | VIN am Anschluss 9–30 V | Kalt- und Wiederanlauf, 0/0,5/2 A, Toleranzen; kein pauschal garantierter 9-V-Start |
| Ausgang | 5 V / 2 A | Spannungsregelung, Transienten, Welligkeit, thermische Verlustleistung |
| AUX | RAW-AUX-Entwurfsziel 1 A | Pfad- und Fehlerlast prüfen, nicht mit geregelten 5V verwechseln |
| Transiente | **200 V / 350 ms ungedämpfter Lastabwurf** vor Eingangsschutz | echte Puls-/SOA-/Spitzen-/Temperaturprüfung; historische 202-V-Angaben nicht übernehmen |
| Temperatur | Umgebung −40 bis +125 °C | Hersteller-Maximalwerte, Ceff, SOA, Derating, nicht mit ungesicherter EVM-Rth gleichsetzen |
| Sicherheitsziel | Brand/Leitungsschaden verhindern | F_MAIN extern austauschbar, Kurzschluss, Überstrom, Wiederholfehler, Leiterbahnen |
| Betriebsverhalten | ACC/HOLD, USB-Betrieb, keine Rückspeisung | VIN=0/RUN/USB, kontrollierte Abschaltung; Reset und Datenverlust können zulässig sein |
| Artefakte | portables KiCad 10 | ERC/Netlist, Footprints/3D, BOM, PCB-DRC erst nach wirklichem PCB, Modell- und Pinprüfung |
| Kosten | 1/10/100 Stk, real lieferbar | reine Komponenten-/Bestückpositionen **und** Schutz-/PCBA-/Testaufwand vergleichen |

**Keine grüne CI mit funktionsfähiger Hardware gleichsetzen.** P01–P10 sind bis zum jeweils dokumentierten belastbaren Nachweis **BLOCKED**.

## Kritische Entscheidungsfragen

### Weg A – LMR38020-Q1

- Nachweisbarer 9-V-Erststart und definierter Wiederanlauf; VS/CAP/RESET/EN inklusive Temperatur, Leckströmen und Bauteiltoleranzen.
- 200-V-/350-ms-Pfad: Q301-SOA im heißen Zustand, Gate-/Zener-/R313–315-Pulsbelastbarkeit und F_MAIN.
- Thermal-/Layout-Reserve bei 30 V, 5 V/2 A, −40…+125 °C.
- Weitere DNP-/Teileersparnisse nur ohne Verlust des Fehlerschutzes oder neuen unsicheren Betriebszustand.

### Weg B – TPSM33620S5QRDNRQ1

- **Harte 36-V-VIN-Betriebsgrenze; 40 V ABS MAX ist kein Betriebsfenster.** Gesonderter Beweis, dass maximale OVP-Schwelle **und** dynamische Spannung am tatsächlichen Modul-VIN-Pad sicher innerhalb der zulässigen Grenzen bleiben.
- Unter allen relevanten OV/UV-Toleranzen sicherer **Wiederanlauf bei 30 V** nach Überlast/OVP.
- 200-V-/350-ms-Schutz mit Q301-SOA, dynamischer Abschaltung und Überschwingern.
- Kosten- und Bestückvorteil gegenüber A inklusive eventuell zusätzlicher OVP-, Clamp- und Filterteile; Vorteil der integrierten Induktivität ist noch keine gesamte Systemersparnis.
- Thermisches Derating und reale Gehäuse-/PCB-Bedingungen dokumentieren.

Aktuelle Referenzstudien zeigen: Ein bloßer R309-Tausch schließt die 36-V-OVP/Wiederanlauf-Lücke **nicht**. Ein solcher Tausch darf nicht als fertige Weg-B-Lösung bewertet werden.

## Einheitliches Reporting je Weg (bei jeder überprüfbaren Revision)

- Branch, Commit-SHA, Datum, geänderte Dateien und Ausgangsrevision.
- Exakte Schaltungsänderungen, elektrische Wirkungsannahmen und Datenblattstellen.
- Nachgewiesen (rechnerisch/Herstellerdaten/Simulation/Messung) und nicht nachgewiesen **getrennt**.
- Aktive Bestückpositionen AUTO/RUN, MPN-Verfügbarkeit, BOM-Kosten für 1/10/100, Handbestückaufwand.
- Reproduzierbare ERC-/Netlist-/DRC-Ergebnisse inkl. genauer Umgebung und ausgeführtem Befehl.
- Temperatur-/SOA-/Puls-/Fehlerszenarien, verbleibende P01–P10-Blocker.
- Klare Entscheidung: akzeptieren / nachbessern / verwerfen mit Begründung.

## Bewertungs- und Freigabeverfahren

1. **Sicherheits-Stop-Gates**: offener Brand-, Kabel-, Q301-SOA-, Überspannungs- oder Kurzschlussnachweis verhindert Freigabe unabhängig vom Preis.
2. **Pflichtfunktion**: 9–30 V, 5 V/2 A, 30-V-Restart und 200-V-/350-ms-Profil sind nachzuweisen bzw. bleiben explizit offen.
3. **Erst danach**: Teilezahl, Handbestückung, Einkauf, thermische Reserve, Leiterplattenfläche und Entwicklungsaufwand vergleichen.
4. **Projektmanager-Empfehlung** ist von Nutzerentscheidung und Hardware-/Fahrzeugfreigabe zu unterscheiden.

## Erststatus

| Kategorie | Weg A | Weg B |
|---|---|---|
| Branch angelegt | Ja | Ja |
| Abweichung von gemeinsamer Baseline bei Erstprüfung | 0 Commits | 0 Commits |
| Architektur | LMR38020-Q1 als Untersuchungsziel | TPSM33620S5QRDNRQ1 als Untersuchungsziel |
| Reproduzierbarer Branch-spezifischer Nachweis | Noch nicht begutachtet | Noch nicht begutachtet |
| Fahrzeug-/Fertigungsfreigabe | NEIN | NEIN |

**Nächste Aktion im Review-Chat:** Beide Branches nach neuen Commits vergleichen, tatsächliche KiCad-/Rechen-/Testdaten prüfen, offene Blocker und eine nachvollziehbare A/B-Empfehlung protokollieren. Kein automatisches Hintergrundmonitoring behaupten.
