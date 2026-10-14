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
