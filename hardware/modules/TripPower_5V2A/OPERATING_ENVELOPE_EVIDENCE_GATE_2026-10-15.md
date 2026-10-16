# TripPower REV2 – Operating envelope: zugesicherte IC-Grenzen vs. Systemnachweis (15.10.2026)

**Keine garantierte Betriebs-Spannungs-/Temperatur-Kombination für das *vollständige* Modul nachgewiesen.** Elektrischer KiCad-10-ERC: 0; native Netzliste zuletzt 105 geprüfte Pins; allein keine Funktions-, PCB- oder Fahrzeugfreigabe. Es existiert noch kein eigenständiges geroutetes TripPower-PCB und kein Laborprotokoll. Bestehende Hardware-Auswahl unverändert: LM74930-Q1, LMR38020-Q1, TPS3760-Q1, REV2-BJT-AUTO/RUN, RVS 9,9 kΩ, D302 A→VS und C308 10 µF.

## 1. Welche Bausteingrenzen sind Herstellerwerte?

- TI [LM74930-Q1 SNOSDF6 S.5–7](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): VS-Betrieb 4–65 V; automotive Umgebung −40…+125°C und empfohlene Tj −40…+150°C; EN sicher HIGH bei ≥1,05 V, sicher LOW bei ≤0,41 V. Der Herstellerbetrieb gilt für **VS am Controller**, nicht unmittelbar für das rohe VIN vor dem RVS-Netz. IQ max 780 µA bei definierten Testbedingungen VS = 12 V, EN = 2 V; **nicht** garantierter Bootstrapping-I(VS,t) oder pauschaler Maximalstrom bei VS=8,539 V.
- TI [TPS3760-Q1 Rev B (März 2026)](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf): VDD 2,7–65 V und Tj −40…+125°C; der aktuelle externe Schmitt-Rückkopplungsteiler und Q304-Basispfad reduzieren **nicht** auf einen vollständig spezifizierten 8/6-V-Schwellwert.
- TI [LMR38020-Q1](https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf): VIN **nach Schutzstufe** 4,2–80 V, bis 2 A, Tj −40…+150°C, reale Last-/PCB-Derating-Anforderungen. Herstellerempfehlung gilt nicht automatisch für komplette kleine TripPower-Platine.
- Aktueller REV2-BJT [Nachweis](RESET_EN_REV2_PROOF_GATE_2026-10-15.md): Bei 20–50-µA-Kollektorströmen fehlen garantierte hFE_min der PMBTA92-Q/PMBTA42-Q über alle Temperaturen; Q303 I_CE_OFF bei +125°C nicht garantiert <18,25 µA. Daher ist **EN-AUS und EN-EIN an keinem definierten Temperaturpunkt voll vom Hersteller nachgewiesen**, auch nicht bei 25°C.

## 2. Rechenwerte am RVS-Vorladeschaltpunkt (keine Funktionszusage)

TripPower nutzt 9.900 Ω zwischen VIN_FUSED und VS_CLAMP vor Gate-Freigabe. Obere **modellierte**, nicht garantierte REV2-READY-Einschaltschwelle: VS = 8,539 V; nominal 8,221 V. Maximaler *statischer* Zufluss bei angenommenem VS = 8,539 V ist (VIN−8,539 V)/9.900 Ω, vor Toleranzen/Ripple und **inklusive aller** VS-Speiselasten:

| VIN_FUSED am Modul | Zufluss bei VS=8,539 V | Kommentar |
|---:|---:|---|
| 9 V | 46,6 µA | Nur etwa 12 µA Modellreserve gegenüber bisherigem illustrativem OFF-Budget 34,6 µA |
| 12 V | 349,6 µA | Knapp; kein garantierter Pumpenstart |
| 13,8 V | 531,4 µA | Knapp; kein garantierter Pumpenstart |
| 18 V | 955,7 µA | Plausibler, aber I(VS,t) und BJT fehlend |
| 24 V | 1.561,7 µA | Mehr statische Reserve, noch **kein** garantierter Start |
| 30 V | 2.167,8 µA | Größte Reserve im nominalen Spannungsbereich, noch **kein** garantierter Start |

