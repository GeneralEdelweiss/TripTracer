# TripTracer V1 – 01F RC-Selbstabschaltung ohne Timer-IC (Vorversuch)

14.10.2026. Im KiCad-10-Hierarchieprojekt liegt eine **tatsächlich verdrahtete, aber isolierte** Alternative zur ACC-Nachlaufzeit aus 01C/01E: `hardware/kicad/01F_RC_SHUTDOWN.kicad_sch`. Sie ist **nicht** an den LM74930_ENABLE angeschlossen und keine fertige Fahrzeugschaltung. Verbindliche Versorgung LM74930-Q1 + LMR36520 bleibt bestehen.

## Ausgangsidee: nur ACC darf nachladen

Die vorher diskutierte Timer/FF-Kombination ist nicht die einzige Lösung. Für einen **maximalen** zeitlich begrenzten ACC-Nachlauf genügt unter klaren Voraussetzungen ein aufgeladenes, **nicht rückladbares** RC-Glied. Ein GPIO darf den Kondensator nur vorzeitig **entladen**, nie nachladen. Damit kann festhängendes MCU_HOLD keine endlose Laufzeit verursachen. Die vorher untersuchte Digital-Latch-Unterseite 01E bleibt bis zum realen Vergleich als Gegenkandidat separat erhalten.

```text
geschützter ACC -> Fahrzeug-5V ACC_VALID_5V -> R801 (220R)
                                        -> D801 BAS116Q -> HOLD_CAP_5V
                                                             | C801 47uF nominal
                                                             | R802 330k nach GND
                                                             | Q801 drain, source GND
                                             MCU_SHUTDOWN -> R803 (10k) -> Q801 gate
                                                           100k gate pull-down
HOLD_CAP_5V --> [NOCH FEHLT: isolierte Einschaltverknüpfung] --> LM74930 EN
```

**Technische Konsequenz:** Wird MCU_SHUTDOWN HIGH, entlädt Q801 das Zeitglied. Falls der Mikrocontroller anschließend wieder LOW liefert, darf sich HOLD_CAP_5V bei ACC AUS nicht aufladen. Wenn MCU_SHUTDOWN nie HIGH wird (Firmware hängt), entlädt R802 zeitbegrenzt. Anders als der digitale Timer braucht dieses passive Modell kein neu startbares Zeitfenster – aber **nur, wenn wirklich keine andere Quelle bei ACC AUS in HOLD_CAP_5V einspeisen kann**.

## Bauteile und CAD

| Referenz | Auswahl für den elektrischen Versuch | Validierungsstatus |
| --- | --- | --- |
| D801 | **Diodes Inc. BAS116Q-7-F**, AEC-Q101, SOT23, Anode pins **1+2** intern gebrückt; Kathode pin **3** | Herstellerpinout geprüft, projektlokales KiCad-Symbol ergänzt, globales `Package_TO_SOT_SMD:SOT-23` vorläufig |
| R801 | 220 Ω, 1206 | Ladestromstoß aus 5 V, V_f, Quellenstrom und thermische Belastung prüfen |
| C801 | **47 µF nominal / 10 V**, 1210-Platzhalter | Hersteller-MPN fehlt; die tatsächliche C_eff bei 4–5 V/Temperatur/Alterung kann deutlich kleiner sein |
| R802 | 330 kΩ, 1206 | 1%-Wert/Derating und Ruhestrom-Fehlerbild prüfen |
| Q801 | Diodes DMN2056U-7, N-MOS, vorhandener projektlokaler SOT23-GDS-Footprint | Off-Leckstrom und Gate bei 3,3-V-GPIO, reale Pinout-Bestückung prüfen |
| R803/R804 | 10 kΩ MCU-Gate-Serie, 100 kΩ Gate-Pulldown, 1206 | GPIO hochohmig/USB-only/Brownout prüfen |

