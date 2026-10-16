# TI-Auslegungsrechner und Simulation: tatsächliche Prüfung

13.10.2026. Keine System-/Schaltungsfreigabe.

## Herstellerquellen

- [TI LM74930-CALC REV-A](https://www.ti.com/tool/download/LM74930-CALC/REV-A), Originaldatei LM74930_ID_Design_Calculator.XLSX, nur gelesen, nicht überschrieben.
- [TI PSpice Transient Model SNOM787](https://www.ti.com/lit/zip/snom787), nur lokaler Importversuch.
- [TI EVM-Handbuch SLUUCW6, Abbildung 3-1](https://www.ti.com/lit/ug/sluucw6/sluucw6.pdf), Schaltplan visuell geprüft.

Der Herstellerrechner verwendet im aktiven typischen OCP-Ergebnis `Equations!I23` die konstante 12 × RSET/(Rs × RILIM), übereinstimmend mit der eigenen Nominalrechnung. `Design Calculator!F32/F34` verwenden vereinfacht 0,88/1,10 des typischen Ergebnisses. Das ist nicht automatisch ein vollständiges TripTracer-Toleranz-/Temperatur-/PCB-/Leckstrommodell. Eine weitere, offenbar nicht für die Hauptanzeige verwendete Formel `Equations!I25` nutzt VINNOM anstelle der Konstanten 12; sie wurde bewusst nicht als allgemeine OCP-Formel übernommen. Keine Änderung am Herstellerrechner.

Der EVM-Schaltplan enthält eine zusätzliche Diode D8 von A nach VS, neben R13=10k, D7 und C18. Daher darf die VS-Startversorgung nicht als bloßer 10k-Widerstand mit dauerhaft aus VS gezogenem Datenblatt-Gesamtruhestrom modelliert werden. Die genaue Start-/Umschaltsequenz bei 6 V ist weiterhin ein offenes Gate. EVM-Strompfad und Bauteile sind kein automatisch taugliches TripTracer-Design.

## Tatsächlicher Simulationsversuch

Lokaler ngspice aus der KiCad-Installation, PSpice-Kompatibilitätsmodus. Modell wurde unverändert eingebunden; das Testnetz ist ein **vereinfachter Start-Testaufbau**, kein Export des TripTracer-Gesamtschaltplans. Test-MOSFET-Modell ist generisch; keine SOA-/Automotive-Aussage möglich.

Modellimport scheitert an `74custom193`/`logicexp`-Syntax. Importfunktion meldete zwar Rückgabewert 0, das Fehlerlog enthält aber `ERROR parsing logicexp`, `ERROR in instance uac193log` und den betroffenen Subcircuit. Die Simulation wurde deshalb nicht gestartet. **Keine transienten Ergebnisse, kein bestandener 6-V-Kaltstart oder Fehlertest.** Rückgabewert allein ist hier kein Erfolgsnachweis.

Die digitale Hersteller-Modelllogik wurde nicht umgeschrieben, um einen scheinbar erfolgreichen Verlauf zu erzeugen. Mögliche nächste Wege: Originalmodell in kompatiblem PSpice prüfen oder nach ausdrücklich dokumentierter, fachlich verifizierter Portierung erneut simulieren. Reale Laborprüfung bleibt zusätzlich erforderlich.

Der GitHub-Bibliotheks-Regressionslauf [38471744787](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38471744787) auf `194d2f7` bestätigt KiCad 10.0.6, Hierarchie/Netzliste erfolgreich, weiterhin 347 ERC-Verstöße und 14 DRC-Verstöße sowie 207 Paritätsprobleme. Neue Bibliotheksdateien allein schließen keinen dieser elektrischen Sperrpunkte.
