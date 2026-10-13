# TripTracer – Codex-Anweisungen

- KiCad 10 ist das Zielsystem. Projekte müssen ohne absolute lokale Pfade portabel bleiben.
- **Elektronik:** V0.3 ist aktuell. **Mechanik und Firmware:** V0.1 ist nur Prototypenstand.
- Keine funktionsfähige, vollständig geroutete oder geprüfte Leiterplatte behaupten.
- Bauteile nur anhand dokumentierter Herstellerdaten, Pinbelegung und Footprint-Geometrie als verifiziert kennzeichnen.
- Nicht mit SoulTracer (Solar-Schmuck) oder der BTN9990LV-Lüftersteuerung vermischen.
- Keine unkontrollierte Änderung an intakten Symbol- und Footprintverknüpfungen.
- Verwende projektlokale `${KIPRJMOD}`-Bibliotheken für reproduzierbare KiCad-Projekte.
- Vor Änderungen Git-Status und bestehende Projektdateien prüfen. Neue Revisionen nachvollziehbar committen.
- ERC/DRC mit KiCad ausführen, wenn vorhanden; Fehlschläge melden. Ungeprüfte Ergebnisse nie als bestanden ausgeben.
- Maximal drei automatische Korrekturzyklen pro Fehlergruppe, danach Ursachenbericht.
- Fahrzeugversorgung: Schutz vor Load Dump, Transienten, Verpolung, ESD/EMV und thermische Reserven vor Feldbetrieb validieren.