**Keine künstliche „garantierte 18-V-Mindestspannung“ ableiten.** Beispiel lediglich zur Größenordnung: 780 µA statische Annahme würde die modellierte 8,539-V-Schwelle erst ab VIN ≈ 16,26 V ermöglichen; aber 780 µA sind kein spezifizierter Starter-/Pumpenstrom bei dieser VS-Spannung. Vor Gate-Anlauf versorgt D302 aus SOURCE_A den VS nicht unabhängig.

### Was an Schwellen rechnerisch stärker belegbar ist

- Mit der aktuellen externen UVLO-Teilung, TI 0,63-V-max rising, 200-nA-Leckstrom und **angenommenen** 1%-R-Werten liegt der rechnerische maximale UVLO-Einschaltpunkt etwa bei 8,35 V VIN_FUSED. Bei konstant 9,0 V **am Eingangspin** würde UVLO allein somit den Start nicht unterdrücken; das sagt nichts über VS aus.
- OVP nominal ca. 35,9 V; analoge 1%-/TI-Leck-/Komparatorszenarien ergeben minimale Abschaltschwelle oberhalb 30 V; folglich verhindert OVP unter diesen Annahmen den **stationären** 30-V-Normalbetrieb nicht. Keine Garantie für 202-V-Schalt-SOA, transiente Pinüberschreitungen oder hochfrequente Störungen.
- Eine externe F_MAIN nahe Quelle ist zwingend und noch nicht konkret I²t/temperaturqualifiziert. Gesamte Roh-Ausgangszweig-Sicherung, 5V/2A-PCB-Thermik und 202V/350ms sind eigene **rote Gates**.

## 3. Aussage nach Bedingungen

| Szenario | Heutiger Evidenzstatus |
|---|---|
| 9V / 25°C / Leerlauf | **KEINE Garantie:** VS/REV2-Pumpe und hFE fehlend |
| 12–13,8V / 25°C / Leerlauf | **KEINE Garantie:** reduzierter VS-Bootstrapstrom und fehlende BJT-Minimalwerte |
| 18–30V / 25°C / Leerlauf | **Plausibler Laborversuch**, aber **KEINE Garantie** |
| 24–30V / −40…+125°C / 5V=2A und RAW=1A | **KEINE Garantie:** Start, REV2, thermische und FET-Stress-Gates |
| 9–30V / −40…+125°C / 5V=2A | Projektziel, **noch nicht qualifiziert** |
| Kurzschluss / 202V Lastabwurf | Elektrische/thermische sichere Reaktion **nicht** nachgewiesen |

**Messplan zur Festlegung eines begrenzten nachgewiesenen Bereichs:** Zunächst VIN_FUSED 24 V, 25°C, 5-V-Last 0/0,5/2 A, RAW 0 A; dann 18 V, 13,8 V, 12 V, 9 V und RUN/AUTO; schließlich bei −40/85/125°C und Roh-Zusatzlast. Jeder Punkt: VIN, VS, CAP−VS, RESET, CTRL_EN, SOURCE_A, V5, Input-/Raw-Strom, Komponenten-T. Quantifizierte Grenzwerte: EN_LOW ≤0,41V, EN_HIGH ≥1,05V, nominelle Versorgung V5 unter Last innerhalb noch festzulegender Gesamt-Toleranz, keine thermische Überschreitung. Falsche Startup-Basis durch Überbrücken des HV-RVS-Netzes bei 202V vermeiden.

**Entscheidung:** Ohne Hersteller-garantierte dynamische VS- und µA-BJT-Eckwerte und ohne qualifizierte PCB-/Hardwaretests gibt es derzeit **keinen nichtleeren *garantierten* vollständigen Betriebsbereich**, auch nicht auf 24-V-Fahrzeuge oder 25°C verengt. Ein Labornachweis für einen bestimmten Prototypen ist danach als *getestet* (nicht automatisch Seriengarantie) zu deklarieren. **Keine stillschweigende Zielabsenkung** des 9–30V-/12/24V-Kompatibilitätsziels.
