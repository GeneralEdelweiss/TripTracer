# TripPower REV2: Worst-Case-Nachweis −40…+125°C und 9-V-Start (15.10.2026)

**VERDIKT: formaler Funktionsnachweis derzeit NICHT ERBRACHT.** Die echte KiCad-10-REV2-Topologie ist durch ERC und Netzliste geprüft, aber Transistor-Datenblätter garantieren die für das konkrete Design erforderliche Kleinstrom-Verstärkung und den Sperrstrom bei +125°C nicht; außerdem ist der dynamische VS-Input-Strom beim erstmaligen LM74930-Ladungspumpenstart bei 9 V nicht maximal spezifiziert. Eine Rechnung mit typischen Daten ist **keine Garantie**. Schaltung **nicht für PCB/Fahrzeug/Fertigung freigegeben**.

## Verifizierte Datenblatt-Grenzwerte (NICHT extrapolieren)

- [Nexperia PMBTA92-Q, Datenblatt 30.03.2022, Table 7](https://assets.nexperia.com/documents/data-sheet/PMBTA92-Q.pdf): PMBTA92-Q (Q303) PNP 300 V, AEC-Q101, **hFE_min 25 erst bei I_C=1 mA, VCE=10V, T=25°C, kurzer Puls**; `I_CBO≤250nA` bei VCB=200V mit **offenem Emitter** und **T=25°C**. Diese ICBO-Angabe darf NICHT als garantierte `I_CEO` für Q303 bei angeschlossenem Emitter/Gate-Bias oder bei125°C verwendet werden.
- [Nexperia PMBTA42-Q, Datenblatt 03.07.2023, Table 7](https://assets.nexperia.com/documents/data-sheet/PMBTA42-Q.pdf): Q304/Q305 NPN AEC-Q101, hFE_min25 bei IC=1mA/VCE10V/T25°C, **keine garantierte hFE_min bei IC≈20µA, I_B≈3µA und −40/+125°C**.
- [TI LM74930-Q1, Datenblatt, elektrische Daten](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): EN LOW sicher bei **VEN≤0.41V** (min Schaltschwelle), HIGH sicher bei **VEN≥1.05V** (max Schaltschwelle), angenommene max. EN-Leckaufnahme 0.2µA. Strom am CAP-Ladestromausgang 1.3mA(min unter spezifizierten Bedingungen) ist **nicht** der maximal aufgenommene Controller-VS-Eingangsstrom während Bootstrap.
- [TI TPS3760-Q1, Rev.B (03/2026), Tabelle 6.5](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf): Referenz 0.792–0.808V, SENSE max100nA, RESET OD max300nA im gültigen Betrieb, RESET bei Versorgung unter POR nicht garantiert; U302 muss vollständig strombegrenzt aus VS versorgt werden.
- [Diodes BAS116Q-7-F](https://www.diodes.com/datasheet/download/BAS116.pdf): D305 korrekte SOT-23 **Anode1/Kathode3/Pin2NC**, Teil der RUN-Collector-Entkopplung; Voll-Temperatur-Sperrstrom und USB-Backfeed gehören ebenfalls in Systemmessungen.

## A. Garantiertes AUS: Q303 bei +125°C

Q303 PMBTA92-Q liefert `CTRL_EN` von `VS_CLAMP` über seinen Kollektor und R318=68k. Nachgeschaltet: R316=22k gegen Masse. Bei ausgeschaltetem Q303 verursacht jeder Kollektor-Sperrstrom einen Spannungsabfall an R316. Bei +1%-Pulldown-Widerstand und maximal angenommener EN-Pinleckaufnahme 0.2µA ergibt sich:

`I_CE_OFF,MAX ≤ 0.41V/(22kΩ×1.01) − 0.2µA ≈ 18.25µA`.

**Für eine belegte Freigabe brauchen wir einen garantierten Q303-Kollektor-Sperrstrom unter 18.25µA bei +125°C im konkreten VCE-/VB-/VE-Betriebspunkt.** Der PMBTA92-Q garantiert hier nur einen anderen Messpunkt bei25°C. **Nicht nachweisbar.** Die alte 250nA-ICBO-Grenze hier einzusetzen wäre fachlich falsch.

## B. Garantiertes EIN: Transistoren bei -40°C und VS≈8V

Bei `VEN=1.05V` braucht R31622k mindestens `I_C,Q303≈1.05V/22kΩ=47.73µA` Kollektorstrom (ohne zusätzliche parasitäre Stromaufnahme).

Nominale Vorbemessung bei VS8V, angenommenen Basis-Emitter-Spannungen0.7V:
- Q303 Basiszufluss: `(8−0.7)/220k −0.7/47k ≈18.29µA`.
- Q303 benötigte effektive Minimalverstärkung: `47.73/18.29≈2.61`.
- Q304 Basisstrom: `(8−0.7)/(R3331M+R3391M)−0.7/R3401M≈2.95µA`.
- Q304 benötigte effektive Minimalverstärkung: `18.29/2.95≈6.20`.

Diese niedrigen nominellen Anforderungen **machen den Entwurf plausibel**, aber die Hersteller geben hFE_min erst ab IC1mA/25°C an. **Kein garantiertes hFE_min bei 20–50µA, −40…125°C**. Zudem sind VBE0.7V und die zugehörigen Basisströme **nicht garantiert**; D305-VF, Emitterstrom Q304, Q305-Sättigung, reale R-Toleranzen und Temperaturlage verändern die Ströme. **Nicht nachweisbar.**

## C. 8-V-/6-V-Hysterese mit angeschlossener NPN-Basis

`R330=825k,R331=100k,R332=1M,R333=1M,R339=1M`. Der Reset-Pullup treibt real auch die Q304-Basis über R339. Aus dem repo-verifizierten Rechenmodell ergeben sich:

| Größe | Nominal | Modellbereich (NICHT garantierter Worst Case) |
|---|---:|---:|
| VS_READY EIN | **8.221 V** | **7.669–8.539 V** |
| VS_READY AUS | **5.998 V** | **5.646–6.336 V** |

Modellannahmen: 1% Widerstände, TI VREF- und Hysteresetoleranz, Sensestrom und Resetleck, angenommener Q304-VBE-Bereich0.55–0.95V. **Q304-VBE-Bereich und hFE über Temperatur sind Szenariowerte, keine garantierten Herstellerwerte.** Der frühere Eintrag **7.974V EIN** in `RESET_EN_DRIVE_REV2_2026-10-15.md` ist ein überholter Rechenstand und darf nicht mehr benutzt werden.

## D. 9V zuerst einschalten: VS-Strombudget

Am Eingang `VIN_FUSED=9.0V`, `R313–R315≈9.9kΩ`. Bei der pessimistischen, aber immer noch **nur modellierten** Einschaltschwelle `VS=8.539V` ist der gesamte mögliche Zufluss:

`I_RVS=(9.000−8.539)/9900=46.57µA`.

Das bisherige illustrative OFF-Budget `5µA LM74930 +2.6µA TPS3760 +10µA C308 +9µA SENSE +8µA weitere Reset/Bias =34.6µA` verbraucht davon bereits 34.6µA. Es verbleiben nur **11.97µA** für ungebundene heiße Leckströme, Toleranzen, Temperatur, Spannungsabfall und Modellfehler. Unter dieser Reserve ist ein **garantierter START bei 9V nicht belegbar**.

Selbst wenn RESET freigibt, muss C303 über die LM74930-Ladungspumpe geladen werden: für ein **rein hypothetisches** Ceff(C302+C308)=8.5µF und eine 3ms lange zusätzliche VS-Stromaufnahme von 5mA ergäbe sich allein `ΔVS=1.765V`, bei8mA `ΔVS=2.824V`; zulässiger VS-Abfall vor Erreichen der Gate-Spannung ist knapp und reale VS-Pumpeneingangsaufnahme sowie Ceff(temp)/ESR nicht garantiert. **CAP-Strom ist nicht VS-Strom; die Szenarien beweisen weder Erfolg noch zwangsläufiges Scheitern.**

## E. Temperaturmatrix / 202V- und Thermalgate

| Testfall | Garantierter Wert vorhanden? | Bewertung |
|---|---|---|
| −40°C hFE_min Q303/Q304 beim tatsächlichen µA-I_C | **NEIN** | EIN BLOCKED |
| +25°C hFE_min beim tatsächlichen µA-I_C | **NEIN** | EIN BLOCKED |
| +85°C hFE_min und I_CE_OFF | **NEIN** | EIN/AUS BLOCKED |
| +125°C max Q303 I_CE_OFF mit Basiswiderstand | **NEIN** | AUS BLOCKED |
| 9–30V unter vollständiger Buck-/RAW-Last inkl CAP-Anlauf | **NEIN**, I_VS dynamisch nicht garantiert | Start BLOCKED |
| Lastabwurf 202V/350ms; VS-Schutzzener ≤65V, Q301 hot SOA, F_MAIN | **NEIN** | Schutz BLOCKED |

Rein ohmsches thermisches Teilbudget bei VS65V: Q303 als aus VS über R31868k gespeister PNP bei sonst idealem System `P_Q303 ≤ VS²/(4R318)≈15.54mW`, R318 `P_R318 ≤ VS²/R318≈62.13mW`. Das sind Näherungsobergrenzen unter **vereinfachter Topologie**, kein Bauteilfreigabebeleg. R318 konkrete 1206-MPN/Puls-/Derating nötig.

## Entscheid

**Keine garantierte 9-V-Startspannung und keine über alle Temperaturen garantierte EN-Abschaltung.** Hier liegt ein echtes **Evidenzproblem**, nicht ein offener KiCad-Fehler. Die aktuelle REV2-Topologie ist schaltungstechnisch konsistent, darf aber noch nicht als „Problem behoben und Fahrzeug-sicher“ bezeichnet werden.

**Zur echten Freigabe nötig:** Herstellerunterlagen/Garantie von niedrigststromfestem hFE_min und +125°C I_CEO/ICEV für gewählte Transistoren, oder ein **integrierter automotive-gerechter Enable-Logik-/Levelshift-Baustein**, der HIGH/LOW und Leck bei −40…125°C explizit garantiert. Danach müssen VS-Pumpeneingangsstrom/Ceff in 9V worst-case mit Modellen und Labormessungen getestet werden. Messtabelle pro −40/25/85/125°C × 9/10/12/13.8/24/30V, AUTO/RUN, RUN HIGH+VIN0, schnelle Wiederanläufe; erfassen VIN_FUSED, VS, CAP-VS, RESET, CTRL_EN, SOURCE_A, VIN_PROTECTED_UNFUSED, 5V_OUT und Versorgungsstrom. Lastfälle 5V0/2A + raw0/1A, Spannungseinbruch; 202V-Puls nur mit qualifiziertem sicherem Laboraufbau getrennt.

**Automatisierte Kontrolle:** `tools/check_trippower_rev2_release_gate.py` gibt bei rechnerischer Konsistenz `"result":"BLOCKED_INSUFFICIENT_MANUFACTURER_GUARANTEES"` aus. Ein grüner CI-Test bedeutet nur, dass niemand aus unpassenden 25°C-Transistorangaben eine nicht vorhandene 125°C-Garantie errechnet hat.
