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

## Wunschliste und neue Ideen

- Vor jeder **inhaltlichen Weiterentwicklung** (Hardware, Schaltplan, PCB, Firmware, Mechanik oder Funktionen) `docs/IDEAS.md` lesen und relevante Einträge berücksichtigen.
- `docs/IDEAS.md` ist ein Ideenspeicher, **kein automatischer Entwicklungsauftrag**. Ideen nicht allein wegen ihres Eintrags implementieren oder als verbindliche Anforderung behandeln.
- Bei der Planung explizit beauftragter Arbeiten prüfen, welche vorhandenen Ideen dazu passen. Konflikte mit Sicherheitsanforderungen, aktueller Architektur, Bauteilverfügbarkeit oder Aufwand offen benennen.
- Nur ausdrücklich vom Nutzer freigegebene Funktionen umsetzen. Neue spontane Ideen nicht ungefragt in fertige Platinen, Firmware oder Stücklisten übernehmen.
- Bei tatsächlich umgesetzten Ideen den Status in `docs/IDEAS.md` mit Version oder Commit aktualisieren; nur getestete Ergebnisse als getestet kennzeichnen.
- Verbindliche Projektentscheidungen separat in den Anforderungs- und Architekturdateien festhalten. Die Wunschliste ersetzt diese Dokumente nicht.

## Hardware-Anforderungen vor Bauteilauswahl

- Bei Schaltplan-, PCB-, Versorgungs- und Mechanikarbeiten zuerst `docs/HARDWARE_REQUIREMENTS.md` lesen und Anforderungen mit dem aktuellen KiCad-Bestand abgleichen.
- Bei gemeinsam geklaerten Entscheidungen die betroffenen IDs und das Entscheidungsprotokoll in `docs/HARDWARE_REQUIREMENTS.md` aktualisieren; nicht voreilig Bauteile festlegen oder offene Punkte als beschlossen ausgeben.
- **Geraetesicherung auf der Platine (PWR-03)**. Das ersetzt nicht den notwendigen Kurzschlussschutz der Fahrzeug-Zuleitung ab der Quelle. Selbst angefertigte M8-Kabel duerfen an bereits abgesicherten Fahrzeugabgriffen betrieben werden; Direktanschluss an die Batterie erfordert quellseitige Absicherung.
- Aenderungen an der Hardware-Architektur mit `docs/ARCHITECTURE.md` und der Wunschliste abgleichen. Die Version V0.3 bleibt historischer Bestand.
