# TripPower Weg B – eigener Branch und unabhaengige Sicherheitsanalyse (2026-10-15)

**Arbeitsbranch: `design/trippower-b`.** Ausgangsbasis: `design/solid-state-power-v1` bei Commit `2cafbf43e24aadc12ede10cd413b962c84579664`. Weg A und aktive REV5-Dateien bleiben unveraendert. Alle Weg-B-Aenderungen erfolgen nur in diesem Branch; vor einer spaeteren Uebernahme ist ein separates Review/PR notwendig.

**Status: VORENTWURF / BLOCKED.** Keine bestueckbare End-BOM, kein fertiger KiCad-10-Schaltplan, kein ERC/DRC, keine 9-V-Start- / 30-V-Restart- / 200-V-350-ms- / 125-C-Freigabe. Das Modul darf nicht bestellt oder im Fahrzeug betrieben werden.

## 1. Verbindliche Schnittstelle aus REV5

* VIN_FUSED: 9–30 V Dauerbetrieb; sicherer Reset unter 9 V gestattet.
* Ungedaempfter Lastabwurf: **200 V fuer 350 ms** (NICHT historische 202 V).
* Geregelter Ausgang: 5 V / 2 A; RAW-Zusatzabgriff: 1 A Entwurfsziel.
* Zielumgebung: -40 bis +125 Grad C. AUTO und RUN_CMD, kein Rueckspeisen; OFF-Gesamtstrom unter 100 uA als noch offenes Gate.
* Austauschbare **externe** F_MAIN vor allen Fahrzeugleitungen. LM74930-Q1 mit Ueberstrom/Verpolung und HV-Q301-Schutzpfad bleibt als Ausgangspunkt bestehen. Q301-SOA/R313-R315-Zener/9-V-VS-Start sind ungeprueft.
* Kein Rueckschreiben nach `design/solid-state-power-v1`, Weg-A-Artefakten oder `main`.

## 2. Herstellergepruefte Bausteine

### U_BBUCK: TPSM33620S5QRDNRQ1

