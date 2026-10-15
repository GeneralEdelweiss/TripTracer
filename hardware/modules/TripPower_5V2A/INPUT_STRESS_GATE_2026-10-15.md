# TripPower – Eingangsschutz: erster Belastungs- und Datenblatt-Gate (15.10.2026)

**Status: ANALYTISCHER CHECK, KEINE FREIGABE.** Nur der eigenständige TripPower-Zweig `design/solid-state-power-v1`, nicht das historische TripTracer-01I. Architecture unverändert: LM74930QRGERQ1, LMR38020SQDDARQ1, `VIN_PROTECTED_UNFUSED` ohne F302, externe `F_MAIN` (3/4/5 A weiter Kandidaten).

## KiCad-Baseline tatsächlich geprüft

[GitHub Actions 38636492660](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38636492660), Commit `27a39c8425413b5c7d361041516d40d9df53bf8c`: natives KiCad-10-ERC für **3 eigenständige TripPower-Seiten: je 0 Verletzungen**. Native Netlist und 46 Powerpath-Checks und PDF-Export erfolgreich. **Der Gesamtworkflow scheiterte weiterhin** am alten TripTracer-Projekt (Root-ERC/DRC). Der spätere Head `245b89273431cf61e68735df058c02ff11d2ddd1` enthält nur die Übergabe-Dokumentation und **keine neue native Abnahme**; aktuelle Commit-Checks nach dieser Änderung abwarten.

## Herstellerdaten / Abgleich mit der aktuellen Schaltung

