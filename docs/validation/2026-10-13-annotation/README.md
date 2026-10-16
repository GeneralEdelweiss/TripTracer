# TripTracer: Annotation und Netzlistenintegrität

13.10.2026, Branch `design/solid-state-power-v1`. Kein Fertigungs-/Fahrzeugnachweis.

Acht doppelte Referenzen kollidierten zwischen AUX-Unterseite und ESP32-/USB-Seite: U201, C201–C203, R201–R204. Die AUX-Referenzen sind jetzt U1201, C1201–C1203, R1201–R1204. Sichtbare Referenzen und hierarchische Instanzreferenzen wurden zusammen geändert. Alle anderen Quelldaten, UUIDs, Bauteilwerte, Footprints, Leitungen und Labelpositionen bleiben identisch; Rücknormalisierung der Namen gegen den vorigen Git-Stand bestätigt dies.

64 Symbolinstanzen auf 13 hierarchischen Seiten geprüft. Neuer Hierarchie-/Annotationscheck findet im vorigen Stand acht doppelte Referenzen und nach Korrektur keine. Dieser Check wird auch auf GitHub ausgeführt und ist ein zusätzliches zwingendes Gate.

Native KiCad-10.0.6-Netzliste nach Änderung: Exitcode 0, keine Konsolenwarnung zur Annotation. C201 (100 nF MCU local) und C202 (22 µF MCU bulk) liegen jeweils zwischen V3V3_SYS und GND; C203 zwischen EN_RESET und GND. U1201/C1201/C1202 bilden die AUX-Instanzen. Die frühere mehrdeutige Netzliste stellte C201/C202 auch im globalen GND-Netz dar; daraus darf kein physischer Kondensatorkurzschluss abgeleitet werden. Es war eine Referenzkollision. Aktuelle Verdrahtung ist damit noch nicht elektrisch freigegeben.

Keine Teile ergänzt oder entfernt, keine Kostenänderung. BOM-Zeilen C201/R201/U201 beschreiben weiterhin MCU/USB und wurden bewusst nicht auf AUX-Teile umbenannt. Die bestehende BOM ist noch keine vollständige Stückliste aller 64 Instanzen; AUX-Kandidaten und die Migration auf Variante C bleiben offen.

Unverändert offen: BUCK_ENABLE ohne Treiber, geschützter VIN ohne integrierten Speisepfad, Variante C noch nicht umgesetzt, 3,3-V-/USB-Power-Path noch Arbeitsblatt, PCB ohne Routing/Umriss, vollständige elektrische/thermische/mechanische Erprobung. Kein blindes NC, PWR_FLAG, Ignorieren oder Entfernen alter Schutzfunktionen. Die Gesamt-ERC-/DRC-Nachprüfung wird durch den Commit-Push auf GitHub gestartet; Ergebnis anschließend anhand des tatsächlichen Läufes prüfen.

## Tatsächliche GitHub-Nachprüfung

Commit `9b5a6e2173ce6165a4c48e3ffaae3b1a18d84eb4`, [Lauf 38470416099](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38470416099), KiCad 10.0.6:

- Hierarchie/Annotation: bestanden, 13 Seiten, 64 Instanzen, keine Referenzkollisionen.
- Native Netzliste: erfolgreich, keine Annotationswarnung im Laufprotokoll.
- ERC: weiterhin 347 Verstöße, Exitcode 5.
- DRC: weiterhin 14 Verstöße, Exitcode 5; Schaltplan-Parität von 209 auf 207 Probleme reduziert.
- Bericht-Artefakt erfolgreich gespeichert, ID 11851323497, 27.209 Bytes, SHA256 `304da7b68cf5aafb0b93fc70a8136792686bb268d41751f5e494c4079a2dd26d`. Auf GitHub einen Tag aufbewahrt; vollständiges Runnerlog im Repository mit diesem Bericht gesichert.
- Gesamtworkflow ist wegen der offenen elektrischen/PCB-Befunde korrekt fehlgeschlagen. Keine Regeln herabgesetzt.
