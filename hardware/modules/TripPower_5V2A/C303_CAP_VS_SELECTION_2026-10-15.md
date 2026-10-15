# TripPower C303 CAP–VS Kondensator: Auswahl / Sicherheitsgate (15.10.2026)

**Echte KiCad-Änderung:** eigenständiges `hardware/modules/TripPower_5V2A/01_Protection_LM74930.kicad_sch`, C303 von unqualifiziertem nominal 100nF/100V auf **KEMET `C1206C474K1RECAUTO7210`** (470nF ±10%, 100V DC, X7R, 1206/3216, -55 bis +125°C, AEC-Q200, max. Bauhöhe 1,80mm, laut Distributor). Standard-KiCad-10-Footprint `Capacitor_SMD:C_1206_3216Metric` statt bisherigem projektlokalem Kondensator-Footprint. Projektspezifische Netze: **U301.CAP pin 23 → C303.1 → C303.2 → VS_CLAMP/U301.VS pin 22**. Direkte Fahrzeug-/202-V-Spannung **liegt nicht über C303**; unter normalen Bedingungen ist die **Differenz CAP–VS** entscheidend.

## Datenblatt-Grundlage (Hersteller)

[TI LM74930-Q1 Datenblatt SNOSDF6, Abschnitt 8.2.2.2, S.25](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): mindestens **0.1µF** CAP-VS; für beide MOSFETs zusammen zusätzlich **C_CAP >= 10 × (Ciss_Q301 + Ciss_Q302)**. Bei Vishay `SQM10250E_GE3` (Ciss max 4050pF) plus Nexperia `BUK7Y4R8-60EX` (Ciss max 5520pF) resultieren `10 × (4050 + 5520)pF = 95.7nF`. Die zwei Ciss-Datenblattbedingungen sind nicht identisch; als nominelles strenges Vorbemessungsmaß zu verwenden, **keine getestete reale Gatelast**.

[TI Abschnitt 7.3.1, S.15](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): CAP–VS-Pumpenspannung **12.2–13.2V typisch**, Maximalwert des turn-off Schwellwerts **14.1V** laut Abschnitt 6.5; CAP–VS abs. max. **15V** laut Abschnitt 6.1. Der 100V/1206 MLCC ist bewusst weit über die anliegende differenzielle DC-Spannung hinaus spezifiziert, um **DC-Bias-Derating** klein zu halten; das ist **kein** Beleg für genügend Kapazität bei jeder Temperatur und jedem Surge.

| C303 CAP | Nennwert | -10% | anschließend noch X7R -15% (ohne DC Bias/Alterung) | Vergleich zum TI-Wert 95.7nF |
|---|---:|---:|---:|---|
| Alt | 100nF | 90nF | 76.50nF | scheitert schon an Toleranz |
| **Neu** | **470nF** | **423nF** | **359.55nF** | **Faktor 3.76 vor DC-Bias/Alterung** |

Der neue Kondensator muss nach nominaler -10%-Toleranz und -15%-Temperaturannahme zusätzlich mindestens `95.7/359.55 = 26.6166%` seiner Kapazität unter DC-Bias behalten, sofern **Alterung, Messgenauigkeit und weitere Sicherheitsreserven noch separat berücksichtigt** sind. Anders formuliert: Diese `26.6%` sind eine rechnerische **untere Schwelle ohne Alterung**, **nicht** die bestätigte KEMET-Kurve. **Verbindlicher Gate:** KEMET K-SIM / Herstellerdaten des exakten MPNs für VCAP–VS **bis 14.1V** über vorgesehenen Temperatur- und Lebensdauerbereich abrufen und als `Ceff_min >95.7nF` nachweisen; zusätzlich angemessene Reserve verlangen.

## Startverzögerung beim Aufladen der Ladungspumpe

