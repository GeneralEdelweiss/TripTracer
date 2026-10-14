# TripPower 5V/2A – LM74800-Q1 gegen LM74930-Q1

> **Folgeentscheidung 14.10.2026:** Nutzer hat LM74930QRGERQ1 als festen Controller fuer das *neue* eigenstaendige TripPower-Modul gewaehlt. Der Originalvergleich bleibt historisch; die **konkrete vorlaeufige** Bestueckungs-/Werteberechnung steht jetzt in [LM74930_DIMENSIONING_2026-10-14.md](LM74930_DIMENSIONING_2026-10-14.md) und [lm74930_design_v1.json](lm74930_design_v1.json). Aktive TripTracer-01I-LM74800-Schaltung bleibt aktuell unveraendert. Mit Benutzerentscheidung NICHT die unqualifizierten Schaltungs- und Layout-Gates ueberspringen.


**14.10.2026 | AGENTS.md COTS-first- und Gate-A-/Kostenvergleich | keine Schaltungsumstellung, kein ERC/DRC, keine Produktions- oder Fahrzeugfreigabe.**

## Entscheidungsfrage

Universelles, standalone nutzbares Modul fuer **9–30 V DC nominal**, 12/24-V-Fahrzeugnetze, **5 V / 2 A (10 W)** und **physischen unregulierten `VIN_PROTECTED`-Ausgang** nach Eingangsschutz. Gemeinsame Eingangs-OV/Verpol-/FET-Stufe, optional RUN_CMD (3,3-/5-V-Logik nach Pegel- und Rueckspeisungspruefung), MCU-HOLD extern im TripTracer. Nach wie vor fahrzeugseitige DC-bemessene Leitungs-Sicherung Pflicht.

**Vorlaeufiges Engineering-Votum: LM74930QRGERQ1 fuer die neue eigenstaendige Platine bevorzugt. Noch NICHT als geaenderte aktive TripTracer-BOM freigegeben.** Die bestehende aktive Platine `01I_LM74800_INPUT.kicad_sch` und der nachgeschaltete `LMR38020SQDDARQ1` wurden bei diesem Vergleich NICHT geaendert. Erst vor einer bewussten Umstellung Vollkosten, 9-V-VS-Hochlauf, EN-Fail-OFF und FET-SOA nachweisen.

## Datenblattvergleich

| Merkmal | TI LM74800QDRRRQ1 | TI LM74930QRGERQ1 |
|---|---|---|
| Betriebsbereich | 3–65 V | 4–65 V |
| Verpol-/Rueckstrom-Sperre | Ja; zwei externe Back-to-Back-N-FETs | Ja; zwei externe Back-to-Back-N-FETs |
| Ein-/Ausschaltung | EN/UVLO | EN plus eigener UVLO |
| OV-Abschaltung | Externer Teiler, HGATE | Externer Teiler, HGATE |
| 200-V-unsuppressed 24-V-Load-Dump | TI-Common-Source-Beispiel, noch nicht hier qualifiziert | TI-Common-Source-Beispiel, noch nicht hier qualifiziert |
| Einstellbare OCP | **NEIN** | **JA**, Shunt, ILIM, TMR |
| Schnelle Kurzschlusserkennung | **NEIN** | **JA**, ISCP, typisch ca. 3 µs nach Ueberschreitung (keine Garantie fuer gesamten Schalt-/Fehlerverlauf) |
| Fehlerlatch / Retry | Nicht integriert fuer OCP | TMR-Programmierung: Auto-Retry oder Latch-Off mit ~100k parallel zu TMR; Reset ueber EN oder VS-Powercycle |
| Optionaler Diagnoseausgang | Kein OCP-FLT / Strommonitor | FLT open-drain; IMON analog |
| Betrieb Iq typisch | 0,412 mA | 0,65 mA |
| Shutdown-Ic typisch | 2,87 µA | 2,5 µA |
| Gehaeuse | WSON12 3x3 mm | VQFN24 4x4 mm (Wetterability/Handloetaufwand pruefen) |
| Zusaetzliche Teile fuer OCP | sonst separater Strom-/Fehlerschutz noetig | Shunt + RSET + RILIM + RISCP/Filter + CTMR, ggf. RTMR/FLT-Bias |
| Externe Quell-Sicherung | weiterhin Pflicht | weiterhin Pflicht |
| Hochvolt-FET, low-volt-FET, VS-Zener/TVS | weiterhin erforderlich | weiterhin erforderlich |

