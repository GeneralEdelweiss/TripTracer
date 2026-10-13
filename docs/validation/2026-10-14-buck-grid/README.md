# Buck-Raster und sichtbare Leitungen – native KiCad-Prüfung

14.10.2026, KiCad 10.0.6 auf Windows. Ausgangscommit 2513fdf. Keine Fertigungsfreigabe.

## Änderungen

Die neun LMR36520-Symbolanschlüsse lagen bei x=±22,58 mm außerhalb des 1,27-mm-Verbindungsrasters. Cache und lokale Symbolbibliothek verwenden jetzt x=±22,86 mm; Symbolkörper x=±17,78 mm erhält unveränderte 5,08-mm-Pinlänge. Nummern, Namen, elektrische Pintypen, MPN und Footprint unverändert. Buck-Symbolpositionen, Wire-Endpunkte, Junctions und Anschlusslabels auf 1,27-mm-Raster verschoben. Keine anderen Seiten gerastert.

Die Standard-Netzklasse enthielt keine Schaltplan-Darstellungswerte. Der native SVG-Export schrieb die Leitungen als `fill:none; stroke:none`; im gerenderten Blatt waren sie unsichtbar. Ergänzt wurden wire_width=6 mil, bus_width=12 mil, line_style=0 und die KiCad-Standardfarbe `rgba(0, 0, 0, 0.000)` als keine eigene Farbübersteuerung. Nach Ergänzung erscheinen Leitungen grün. Leiterbahnbreiten, PCB-Abstände, Prüfregeln und Ausschlüsse bleiben unverändert. Ein Versuch mit solid statt default beim Wire-Stroke löste den Darstellungsfehler nicht; diese Änderung wurde vollständig zurückgenommen.

Schemafeld-Namen/Größen folgen dem [offiziellen KiCad-Hierarchie-Demoprojekt](https://gitlab.com/kicad/code/kicad/-/blob/9.0/demos/complex_hierarchy/complex_hierarchy.kicad_pro?ref_type=heads). Das lokale Projekt bestätigt die Wirkung mit dem nativen SVG-Vorher/Nachher-Export.

## Tatsächliche Prüfung

| Prüfung | Befund |
|---|---|
| Native vollständige Netlisten vor/nachher | Alle 260 Pin-Netz-Zuordnungen, Netznamen und Knotenmengen exakt identisch |
| Vollständiger hierarchischer ERC | 304 Meldungen statt 347; alle 43 Buck-Rasterwarnungen behoben |
| Übriger ERC | 227 Rasterwarnungen, 4 isolierte Pinlabels, 56 unverbundene Pins, 11 ungetriebene Versorgungspins, 6 ungetriebene Eingänge |
| Vollständiger PCB-DRC einschließlich Parität/Zonenfüllung | Weiterhin 14 DRC-Meldungen, 207 Paritätsprobleme, 0 unverbundene PCB-Elemente; PCB ohne Routing/Netzzuweisung bleibt nicht freigegeben |
| Hierarchie/Annotation | 13 Seiten, 64 Symbole, keine Struktur-/Referenzfehler |
| Native SVG + PNG-Sichtprüfung Buck | Leitungen sichtbar; Schnittstellen unverändert. Beschriftungen weiterhin teils zu dicht/gedreht; keine vollständige visuelle Abnahme aller Seiten |

Keine PWR_FLAGs, NC-Markierungen oder Warnungsunterdrückung hinzugefügt. BUCK_ENABLE und geschützter VIN-Eingang bleiben ohne echten Treiber/Speisung; dadurch weiterhin ungetrieben. LM74930-Frontend/ACC-HOLD sind noch nicht integriert. Kein Funktions-/Labor-/Transientennachweis. Kosten/BOM unverändert, keine neuen Bauteile.

Die Originalausgaben liegen in before.net, after.net, erc-after.json, drc-after.json und verification.json. buck-after.svg ist der native Buck-Export. Das mechanische PCB und sämtliche anderen Bibliotheksgeometrien wurden durch diese Symbol-/Darstellungskorrektur nicht freigegeben.

## GitHub-Bestätigung

[Run 38475460659](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38475460659) am Commit ee121f1b0a2673c3258a3865c458360ff04b5260: KiCad 10.0.6 bestätigt ERC 304, DRC 14, Parität 207; Hierarchie und Netliste erfolgreich. Gesamtprüfung bleibt fehlgeschlagen. Tatsächliches Rohlog in github-run.log.
