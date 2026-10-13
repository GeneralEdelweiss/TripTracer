# ACC/HOLD aus Fahrzeug-5-V statt ständigem BAT-Enable-Pull-up

14.10.2026. **Neuer Schaltungskandidat; 72 vereinfachte DC-Fälle ausgeführt, keine Hardwarefreigabe.** Die zuvor untersuchten ständig aus VS gespeisten Bias-Schaltungen bleiben wegen Sperrstrom-/Ruhestromproblemen verworfen; siehe ACC_HOLD_DC_REVIEW.md. Noch keine neue KiCad-Unterseite oder Migration des aktiven Schutzpfads.

## Schaltung und Schnittstellen

ACC speist LM74930_EN über zwei 100k-Serienwiderstände, eine vorläufige Zenerklemme gegen GND am Eingang einer OR-Diode und diese OR-Diode. EN besitzt 100k Pull-down und 10n gegen GND. Der alternative HOLD-Zweig speist EN über einen P-MOSFET und eine zweite OR-Diode aus **V5_BUCK_RAW vor der USB-Zusammenführung**. Der P-MOS-Gate-Pull-up liegt mit 4,7k an derselben Fahrzeug-5-V-Quelle; ein kleiner N-MOS zieht das Gate bei MCU_HOLD herunter. Sein MCU-Eingang hat 10k Serie und 100k Pull-down.

Gewünschte Logik weiterhin ACC ODER (MCU_HOLD UND Fahrzeug-5-V). Kein stets aus BAT gespeister Enable-Biaszweig. USB-only darf V5_BUCK_RAW nicht speisen; diese Isolation muss die kommende USB-/Power-Path-Schaltung tatsächlich leisten. Die MCU darf HOLD während des Betriebs vor ACC AUS setzen und nach Dateischluss zurücknehmen. Ein dauerhaft festhängendes HOLD wird von dieser Grundschaltung **noch nicht zeitlich begrenzt**; die Hardware-Deadline gemäß PWR-23/34 bleibt offen.

Die OR-Diode zwischen P-MOS-Ausgang und EN ist erforderlich: sonst könnte ACC-Enable über die P-MOS-Body-Diode in die ausgeschaltete Fahrzeug-5-V-Schiene zurückspeisen. Ebenso verhindert die ACC-OR-Diode die Entladung/Rückspeisung nach ACC AUS. Die ACC-Zenerklemme liegt **vor** ihrer OR-Diode und klemmt negative Eingänge in Vorwärtsrichtung; damit sieht die kleine OR-Diode im Normalmodell nicht direkt den negativen Fahrzeugimpuls. Pulse noch nicht geprüft.

## Tatsächliche DC-Ergebnisse

`tools/simulate_acc_hold_vehicle_source.py` nutzt ngspice mit generischen MOS-/Zener-/Diodenmodellen. Acht Eingangskombinationen bei 6/9/30 V für drei Profile; 72 auswertbare Arbeitspunkte ohne Simulatorfehler. MCU-HIGH angenommen 2,4 V vor dem 10k/100k-Gateteiler. Rohdaten in `docs/validation/2026-10-14-acc-hold-vehicle-source/`.

| Profil | Fälle | Modell-Logikkriterien verletzt |
|---|---:|---:|
| Nominal, ohne zusätzliche MOS-Sperrstromquellen | 24 | 0 |
| Diodes-BSS84-Stress: P-MOS 2 µA, N-MOS 5 µA | 24 | 0 |
| onsemi-BSS84-Stress: P-MOS 60 µA, N-MOS 5 µA | 24 | 3 |

Bei ACC EIN, HOLD AUS, Fahrzeug-5-V AUS und 6 V ergibt das Diodes-Stressmodell EN=**1,803 V**, oberhalb des verwendeten TI-EN-HIGH-Kriteriums 1,05 V. Bei ACC/HOLD AUS, aber noch vorhandenen Fahrzeug-5-V ergibt es **0,180 V**, unterhalb des verwendeten EN-LOW-Kriteriums 0,41 V. Beim onsemi-Sperrstrom-Stress steigt EN dagegen auf **4,353 V**: das Abschalten würde im Modell scheitern. Deshalb keine Freigabe für beliebige gleichnamige BSS84-Ersatztypen.

