# Bibliotheken und Rechnerwechsel

Das aktuelle KiCad-Projekt liegt unter `hardware/kicad` und enthaelt **alle eigenen** Bibliotheken direkt im selben Ordner: `Tripmaster_Sym.kicad_sym`, `Tripmaster.pretty` und `Tripmaster_3dmodels.3dshapes`. Die Verknuepfungen benutzen `${KIPRJMOD}`. Die Namen wurden bewusst nicht umbenannt, um die V0.3-Referenzen nicht zu zerstoeren. Das GitHub-Repo heisst *TripTracer*.

Die zusaetzliche zentrale Bibliothek liegt unter `symbols`, `footprints`, `3dmodels`. Um sie global zu benutzen, in KiCad einen Pfad `TRIPTRACER_LIB` auf das geklonte Repository legen und die jeweiligen Bibliotheks-Eintraege aus `integration/*.example` **in** bestehende Bibliothekstabellen integrieren. Vorhandene Tabellen nicht ueberschreiben.

Fuer reproduzierbare Projekt-Snapshots sind die lokalen Bibliotheken massgeblich. Die zentrale Bibliothek ist ein Kopier-/Wiederverwendungsangebot, kein Ersatz fuer konkrete DRC/ERC-Pruefungen.
