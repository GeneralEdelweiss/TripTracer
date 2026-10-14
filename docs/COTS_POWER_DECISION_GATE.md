# TripTracer V1 — COTS-first Stromversorgungsentscheid und Stop-Gates
**14.10.2026 | Branch `design/solid-state-power-v1` | Engineering-Stand, keine Fahrzeug-/Fertigungsfreigabe.**

## Entscheidung für die nächste praktische Iteration
**Die 5-V-Reglerstufe bleibt TI LMR38020SQDDARQ1 (U101, bereits im aktiven KiCad-10-Schaltplan).** Dieser industriell erhältliche Automotive-IC ist selbst ein bewährter Kauf-Funktionsblock mit TI-Referenzbeschaltung; keine proprietär neu entwickelte Buck-Topologie. Er kann auf `BUCK_ENABLE` durch bereits verschaltete ACC-/MCU-HOLD-Stufe gesteuert werden. Das 5V/2A-Ziel wird **nicht** durch eine aktuelle Messung bestätigt. Den vorhandenen USB-Umschalter TPS2116 und den 3V3-Folgeregler beibehalten, bis Tests etwas anderes nahelegen.

**Eingangsschutz ist noch nicht fertig.** Die live verschaltete 01G-Version hat eine 1000-V-Seriendiode D901 mit hoher möglicher Verlustleistung und eine 58-V-TVS D902 ohne bestätigte Kleinmengen-Verfügbarkeit. Die alternative LM74930-Schaltung in `01D_INPUT_PROTECTION` ist lediglich ein *inaktiver Schaltungsversuch* mit nicht vollständig verdrahteten Schutzfunktionen, kein umschaltfertiges Modul. Das ist keine Freigabe der heutigen 01G.

## Gleiche Anforderungen, fairer Kaufteilevergleich
| Option | Positiv | Ausschluss-/Prüfkriterium | Beschluss |
|---|---|---|---|
| **LMR38020-Q1** + bestehende Beschaltung | 80-V-IC, 2 A, EN, mit bestehenden TPS2116/ACC-Netzen verbunden; Referenzwerte/CI vorhanden | Spule/MLCC/EMV/Thermik/ISO und PCB noch ungeprüft | **5-V-Prototypenbasis beibehalten** |
| **RECOM R-78K5.0-2.0L** | Kompletter handlötbarer 5-V/2-A-SIP3-Buck; geringe Designarbeit | 6,5–36-V-Grenzen, 30V plus OVP-Toleranz, **kein EN**, zusätzlicher OFF-Schalter und eigener Einbau-/Thermiknachweis | Als Ersatz derzeit nicht vorteilhaft |
| **RECOM RPH-3.0-CT** | Integriertes flaches 55-V-/3-A-SMD-Modul, EN vorhanden | QFN47-Bestückung, Beschaffungskosten, PCB-/EMV-/Abwärmeprüfungen | Alternative bei Schaltungsneustart |
| **LM74800-Q1** vor einem der Bucks | TI 200-V-Referenz mit zwei MOSFETs und OV | **Keine selbständige Überstromabschaltung**; zusätzlicher Gerät-/Leitungsschutz nötig | Nicht als alleiniger Schutz |
| **LM74930-Q1** vor dem Buck | TI-Referenz für 200 V, integrierte Overcurrent/Short-Circuit/OV/UV, niedriger Verlust möglich | 9V-Start vs. VS-Vorwiderstand/200V-Puls, 250-V-FET-SOA, Shunt, Off-Strom, reale Stückkosten offen | **Bevorzugter Schutz-Redesign-Kandidat** nach Nachweis |

TI LM74930-Q1 Datenblatt Abschnitt 8.2 nutzt Common-Source-FETs, VS-Zener und Schutzteiler für ungedämpften 200-V-Load-Dump. Die Beispielwerte (u. a. 10-kΩ-VS-Zufuhr) dürfen **nicht** ohne Boot-/Pulsrechnung und Temperaturgrenzen kopiert werden. Die 250-V-FET-Alternative onsemi FQD16N25CTM hat bei 10 V Gate **max. 270 mΩ @25°C** und kann bei kaltem Bordnetz/hoher Temperatur trotzdem zu viel Spannungsabfall/Wärme verursachen.

## Konkrete Bestands-/Kostenbeobachtungen (Momentaufnahme, nicht komplettes Angebot)
- RECOM SIP3: bei deutschen Händlern ungefähr **5–6 € einzeln** (MwSt.-Basis je Händler verschieden). Das ist **nur** der Buck, ohne EN-Abschalter/Schutz.
- TI LMR38020SQDDARQ1: in älterer Mouser-Abfrage **ca. 3,92 € / 1, 2,98 € / 10 netto**; Spule/Kondensatoren kommen hinzu.
- TI LM74930QRGERQ1: Mouser DE am 14.10.2026 **ca. 5,39 € / 1, 4,13 € / 10** und nur rund 62 kurzfristig gelistet. **Plus** zwei MOSFETs, Shunt, mehrere passive Schutzteile und PCB. 
- onsemi FQD16N25CTM: LCSC am 14.10.2026 **0,9493 USD / 1, 0,8064 USD / 10**, gelistet lagernd; AEC-Q101 nicht belegt.
- TI TVS5800VEBR: bei früherem Bestandsabgleich **kein bestätigter Kleinmengenbestand**; Einsatz der aktuellen 01G-Variante damit einkaufsseitig blockiert.
- Mischwerte in USD/EUR und brutto/netto nicht direkt addieren. **11–14 € für vollständige Versorgung sind nicht nachgewiesen**.