[Diodes BSS84](https://www.diodes.com/datasheet/download/BSS84.pdf) nennt maximal 2 µA Drain-Sperrstrom bei 125 °C/-50 V, Bestelltyp BSS84-7-F. [onsemi BSS84](https://www.onsemi.com/download/data-sheet/pdf/bss84-d.pdf) nennt 60 µA bei derselben Temperatur/-50 V. Diese Maxima dienen als separate konservative Stromquellen im Modell; tatsächliches VDS liegt viel niedriger. Der N-MOS-Stress von 5 µA folgt dem zuvor geprüften onsemi-BSS138-Wert bei 125 °C/50 V. **Kein gemeinsamer garantierter Temperatur-/Bauteileckwert**, insbesondere nicht bei 150 °C und minimalem GPIO-Pegel.

## Dioden und Zener sind noch nicht final ausgewählt

[Nexperia BAV199](https://assets.nexperia.com/documents/data-sheet/BAV199.pdf) ist ein untersuchter, handbestückbarer SOT23-Leckstromkandidat: maximal 80 nA bei 150 °C/75 V; VF maximal 0,9 V bei 1 mA/25 °C. **Die beiden internen Dioden sind in Serie**, keine gemeinsame Kathode: zwei OR-Zweige dürfen daher nicht fälschlich als ein BAV199-Package verschaltet werden. Entweder zwei Gehäuse, ein tatsächlich passendes Dual-OR-Bauteil oder geeignete Einzeldioden wählen. Im Simulator sind nur generische Einzeldioden enthalten, keine BAV199-Modelle.

[Nexperia BZX84J-Serie, Rev. 4](https://assets.nexperia.com/documents/data-sheet/BZX84J_SER.pdf) wurde als Klemmenvergleich geprüft. Die 4,7-V-/5,1-V-Typen besitzen relevante Leckströme und weiche Knie bei kleinen Strömen; 6,2-V-Typen verlagern das Problem, haben aber ebenfalls keine vollständige Heiß-Leckstromgarantie aus der 25-°C-Tabelle. Die im DC-Modell verwendete generische 4,7-V-Zenerdiode ist deshalb **kein ausgewählter Herstellerartikel**. Kaltstart/Leckstrom bei µA, negative Pulse und Kondensator-/Gate-Ratings vor Übernahme prüfen.

Bei 200 V und angenommener 4,7-V-Klemme beträgt der Strom durch die beiden 100k ungefähr 0,977 mA; jeder Widerstand dissipiert etwa 95,4 mW. Das ist nur ein konstantes Rechenszenario, kein bestandener Lastdump-/ISO-Test. Reale 1206-MPNs, 100-V-Spannungsanteil je Widerstand, Toleranzverteilung, Temperatur-Derating und Pulsratings prüfen.

## Kosten, Systemgrenzen und nächste Gates

Zwei kleine MOSFETs statt vier beim invertierten Kill-Kandidaten; kein zusätzlicher Schutzcontroller. Der 4,7k-Gate-Pull-up verbraucht während HOLD aktiv ungefähr 1,06 mA aus Fahrzeug-5-V, bei ausgeschaltetem Fahrzeug-Buck keine entsprechende BAT-Biasleistung. **Gesamter OFF-Strom noch nicht nachgewiesen**: LM74930, VS-Zener/TVS, Messpfade, USB und PCB-Leckströme bleiben im Budget. Preise/Warenkorb und konkrete deutsche Lieferbarkeit **NICHT BELASTBAR**; keine Bestellung oder Serien-BOM festgelegt.

Vor Integration offen: realer Bootstrap und EN-Ansteuerung bei fehlendem VS, vollständige 6-V-Kaltstartrechnung, Transienten beim Einschalten/ACC AUS/Abschalten/USB, Hardware-Deadline gegen festhängendes HOLD, EN-Kapazität und minimale GPIO-HIGH-Spannung, reale Zener-/Diodenkennlinien, kalte MOS-Schwellwerte, Rückspeisung und Fehlerfälle. Der unverändert fehlende gespeiste Hauptstrompfad wird durch diese DC-Untersuchung nicht als umgesetzt erklärt.