**Wichtig:** LM74930 ist eine *einstellbare Abschalt-/Circuit-Breaker*-Schutzfunktion, nicht automatisch eine dauerhaft analog begrenzende elektronische Stromquelle. Ein Fehler **vor** dem FET-/Shunt-Pfad (oder verschweisster/kurzgeschlossener FET) muss weiterhin durch externe Leitungssicherungen und Fehleranalyse beherrscht werden. Der zusaetzliche `VIN_PROTECTED`-Anschluss bekommt gemaess Modulvertrag **eigenen nachgewiesenen Abzweig-Kurzschlussschutz**, z. B. passende wartbar austauschbare DC-Sicherung oder eigenen begrenzenden Zweig; globale OCP ersetzt das nicht automatisch.

## Echte TI-Referenz und sinnvolle Topologie

**TI LM74930-Q1 Datenblatt, Figure 8-1 (S. 24):** 200-V-Load-Dump-Common-Source-Referenz; 10-kOhm/60-V-VS-Zener-Zufuhr, Back-to-Back-FETs, 1-mOhm-Rsense bei TI-Beispiel-OCP 5 A / SCP 20 A, OV ca. 37 V. **Diese Schwellen sind NICHT passend als unveraenderte 5-V-TripPower-Dimensionierung:** 5 A Dauer und 20 A Kurzschluss waeren fuer unsere kleine Kopierplatine unnötig hoch. 200-V-FET-SOA/TVS und 9-V-Start noch nicht freigegeben.

**RSENSE muss unmittelbar HINTER dem gemeinsamen FET-Paar liegen und VOR der Aufteilung in Buck-VIN und externen Abzweig:**

```text
VIN_FUSED -> TVS/VS-Klemme -> Q_HV / Q_IDEAL -> RSENSE ----> LMR38020 VIN -> 5V_OUT
                                                     |
                                                     + -> separater Abzweig-Schutz -> VIN_PROTECTED (Klemme)
```

Damit erkennt LM74930 den kombinierten Eingangsstrom, auch bei externem `VIN_PROTECTED`-Kurzschluss. Die angegebene Stromgrenze bezieht sich auf **den Gesamtstrom hinter dem Rsense** und nicht direkt auf 2 A des 5-V-Ausgangs; beide Stroeme unterscheiden sich wegen Spannungswandlung.

### AuslegungsBEISPIEL, noch kein Bauteil-Freeze

Angenommen **85 % Wirkungsgrad** fuer den LMR38020 bei 5 V/2 A:
- Buck-Eingangsstrom ca. **1,31 A bei 9 V**, **0,98 A bei 12 V**, **0,49 A bei 24 V**.
- Bei weiteren **1 A** durch `VIN_PROTECTED` (nur als Lastannahme; Abzweig-Nennstrom noch offen) zusammen **2,31 A bei 9 V**.
- Der LM74930-Referenzansatz mit hypothetisch **RSENSE=5 mOhm** und **RSET=50 Ohm** und `ILIM = 3 A` ergibt laut TI Gl. 15 **RILIM = 12 x 50 / (3 x 0.005) = 40 kOhm**. 20-mV-SCP-Schwelle entspraeche nominell **4 A**; TI spezifiziert 17,4–22 mV fuer den HV-Komparator, also allein daraus 3,48–4,4 A plus Shunttoleranz. **Nicht als qualifizierte Ausloesestromgrenze einsetzen.** 5-mOhm-Shunt-Verlust bei 3 A ~**45 mW**, vorausgesetzt geeigneter 4-Leiter-/Kelvin-Pfad.
- Diese Zahlen dienen nur zur Topologieentscheidung; **RILIM/RSENSE/CTMR** erst nach Festlegung des maximalen externen Abzweigstroms, der Buck-Einschaltstromspitzen und des FET-SOA/I²t festschreiben. Ein ca. 1-ms-Timer nach TI ist kein Ersatz fuer die separate schnelle SCP; Kurzschluss-Impulse, Reset und Lasttransienten pruefen.
- Der vorhandene HV-FET `STD17NF25` wird durch den Abzweig zusaetzlich warm: bei angenommenen 0,165 Ohm und 2,31 A etwa **0,88 W** rein ohmsch bei Nenn-Rds(on), ohne temperaturbedingten Anstieg. FET-/Kuehlflaechen-Upgrade oder kleinerer Abzweigstrom kann erforderlich werden.

## Deutscher Einkaufspreis fuer genau den Schutz-IC

**Mouser Deutschland, Abruf 14.10.2026, gelistete EUR-Artikelpreise, zzgl. Versand/ggf. USt.; keine verbindliche Nettogesamt-BOM:**

| Menge | LM74800QDRRRQ1 | LM74930QRGERQ1 | Aufpreis / Stueck |
|---:|---:|---:|---:|
| 1 | 2,58 € | 5,39 € | **2,81 €** |
| 10 | 1,94 € | 4,13 € | **2,19 €** |
| 100 | 1,59 € | 3,47 € | **1,88 €** |

