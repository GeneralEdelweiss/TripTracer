# TripPower Weg A – Runde 3: redundante VS-Klemme als **separater KiCad-Prototyp** (2026-10-15)

**Arbeitsbranch:** `design/trippower-a`. Gelesen: `docs/TRIPPOWER_A_B_REVIEW_ROUND2_2026-10-15.md` auf `design/trippower-review` sowie `WEG_A_EXECUTABLE_P03_P04_P01_EVIDENCE_2026-10-15.md` im A-Branch. Arbeitsziel: D301-OFF-Einzelfehler konstruktiv entschärfen statt nur weitere Risikotexte produzieren.

**Entscheidung:** **PROTOTYP JA, REV5-PRODUKTIONSBOM/PCB-RELEASE NEIN.** Eine unabhängige zweite 56-V-Schutzdiode D306 ist *physisch in einem alternativ exportierbaren KiCad-Schutzblatt* eingefügt. Die originale REV5-Hierarchie/Bestückung ist **unverändert**. Die native A-KiCad-10-CI überprüft beide Stände und die einzige zusätzliche D306-Verbindung (K→VS_CLAMP/A→GND). Unterbrechung von D301 ist damit **nicht mehr das einzige externe Klemmen-Ausfallereignis**, solange D306 elektrisch und thermisch tatsächlich überlebt. Für die Forderung -40…+125°C und 200V/350ms ist diese Überlebensfähigkeit **noch nicht bewiesen**. P01–P10 bleiben offen.

## 1. Reale Netzliste / Expositionspfad

Aktives originales Schaltblatt `01_Protection_LM74930.kicad_sch` mit **nativem KiCad 10 exportierter** Hierarchie-Netzliste:

| Signal/Teil | Native Pins | Einfluss D301-offen |
| --- | --- | --- |
| Eingangsquelle | VIN_FUSED → R313.1, R313.2=VS_SERIES_A; R314.1=VS_SERIES_A/2=VS_SERIES_B; R315.1=VS_SERIES_B/2=VS_CLAMP | 9,9k ohm bei 25°C; DC-Energiequelle auch bei abgeschalteten Q301/Q302 |
| D301 | K1 VS_CLAMP / A2 GND | Bei OFFEN entfällt externer 56-V-Shunt |
| D302 | K1 VS_CLAMP / A2 SOURCE_A | SOURCE_A ist beim initial abgeschalteten Q301 nicht zuverlässig verfügbar; D302 ist **keine** unabhängige VIN→VS-Backupleitung |
| U301 LM74930 | VS pin22 und MODE pin7 an VS_CLAMP; EN/TPS38-Netz über VS-Pullup | VS-Betrieb max65V, abs70V; weitere an VS gebundene Pins sind separat in Herstellergrenzen zu betrachten |
| U302 TPS38A010122DSKRQ1 | VDD pin1 VS_CLAMP, SENSE1 VS_SENSE über R330/R331, RESET1/2 direkt CTRL_EN über R333 | VDD Betrieb max65V, abs70V; TI sagt explizit, keine internen Hochspannungs-Clamps als Schutz annehmen |
| C302/C308/C312 | 1uF+10uF+10uF jeweils VS_CLAMP→GND | alle mit 100V Nennspannung, DC-deratiertes Ceff unbekannt |
| Alternative D306 | K1 VS_CLAMP / A2 GND | zweite externe Shunt-Zener, keine RVS-/C-/Steuersignaländerung |

Bei **D301 offen und ohne D306**, SOURCE_A=0, ohne IC-Last und ohne innere Clamps erhält man für ideal konstant 21uF: `VS(t)=200-(200-VS0)*exp(-t/(9900*21uF))`. Bei VS0=0 liegt VS bei 350ms ~162,9V, bei VS0=56V ~173,3V; 65V können bereits nach ~82ms bzw. ~13ms überschritten werden; anschließend werden 70V-abs-Pins und die 100V-Kondensatoren im Modell erreicht bzw. überschritten. **Dies ist ein absichtlich ungünstiges RC-Gegenbeispiel, nicht die gemessene reale IC-Spannung.** Das Diagramm/der Schutz darf nicht implizit auf den 200-V-Lastdump-Freigaben anderer Designs beruhen.

## 2. Konkrete Schutzmaßnahme D306