- **TI LM74930-Q1:** TI [SNOSDF6](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), [SNOAAA1 200-V-Anwendungsbericht](https://www.ti.com/document-viewer/lit/html/snoaaa1). Eine 10-kΩ-VS-Vorspeisung samt Zener ist eine **Referenzidee** für 200-V-Lastdump, **kein** Nachweis für die konkret verwendeten drei Widerstände oder 9-V-Start. TI unterscheidet korrekt **RAW-gesteuerte OV-Abschaltung** von linearem Clamp-Betrieb; TripPower will Abschaltung. Tests bei TI sind **keine** Tests an TripPower.
- **ST STD17NF25** [DS5089 Rev.5](https://www.st.com/resource/en/datasheet/std17nf25.pdf): VDS=250 V, RDS(on) maximal 165 mΩ **bei 10 V Gate**; Tj bis 150 °C. RthJA **50 K/W nur mit 1 in² FR-4 und 2 oz Kupfer**. ST führt das Teil als **Industrial**, kein AEC-Q101-Beleg. Bei unserer kompakten 35-µm-Platine darf der günstige thermische Kennwert **nicht als Baugruppenbeweis** dienen. SOA-Kurven gelten mit separaten Pulsdauern und Starttemperaturen.

## Reproduzierbare Eckwerte (keine elektrotechnische Qualifikation)

Quelle: `python3 tools/check_trippower_input_stress.py`. Als **bewusst konservative künstliche Rechteckbelastung** 202 V **während der vollen 350 ms** ansetzen. Der echte ISO-Impuls ist keine Rechteckkurve; Netzimpedanz und Einschwing-/Clampingdynamik sind hier nicht enthalten.

| Stressfall | Ergebnis | Nachweisstatus |
|---|---:|---|
| VS-Feed R313–315 = 3 × 3,3 kΩ, Zener nominal 56 V | 14,66 mA / **0,718 W und 0,251 J je R** bei 202 V; rund 48,7 V je R | **Offen**: kein pulsgeprüfter Hersteller-MPN; 1210/2512-Nennwatt allein unzureichend |
| VS-Zener kurz, 3 × 3,3 kΩ bei −1 % (Einzelfehler-Sensitivität) | ca. **0,486 J je R** über 350 ms | **Offen**: Sicherheitsreaktion/Übertemperatur; nicht einfach weiterlaufen lassen |
| OV-Teiler 2 × 750 kΩ + 25,5 kΩ am RAW | je 750k rund **99,3 V**, rund 0,013 W bei 202 V | Impuls- und Dauerspannungsfestigkeit je MPN, Leckstrom/Temperatur offen |
| Q301 bei 9 V, 10 W Buck mit **angenommenen 80 %** + 1 A Rohabgriff | **2,39 A** gesamt, **0,94 W** bei 165 mΩ (RDS 25 °C / 10 V Gate) | Heißer RDS / VGS / Schaltverlust / Kupfer / SOA **offen** |
| Q301 stark vereinfachter thermischer Vergleich | 85 °C + 0,94 W × 50 K/W = **~132 °C**; bei *illustrativ* 1,5 × RDS **~156 °C** | **Warnung**: 50 K/W nur große **2-oz**-Fläche; heiße Rückkopplung nicht modelliert; 1,5 ist keine garantierte Herstellerangabe |
| 9-V-Kaltstart und 9,90-kΩ-VS-Zweig | bei hypothetisch 0,65 mA Last fallen 6,44 V am RVS ab, bleiben ~2,56 V | Keine dynamische VS-Berechnung; **A→VS D302 beibehalten und testen** |

Wichtig: Der statische **250-V-VDS-Wert beweist nicht** die Schalt-SOA für 202 V. Die 202-V-Spannung darf nicht bei vollem Strom für 350 ms pauschal als MOSFET-Wärme angesetzt werden, weil die Auslegung **OV abschaltet**; tatsächliche Gate-Abschaltzeit, Einkopplung, Restlast und Inrush sind separat zu messen und mit der SOA zu vergleichen.

## Reale Bauteilkonkretisierung – 2512 statt 1206 (15.10.2026)

R313/R314/R315 wurden in der Standalone-KiCad-Unterseite auf **Vishay CRCW25123K30FKEGHP**, **3,3 kΩ ±1 %**, **CRCW-HP e3, AEC-Q200**, mit **KiCad-Standard-Footprint `Resistor_SMD:R_2512_6332Metric`** umgestellt. Das ist eine **MPN-/Footprint-/Werte-Entwurfsentscheidung, keine Liefer-/Fertigungsfreigabe**. [Herstellerdatasheet Rev. 17-Mar-2026, Seiten 1 und 5–6](https://www.vishay.com/docs/20043/crcwhpe3.pdf): P70=1,5W **nur bei erforderlicher PCB-Waermeabfuhr**, 2W wenn Anschluss-Pad-Temperatur maximal 105 °C passend kontrolliert, Umax 500V, maximale Filmtemperatur 155 °C, Kurven für Einzel-/wiederholte Pulse. Bei 350 ms liegt der nominelle ~0,718-W-Stress deutlich unter der 2512-HP-Kurvenlinie; **kein Nachweis** für beliebige heisse Wiederholpulse, eingangsseitige 202-V-Wellenform oder Zener-Kurzschluss.

**Mouser Europe Preisindikatoren** ([Produktseite](https://eu.mouser.com/en/ProductDetail/Vishay/CRCW25123K30FKEGHP), Einsicht 15.10.2026; Webbestände können schwanken): 1 St. 0,645 €; ab 10 St. 0,390 €/St.; ab 100 St. 0,273 €/St. / Bestand beobachtet je nach Ergebnis 2715–5120 St.; **Steuern, Versand und tatsächlicher Warenkorb ungeprüft**. Keine JLCPCB Basic/Extended-Behauptung. Hersteller-Koerper 6,3×3,15×0,6 mm. Die 2512-Landpattern-Auswahl ist eine KiCad-Standardgeometrie und **muss noch gegen konkrete Terminations-/Reflow-/Handlotdaten und PCB-Thermik manuell geprueft** werden.

Eckwerte jetzt **3 × 3,3 kΩ = 9,90 kΩ**, statt 9,96 kΩ; `tools/check_trippower_input_stress.py` und `tools/check_trippower_lm74930_values.py` rechnen auf neuer Basis. Kein neuer aktiver Sicherungszweig, keine Aenderung des LM74930/LMR38020-Strompfads oder der nom. Schutzschwellen.

## Entscheidung nach Gate A/B

1. **R313/R314/R315 NICHT für die Fertigung freigeben** bis 350-ms-Pulskurve, Temperatur, Toleranzen und Wiederholung sowie physisches Footprint/Platinenthermik gegen den Hersteller geprüft sind. Für die erste PCB-Auslegung wurde der konkrete Vishay-2512-Kandidat gewählt; dies bleibt ein Entwurf.
2. **Q301 STD17NF25 bleibt PROTOTYP-KANDIDAT, THERMIK-/SOA-BLOCKER.** Erst reale Hochtemperatur-RDS- und Gate-Spannungsrechnung auf der vorgesehenen 35-µm-Kupferfläche plus 202-V-Abschalt-SOA belegen oder einen besser geeigneten, verfügbaren 250-V-FET auswählen.
3. **D301 (56-V-Zener), D303/D304 (TVS), Q302 (60-V-FET), R307/R308/R310/R311 (RAW-Divider)** benötigen eigene Worst-Case-Nachweise. Zusätzlich `RUN_CMD` Fail-OFF/Hot-Leckstrom prüfen.
4. **F_MAIN bleibt extern und noch ohne Nennwert**: bei 9 V und Voll- plus AUX-Last 2,39 A, bei 80 °C die 3-A-Fuse nicht voreilig festlegen. Die realen 12-/24-V-DC-Fuse-Kurven, I²t, Quellimpedanz und *alle* nachgelagerten Leitungen/Stecker/Kupfer unter Kurzschluss **und** Kurzschluss-FET-Fehler nachweisen.
5. **Noch kein eigenständiges PCB-Layout anfangen oder eine Fertigung freigeben**, solange die kritischen Werte/Footprints nicht belegbar sind. Nächster konkret abschließbarer Schritt: passende, dokumentiert pulsfeste R313–315-Serien-MPNs beschaffen und anhand 202-V-/350-ms-Herstellerkennlinien vergleichen; parallel Q301 gegen einen thermisch/automotive besser geeigneten 250-V-FET rechnen.

Rechencheck meldet bei korrekter Mathematik **"BLOCKED"** für die offenen technischen Nachweise, auch wenn er im CI grün ist. Keine ERC-/DRC-/ISO-/Fahrzeug-/Thermik- oder Einkaufsfreigabe aus diesem Bericht ableiten.
