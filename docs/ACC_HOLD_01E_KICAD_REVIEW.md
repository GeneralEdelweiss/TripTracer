# TripTracer V1 – 01E automotive OFF-Latch: KiCad-Prototyp

Stand 14.10.2026; Branch `design/solid-state-power-v1`. **Echte, in die Root-Hierarchie eingehängte KiCad-Unterseite, aber bewusst noch NICHT mit dem LM74930-/Buck-MAIN_ENABLE verschaltet.** Keine Fahrzeug-/Fertigungsfreigabe.

## Verdrahteter Schaltungsblock

`hardware/kicad/01E_OFF_LATCH.kicad_sch` umfasst **9 Symbolinstanzen**: U701, Q701, R701–R704, D701–D702 und C701. In der projektlokalen `TripTracer_V1.kicad_sym` ist der neue U701 vollständig eingetragen.

- **U701:** TI **SN74LVC2G74QDCURQ1**, AEC-Q100, DCU/VSSOP-8, `Package_SO:VSSOP-8_2.3x2mm_P0.5mm`. Pin 1 CLK, 2 D, 3 /Q, 4 GND, 5 Q, 6 /CLR, 7 /PRE, 8 VCC. Pinbelegung direkt aus [TI SCES563C](https://www.ti.com/lit/ds/symlink/sn74lvc2g74-q1.pdf), Seite 1; TSSOP/ähnliche Bauteile **nicht** ohne Padprüfung tauschen. Quelle: [TI DCU-Gehäuseübersicht](https://www.ti.com/packaging/docs/searchtipackages.tsp?packageName=SO). /Q ausdrücklich NC.
- **Q701:** NPN MMBT5551 (bereits vorhandenes projektspezifisches Symbol); steuert /PRE aus `ACC_VALID_5V`. R701 10 kΩ Basisserie, R703 100 kΩ Basispulldown, R702 10 kΩ Kollektor-Pullup gegen `V5_BUCK_RAW`. Bei ACC HIGH /PRE LOW → Q setzt asynchron HIGH; bei ACC LOW /PRE HIGH.
- **D701/D702:** je BAT54WS, anodenseitig an `ACC_VALID_5V` bzw. `HOLD_CONTINUE_5V`, kathodenseitig gemeinsames `HOLD_CLR_N`; R704 47 kΩ nach Masse. Nur falls wenigstens einer der beiden 5-V-Logikzweige gültig HIGH ist, soll /CLR HIGH sein. Die Schottky-Vorwärtsspannung bei kleinem Strom, Reverse Leakage über Temperatur und die resultierenden TI-VIH-/VIL-Ecken sind **noch nicht nachgewiesen**.
- **U701 D (Pin 2) und CLK (Pin 1):** fest GND; Q ist der asynchron gesetzte/gelöschte Zustandsausgang `HOLD_LATCH_Q_5V`. GND und VCC projekttypisch per globalen Labels angeschlossen, C701 100 nF zwischen Fahrzeug-5-V und GND vorgesehen. C701-Spannungsfestigkeit und tatsächlich erreichbarer 5-V-Ripple noch prüfen.

Logische asynchrone Sollfunktion bei stabiler V5_BUCK_RAW-Versorgung:

| ACC_VALID_5V | HOLD_CONTINUE_5V | /PRE | /CLR | Q |
| --- | --- | --- | --- | --- |
| 0 | 0 | 1 | 0 | wird LOW, danach verriegelt |
| 0 | 1 | 1 | 1 | bleibt im letzten Zustand |
| 1 | 0 | 0 | 1 | wird HIGH |
| 1 | 1 | 0 | 1 | wird HIGH |

Der **verbotene** U701-Zustand /PRE=0 UND /CLR=0 kommt in diesem *statischen* idealen Wahrheitstableau nicht vor. **Beim Einschalten oder ACC-Flankenwechsel sind beide Pins jedoch analog, verzögert und unterschiedlich schnell.** Dioden-, BJT- und 5-V-Rampen können den verbotenen Momentanfall erzeugen; die Tabelle beweist also kein fehlerfreies Einschalten.

## Wesentliche Integration-Gates

1. **ACC_VALID_5V existiert noch nicht als fertige, geschützte Fahrzeug-5-V-Logik.** Die tatsächliche Starterbypass-Schaltung muss den Buck ohne V5_BUCK_RAW einschalten, Signalerzeugung darf später nicht aus USB stammen.
2. **HOLD_CONTINUE_5V ist noch nicht implementiert.** Er muss 5-V-CMOS-pegelgerecht aus MCU_HOLD und **nicht retriggerbarem** Zeitfenster kommen. Sicherstellen, dass das Signal beim Ende von ACC rechtzeitig HIGH ist, sonst löscht /CLR die Freigabe sofort (Race Condition). Den Timer keinesfalls einfach nach der ersten abfallenden ACC-Flanke langsam starten und den Übergang ungeprüft erwarten.
3. **Keine Selbstversorgung nach Shutdown:** Ein am Buck-Ausgang hängender Latch kann nach einem Abfall seiner Versorgung nicht zuverlässig seinen Q-Zustand speichern. Das ist beabsichtigt: Q und Treiber müssen ohne Fahrzeug-5-V elektrisch garantiert OFF sein; nur ein **neues qualifiziertes ACC** darf den Analogstart zulassen. Dieses Gate ist noch kein fertiger externer Treiber.
4. U701 Q wird bislang **nicht an MAIN_ENABLE angeschlossen**. Die alte 01A–01D-Relais/eFuse-Teilarchitektur bleibt stehen; aus deren Existenz keine fertige Variante C folgern.
5. Abschalten im transienten Fall mit MCU_HOLD stuck HIGH; ACC-Prellen, schwache 6-V-Buck-Rampe, USB-Only, DIP-/Diodenleckstrom, -40…+125 °C, 9–30 V, Fehlerfälle und galvanische Rückspeisung prüfen.
6. **KiCad 10 native ERC/DRC, Hersteller-Footprint-GUI und exakter Leiterplatten-Netzvergleich sind noch offen**. Eine parserbasierte Struktur-/Pinprüfung ist kein Ersatz.

Die Beschaffung ist noch **nicht abgeschlossen**: keine geprüften Preise/Mengen/Versand und keine neue Bestellfreigabe. Die kleine VSSOP-Hülle lässt sich mit Handlöten und Flussmittel versuchen, aber Eigenbestückung beim Prototyp erfordert Sichtkontrolle und passende Löttechnik. Der Baustein wurde als elektrisch passender Automotive-FF für den ersten Schaltungsschritt gewählt, **nicht** als kostenseitig freigegebene finale Auswahl.
