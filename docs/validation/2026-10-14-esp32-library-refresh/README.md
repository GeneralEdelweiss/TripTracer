# U201-Bibliothekskopie nativ aktualisiert

14.10.2026, KiCad 10.0.6 Windows. Ausgangsstand 2a5f5a8. **Keine Hersteller-/Antennen-/Mechanik-/Fertigungsfreigabe.**

Die DRC-Warnung U201 lib_footprint_mismatch wurde durch eine normale Aktualisierung aus der bestehenden lokalen Footprintbibliothek behoben. Vorheriger PCB-Footprint und Bibliotheks-Footprint wurden mit der nativen KiCad-Footprint-Speicherung normalisiert und verglichen: nach Standardisierung von Referenz/Wert und Entfernung von instanzabhängigen UUIDs/Dateinamen sind die Dateien identisch. Beide normalisierten Originalausgaben liegen als cached.kicad_mod/library.kicad_mod bei. Die genaue interne Ursache der Warnung wurde damit nicht abschließend identifiziert.

Alle **73 physischen Pads**, einschließlich mehrfacher GND-Padnummern, wurden einzeln verglichen: Position, Größe, Bohrung, Form, Orientierung und Kupfer-/Masken-/Pastenlagen unverändert. Aktualisierung erhält U201-Position/Orientierung, PCB-UUID, Root-Schaltplanpfad und Wert. Sämtliche vorhandenen PCB-Pad-Netze bleiben unverändert. Beide bereits enthaltenen Antennen-Keepout-Zonen bleiben vorhanden; es wurden keine Schutz-/Keepout-Funktionen entfernt. Das prüft den Bibliotheksabgleich, nicht die Vollständigkeit der Hersteller-Antennenfreiräume.

## Tatsächliches Ergebnis

Native DRC: **5 Meldungen** statt 6 (4 USB-Lochabstände, fehlender Edge.Cuts-Umriss), **79 unverbundene Verbindungen**, **43 fehlende Footprints** als Paritätsprobleme. Keine neue Meldung, lib_footprint_mismatch entfällt ohne Ausschluss/Regeländerung. Gesamtprüfung weiterhin fehlgeschlagen. Kein Routing, keine weiteren Platinenbauteile oder Kontur ergänzt.

Die Python-KiCad-Bindings meldeten nach dem Kopieren eine SWIG-Warnung zu einem FOOTPRINT-Destruktor/Prozessspeicher; Speichern/Neuladen und die anschließende native CLI-Prüfung wurden trotzdem erfolgreich ausgeführt. Diese Warnung wird nicht als elektrischer Fehler oder bestandene Prüfung umgedeutet.

Kosten/BOM unverändert, keine neue Hersteller-/Teileauswahl. Hersteller-Pin-/Gehäusefreigabe, RF-/Antennenabstände, 3D-/Bestückungsprüfung und die gesamte LM74930-Versorgung bleiben separate offene Gates.