**D306: Comchip `ACZRC5370B-G`, 56V ±5%, AEC-Q101, 5W* (herstellerabhängige Kühlbedingung), max Zzt 35ohm beim Datenblatt-Izt, max IR 0,5uA @42,6V im spezifizierten Prüfpunkt, Gehäuse SMC/DO-214AB.** Aktuell DigiKey DE Bestandsaufnahme 613 Stück; einzeln 1,23€, bei zehn 0,776€, bei 100 0,5138€ **jeweils vor MwSt./Versand**, Preise Momentaufnahme, keine garantierte Folgelieferung: https://www.digikey.de/en/products/detail/comchip-technology/ACZRC5370B-G/5020125 .

Alternativ zuvor geprüft: onsemi `SZ1SMB5943BT3G` (56V, automotive, SMB, 3W an definierter Lead-Bedingung; bei Mouser EU ~0,937€/1, 0,43€/10, 0,323€/100). Bevorzugt wird **Comchip 5W im größeren SMC statt einer zweiten 3W-SMB**, um eine vom D301-Hersteller unterschiedliche, größere Schutzkomponente unterzubringen. Höhere Katalogwattzahl allein ist **keine** 125°C/350ms-Freigabe. Beschaffung und AEC-Q101 sind belegbar; thermische Applikationsgrenzen bleiben offen.

**Exakter KiCad-Prototyp:** `hardware/modules/TripPower_5V2A/01_Protection_LM74930_D301_BACKUP_PROTOTYPE.kicad_sch`. D306 hat MPN + Datenblatt-Eigenschaft, `Diode_SMD:D_SMC` als Standard-KiCad-Footprint und echte anliegende globale VS/GND-Netze. Bei der ersten Version wurden vom *nativen ERC* drei Off-Grid-Endpunkte entdeckt. Sie wurden auf das bestehende 1,27-mm-Raster korrigiert. **Erfolgreicher nativer Prüf-Run:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38728505510 . Weitere grüne Regressionen/CI-Logs: https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38728846904 . Die CI führt `cp -a` des Moduls in ein temporäres Build-Verzeichnis durch, ersetzt **dort** das Schutzblatt durch die isolierte Alternative, exportiert native KiCad-10-ERC/Netzliste und prüft den Netzdifferenzensatz `{(VS_CLAMP,D306,1),(GND,D306,2)}`. Keine Änderung an aktiven REV5-Dateien.

### BOM-/Kostenbilanz

| Merkmal | Aktiver REV5 | Alternativ-Prototyp |
| --- | ---: | ---: |
| Bestückt AUTO | 57 | **58** |
| Bestückt RUN | 58 | **59** |
| R313–R315 und D301 | unverändert | unverändert |
| D306 | fehlt | 1x Comchip ACZRC5370B-G (+1 Bauteil, SMC) |
| Preisänderung inkl. Bauteil ohne weitere Kosten | 0€ | ca **+1,23€ / +0,776€ / +0,5138€** bei Menge 1/10/100 |
| PCB-Fläche, zusätzliche Lötstellen, D306-Temperatur | Baseline | mehr, noch nicht geroutet |
| Restfunktion bei D301-OFF | kein externer Backup-Zener | **zweiter externer Pfad vorhanden**, dessen Energieaufnahme noch zu qualifizieren ist |

Maschinenlesbares Delta: `WEG_A_D306_PROTOTYPE_BOM_DELTA_2026-10-15.csv`. Die bisherige 57/58-REV5-BOM bleibt eingefroren. Nicht als automatisch freigebene Bestückung behandeln.

## 3. Temperatur-/200V-Stress und **wesentliche Vorbehalte**

Rechenmodell `tools/trippower_a_d301_backup_analysis.py`, regressionsgesichert `tools/test_trippower_a_d301_backup.py`. Annahmen: Ideal 200V/350ms Rechteck, feste angenommene Zenerspannung, R_min inkl 1%-Toleranz und -100ppm/K von 25→125°C = 3×3300×0,9801 = **9702,99ohm**. **Beide Dioden NICHT als gleichmäßig stromteilend annehmen:** Im Einzelfehler muss D306 den vollen Shuntstrom tragen.

