# Dauerbetrieb auf 30 V angepasst

Anforderungsänderung vom 13.10.2026: 9–30 V Dauerbetrieb, weiterhin 6 V Motorstartziel. Reproduzierbare Eckwertrechnung mit `tools/calculate_power_corners.py`: Eingangsszenarien 6/9/12/24/30 V, OVP-Kandidat 100k/1,8k mit 1-%-Widerständen und ±0,2 µA Eingangsleckstrom ergibt 32,422–36,357 V steigende Schwelle. Rechnerisch geprüft; kein eingesetzter Teiler, keine Messung. Separate Transientenziele unverändert.

Schaltplan und PCB wurden durch diese Anforderungsänderung nicht verändert; keine neue ERC-/DRC-Messung daraus ableiten. Die bisherigen Fehler und offenen elektrischen/mechanischen Prüfungen bleiben bestehen. Keine Fertigungsfreigabe.

GitHub KiCad 10.0.6: Run [38474082917](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38474082917), Commit d16adfb606975862df1078a8f6f9961b56a04bd2. Hierarchie/Annotation und Netlistenexport erfolgreich, ERC 347 Meldungen, PCB-DRC 14 Meldungen und 207 Schaltplan/PCB-Paritätsabweichungen. Gesamtprüfung fehlgeschlagen; Rohlog in github-run.log. Keine neue Hardwareprüfung bestanden.
