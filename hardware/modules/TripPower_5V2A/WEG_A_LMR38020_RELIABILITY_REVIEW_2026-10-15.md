# TripPower Weg A – 80-V-LMR38020-Q1: unabhängiger Robustheits- und Reduktionsreview (15.10.2026)

**Branch:** `design/trippower-a`, abgezweigt von `design/solid-state-power-v1`. **Weg B wird nicht verändert.**

**Status:** Engineering Review / **P01–P10 BLOCKED**. Keine Freigabe für Hardware, KiCad-DRC, ISO 16750-2, Fertigung oder Fahrzeug. Dieser Review verändert **keine** elektrischen KiCad-Baseline-Werte, weder die REV5-BOM noch den 80-V-Regler. Priorität: reproduzierbare Nachweise und weniger technische Ungewissheit statt „billigerer“ riskanter Schnelltausch.

## Verbindlicher Ausgangspunkt und Entscheidungen

Gelesen und berücksichtigt: `AGENTS.md`, `hardware/modules/TripPower_5V2A/START_HERE_NEXT_CHAT.md`, `REV5_DESIGN_BASELINE.json`, `MPM3551_SWAP_DEEP_DIVE_2026-10-15.md`, `REV5_OPTIMIZATION_IMPLEMENTATION_2026-10-15.md`, aktuelle Unterseiten `01_Protection_LM74930.kicad_sch`, `02_5V_LMR38020.kicad_sch`, `03_VS_READY_TPS3760.kicad_sch` und die Q301-/C303-Studien.

- 9–30 V am **VIN_FUSED-Eingang des Moduls**, 5 V / 2 A Dauerlast, zusätzlicher geschützter RAW-Abgriff bis 1 A als Auslegungsziel.
- Separater **ungedämpfter 200-V/350-ms-Lastabwurf** (nicht 202 V). Rechteck-Sensitivität nur für obere Bauteilenergie-Abschätzung; ISO-Wellenform und Innenwiderstand müssen getrennt geprüft werden.
- -40 bis +125 °C Entwicklungsumgebung; externer, austauschbarer und nach Quell-/Kabel-/Kupferdaten dimensionierter `F_MAIN`; keine Löt-Schmelzsicherung.
- **LMR38020SQDDARQ1 beibehalten** (80 V, 2 A), mit 400-kHz-RT, 15-µH-L101 und vorhandener TI-naher 3×22-µF-Ausgangsfilterung; `LM74930QRGERQ1` und `TPS38A010122DSKRQ1` behalten.
- Aktive REV5-Bestückung **57 AUTO / 58 RUN** (R305 und R321 sowie Modus-DNP wie baseline). Weitere Entfallpositionen derzeit **null ohne zusätzliche Nachweise**; eine unqualifizierte Reduktion wird nicht als Verbesserung gewertet.

## Gate A1 – 200 V: TVS-Stack ist keine garantierte 250-V-Klemme

Aktives Netz `VIN_FUSED -> D303 SMBJ150A-13-F -> TVS_STACK -> D304 SMBJ33CA-13-F -> GND`. Die beiden Dioden sind in Serie (D304 bidirektional). Diodes Inc. Datenblätter/Produktparameter:

- SMBJ150A: Mindest-Durchbruchspannung **167 V**, maximale Durchbruchspannung **192,5 V**, Klemmspannung bei spezifiziertem IPP **243 V**.
- SMBJ33CA: Mindest-Durchbruchspannung **36,7 V**, maximale Durchbruchspannung **42,2 V**, Klemmspannung bei spezifiziertem IPP **53,3 V**.
- Serien-Durchbruchbeginn (typisierende Bounds bei angegebener Prüfstromeinstellung) **167 + 36,7 = 203,7 V minimal**, bis **192,5 + 42,2 = 234,7 V maximal**. Der verlangte **200-V-Scheitel liegt unter der minimalen Summe**: kein garantiertes TVS-Klemmen während des 200-V-Plateaus. Die Summe zweier separat spezifizierter Maximal-Klemmspannungen **243 + 53,3 = 296,3 V** bei den *jeweiligen* Datenblatt-IPPs ist **keine gemeinsame Betriebskennlinie**, zeigt aber, dass „TVS schützt sicher Q301 bis 250 V“ nicht ableitbar ist.
- Die 600-W-Klassenangabe ist auf den definierten kurzen Datenblattimpuls bezogen und **kein 350-ms-Dauerleistungsnachweis**. Der Stack könnte für schnelle Überschwinger/andere Verpol-Ereignisse trotzdem benötigt werden: **nicht entfernen**, bis der Gesamttransient und negative Schutzfunktion qualifiziert sind.
- `SQM10250E_GE3`: 250-V-Abs.-Max.-VDS, beim vorgegebenen 200-V-Scheitel rechnerisch nur **50 V nomineller Überschwingerabstand**, ohne Oszillation, Quelleninduktivität, Exemplarstreuung und heißes Turn-off. Ein sicherer Q301-Abschalt-SOA-Beweis benötigt `VDS(t)`, `ID(t)`, `VGS(t)` und Tj-Ausgangswert, nicht nur 250-V-Nennwert.