| Angenommene Zenerklemmspannung | Strom durch RVS | P D306 alleine | E D306 in 350ms |
| --- | ---: | ---: | ---: |
| 53,2V | ~15,13mA | ~0,805W | ~0,282J |
| 56V | ~14,84mA | ~0,831W | ~0,291J |
| 58,8V | ~14,55mA | ~0,856W | ~0,300J |
| 65V (obere *Betriebs*grenze, nicht als erlaubte Klemme definieren) | ~13,91mA | **~0,904W** | **~0,317J** |

**Hersteller-Hot-Derating-Achtung:** onsemi 1SMB59xx-Zener: 3W bei TL75°C, Abwertung 40mW/K → bei einer auf exakt 125°C gehaltenen Anschlussleitung nur 1W; auf dem im Datenblatt spezifizierten FR4-Referenzboard gilt 0,55W bei TA25°C mit 4,4mW/K Abwertung → bei TA125°C nur **0,11W Dauerleistung**. Für 0,904W am Hot-125C-Punkt müsste bei diesem Bauteil TL unter ~127,4°C bleiben, also praktisch aktive thermische Kupferanbindung ohne nennenswerte weitere Lead-Erwärmung; das ist **kein vorhandener Layoutnachweis**. Quellen onsemi https://www.onsemi.com/pdf/datasheet/1smb5913bt3-d.pdf Seiten 1/3. Für den **neuen Comchip 5W** benötigt das tatsächliche PCB ebenfalls herstellergültige Derating- und transiente 350-ms-Zth bzw. Lead-Temperatur; aus „5W“ folgt kein Hot125-Nullrisiko. Quelle Produkt-Datenblatt Comchip `ACZRC53xxB-G Series RevD`, https://www.comchiptech.com/admin/files/product/ACZRC53xxB-G%20Series%20RevD.pdf (Dokument-Link serverseitig zeitweise umgeleitet).

**Weitere Grenzen:** Angegebene ±5% Zenerspannung gelten an bestimmtem Prüfstrom/Temperatur, nicht als absolute VS-Obergrenze bei 15mA und +125°C. Das Herstellerzertifikat AEC-Q101 allein garantiert weder 65V am IC noch pulse-/hot-SOA; die angegebene Zzt ist ein Wechselstromkennwert am Prüfpunkt, keine 350-ms-Grenze für alle Temperaturen. Weitere Kondensator- und IC-Inrush-Störungen lassen VS kurzzeitig über Zener-Typwert steigen. Offener D306 zusätzlich zu offenem D301 ist Doppelfehler, kein ersatzloser Ausfall der weiteren Schutzgates.

### Explizite Einzelfehlerzustände

- **D301 OFFEN:** D306 weiterhin VS→GND vorhanden → gewünschte *topologische* Redundanz. Temperatur + Spannung unter realem Strom noch nicht garantiert.
- **D306 OFFEN:** D301 bleibt vorhanden → alter Hardwarepfad; alte thermische Ungewissheit bleibt.
- **D306 oder D301 KURZ:** VS kann auf 0 fallen; R313–315 tragen den vorher bereits errechneten Kurzschluss-Puls (~0,476J je R bei −1%) und F_MAIN löst bei kleinen Strömen nicht zwingend aus. FAIL-OFF und Widerstands-SOA brauchen echten Nachweis.
- **D301 UND D306 offen, gemeinsamer RVS-Ausfall, 200V FET-stuck-ON:** offen/gefährlich, inklusive 60V Q302 und Buck. Keine Lösung durch eine einzige zusätzliche Zener.
- **Thermische Gemeinsamkeit:** Beide Zener mögen bei +125°C/350ms gemeinsam ausfallen. Auf einem zukünftigen PCB unterschiedliche Kupferwärmewege vorsehen; keine angenommene Wahrscheinlichkeit ohne FMEA/Werte.

## 4. Q301/TVS: bewertete echte Alternativen, **kein ungeprüfter Swap**

**Vishay Q301 aktiv `SQM10250E_GE3`:** 250V AEC-Q101, ~30mohm maximal bei 25°C/10V, Hersteller-SOA bei 25°C auf gedruckter Kurve, keine bereits belegte *hot* 200V/350ms-Unterbrechungs-SOA. Quelle: https://www.vishay.com/docs/75035/sqm10250e.pdf .

