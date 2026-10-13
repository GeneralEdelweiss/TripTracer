# TripTracer V1 – Eingangsschutz, eFuse, Dauerplus und ACC

**Stand: 13.10.2026 · Baugruppe 01D, Vorab-Auslegung.** Dieser Text und das neue KiCad-Blatt sind **KEIN vollständiger Fahrzeug-Eingangsschutz**, keine bestandene KiCad-ERC-/DRC-Prüfung, kein validiertes Relaiskontakt-/Kaltstartdesign und keine Fertigungsfreigabe.

Verbindliche Beschlüsse: [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md), PWR-01–12/15–24/30–36, HW-25–36/82–86. 9–36 V reguläre Versorgung, **gleiche Hardware für 12- und 24-V-Fahrzeuge**, über M8 Pin 1 **ACC**, Pin 3 **GND**, Pin 4 **BAT+**. **ACC und BAT+ fahrzeugseitig jeweils passend absichern**. Keine zusätzliche Energiespeicherung für vollständigen M8-Abzug. Motorstartspannungseinbrüche bleiben getrennt zu erfüllen.

## 1. Besonderheit der vorgeschalteten Always-on-Architektur

Die eigentliche Haupt-eFuse darf **nicht dauerhaft bestromt vor dem Relais sitzen**, wenn wir das BAT+-OFF-Ruhestromziel unter 100 µA verfolgen: Der Kandidat TPS26631 hat im eingeschalteten Zustand **1,38 mA typ. / 1,7 mA max. Eigenstrom**, selbst ohne angeschlossene Last. Im abgeschalteten Zustand braucht er typisch 21 µA. Quelle: [TI TPS2663 Datenblatt Rev. G](https://www.ti.com/lit/ds/symlink/tps2663.pdf), Abschnitte 6.5 und 8.

Stattdessen sind **zwei unterschiedlich belastete Pfade** nötig:

```text
M8 Pin 4 BAT+ -- fahrzeugseitige Sicherung -- [Kfz-Surge-/Reverse-Basisschutz] -- BAT_AUX_PRE
                                                                     |
                                 +---[niedrig-Iq-AUX-Schutz]---[LM5164-Q1 5V]---K101-Spule/Startlogik
                                 |
                                 +--- K101 NO (COM4/NO5) --- BAT_SW_BEFORE_EFUSE
                                                                    |
                                       [externes Blocking-MOSFET + Pulldown-MOSFET]
                                                                    |
                                             TPS26631 PWP/eFuse --> HV_PROTECTED_AFTER_EFUSE
                                                                      --> 5V_MAIN-Buck
M8 Pin 1 ACC -- eigene fahrzeugseitige Sicherung -- [ACC-Surge-/Reverse- und Filter] -->
                                                          ACC_PROTECTED_IN -> 01B/01C
M8 Pin 3 GND ------------------------------------------------------ GND
```

**Wesentliche Warnung:** K101 liegt derzeit vor der eFuse; **dessen Kontakt muss den Vorstrom-/Kondensator-Einschaltstoß selbst vertragen**. Eine eFuse *hinter* K101 verhindert den Stromstoß in davorliegende Kondensatoren nicht. Möglichst kleine, datenblattkonforme Eingangskapazität vor eFuse; Kontakteignung bei **36 VDC, 9-V-Volllast und kapazitiver Last** prüfen. Das Omron G6S-2F DC5 ist für **2 A bei 30 VDC ohmscher Last** spezifiziert, nicht automatisch für 36 V mit Hot-Plug-/Capacitor-Inrush. Bei ungeeigneten Kontakten eine gezielte alternative Relaisauswahl vorlegen – nicht das Relais stillschweigend freigeben.

## 2. eFuse-Kandidat mit angemessenem 36-V-Betrieb

**TI TPS26631PWPT**, HTSSOP PowerPAD-20, vorläufige bevorzugte Variante im Hauptpfad ([TI-Datenblatt](https://www.ti.com/lit/ds/symlink/tps2663.pdf)):

- **4,5–60 V empfohlen**, maximal **67 V absolut** (IN_SYS; Bedingungen der anderen Pins prüfen). Industrie-eFuse, **nicht per se AEC-Q100/automotive-zugelassen**. Alle relevanten Automotive-Transienten-/Load-Dump-Pulse sind außerhalb des bloßen IC-Nennbetriebs eigenständig abzusichern.
- **PWP-20** statt 24-Pin-QFN, besser handlötbar. Durch Herstellerdatenblatt verifizierte 20 **Signalpins**: IN 1/2/3; B_GATE 4; DRV 5; IN_SYS 6; UVLO 7; OVP 8; GND 9; dVdT 10; ILIM 11; MODE 12; SHDN 13; IMON 14; FLT 15; PGTH 16; PGOOD 17; OUT 18/19/20. **Thermisches PowerPAD: Muss auf GND-Fläche; Lötpadnummer/konkreter Footprint noch offen.**
- **Auto-Retry:** `MODE` an GND, nicht offen (offen = Latch). R_ILIM nach Gleichung (8): `R_ILIM[kΩ] ≈ 18/I_LIMIT[A]`. **Vorläufig 7,5 kΩ ≈ 2,4 A**, aber Fehlerschutz/untere 9-V-Hauptlast und Puffer-/Startströme vor Freigabe testen.
- **Ausgangsanstieg:** `dVdT` mit mindestens 10 nF gegen GND; **100 nF als rein vorläufiger Startpunkt** analog zur TI-Applikation für hohe Ausgangskapazität. Ausgangsstromspitze und 1.25-s-Thermal-Retry von PWP/Cap-Bank abhängig. Noch keine Berechnung der finalen Belastung.
- **OVP:** TPS26631 besitzt **einstellbare Abschaltung** (statt fest ca. 35 V oder 39 V begrenzender TPS26632/35). Unabhängiger Widerstandsteiler als Vorentwurf `390 kΩ / 12 kΩ` an `OVP` → nominell `1,2·(390+12)/12 = 40,2 V`. **Nur Arbeitspunkt**, keine Durchlass-/UVLO-/OVP-Toleranzfreigabe oder Beweis, dass der IC bei Automotive-Pulsen nie >60 V sieht. Bei 36-V-Normalbetrieb zusätzlich Teilerfehler, Leck-/Transienten und Filter berücksichtigen.
- **UVLO:** mit externem Reverse-FET muss `UVLO` nach TI-Regel über mindestens 300 kΩ an IN_SYS angeschlossen werden, wenn keine separate UVLO-Schwelle vorgesehen ist. Das konkret sinnvolle Crank-/Restart-Verhalten muss gemessen werden. Die standardmäßige interne 15,46-V-UVLO-Einstellung (**UVLO direkt GND**) wäre mit 12-V-Bordnetz inkompatibel.
- **Externes Blocking-NMOS vorgeschrieben**: `SOURCE = IN_SYS`, `DRAIN = IN`, `GATE = B_GATE`; separater kleiner MOSFET für `DRV/B_GATE/IN_SYS` gemäß TI Abb. 8-7. Ohne beide MOSFETs ist TPS26631 **nicht verpolsicher**. Konkrete MOSFETs/Footprints/Schaltungsdetails für 60-V-Differenzen, sicheren Aus-Zustand und negative Surge noch auszuwählen.
- `PGTH`-Teiler und nachgeschaltetes `PGOOD` im Zusammenhang mit Hauptbuck-UVLO auslegen; `IMON`/FLT für Diagnose optional. Für `SHDN` Hersteller-Logikpegel, Auto-Retry und Fehlerneustart prüfen; bei aktivem Haupt-BAT_SW nicht offen lassen.

**Wichtig:** Das 01D-KiCad-Blatt wird bewusst **nicht so verbunden, als wäre ein fehlender MOSFET ein Draht**. Die eFuse ist ein korrekt benannter Bauteilkandidat mit beispielhaften Parametern; ihre Schutzpfade/OVP-/UVLO-Netze und Leistungsein-/ausgänge sind bis zur vollständigen Bauteilauswahl **nicht zur Inbetriebnahme freigegeben**.

## 3. TVS, Verpolschutz und Lastabwurf – Systementscheidung offen

Eine reine 1500-W-TVS (z. B. SMCJ36A als **vergleichender Kandidat**, 36 V VRWM) kann bei kurzem ESD/Transientenimpuls helfen. **Nicht behaupten**, sie könne *beliebige* 24-V-Load-Dump-Pulse so klemmen, dass jeder 60-V-Schaltregler/eFuse garantiert innerhalb seiner maximal zulässigen 60/67 V bleibt. Klemmspannung hängt vom Pulsstrom ab; etwaige 40–60-V-Klemme und TVS-Lebensdauer müssen bei passendem ISO-7637/ISO-16750-Impulsstrom und Quellimpedanz belegt werden. Zusätzlich muss die TVS-Leckstrombilanz bei hoher Temperatur zu <100 µA OFF passen.

Die **immer aktive 5-V-AUX-Stufe** muss **vor** K101 einen eigenen Überstrom-/Verpol-/Surge-Schutz erhalten. Die Haupt-eFuse schützt sie nicht. Die 100-V-Eingangsfestigkeit des LM5164-Q1 ersetzt weder dessen Grenzwerte am Schaltknoten noch sicheren Leitungsschutz. Ein kleiner, rückwärtsfester Serien-Gleichrichter im AUX-Teil oder geeignete Ideal-Diode/MOSFET-Schaltung ist wegen des geringen AUX-Stroms preislich zu vergleichen; im **primären Hauptstrompfad** gilt weiterhin HW-26, also Verpolschutz durch dokumentierte eFuse+externes Blocking-FET-Konzept.

**Noch offen vor Schutzfreigabe:** tatsächliches 24-V-Load-Dump-Profil (suppressed/unsuppressed, Quellimpedanz, Energie, Fahrzeugklasse); Thermik/Spannung von 60-V-Kandidaten; TVS-/Kontakt-Worst-Case; ACC-Eingangs-Puls-/Negativspannung; Verpolung bei gleichzeitig vorhandenem USB; Ruhestrom an 85 °C; kontaktkompatible Vor-eFuse-Kapazität; PCB-Masse/TVS-Rückstromlayout.

## 4. Konkrete Freigabe-Reihenfolge und Fehlerfälle

1. **Einspeisefälle** 9/12/24/36 V, getrennt ACC/BAT+, M8 vertauscht, ACC 0 bei BAT+ vorhanden, BAT+ 0 bei ACC vorhanden, beide Plusadern vertauscht/negativ und USB-only bestimmen; alle ohne Rauch/absolutes-Maximum-Überschreiten.
2. **Relaiskontakt schützen:** vor eFuse nur zulässige Eingangskapazität; Lade-/Einschaltstrom und DC-Abschalten bei 36 V gegen Omron-Kurve belegen.
3. **Kfz-Transienten/Verpolung** am Always-on-AUX und am eFuse-Hauptpfad vor konkreter TVS-/MOSFET-/eFuse-Wertefreigabe auslegen.
4. **TPS26631** mit vollständiger B_GATE/DRV-Topologie, 9–36-V-Schwellen, 2,4-A-Grenze, Auto-Retry und dVdT dimensionieren; Fußabdruck TI PWP-20+PowerPAD mit Herstellerlandpattern zuordnen.
5. **01D mit 01A/01B/01C/02 verschalten**, separate/geeignete Sicherungen und Eingangsschutz nachweisen; keine PWR_FLAG-/no-connect-Tricks zum Verdecken unverbundener oder ungeschützter Netze.
6. Echte **KiCad-10-ERC + DRC**, gemessene Impulse, Kontakt- und Power-Budget, 12-/24-V-Kaltstart, ACC AUS samt SD-Flush, nachfolgende Labor-/Fahrzeugtests. **Keine Fertigungsfreigabe vorher.**

**Quellen:** [TI TPS26631 (Datenblatt Rev. G)](https://www.ti.com/lit/ds/symlink/tps2663.pdf); [TI TPS26630/33 EVM](https://www.ti.com/lit/ug/slvubi8a/slvubi8a.pdf); [TI LM5164-Q1](https://www.ti.com/lit/ds/symlink/lm5164.pdf); [Omron G6S-2F DC5](https://www.fa.omron.co.jp/product/item/G6S-2F_DC5/).

## 5. Prüfergebnis der nächsten Auslegungsrunde (13.10.2026)

**Ergebnis: noch keine sichere Verdrahtungsfreigabe für 01D.** Das vorhandene Blatt `01D_INPUT_PROTECTION.kicad_sch` enthält U401 als absichtlich unverdrahteten Kandidaten. Vor dem ersten Einschaltversuch müssen insbesondere zwei Probleme gelöst werden: (1) K101 schaltet derzeit die gesamte ungeregelte BAT+-Hauptleitung **vor** der eFuse; (2) die dauerhaft versorgte AUX-Stufe wird durch U401 **nicht** geschützt. Beide Pfade sind für 9–36 V sowie Transienten gesondert zu dimensionieren. Dies ist ein **dokumentierter Sicherheitsstopp, kein ERC-Fehler, der durch Labels oder PWR_FLAG geheilt werden könnte**.

### 5.1 Verifizierte Kenndaten und konkrete vorläufige Teile

| Position | Stand / Datenblattbezug | Folgerung / Status |
|---|---|---|
| U401, TI **TPS26631PWPT** | 4,5–60 V Betriebsbereich, 67 V abs. max.; HTSSOP-20 mit PowerPAD; externer Blocking-N-FET für Reverse Polarity/Reverse Current erforderlich. `MODE = GND` bedeutet Auto-Retry. | Kandidat **für den geschalteten Hauptzweig**, nicht für den ungeschützten Dauereingang. Industriegerät, keine behauptete Automotive-AEC-Q100-Freigabe. [TI Produktseite](https://www.ti.com/product/TPS2663/part-details/TPS26631PWPT). |
| Q402, **BSS138-7-F** (Diodes Inc., LCSC **C40912**) | 50 V `VDS`, ±20 V `VGS`, `Ciss ≤ 50 pF` bei 10 V, `VGS(th) max. 1,5 V` bei 250 µA; SOT-23. | **Kandidat** als schneller Gate-Pulldown-FET an U401: Gate→DRV, Drain→B_GATE, Source→IN_SYS nach TI Abb. 8-7. Bauteil- und Pad-Nummern müssen vor Symbol-/Footprint-Freigabe verifiziert werden. [DigiKey](https://www.digikey.de/en/products/detail/diodes-incorporated/BSS138-7-F/717723), [LCSC](https://www.lcsc.com/de/product-detail/C40912.html). |
| Q401, externer Blocking-N-MOSFET | Nach TI Abb. 8-7 **Source→IN_SYS, Drain→IN(1/2/3), Gate→B_GATE**. Sein `VDS`, `VGS`, Verlustleistung, SOA, Impulsrobustheit und passender SMD-Footprint sind noch **nicht** verifiziert. | **Keine freie MOSFET-Teilenummer erfinden**. Der Weg über den FET darf nicht mit einer Drahtbrücke ersetzt werden. |
| R_ILIM, Entwurfswert bisher **7,5 kΩ** | Aus TI Gl. 8: `I_OL ≈ 18 / R_ILIM[kΩ]` → nominal **2,40 A**; mit **9,09 kΩ** wären es nominal etwa **1,98 A**. | **7,5 kΩ bleibt kein freigegebener Wert.** TPS26631 besitzt nach aktiviertem PGOOD einen kurzzeitigen **2×-Überstrommodus**. Selbst ein nominelles 2-A-Limit ist somit **keine 2-A-Obergrenze** für Relaiskontakt/Kabel. Lastspitzen, Leiterquerschnitt und Sicherungen gesondert prüfen. [TI Rev. G, § 8.3.7 und § 9.2.2](https://www.ti.com/lit/ds/symlink/tps2663.pdf). |
| OVP, Kandidat **390 kΩ/12 kΩ** | Bei 1,2 V nominaler Schaltschwelle ca. **40,2 V**. Dauerstrom im Teiler bei 36 V: ca. **89,6 µA**, **nur falls hinter K101 versorgt**. | Für 36-V-Nennobergrenze plausibler **Startpunkt**, aber Schwellwerttoleranz, Teilerderating, EMV-Eintrag und ausreichende Reserve zum Buck-VIN-Maximum fehlen; kein Load-Dump-Beweis. |
| UVLO und dVdT | Mit externem Blocking-FET verlangt TI für eine ungenutzte UVLO-Funktion mindestens **300 kΩ** zu IN_SYS. dVdT-Kondensator gegen GND; 100 nF ist lediglich ein noch nicht gerechneter Ausgangsrampen-Kandidat. | Die tatsächliche UVLO-Hysterese muss zum 9–36-V-Dauerbetrieb, 3-/6-V-Startprofil und Relaisverhalten passen. **Nicht UVLO auf GND legen**, da sonst die interne hohe UVLO für den 12-V-Betrieb ungünstig ist. |

**TI-Originalschaltung:** [TPS2663 Rev. G, Abb. 8-7 (B_GATE/DRV), Abb. 9-2 (externes NMOS + BSS138, Schutzbeschaltung)](https://www.ti.com/lit/ds/symlink/tps2663.pdf). Die dort gezeigte **18–33-V-PLC-Anwendung** ist **nicht 1:1** auf die beschlossenen **9–36 V in 12-/24-V-Fahrzeugen** übertragbar. Besonders die UVLO/OVP-/TVS-Auswahl muss neu gerechnet werden.

### 5.2 K101-Strompfad als Blocker, nicht als Nebenbedingung

Herstellerangabe für **Omron G6S-2F DC5**: **2 A / 30 VDC bei ohmscher Nennlast**, **60 W** maximale DC-Schaltleistung, 2 A maximaler Kontaktstrom; die maximal zulässige Spannung **220 VDC** ist **keine Freigabe für 2 A bei 220 V**. [Omron G6S-2F DC5](https://www.fa.omron.co.jp/product/item/G6S-2F_DC5/), [Omron G6S Datenblatt](https://components.omron.com/eu-en/system/files/2023-01/datasheet_pdf/K093-E1.pdf).

- Bei **36 V** entspricht die bloße **60-W-Hüllkurve** höchstens **1,67 A** für geeignete ohmsche Bedingungen; die konkrete DC-Schaltkennlinie und Kapazitätslast können **noch niedrigere** Werte erfordern. Die 2,4-A-eFuse-Grenze liegt oberhalb des 2-A-Kontaktstromlimits. Der kurzzeitige 2×-Modus verschärft den Konflikt.
- Ein nach dem Kontakt sitzender eFuse/dVdT-Ausgangsschutz reduziert **nicht** automatisch den Kontakt-Einschaltstrom in Kondensatoren **vor U401**. Die dortige Kapazität, Serienimpedanz, Spannung und die mechanische Prellphase müssen bekannt sein.
- **Kein K101-Footprint/Schaltplan als 36-V-tauglich freigeben**, nur weil eine 220-V-Maximalangabe auf dem Datenblatt steht. Erst maximale reale Lastaufnahme (9 V = höchster Betriebsstrom), 36-V-Schaltkurve und Kontakteinschaltstoß quantifizieren.

**Entscheidung vor der finalen Verschaltung nötig:**

- **A – bisherige Sollarchitektur beibehalten:** K101 schaltet BAT+ vor U401. Dann konkrete Kontakt-/Inrush-Eignung nachweisen oder ein geeignetes Mikrorelais vorschlagen. Immer-aktive AUX-Leitung benötigt separat verifizierten negativen/positiven Surge-, Verpol- und Leitungsschutz.
- **B – mögliche kostensensible Alternative, noch NICHT beschlossen:** K101 schaltet lediglich den **stromarmen Enable-/Freigabepfad**; U401 bleibt an BAT+ vor dem Leistungspfad und wird im OFF-State abgeschaltet. Das entlastet den Kontakt von Hauptlast-/Kondensatorstrom, aber der U401-OFF-Eigenstrom (ca. 21 µA **typisch**, max./85 °C gesondert messen) erhöht den BAT+-Ruhestrom; ACC-Start, HOLD, galvanische/USB-Rückspeiseabgrenzung, Failsafe und eFuse-Ausfallmodus müssen komplett neu bewertet werden. Dies wäre eine **Architekturänderung**, keine stillschweigende Optimierung.

### 5.3 Verifikation vor dem Verdrahten / vor dem Einschalten

| Gate | Benötigter Nachweis |
|---|---|
| G1 – Fahrzeug-Transiente | Für **12 und 24 V** eine definierte Stör-/Load-Dump-/Reverse-Polarity-Prüfmatrix inklusive Quelle, Quellimpedanz, Pulsdauer und Polarität; danach erst konkrete TVS/Suppression, thermische Energie und maximalen VIN an **AUX** und **U401** berechnen. Eine nackte SMCJ36A garantiert keine sichere Begrenzung eines unsuppressed 24-V-Load-Dumps. |
| G2 – K101 | Reale elektrische Leistungsbilanz bei 9/12/24/36 V, Ein-/Ausschaltenergie bei 36 V, Pre-eFuse-Kapazität, 2×-Pulsmodus und Relais-Nennkennlinie abgleichen. Bei Misserfolg K101/Schaltprinzip gezielt ändern, **nicht** die 2-A-Angabe umdeuten. |
| G3 – OFF-Ruhestrom | Bei ausgeschaltetem ACC und vorhandenen BAT+ 9/12/24/36 V: **Gesamter** Dauerruhestrom inkl. LM5164-AUX, ACC-Erkennung, TVS-Leckstrom (auch warm), eFuse (je nach Architektur), Spannungsteiler und Relaislogik. Ziel **unter 100 µA**, Worst Case bei Temperatur, nicht nur typische Einzelwerte. |
| G4 – eFuse | U401 Pinout (inkl. PowerPAD/GND), Q401/Q402-Pin-Pad-Zuordnung, UVLO/OVP/ILIM/dVdT, Retry-Dauer und thermisches Fehlerverhalten gegen TI-Datenblatt prüfen. Schutz/Abkopplung bei gleichzeitigem USB und negativem BAT/ACC. |
| G5 – Motorstart und Abschalten | 3 V / 15 ms, anschließend 6 V über Sekunden (12-V-Zielprofil), analog 6→10 V für 24 V; Datenaufnahme ohne Reset, SD-Flush nach ACC AUS über BAT+-Selbsthaltung; **keine** garantierte Notenergie bei komplett entferntem M8. |
| G6 – Projekt-/Hardwarefreigabe | Nach vollständiger **elektrischer** Verdrahtung: KiCad 10 projektweit ERC, ERC-Meldungen prüfen, VIN/VOUT/USB-Powerpfade und richtige Hersteller-Footprints einzeln abgleichen, PCB synchronisieren/DRC, Netzteil-/Transienten-Tests. **Bis dahin keine Fahrzeug-/Fertigungsfreigabe.** |

**Umsetzungsstand dieser Runde:** Primärdatenblatt, K101-Lastkennzahlen und Q402-Kandidat geprüft; **kein 01D-Schaltplan elektrisch verbunden, kein KiCad-ERC, kein PCB-DRC, keine Last-/Surge-Messung durchgeführt.** Die sicherheitskritische Architektur- und Teileauswahl hat Vorrang vor formaler ERC-Kosmetik.
