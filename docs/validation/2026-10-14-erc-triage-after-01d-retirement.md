# KiCad 10.0.6: ERC-Triage nach Entfernung der TPS26631 (14.10.2026)

Verifizierter GitHub-Actions-Lauf: [38519728228](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38519728228), Commit `8e590d1`. Originale KiCad-CLI JSON-Reports sind als Action-Artefakt verfügbar; die neue automatische `tools/triage_kicad_erc.py`-Auswertung wird zusätzlich in die Job-Zusammenfassung geschrieben.

## Natives Ergebnis

- **Hierarchieprüfung bestanden:** 15 Seiten, 79 aktive Symbolinstanzen, keine doppelten Referenzen/fehlenden Unterseiten.
- **Native Netlist exportiert.**
- **ERC nicht bestanden:** 285 Meldungen. Genau 226 `endpoint_off_grid`-Warnungen, 36 `pin_not_connected`-Fehler, neun `lib_symbol_issues`-Warnungen, sieben `power_pin_not_driven`-Fehler, sechs `isolated_pin_label`-Warnungen, ein `pin_not_driven`-Fehler.
- **PCB-DRC nicht bestanden:** fünf DRC-Meldungen, 79 unverbundene Leiterplattenobjekte, 51 Schaltplan-/PCB-Paritätsprobleme.

## Nächste Arbeitsreihenfolge nach wirklichen Ergebnissen

1. Die **36 unverbundenen Pins der ESP32-Seite** sind echte, noch nicht ausgelegte Signale/Versorgungen; nicht mit `no_connect` zudecken, bevor die USB-/BOOT-/3,3-V-Architektur fertig ist.
2. Die **sieben fehlenden Power-Treiber** unterscheiden zwischen absichtlich isolierten 01E/01C-Designkandidaten und der noch nicht integrierten Hauptversorgung. Echte Source-/Enable-Pfade bauen, keine kosmetischen Power-Flags.
3. Das **226er Off-grid-Cluster** liegt komplett in der Root-Schemaansicht; das bedarf einer gezielten Koordinaten-/Netz-ID-Korrektur ohne Änderung der elektrischen Pinverbindungen und anschließendem Netlist-Diff.
4. Bibliothekssymbolfehler (neun) in konkreten Projektsymbolen prüfen, nicht ignorieren.
5. Erst nach physisch richtiger Hauptstrompfad-/GPIO-/USB-Schaltung PCB-Layout/Parity synchronisieren.

Die mittlerweile existierenden 01E/01F sind **verdrahtete, aber isolierte Entwicklungskandidaten**, kein nachgewiesenes End-to-end LM74930-Frontend. Die Entfernung von U401 TPS26631 war technisch geboten, beseitigt aber weder den echten LM74930-Versorgungspfad noch die obigen Fehler.

**Fertigungsstatus:** NICHT FREIGEGEBEN.

## Ergänzung: reale Pinoutkorrektur 01F – neuer nativer Check

Beim erneuten Abgleich mit dem [Diodes BAS116Q-Datenblatt DS30233, Seite 1](https://www.diodes.com/datasheet/download/BAS116.pdf) wurde ein kritischer Fehler im 01F-KiCad-Symbol entdeckt: **Pin 2 ist NC und nicht eine zweite, intern verbundene Anode**. Das Bauteil hat A1, NC2 und K3. Lokale Projektbibliothek, eingebettetes Schaltplansymbol und Anoden-Pin-2-Wire wurden korrigiert. Ebenfalls wurde die interne Symbolbenennung für den N-MOS Q801 auf `NMOS_GDS_127` vereinheitlicht und dessen G1/S2/D3-Belegung mit dem [Originaldatenblatt DMN2056U](https://www.diodes.com/datasheet/download/DMN2056U.pdf) gegengeprüft. Dieser 20-V-MOSFET ist **ausschließlich** im galvanisch vom 9–30-V-Fahrzeugnetz getrennten 5-V-RC-Prototyp zulässig, nicht als Hochvolt-Eingangs-FET.

Das GitHub-Actions-Skript `tools/check_kicad_custom_pinouts.py` prüft beide Pinbelegungen automatisiert. Der aktuelle Lauf [38521195946](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38521195946) bestätigt: Hierarchie, Pinout-Prüfung und nativer Netlist-Export erfolgreich. **KiCad-10-ERC bleibt mit 277 Meldungen und PCB-DRC mit fünf Meldungen / 79 Unconnected / 58 Paritätsproblemen nicht bestanden.** Der zuvor erwähnte lokale Debug-Lauf der Pinoutprüfung hatte einen Regex-Escaping-Fehler, der anschließend korrigiert und im obigen Lauf erfolgreich gegengeprüft wurde.

Die 277 ERC-Meldungen gliedern sich in 226 `endpoint_off_grid`, 36 `pin_not_connected`, 7 `isolated_pin_label`, 7 `power_pin_not_driven`, 1 `pin_not_driven`; die separate 01F-Pinfehlerkorrektur hat zudem die früheren Bibliothekssymbolwarnungen beseitigt. Der LM74930-Hauptleistungspfad bleibt weiterhin nicht verdrahtet; ausdrücklich **keine Fahrzeug- oder Fertigungsfreigabe**.