**Lieferbarkeits-Snapshot:** Mouser DE listete ca. **1.442 Stueck LM74800QDRRRQ1** und **62 Stueck LM74930QRGERQ1**. DigiKey DE zeigte **LM74930 0 sofort lieferbar**, LM74800 dagegen viele Tausend. **LCSC C22428070** zeigte je nach Live-Abruf mehrere Tausend LM74930 auf Lager (USD-Preise, nicht mit EUR mischen). Regionale Mouser-Staende schwanken teils erheblich; vor Bestellung aktiven Bestand und Nettopreis separat verifizieren. Fuer 100 Stueck ist DE-Sofortbestand des LM74930 derzeit **nicht** ausreichend.

**Gesamt-BOM-Vergleich noch offen:** Aufpreis von 1,88–2,81 € ist **nicht** die komplette Differenz, da LM74930 Shunt, Timer, einige kleine Widerstaende/Filter sowie VQFN-Bestueckungsrisiko hinzufuegt. Umgekehrt entfaellt ggf. ein kompletter separater Eingangs-eFuse-/OCP-Controller mitsamt seinen MOSFETs/Passiven. Festlegung erst mit gleicher Sicherheitsfunktion und realen 1/10/100 Stueck, Handloeten/PCBA, PCB, MwSt., Versand. Der LMR38020-Buck bleibt identisch.

## Verbindliche Stop-Gates vor IC-Wechsel

1. **Versorgung/Kaltstart:** 9-V-Start an der 10k/VS-Zener-200V-Referenz, interne Chargepump-Stromspitze und CVs; 30V Dauerbetrieb; Stromrueckspeisung durch RUN/USB. Der Chip ist 4–65 V spezifiziert; das allein garantiert nicht die konkrete RVS-startende Schaltung.
2. **Ruhestrom & Enable:** Vorhandene TripTracer-LM74800-ACC-HOLD-Schaltung ist nicht 1:1 mit LM74930 zu verbinden. 3,3-/5-V-RUN und ALWAYS_ON getrennt konstruieren; BAT-OFF-Ziel <100uA ueber gesamten VIN-Rohpfad inkl. OV/UV-Teiler/TVS/Leckstrom/Backfeed nachweisen. Vorheriger 660k/23.2k-OV-Teiler und dessen Toleranz wird NICHT still kopiert; LM74930-OV-Referenz ist 0,6V und anderer Pin.
3. **Sicherheitsfunktion:** Gemeinsamer Shunt **vor beiden Lastzweigen**. Eigenes `VIN_PROTECTED`-Abzweigschutzglied **nach** Shunt. Kabelquelle und Leitungen separat absichern. Kurzschluss vor und hinter dem Shunt, FET kurzgeschlossen, OCP/SCP/Latch-Off/Auto-Retry, Shunt-Offenbruch, MOSFET-Thermik und Anlauf prüfen.
4. **Transienten:** 200-V-Test-A und begrenzter Test B gesondert; FET 250V Vds/SOA, Q2 60V-Belastung, RVS-Pulsenergie, 56/60V-Zener, TVS, OV-Schaltung, negative ISO-Transienten und realer PCB-Strompfad.
5. **KiCad:** Eindeutiges TI RGE-24 Pad-1..24+EP landpattern mit Herstellergeometrie / lokal, echte netzlistenbasierte Native KiCad 10 ERC/DRC vor Freigabe, eigene kopierbare Platine. QFN-Handloetaufwand ggü. WSON-12 dokumentieren.
6. **Ausgangsleistung:** Bei voller 5V/2A-Last plus externem `VIN_PROTECTED`-Verbraucher liegt der relevante **Eingangsschutz-Strom hoeher**. Kein 5A-Referenz-Schwellenwert ungeprueft als Sicherheitsabdeckung ausgeben.

## Quellen

- TI [LM74800-Q1 Datenblatt Rev C](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf), insb. Fig. 10-25, S.29.
- TI [LM74930-Q1 Datenblatt](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), insb. Fig. 8-1 S.24, Gl. 15, OCP/SCP / TMR S.17–20.
- [Mouser DE LM74800QDRRRQ1](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74800QDRRRQ1) und [Mouser DE LM74930QRGERQ1](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74930QRGERQ1)
- [DigiKey DE LM74930QRGERQ1](https://www.digikey.de/de/products/detail/texas-instruments/LM74930QRGERQ1/22147207) und [LCSC LM74930QRGERQ1 C22428070](https://www.lcsc.com/product-detail/C22428070.html).

**Stand:** Kontroller-Entscheidung fuer NEUES TripPower-Modul begruendet (LM74930 **empfohlen**), Bauteil- und Schaltungs-Freeze wegen fehlender FET-/Shunt-/Thermik-/Kaltstart-/Hot-OFF-Pruefungen **noch nicht moeglich**. Kein Umbenennen von `HV_PROTECTED_AFTER_EFUSE` in eine als eFuse getestete Schiene; keine neuen KiCad-Entwuerfe vor A/B-Gate.