## Elektrische Auslegungsrisiken
1. **9-V-Fahrzeugquelle:** Vorlasten (Sicherung, Kabel, Stecker, D901) reduzieren VIN. Eine dokumentierte, ausdrücklich angenommene Rechnung für 10W/80% und 0,35Ω Schleife liefert ca. 1,83 A und **2,75 W D901** — thermisch nicht freigegeben. Die 9-V-Boot-/HOLD-Rechnung darf nicht mit 9 V am Regler-Eingang gleichgesetzt werden.
2. **30 V Dauerbetrieb:** RECOM-SIP3 bei höchstens 36 V erlaubt ohne nachgewiesene Schutzschwellen/Toleranzen nicht einfach eine 33-V-OVP als fertig. 58-V-Ladedump ist ein bestimmtes lokales Profil, nicht jede ISO-Störform.
3. **200-V-Load-Dump (Test A):** Die heutige 01G (Diode + TVS) ist **nicht** dafür freigegeben. LM74930-Q1 wäre ein Entwicklungspfad; zu beweisen sind VS-Pulsenergie, FET-VDS/SOA, OVP-Abschaltzeit und Schutz vom 80-V-Buck.
4. **Kurzschluss:** Die externen 58-V-Leitungssicherungen schützen den Leitungsstrang nur mit korrekter Auslöse-/Kabel-/Steckerabstimmung. Buck-Hiccup alleine schützt nicht den Kurzschluss auf VIN vor dem Buck. Bevorzugt elektronisches OCP-Konzept des LM74930, physisch zu prüfen.
5. **USB/ACC:** USB allein soll MCU/SD betreiben, nicht ins Fahrzeugnetz zurückspeisen. M8 hat Vorrang, und Aus nach bounded MCU-/TLC555-Hold muss sicher erfolgen. Netlist-Prüfung ist keine Fail-Injection-Messung.
6. **Ausgangsqualität:** Ripple, 3V3 LDO-Thermik, Displaylast und USB/SD-Spitzen sind nach Lastprofil zu messen; die 2-A-Maximum-Angabe ersetzt keinen Temperaturtest.

## Mindest-Nachweise für einen wirklich fertigen Abschnitt
- [x] COTS/Referenzdesign vor Eigenentwicklung beurteilt; bereits eingesetzten TI-Buck als bewährtes IC erkannt.
- [x] Ist-Bestückung mit `hardware/kicad/power_selection.json` maschinenlesbar; CI-Sanity-Test prüft konkrete Symbol-MPNs/Hie­rarchie.
- [x] KiCad-Netlist-Bauteil-/Power-Path-Assertions aus Vorläufen vorhanden.
- [ ] **Beschaffbarer** input-overvoltage/reverse/short-circuit Schutz mit tatsächlichem nachweisbarem 9–30-V-/Startverhalten auf dem aktiven Eingangsschaltplan, inklusive 58-V-/200-V-Abgrenzung.
- [ ] Worst-case SOC/FET/Diode/TVS/Fuse-I²t/PCB-Copper-/Ruhestrom-/Kaltstart-Rechnung und Temperatur-/Fehlerprüfungen.
- [ ] Alle relevanten KiCad-10-ERC-Verstöße geklärt und **reale PCB-Parität/routed DRC sauber**; project-lokale Footprints/Modelle aktualisiert.
- [ ] USB-Backfeed, ACC-HOLD und SD-Abschalten durch gemessene Fault-Injection bestätigt.
- [ ] 9/12/24/30-V-Lastmessung bei 5V/2A und 0,3–1A, Ripple, EMV und ISO-Profile Test B; Test A nur bei gewählter Anforderung.
- [ ] Kauf-BOM für 1/10/100 inklusive Steuern, Mindestmenge, Montage, doppelte Quellen, tatsächlich bestellbare MPNs.

**Keine Elektro-/Fertigungsfreigabe.** Bis diese Gates erfüllt sind, kann ein dokumentierter, elektrisch plausibler Schaltplan nicht als fertig getestete Fahrzeugversorgung bezeichnet werden. Der bestehende Schutzpfad wird nicht aus kosmetischen Gründen durch eine ebenfalls ungeprüfte Alternative ersetzt.

## Herstellernachweise
- [LMR38020-Q1](https://www.ti.com/product/LMR38020-Q1) · [LM74930-Q1 mit Herstellerreferenz und ISO-Test-A-Design](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf) · [TI Anwendung 200-V-Load-Dump](https://www.ti.com/document-viewer/lit/html/SNOAAA1) · [RECOM SIP3](https://recom-power.com/de/products/switching-regulators/switching-regulators-sip/rec-p-R-78K5.0-2.0L.html) · [RECOM RPH](https://recom-power.com/en/rec-s-RPH-3.0.html) · [FQD16N25CTM Verfügbarkeit](https://www.lcsc.com/product-detail/C415866.html).