**Konkrete 300-V-Alternative `SQM35N30-97_GE3`:** AEC-Q101, TO-263-3, 97mohm max @10V/25°C, Qgmax 130nC vs bisher Q301 ~75nC, Ciss max 5650pF (statt Q301 ~4050pF); bei DigiKey DE Snapshot ~1150 Stk., 4,48€/1, 2,963€/10, 2,1059€/100. Quelle Hersteller https://www.vishay.com/docs/66742/sqm35n30-97.pdf und https://www.digikey.de/en/products/detail/vishay-siliconix/SQM35N30-97-GE3/7566806 . Nominell 300−200=100V statt 50V Spannungsbudget. Aber bei 9V und angenommenem 80%-Buck +1A-RAW wird I≈2,389A; bereits **bei 25°C etwa 0,382W zusätzlicher FET-Leitverlust** durch (0,097−0,030)ohm×I², höhere Gatekapazität und langsamere Reaktionscharakteristik möglich. Die Datenblatt-SOA-Grafik zeigt schnelle Pulse, keine **125°C-/350ms-Grenzgarantie**. **Kein Drop-in/Q301-Änderungscommit**: thermisch und schutzdynamisch nicht eindeutig besser.

**TVS D303 SMBJ150A + D304 SMBJ33CA:** positive Serien-Avalanche-Bruchgrenzen bei den jeweiligen Datenblatt-Prüfbedingungen mindestens 167+36,7 = **203,7V**; bei 200V damit **keine garantierte Plateau-Stromklemme**. TVS-Auswahl mit niedrigerem Breakover und höherem 200V-Strom würde andererseits bei 350ms andere Größenordnungen an Energie übernehmen und müsste zwingend mit Generatorquellenwiderstand und Hot-TVSSOA bewertet werden. Eine bloße neue SMCJ/SMBJ-Nennspannung oder Summation der getrennten VC@verschiedenen IPP ist kein konstruktiver Nachweis. **D303/D304 unverändert**; zuerst 200V Quelle R/L, Layoutinduktivität und gemeinsame TVS-Stromkennlinie festlegen.

## 5. 9V-Start: erweiterte, tatsächlich TI-belegte Zeit-/Stromparameter

`tools/trippower_a_start_manufacturer_bounds.py` führt echte, **spezifizierte** Teilewerte von hypothetischen Lastparametern getrennt:
- **TI TPS38-Q1 CTR intern 877/1000/1147kΩ** min/typ/max (TI SNVSBI8E §7.5) und Reset-Kapazität C311 **nominal 330nF**. TI-Gleichungen §8.3.4.1: `tCTR_typ=-ln(0.28)×RCTR_typ×Ceff +t_no_cap`, `min=-ln(0.31)×RCTR_min×Ceff_min +t_no_cap_min`, `max=-ln(0.25)×RCTR_max×Ceff_max+t_no_cap_max`. Der **typische kapazitive Beitrag** bei 330nF ist **~420ms** (nicht die ältere beliebige 250ms-Modellannahme). `t_no_cap` und die vom realen DC-Bias/T/Alterung abhängigen Cmin/Cmax dürfen nicht ohne Testbedingungen pauschal ergänzt werden. Das Hauptmodell `tools/trippower_a_model.py` nutzt jetzt ~420ms als nominale Sensitivität, nicht als Garantie.
- **TI LM74930-Q1**: 5µA max im Shut-Down/780µA max im aktiven Zustand **bei VS12V/EN 0 bzw. 2V**, kein zugesicherter Grenzwert für `I_VS(t)` während 9V-Kaltstart/Chargepump. CAP-Ausgangsstrom darf nicht als VS-Versorgungsstrom behandelt werden. `I_VS_PUMP_MAX_9V` bleibt **null / unbekannt**. Datenblatt TI https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf §6.5.
- **TI TPS38-Q1**: max 2,6µA IDD in spezifiziertem VDD-Bereich, Sense max 100nA für 0.8V-Gerät, aber der konkrete CTRL_EN-Feedback-Teiler und RUN-Leckage sind Zusatzlast. Auch TPS38 hat ohne effektive C311-Werte keine garantierte Verzögerungszeit und ohne Herstellerangaben keinen Restladungsneustart über jede Unterbrechung.
- **D306**: Händlerdaten 0,5µA Leckage bei **VR42,6V**; kein veröffentlichtes Max bei **VS~9V und +125°C**. Nur als offenes Messgate oder frei angenommene Sensitivität verwenden, nicht als 9-V-Max.
- **VS-Reservoir:** 21uF nominal, Ceff_min bei Temperatur/Bias/Alterung **nicht verfügbar**. In `tools/trippower_a_model.py` bleiben die frei gewählten Zusatzpumpenströme und FET-Hochlaufzeiten ausdrücklich hypothetisch.