TI Gleichung (1), S.15: `TDRV_EN = 175µs + C_CAP × 6.6V / 2.7mA` (typisch). Nur rechnerisch:
- ALT 100nF: **419µs**.
- NEU 470nF: **1324µs**.
- Differenz: **+905µs**. Mit 1.3mA als illustrative Ladestrom-Sensitivität `175µs+470nF×6.6V/1.3mA = 2561µs`. Das ist **keine garantierte schlimmste Startzeit**: Pumpenstrom vs. VIN/Vcap/Temperatur ist dynamisch, zusätzliche Gate-Last und EN/OV/UVLO noch nicht modelliert.
- Beabsichtigtes Betriebsverhalten: kurzes verzögertes Zuschalten bei Einschalten zulässig; **9V Motorstart inklusive VS-Dioden-Hilfszweig** und Wiederzuschalten nach OV/UV auf reale Last prüfen. Größe 470nF bewusst statt 1µF, um Pumpenstartzeiten nicht übermäßig zu verlängern.

## Bauteilwahl / Kostenstichprobe, 15.10.2026

| Funktion | MPN | 100V/1206 | Automotive | Deutschland: Einzel/10/100 Stück **netto pro Stück** | Verfügbarkeit |
|---|---|---|---|---|---|
| **Bevorzugt / in KiCad** | [KEMET C1206C474K1RECAUTO7210 (Mouser DE)](https://www.mouser.de/de/ProductDetail/KEMET/C1206C474K1RECAUTO7210) | ja | AEC-Q200 | **0.318 / 0.210 / 0.131 EUR** | Mouser DE ~7,772 lagernd |
| Gute Alternative | [TDK CGA5L2X7R2A474K160AA (DigiKey DE)](https://www.digikey.de/en/products/detail/tdk/CGA5L2X7R2A474K160AA/2443884) | ja | AEC-Q200 | **0.470 / 0.285 / 0.1917 EUR** | DigiKey DE ~55,501 lagernd |
| KEMET alternative Serie (nicht bevorzugt) | [C1206C474K1RACAUTO (DigiKey DE)](https://www.digikey.de/en/products/detail/kemet/C1206C474K1RACAUTO/3314533) | ja | AEC-Q200 | **1.41 / 0.922 / 0.6668 EUR** | ~3,738 lagernd; teurer |

Preise/Bestände sind **Momentaufnahmen**. Kein MwSt.-/Versand-/Beschaffungs-Mischpreis; MOQ beachten: DigiKey der konkreten KEMET `...RECAUTO7210` zeigte nur Bestellmöglichkeit auf voller Rolle, **Mouser DE** hat dagegen Cut-Tape ab 1 Stück. TDK ist sinnvolle zweite Lieferantenoption und nicht heimlich identisch im DC-Bias; Austausch nur nach gleichem elektrischen Gate. LCSC/JLCPCB-Basic-Status nicht verifiziert.

## Status und Regression

- `C303` Wert, 1206-Standard-Footprint, MPN, Supplier_URL, Alternative_MPN im **echten KiCad-Schaltplan** gesetzt; `lm74930_design_v1.json` synchronisiert.
- `tools/check_trippower_input_stress.py` prüft MPN und rechnerische 470nF-Headroom- und Startzeit-Sensitivität.
- `tools/check_trippower_native_netlist.py` fordert C303.1 am CAP_PUMP und C303.2 am VS_CLAMP. **Native ERC / Netlist an aktueller Commit-SHA müssen per CI ausgewertet werden.**
- Ungeprüft: Hersteller K-SIM-Bias über Temperatur/Alterung, 9V dynamischer Start, CAP/VS 202V Lastabwurftransienten inkl. Fehlerfall, C303 Löt-/Flex-Beschädigung, mechanische 1.8-mm Höhe/Footprint im späteren PCB, 202V Q301 hot SOA und `F_MAIN` Sicherungs-I²t. **Keine PCB/DRC/ISO-/Fahrzeug-/Fertigungsfreigabe.**