Die [BAS116-Datenblattrevision 13](https://www.diodes.com/datasheet/download/BAS116.pdf), Seite 2, spezifiziert einen **maximalen Rückstrom von 80 nA bei 75 V und 150 °C** sowie 5 nA bei 75 V/25 °C. Dieser *Sperrstrom* entlädt bei Diodenkathode am Kondensator und Anode an einem niederohmig LOW gehaltenen ACC-Signal das Zeitglied zusätzlich; **er liefert nicht von selbst eine Batteriequelle zum Nachladen.** Unbedingt korrekte Anodenführung, Quellen-Pulldown und jedes verbleibende BAT/USB-Rückspeiserisiko prüfen. Die Anodenpins 1/2 müssen elektrisch zusammengehören, nicht wie ein BAS116 anderer Hersteller mit NC-Pin behandeln.

## Abschaltzeit – rein analytisch, nicht getestet

TI spezifiziert für [LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf) die EN-Fallschwelle mit **0,41 V min / 0,7 V max** und den EN-Strom mit **200 nA max**. Für eine erste Rechnung mit 4,5 V Kondensatorspannung, 0,41 V Schwelle und R=330 kΩ gilt ohne Einspeisung `t = R*C_eff*ln(4.5/0.41)`.

| Tatsächliche C_eff | Ohne Stromeinspeisung | Mit +200 nA Einspeisung |
| --- | ---: | ---: |
| 10 µF | 7,91 s | 8,44 s |
| 15 µF | 11,86 s | 12,65 s |
| 22 µF | 17,39 s | 18,56 s |
| 30 µF | 23,72 s | 25,31 s |
| 47 µF | 37,16 s | 39,65 s |

Sobald **positiver** Leckstrom in den Kondensator mindestens `0.41 V / 330 kΩ = 1,24 µA` beträgt, fällt die Spannung in diesem vereinfachten Modell nie unter die konservative EN-Fallschwelle. **Das ist ein wichtiges Freigabe-Gate, kein bestandener Nachweis!** Der genaue Wert bei R-Toleranz, C-DC-Bias und tatsächlicher Leckströme ist erst zu bestimmen. Bei ausgeschaltetem Regler darf der RC-Zweig nicht dauerhaft aus BAT gespeist werden; der OFF-Ruhestrom aus R802 ist nur dann vernachlässigbar, wenn der Kondensator sich auf 0 V entladen hat.

Reproduzierbare Rechnung: `python3 tools/analyze_rc_shutdown.py`. Dieses Tool ist eine analytische Sensitivitätsrechnung, keine native SPICE-/Laborprüfung.

## Die entscheidenden offenen Schnittstellen

1. **ACC_VALID_5V ist noch kein realer, vor Transienten geschützter, ausschließlich fahrzeuggespeister Eingang.** Zum Start darf die 5-V-Stufe nicht von sich selbst abhängen: über einen getrennten robusten ACC→LM74930_EN-Bootstrap muss der LM74930 unabhängig von V5_BUCK_RAW anlaufen.
2. Erst wenn V5_BUCK_RAW vorhanden ist, darf ACC_VALID_5V den Ladekondensator schnell aufladen; ACC OFF muss diesen Quellenpfad **niederohmig LOW** halten und BAT-/USB-Kopplung verhindern.
3. Das RC-Zeitglied muss mit einer entkoppelten OR-/Treiberstufe an LM74930_EN angebunden werden. Deren eigene Leckströme, Ausgangs-Gate-Ladung und Rückspeisung können das maximale Haltefenster verlängern oder verhindern. Eine schlichte Drahtverbindung ist keine fertig dimensionierte Lösung.
4. C801-MPN, echte Effektivkapazität, positive Leckstromsumme, Temperatur, Kaltstart bei 6 V, ACC-Ausfall/Prellen und **maximal benötigte SD-Flush-Zeit** messen. 47 µF nominal garantiert keine Mindest-Nachlaufzeit.
5. Die Quelle `MCU_SHUTDOWN_3V3` ist ein **aktiver Ausschaltbefehl** (HIGH = OFF), nicht das zuvor genannte positive MCU_HOLD. Ein hängender GPIO LOW wird durch R802 begrenzt. Bei ACC EIN darf ein früher MCU_SHUTDOWN-Befehl den direkten ACC-Startpfad nicht blockieren.
6. Die konkrete Endstufe, FET-Rückstromrichtung und gesamte Fehler-/Surge-Matrix zuerst nachweisen. **Keine Fertigung, kein Normalfahrzeugbetrieb, keine Änderung an der Freigabe.**

**Kosten:** Ohne zusätzlichen Timer-IC oder FF als Serienpflicht könnten Teile eingespart werden, aber C801, Schutz, Ladesignal-Gate und etwaige Buffer können die Ersparnis beeinflussen. **Keine belastbare BOM oder Einkaufssumme, keine Serienbauteilwahl.**
