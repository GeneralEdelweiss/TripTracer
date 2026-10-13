# Portabler KiCad-10-Einsatz

Nach dem Archivimport liegt der aktuelle Schaltplan unter `hardware/kicad/Tripmaster_V0_3.kicad_sch`. Daneben liegen:
- `Tripmaster_Sym.kicad_sym`
- `Tripmaster.pretty/`
- `Tripmaster_3dmodels.3dshapes/`
- `sym-lib-table` und `fp-lib-table`.

Diese Dateien bleiben zusammen. 3D-Referenzen sind projektlokal über `${KIPRJMOD}` vorgesehen. Damit kann der Clone auf verschiedenen PCs an beliebigen Orten liegen.

Die zusätzliche zentrale Bibliothek ist in `symbols/`, `footprints/`, `3dmodels/` verfügbar; für eine globale Einbindung `TRIPTRACER_LIB` auf das jeweilige Repo-Verzeichnis setzen und Beispiele aus `integration/` in vorhandene KiCad-Bibliothekstabellen **integrieren**, nicht blind überschreiben.

KiCad-10-Öffnungsprüfung/ERC/DRC nach dem Import stehen aus.