Bei **9V direkt am Modul** und konservativer VS-READY-ON-Sensitivität von 7,51V ergibt sich ein idealer stationärer RVS-Gesamtvorstart-Stromhaushalt von **150,5µA** bei 9,9kΩ; mit R +1% und +100ppm/K über100K ca **147,54µA**. Dies ist **kein garantiert verfügbares** Reservebudget: unbekannter Vorstartversorgungsstrom, D306-Heißleckage, CTRL_EN-Feedback und Ceff/Timer/Teilentladung müssen empirisch bzw. über konkrete Hersteller-Bounds ergänzt werden. Bei 9V/VS~8V nur ca101µA Speisung. Die nicht spezifizierte Pumpenstromspitze kann nach Enable VS absenken. 9V-Start weiterhin P01/P02/P06/P10 **BLOCKED**.

## 6. Reproduzierbarkeit, Stop-Gates und konkrete nächste Aktion

**Regression / native CI:**

```bash
python3 tools/trippower_a_d301_backup_analysis.py
python3 tools/trippower_a_start_manufacturer_bounds.py
python3 -m unittest discover -s tools -p 'test_trippower_a_*.py' -v
# KiCad10 via .github/workflows/trippower-a-verification.yml
```

**Offen vor Designentscheidung und Hardwareorder**:
1. D306 Comchip 56V Zener **wirkliche Vz_max(I=0..20mA,T=-40..125°C)** und pulsstationäre Zth/Pmax für **350ms Rechteck aus 125°C**; bei Bedarf robustere Zener-/eigene redundante HV-Supply-Lösung. Die Dimensionierung muss VS auch bei T und Bias unter **65V** halten; bloße 100V MLCC abs schützen den 65V-TPS38 nicht.
2. Separater D301-/D306-Wärmeweg im tatsächlichen PCB mit Hersteller-Pad, Lead-T, Kupfer/I²t und wiederholten Pulsen nachweisen. **Keine** PCB-Dimension/Hot-Test behaupten; kein PCB existiert.
3. Sicheren Q301-200V-turnoff und D303/D304/Quelle-Nennimpedanz-SOA inklusive 125°C, Leitung-L, VDS/VGS-Flanken beweisen. Wenn Q301-alternative nötig: erst SOA für ca 2,4A Abfallstrom und Layoutthermik, nicht nur VDSmax.
4. Im 9V-Bench-Test VIN_FUSED, VS_CLAMP, CAP_PUMP−VS_CLAMP, CTRL_EN, TPS38 CTR1, SOURCE_A, Q301 VDS/VGS sowie 5V/2A + RAW1A und RUN-High/VIN0 messen. Vergleichsversuch D306 unbestückt/bestückt und simuliertem D301-OFF **nur auf geschütztem Niedervolt-Prüfstand**; 200V-Impulse ausschließlich an qualifizierter sicherer HV-Ausrüstung.
5. Externe austauschbare F_MAIN, Q301-stuck-ON, Ausgangskurzschluss, negative Pulse, D306 Kurzschluss und 2× Zener offen in FMEA prüfen. Anschlusslayout/Stecker/Temperatur erst dann formell freigeben.

**Abschlussentscheidung:** Die neue D306-Topologie ist ein echter, messbarer **Einzelfehler-Risikoreduktionskandidat mit nativer KiCad-10-Validierung**. Ein garantierter 65V-VS-Hot-Clamp ist noch **nicht** bewiesen, genauso wenig 200V/350ms Gesamtbetrieb, 9V-Start, Q301-SOA oder PCB-Fertigung. Daher bleibt das Hauptblatt unverändert; Branch-Weg A enthält nur reversible Prototyp- und Prüfartefakte. Weg B wurde nicht verändert.
