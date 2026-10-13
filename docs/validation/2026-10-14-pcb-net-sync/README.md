# Vorhandene PCB-Pads aus echter Root-Netzliste zugeordnet

14.10.2026, KiCad 10.0.6 Windows. Ausgangscommit c893858. **Keine Routing-/Mechanik-/Fertigungsfreigabe.**

Die 21 bereits vorhandenen PCB-Footprints besitzen passende Schaltplanreferenzen. Aus dem nativen Root-Netzlistenexport wurden 142 nummerierte Pads ihren Netzen zugeordnet. Zwei unnummerierte USB-Bohrungen sind NPTH und bleiben bewusst netzlos. 20 Werte wurden aus dem Schaltplan übernommen, ausschließlich bei identischem Footprint-Library-Identifier. L101 bleibt mit seinem bisherigen Wert, weil sein alter SRN6045-Footprint nicht zum ausgewählten SRP6030VA-100M gehört; kein falscher MPN auf falscher Geometrie.

Native pcbnew-API prüfte nach Speichern/Neuladen alle Pad-Netznamen gegen die Netzliste und unveränderte Footprintpositionen/-orientierung/-Library-IDs sowie Padpositionen/-formen/-größen/-bohrungen/-lagen. Keine Bauteile verschoben, keine Leiterbahnen/Vias/Zonen oder Boardkontur hinzugefügt, keine Regeln abgeschwächt. KiCad 10 speicherte die PCB-Datei nativ neu, daher größere Formatänderungen.

## Tatsächlicher nativer DRC

| Befund | Vorher | Nachher |
|---|---:|---:|
| DRC-Meldungen | 14 | 6 |
| Kupfer-Abstandsverstöße USB | 4 | 0 |
| Lötstoppbrücken USB | 4 | 0 |
| Loch-Abstandsverstöße USB | 4 | 4 |
| Fehlender Edge.Cuts-Umriss | 1 | 1 |
| U201 weicht von Bibliothekskopie ab | 1 | 1 |
| Unverbundene Verbindungen | 0, mangels Netzen nicht aussagekräftig | 79, jetzt korrekt sichtbar |
| Schaltplan/PCB-Paritätsprobleme | 207 | 45 |

Überlappende USB-Padpaare tragen nun entsprechend der nativen Schaltplannetze gleiche GND-/VBUS-Netze; die 8 entsprechenden Kupfer-/Maskenmeldungen entfallen ohne Geometrieänderung oder DRC-Ausschluss. Die Lochabstände bleiben unverändert 0,1944 mm bei geforderten 0,25 mm. Keine automatische Freigabe der USB-Geometrie.

Parität aktuell: 43 fehlende Footprints und zwei L101-Abweichungen (Wert/Footprint). Alle vorhandenen nummerierten Pad-Netze stimmen mit der geprüften Root-Netzliste überein. Der aktuelle Schaltplan selbst ist noch unvollständig; richtige Übernahme seiner Netze macht die Gesamtversorgung nicht funktionsfähig. U201-Library-Geometrieabweichung, USB-Bohrungen, Spulen-Footprint, sämtliche fehlenden Bauteile, Routing und Mechanik bleiben offen.

Datenblatt-/Pinoutfreigaben aller Bauteile, Thermik, Last-/Transiententests und die LM74930-Migration stehen weiter aus. Keine Bauteile gekauft oder neu hinzugefügt; BOM-Kosten unverändert. DRC gesamt fehlgeschlagen. Reale JSON-Ausgabe und vollständige 142-Pad-Zuordnung in drc-after.json/verification.json.
