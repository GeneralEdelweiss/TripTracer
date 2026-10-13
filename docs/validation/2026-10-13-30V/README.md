# Dauerbetrieb auf 30 V angepasst

Anforderungsänderung vom 13.10.2026: 9–30 V Dauerbetrieb, weiterhin 6 V Motorstartziel. Reproduzierbare Eckwertrechnung mit `tools/calculate_power_corners.py`: Eingangsszenarien 6/9/12/24/30 V, OVP-Kandidat 100k/1,8k mit 1-%-Widerständen und ±0,2 µA Eingangsleckstrom ergibt 32,422–36,357 V steigende Schwelle. Rechnerisch geprüft; kein eingesetzter Teiler, keine Messung. Separate Transientenziele unverändert.

Schaltplan und PCB wurden durch diese Anforderungsänderung nicht verändert; keine neue ERC-/DRC-Messung daraus ableiten. Die bisherigen Fehler und offenen elektrischen/mechanischen Prüfungen bleiben bestehen. Keine Fertigungsfreigabe.
