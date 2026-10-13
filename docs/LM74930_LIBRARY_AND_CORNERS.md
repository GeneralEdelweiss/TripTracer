# LM74930-Q1: lokale Bibliothek und Vorabdimensionierung

Stand 13.10.2026. **Bibliothekskandidat; noch nicht in den Strompfad integriert. Kein Fertigungs-/Fahrzeugnachweis.**

## Tatsächlich angelegte und geprüfte Dateien

`TripTracer_V1:LM74930_Q1_RGE` in der bestehenden lokalen Symbolbibliothek; Footprint `Tripmaster:TI_LM74930_RGE0024T_FLOAT_EP`. MPN: TI LM74930QRGERQ1. Quelle: [TI SNOSDF6, Abschnitt 5 und RGE0024T-Zeichnung 4228214/A](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf). Pinbelegung:

| Pad | Signal | Pad | Signal |
|---|---|---|---|
| 1 | DGATE | 14 | HGATE |
| 2 | A | 15 | OUT |
| 3 | SW | 16 | OVCLAMP |
| 4 | UVLO | 17 | NC |
| 5 | OV | 18 | ISCP |
| 6 | EN | 19 | CS− |
| 7 | MODE | 20 | CS+ |
| 8 | NC | 21 | NC |
| 9 | TMR | 22 | VS |
| 10 | IMON | 23 | CAP |
| 11 | ILIM | 24 | C |
| 12 | FLT | 25 | RTN, **elektrisch frei** |
| 13 | GND | | |

Pad 25 darf **nicht an GND**: isolierte 2,1 × 2,1-mm-Kupferinsel, ohne Masse-Vias. Signalpads 0,6 × 0,25 mm, 0,5-mm-Raster, Reihenabstand 3,8 mm; Pad 1 links oben in Draufsicht. Vier vorläufige Pastenfenster 0,9 × 0,9 mm ergeben 73,47 % EP-Bedeckung. Maskenzugabe 0,025 mm; Prozessprüfung steht aus. Kein erfundenes 3D-Modell.

Native KiCad-10.0.6-Symbol-/Footprint-SVG-Exporte: Exit 0, visuell geprüft. Native pcbnew-Ladung bestätigt 25 nummerierte Pads, Pinorientierung, EP-Größe und vier unnummerierte Paste-only-Fenster. Rechnerische Signalpad-Abstände 0,25 mm, EP/Signal 0,55 mm, Maskensteg zwischen Nachbarn 0,20 mm. Dies ersetzt kein fertiges PCB-DRC oder mechanisches Gehäusemodell.

Die bisherigen aktiven Schaltplanseiten bleiben erhalten: alte Schutzfunktionen werden erst durch einen vollständig dimensionierten, geprüften Ersatz abgelöst. Kein neues Platzhalterblatt als fertige Baugruppe integriert.

## Reproduzierbare Berechnung

`python tools/calculate_power_corners.py` erzeugt transparente Szenarien. Eingangslastannahme: maximal 10 W Buck-Ausgang, Wirkungsgrad **angenommen**, keine gemessene Geräteleistung. Bei 6 V und 80 % ergibt sich 2,083 A vor zusätzlichem Frontend-Spannungsabfall. Ein 2-A-Circuit-Breaker wäre zu knapp. Shunt-/Leistungsvarianten werden gerechnet, nicht freigegeben.

Eigene Eckwertrechnung mit 1-%-Widerständen und ±0,2-µA-Eingangsleckstrom:

| Teiler | Berechneter Bereich | Konsequenz |
|---|---|---|
| OV, TI-Beispiel 100k/1,65k | 35,318–39,603 V steigend | Kann 36-V-Normalbetrieb abschalten; ungeeignet als ungeprüfte Kopie |
| OV, Kandidat 100k/1,58k | 36,857–41,329 V steigend | Rechnerisch mehr Abstand zu 36 V; Verzögerung/Surge/FET-Grenzen offen |
| UVLO-Kandidat 100k/12,4k | 4,726–5,308 V fallend; 5,190–5,833 V steigend | Nur Teilerrechnung; Spannungsabfall/6-V-Kaltstart und Filter offen |

Nominale OCP-Formel: RILIM = 12 × RSET / (ILIM × RSENSE). **Keine garantierte Schwelle aus dem Nominalwert behaupten**: Offset-/Gain-/Comparator-Toleranzen und Timing müssen vollständig geprüft werden. ISCP-Anpassung beeinflusst die schnelle Betriebs-Schwelle; die LV_SCP-Startschwelle bleibt fest. Größere Shunts verbessern Auflösung, können aber das Einschalten durch die feste Startschwelle begrenzen.

VS-Schutz-Szenario: 200 V, angenommene 60-V-Klemme, 10k Serienwiderstand → 1,96 W Spitzenleistung im Widerstand und 0,84 W in der Zenerdiode. 350 ms konstantes Plateau ergäbe 0,686 J Widerstandsenergie als konservatives Szenario, **kein normatives Lastdump-Profil**. Gewöhnliches 1206-Pulsvermögen darf daraus nicht vorausgesetzt werden. VS-Start bei 6 V und Ladungspumpenstrom gesondert klären.

## Kosten und offene Gates

Kein zusätzlicher Schutzcontroller, keine neuen Funktionen, keine Bestellung. Der bereits ausgewählte LM74930 bleibt; vorhandene Kostenstudie ist kein aktuelles Angebot. Exakte Shunt-/FET-/Zener-/ACC-MPNs, deutsche Lieferbarkeit, 2-/10-/100-Geräte-Gesamtkosten, LCSC/PCBA-Kategorie und Bestückungsprozess noch offen. VQFN-Unterseitenpad benötigt Paste/Reflow oder passenden Heißluftprozess; Handlötkolben allein ist keine belastbare Montageplanung.

Offen: Vollständiger VS-/Gate-/Zener-Strompfad, 6-V-Kaltstart, OC/SCP-Eckwerte, sicherer Latch-Off/Retry, ACC/HOLD-Failsafe, USB-Rückspeisung, MOSFET-SOA, Pulsbauteile, Temperatur, PCB/EMV und Laborprüfungen. Noch keine Baugruppe als Gate A/B/C bestanden erklären.