TI Datenblatt [TPSM336xx-Q1 SNVSCS7E](https://www.ti.com/lit/gpn/tpsm33620-q1), Stand September 2026:
* Automotive AEC-Q100, 5 V fixed, 2 A, 2,2 MHz, integrierte Leistungs-MOSFETs, Drossel und Bootstrap-Kondensator.
* **Empfohlener VIN-Betrieb 3 bis 36 V; VIN absolut max 40 V.** 40 V ist keine Betriebsfreigabe. Transiente VIN-Pad-Ueberschwinger koennen den IC schaedigen.
* RDN / QFN-FCMOD, **11 Pads**, 4,5 x 3,5 mm. Gegen das TI-Package-Landpattern neu pruefen, **nicht** vorhandenen LMR-Footprint verwenden.
* Hersteller-Pinmap: 1 PGOOD; 2 EN; 3 VIN; 4 VOUT; 5/6 SW (nicht extern anschliessen); 7 BOOT (interner C, nicht extern beschalten); 8 VCC (1-uF-C nach GND); 9 FB (**direkt an VOUT** bei 5-V-fixed); 10 GND; 11 MODE/SYNC (z.B. GND fuer AUTO, nicht floaten).
* TI-Referenz fuer 5-V/2-A fixed: **ein 4,7-uF-Eingangskondensator, ein 100-nF-Eingangskondensator, zwei 22-uF-Ausgangskondensatoren, ein 1-uF-VCC-Kondensator**. Das sind fuenf **diskrete Kondensatorplatzierungen** und ein Modul = **sechs Positionen**, nicht nur vier gezaehlte Bestueckpositionen. Effektive Kapazitaet unter DC-Bias / Temperatur vorgeben, nicht Nominalwerte blind als Mindestkapazitaet akzeptieren.
* PGOOD kann ungenutzt bleiben. EN und MODE/SYNC duerfen nicht offen sein. Hohe TA=125 C bei voller Leistung und 30 V muss anhand TI-Derating, PCB-Thermik und Messung bewiesen werden.

### U_BOV: TPS3760E012DYYRQ1 – vorlaeufige praezise OV-Abschaltung

TI Datenblatt [TPS3760-Q1 SBVS419B](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf), Stand Maerz 2026:
* Exakte von TI gelistete Automotive-MPN **TPS3760E012DYYRQ1** = OV, externe 0,8-V-SENSE, 2 % Hysterese, **Open-Drain LOW bei OV**, kein Latch. Versorgung VDD 2,7–65 V, -40 bis +125 C.
* 0,8-V-SENSE VITP 0,792 / 0,800 / 0,808 V; SENSE-Strom max 100 nA unter TI-Bedingungen. RESET-OD LOW max 0,300 V unter spezifizierten Bedingungen, Leck max 300 nA; bei einer direkten wired-LOW-Verbindung zu LM74930 EN weitere Pull-Up-/Leckage-/RUN-Pegel berechnen.
* CTS unbestueckt: 8 bis 17 us **Erkennungsverzoegerung** bei 20 % SENSE-Overdrive, 1 V/us Ramp, TI-Testlast. **Das ist nicht die Gesamt-Abschaltzeit von Q301 und garantiert keinen VIN-Pad-Grenzwert.** TI nennt zudem bis 2 ms Power-on-Startup-Delay; RESET-State vor POR und bei VIN0 separat pruefen.
* DYY SOT-23-THN **14 Pins**: VDD1, SENSE3, RESET6, GND8/13, CTS10, CTR9; restliche Pins gemaess Hersteller NC. Fuer einen neuen KiCad-10-Footprint muessen Landpattern und alle Pads geprueft werden.
* TI direkt meldete zum Abruf keinen kaufbaren Lagerbestand; Lieferbarkeit bei deutschen Distributoren sowie alternative OPN vor BOM-Freeze pruefen. Kein ungepruefter Bestellstatus.

## 3. Nur statische OVP-Probe – nicht als sicherer Schutz interpretieren

Probe: 2 x 470 kOhm 1 % (Top in Serie) und 23,2 kOhm 1 % (Bottom) zwischen **VIN_FUSED** und GND, SENSE am Mittelpunkt; Ausgang muss am **LM74930-EN-/HV-Serien-FET-Abschaltpfad** wirken, NICHT nur am TPSM-EN.

Einfache Modelle:

`V_TRIP = V_SENSE*(1 + R_TOP/R_BOTTOM) +/- I_SENSE*R_TOP`.

* Steigende Schwelle nominal: **33,214 V**. Konservative Eck-Modellhuelle mit unabh. 1%-Widerstaenden, 0,792–0,808 V SENSE und +/-100nA Bias: **ca. 32,15–34,30 V**.
* Fallende Schwelle nominal bei angenommener 2%-Hysterese: **32,55 V**. Beispielhafte Eck-Modellhuelle mit zusaetzlich angenommener +/-1,5%-relativer Hysterese-Abweichung: **ca. 31,50–33,63 V**. Die genaue Hersteller-Hysterese-Interpretation, Drift und Fehlerkorrelation fuer einen verbindlichen Worst Case erneut verifizieren.
* Bei 30 V belastet der Teiler VIN mit **31,15 uA**; OFF-Gesamtstrombudget muss diese Last einschliessen.
* Bei 200 V ergibt der Teiler ideal ca. **4,82 V an SENSE**, ca. 20,3 mW pro 470-kOhm-Widerstand, ca. 7,1 mJ je Widerstand in 350 ms; reale 1206-Impuls-/Spannungsdaten und Ueberlagerung mit anderen Pulsen pruefen.
* **Das ist nur eine Schwellenrechnung, keine 30-V-Wiedereinschaltgarantie:** Stromversorgung des Supervisors, POR, VS_CLAMP 65-V-Grenze, Open-Drain-UND-Logik, RUN, Restladung, Hochlauf, Hysterese, Temperatur und Abschaltdynamik koennen die Zusage brechen.

## 4. Architektur/Fehlerrisiken mit Prioritaet

1. **200-V/350-ms-Spannung bleibt vor dem FET.** LM74930 + Q301 und VS/R313–315/56-V-Zener bleiben kritische und nicht bestandene 200-V-SOA-/Energie-Gates. Ein nachgeruesteter Monitor ersetzt keine energiefeste Leistungsstufe.
2. **Dynamischer TPSM-VIN-Pad-Schutz OFFEN:** OV-Erkennung + EN-Signal + Ladung/Gate-Q301 + Leiterbahninduktivitaet + Eingangs-MLCC und Kabelringing muessen maximalen VIN an TPSM beweisbar <=36 V unter zulassigen Betriebsbedingungen halten und niemals 40 V abs max ueberschreiten. Ein 33-V-TVS ist ohne Clamp-Kurven/ESL/Temperatur/Peakstrom keine Loesung. Bei fehlendem Schutz darf kein TPSM bestueckt werden.
3. **OV-Logik kann beim Power-on undefiniert sein:** TPS3760E012 moeglicherweise aus VS_CLAMP versorgen, jedoch ist dessen 9-V-Erststart schon im REV5 nicht garantiert; bei unversorgtem Monitor kann ein Open-Drain-Ausgang nicht als sicherer Schutz gelten. Auch RUN_CMD=HIGH bei VIN=0 ist ein Rueckspeisegate.
4. **Wired-LOW zu vorhandener TPS38-Dual-UV-Supervision:** Bei direktem Gating auf LM74930 EN muss feststehen, dass LOW aus irgendeinem Supervisor sicher gegen den gemeinsamen Pull-up gewinnt und in Freigabe HIGH garantiert erreicht wird – besonders bei 125 C / maximalen Leckagen.
5. **Geringere Bauteilzahl nicht ueberbewerten:** REV5 Buck-Stufe hat 12 aktive Positionen. TPSM-Referenz 6 Positionen -> **6 Ersparnis**. Zusaetzlicher TPS3760 + 3 Widerstaende + 100-nF-VDD-Bypass -> **mindestens 5 neue Positionen**, also nur **1 Position netto** weniger, falls keinerlei weitere Schutz-/Pullup-/Dampingteile gebraucht werden. Kosten der QFN-/14-Pin-Bestueckung und Messkosten kommen dazu.
6. **Footprint-/3D-/BOM-/ERC-/DRC-Status:** Fuer Weg B noch keine Geometrien gebaut/qualifiziert, keine native KiCad-Ausfuehrung. Keine Ersetzung des bestehenden aktiven `02_5V_LMR38020.kicad_sch`, keine Aenderung der REV5-Baseline, bevor ein isoliertes Weg-B-Standalone-Projekt elektrisch und geometrisch nachgewiesen ist.

## 5. Naechste konkrete Weg-B-Schritte (nur auf diesem Branch)

1. Neue Weg-B-KiCad-Projektkopie unter `hardware/modules/TripPower_5V2A/weg_b/` mit eigener Root, unabhaengigen Symbols/Footprints/3D und BOM; weder gemeinsame REV5-Schaltplaene noch Basis-BOM ueberschreiben.
2. Hersteller-Landpattern TPSM RDN11 und TPS3760 DYY14 fuer KiCad 10 abbilden und Pin-zu-Pad sowie Hersteller-Referenzschaltung kontrollieren.
3. Aus TPS3760 + LM74930 + TPS38 ein vollstaendiges FAIL-OFF-Interlock inkl. Power-on und 30-V-Restart-Eckzustand dimensionieren; vor dem routen **dynamischen Buck-VIN-Schutz** fuer 200-V-Puls schaffen.
4. Reproduzierbare Regressionen 9/12/24/30 V, RUN/AUTO, OFF-Strom, 200 V / 350 ms, Q301-SOA, Thermik und F_MAIN. Native KiCad-10-ERC/-Netlist/-DRC nur als bestanden markieren, wenn wirklich ausgefuehrt; abschliessend echte Labor-/Transienten-/Heisspruefung.

**Fazit:** TPSM33620 ist ein technisch valider Buck-IC, aber der derzeitige Schutzentwurf ist noch KEINE gefahrlos einsetzbare 9–30-V-/200-V-Loesung. Die wenigen netto gesparten Bestueckpositionen koennen gegen mehr Risiko und Qualifikationsaufwand stehen. Weg B getrennt bearbeiten und erst nach mess-/herstellerbasierten Proof-Gates mit Weg A vergleichen.