**Entscheidung A1:** Q301, D303 und D304 vorerst unverändert; **P03 bleibt CRITICAL**. Zwischen MOSFET- und TVS-Auswahl erst reale kombinierte Quellen-/Leitungs-/Clamp-Kennlinie inklusive Flanke, 200V/350ms und Worst-Case-Generatorinnenwiderstand nachweisen. Eine nur auf den TVS-Teilewerten beruhende 250-V-Marge ist nicht akzeptabel.

Quellen: [Diodes SMBJ150A](https://www.diodes.com/part/view/SMBJ150A), [Diodes SMBJ33CA](https://www.diodes.com/part/view/SMBJ33CA), [Vishay SQM10250E](https://www.vishay.com/docs/75035/sqm10250e.pdf), [TI 200-V-Lastdump-Anwendung](https://www.ti.com/document-viewer/lit/html/SNOAAA1/GUID-A29F6540-095F-4408-8FD4-388A1740884B).

## Gate A2 – VS-Zweig: 9-V-Erststart gegen 200-V-Puls

Aktive R313–R315: 3×3,3 kΩ, gesamt 9,9 kΩ, VS-Nenn-Zener 56 V; `C302 + C308 + C312` nominal **21 µF**, reale bias-/temperaturabhängige Mindestkapazität **unbekannt**. Der LM74930 lädt die VS-Domäne zu Beginn ausschließlich durch die Widerstandskette; `D302 SOURCE_A -> VS_CLAMP` kann den Strom erst **nach** erfolgreichem Einschalten des Serienpfades liefern.

**200-V-Vergleichsrechteck**, 56 V als ausdrücklich **nur angenommene konstante Zenerspannung**, 0,35 s:
- I_RVS = (200−56)/9900 = **14,545 mA**.
- P je 3,3k = I²×3300 = **0,698 W**; 350-ms-Energie **0,244 J je Widerstand**.
- P_Zener = 56×I = **0,815 W**, Energie **0,285 J**.
- **Zener-Kurzschluss als Einzelfehler:** bei ideal 200 V und drei Widerständen je −1 % Widerstand P je ≈**1,36 W**, E je ≈**0,476 J**. Die 2512-Widerstands-Puls- und Deratingkurve muss **diesen Fehler** bei heißer Ausgangstemperatur abdecken; die nominelle 1,5/2-W-Angabe allein reicht nicht.
- Ein Tausch auf 1 kΩ erhöht I bei 200V/56V hypothetisch auf **144 mA**, P im Widerstand auf **20,74 W**, E auf **7,26 J** und P_Zener auf **8,06 W**. **Verboten als Drop-in.**

**9-V-Bootstrap:** Bei VS ≈8 V liefern 9,9 kΩ nur **~101 µA**. Der TI-Nenn-Ruhestrom in aktivem Zustand liegt wesentlich höher, sodass der Start nur über vorab geladenes `Ceff`, zeitgesteuerte EN-Freigabe und danach D302-Stützung funktionieren *kann*. Die 21 µF sind ausschließlich Nennwerte, keine garantierte Ladungsreserve. Das TPS38-Zeitglied C311 330 nF ist kein Nachweis für einen garantierten VS-Mindestwert unter Pumpen-/Leck-/Temperatur-Einfluss. Besonders messen: 0→9V bei Kälte/Hitze, unvollständige Spannungsausfälle, RUN-HIGH bei VIN=0 und READY/EN-Hysterese.

**Entscheidung A2:** R313–315, D301, C308/C312, C311 und TPS38-Verriegelung unverändert. Für 9-V-Anlauf **zuerst** gemessene `VS_CLAMP`, `CAP_PUMP−VS`, `CTRL_EN`, `SOURCE_A`, `HGATE−SOURCE_A` mit 0/2-A-5V und 0/1-A-RAW. Vorher keinen weiteren Kondensator verbauen oder wegstreichen. `P01/P02/P04/P06/P10` bleiben offen.

Quellen: [TI LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), [Vishay CRCW-HP](https://www.vishay.com/docs/20043/crcwhpe3.pdf), [TI TPS38-Q1](https://www.ti.com/lit/ds/symlink/tps38-q1.pdf).

## Gate A3 – Thermik und Wandlerinduktivität

Aktiver Buck: `LMR38020SQDDARQ1` 400 kHz, `FCH0650-150M` nominal 15 µH ±20 %, laut LCSC 5 A Stromrating, 5,5 A Sättigung, **54 mΩ DCR**. Die folgende idealisierte Buck-Abschätzung ist **kein EMV-/Hot-/CCM-Gesamtnachweis**:

| VIN | L | ΔI_L (p-p) ideal | I_L peak @ 2 A | 54-mΩ-Kupferverlust bei 2 A + Ripple, 25°C |
|---|---:|---:|---:|---:|
| 9 V | 15 µH | 0,370 A | 2,185 A | ~0,217 W |
| 30 V | 15 µH | 0,694 A | 2,347 A | ~0,218 W |
| 30 V | 12 µH (−20 %) | 0,868 A | 2,434 A | ~0,219 W |

Bei angenommener Cu-Widerstands-Temperaturkonstante 0,00393/K steigt die Kupferwärme in der 125°C-Wicklung grob auf **0,30 W** – ohne Kernverluste, IRMS-Derating und umliegende Bauteile. Die nominelle 5,5-A-Isat-Zahl kann nicht ohne Hersteller-T-Kennlinie als heißer Garantiewert gelten.

**Bewertung:** Der 80-V-LMR bietet deutlich mehr VIN-Reserve als ein 36-V-Wandler und bewährten 400-kHz-Betrieb. Er garantiert **keine 2 A bei 125°C auf beliebig kleiner 35-µm-PCB-Fläche**. TI-EVM: 4 Kupferlagen, Thermalvias unter PowerPAD, nach TI EVM-Dokument teils 2 oz äußere Kupferlage; ein kompaktes 2-Lagen-/1-oz-Layout darf dessen thermischen Kennwert nicht übernehmen. Beispiel: Würde 1 W im Regler-IC landen, wären bei 125°C Umgebung und maximal angenommenen 150°C Sperrschicht nur **25 K/W effektiver** IC-Thermalwiderstand zulässig (vereinfachte stationäre Gleichung). Regler- und Induktorverluste sowie FET-Verluste einzeln modellieren und messen.

**Entscheidung A3:** Keine spontane L-/RT-/COUT-Reduktion; 3×22µF folgt der TI-5V-Referenz. Durch thermisch korrektes **PCB-Layout** (Pad-Kupfer-/Thermalvia-Kopplung, Grundflächen, Hotspots von Q301/Schottkys, gegebenenfalls 4 Lagen statt 2) ist mehr Zuverlässigkeit zu gewinnen als durch einen unbewiesenen 1-Position-Tausch. `P08/P09` offen.

Quellen: [TI LMR38020-Q1](https://www.ti.com/product/LMR38020-Q1), [TI LMR38020QEVM](https://www.ti.com/tool/LMR38020QEVM), [FCH0650-150M](https://www.lcsc.com/de/product-detail/C20415538.html).

## Gate A4 – Bauteilzahl und Bestückungsentscheidung

**57 AUTO / 58 RUN** bleiben die korrekten REV5-Sollwerte; R305 (IMON) und R321 (unbenutzter FLT-Pull-up) bereits DNP. Nicht doppelt als neue Einsparung zählen. Die bestückte Buck-Teilzahl beträgt laut aktivem Blatt **12** (Regler/Spule/Ein- und Ausgangskondensatoren/BOOT/2 FB/RT). Keine dieser weiteren Positionen ohne TI-Referenz-/Worst-Case-Daten reduzieren:

1. C101/C108 und C107: VIN-Entkopplung und Schaltspitzen, unter Bias nicht nominal wirksam.
2. C104–C106: TI empfiehlt 3×22µF bei 5V; Entfernen verschlechtert möglicherweise Loop/Loadstep und spart nur 1 Position.
3. R103: RT/SYNC darf laut TI nicht floaten.
4. C303, C308, C312 und C311: begründen jeweils eigenständige CAP-Pumpen-/Start-/Reset-Stabilität; erst Ceff nachweisen.
5. R303 ISCP, C301 TMR, Schutz-FETs und VS/OV-Split-Widerstände: Schutzfunktion/Fehlerausfall; **kein** DNP für den Einkauf freigeben.

Kein MPM3551 oder 36V-TPSM auf diesem Weg. Kein neu erfundener AEC-Ersatz für LMR. Kein weiterer reiner Stückzahl-Commit ohne Mess- oder Herstellergrenzwert.

## Nachweisplan mit eindeutigen Kriterien

| Gate | Test/Nachweis vor PCB-Freigabe | Abnahmelogik |
|---|---|---|
| P01/P06 9V | Cold start 0→9 V, Rampen, Brownout/Restart bei −40/25/85/+125°C, VS/CAP/EN/HGATE zeitgleich, Ceff über V/T/Alterung | Start reproduzierbar oder definiert sicher aus; Herstellergrenzen nicht verletzt |
| P02/P10 | AUTO/RUN, RUN=0/3,3/5V, VIN=0 und Pulsunterbrechung; EN LOW ≤0,41V / HIGH ≥1,05V nach realer Hysterese; BAT-OFF-Systemstrom | Fail-OFF, keine USB-Rückspeisung, Restladungstest |
| P03/P04 | 200V/350ms Quellmodell + Schaltflanken, hot SOA Q301, Zener- und drei RVS-Pulse, D303/D304 | Kein VDS/VGS/VS/Pin/Peak-/SOA-/Temperaturverstoß |
| P05 | externe F_MAIN mit Kabel/Stecker/35µm-Kupfer I²t inkl. FET stuck-ON und RAW-Kurzschluss | Sicheres Fehlerinventar ohne gefährliche Leiterbahnerwärmung |
| P07/P08 | C306 exakter MPN/63-V-Domain, Buck 9/12/24/30 V @ 0/0,5/1/2 A und AUX 0/1 A, Hotspot-Messung | 5V-Regelung, Ripple und Temperaturen innerhalb Herstellergrenzen |
| P09 | eigenständiges tatsächlich geroutetes KiCad-10-PCB, ERC/Netlist/DRC, Pin1/Footprints/3D/thermal vias | Alle nativen Checks bestanden, visuelles Review und Messpunkte vorhanden |

**Praktische Reihenfolge:** (1) sicheren 9V-VS-Start und EN-Interlock nachweisen, (2) Q301/TVS-/Zener-/RVS-Puls-SOA im 200-V-Lastdump inklusive Fehlerfall bewerten, (3) thermische Buck-/FET-/Induktor-Strecke auf realem Lagenaufbau qualifizieren, (4) erst dann BOM reduzieren und PCB/Fab-Gates schließen.

## Änderung gegenüber Ausgangsbaseline, Prüfung und Grenzen

- **Neu:** eigenständiger, versionierter Weg-A-Review mit überprüfbaren Start-/Puls-/Thermik-Rechnungen und dokumentiertem TVS-Serien-Durchbruchvorbehalt.
- **Unverändert:** alle KiCad-Symbole, MPNs, Footprints, R-/C-Werte, Schwellwerte, EN-Topologie, aktive AUTO/RUN-BOM (57/58), REV5-JSON, AGENTS.md und sämtliche Weg-B-Dateien.
- **Werkzeugstatus:** Dieser Review hat Repositorydateien gelesen und Herstellerquellen gegengeprüft, aber **keinen nativen KiCad10-ERC/DRC-Lauf, keine Simulation und keine physische Messung** durchgeführt. Gerade weil keine elektrische Schaltung modifiziert ist, entsteht keine neue konstruierte Funktionsbehauptung. Die stop-gates P01–P10 bleiben verbindlich.
