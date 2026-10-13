# TripTracer – Regeln fuer KI/Codex

- Ziel: KiCad 10 und vollstaendig portable lokale Projektbibliotheken.
- V0.3-Schaltplan ist aktueller Elektronikstand. V0.1-Firmware und -Mechanik nur als Prototyp-/Referenzstand behandeln.
- Keine gepruefte PCB-Fertigung, keine bestandenen ERC/DRC, keine Automotive-Sicherheitsfreigabe behaupten.
- Vermeide Vermischung mit SoulTracer (Solar-Schmuck) oder BTN9990LV-Lueftersteuerung.
- Bei Aenderungen so wenige Dateien wie moeglich anfassen; Git-Commit und Aenderungsbericht erstellen.
- Projektlokale Bibliotheken und Modellpfade relativ `${KIPRJMOD}` halten, keine absoluten Windows-Pfade.
- Neue Bauteile mit Hersteller-/Teilenummer, Geometriedatenquelle, Pinout und Geometriepruefung dokumentieren.
- Wiederholte Korrekturen: maximal 3 Versuche pro Fehlergruppe; offene Fehler klar benennen und nicht stillschweigend unterdruecken.
- Erst nach elektrischem Test, KiCad ERC/DRC, manueller Pin- und Footprintpruefung und Automotive-Pruefung fuer Fertigung freigeben.
