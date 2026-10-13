# TripTracer V1 – Baugruppe 01: ACC/BAT+-Mikrorelais und Selbsthaltung

**Stand:** 13.10.2026 · **Entwurfsstufe:** Kandidaten-/Schnittstellenprüfung, **nicht elektrisch, ERC-/DRC- oder Automotive-freigegeben**.

**Quelle der Entscheidungen:** [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md), insbesondere PWR-02/05/09/10/16/19–24/34–36 und HW-82–86. Die Schaltung in `hardware/kicad/01_Eingangsschutz.kicad_sch` enthält derzeit **nur Planungshinweise, keine angeschlossenen Symbole**. Diese Notiz darf nicht als bereits vorhandener Schaltplan ausgegeben werden.

## 1. Festgelegte Anschluss- und Betriebsfunktion

**Dreipoliger M8-A-codierter Stecker:** Pin 1 = **ACC / geschaltetes Zündplus**, Pin 3 = **GND**, Pin 4 = **BAT+ / Dauerplus**. Beide Plusadern **im Fahrzeug jeweils geeignet absichern**. Die **exakte Kontaktansicht des gewählten M8-Teils** ist vor Footprint/Stecker-Freigabe zu verifizieren. Ein einziger TripTracer soll 12- und 24-V-Fahrzeuge über **9–36 V reguläre Eingangsspannung** bedienen.

Normaler Ablauf: ACC wird aktiv → kleine Relais-Ansteuerung zieht **vor dem ESP32-Boot** an → Relaiskontakt schaltet geschütztes BAT+ zum Hauptwandler → ESP32 wird versorgt und setzt `RELAY_HOLD` → bei ACC AUS erkennt ein **separater ACC-Sense-Eingang** den Zustand → Display/Leuchtringe/GNSS/Sensoren aus, FRAM/GPX/CSV/SD konsistent schließen → `RELAY_HOLD=0` → Relais öffnet → OFF.

**Nicht zu dimensionieren:** Notenergie für **komplett abgezogenen M8**, BAT+-Leitungsabriss oder Masseverlust. Dieser Fall wird auf Nutzerwunsch als Bedienfehler ohne garantierten letzten Dateischluss akzeptiert. **Motorstart-Unterspannung und Bordnetztransienten bleiben normale Konstruktionsanforderungen.**

**Manueller Standby mit ACC EIN:** per existierender Fronttaste SD-Dateien geordnet schließen, ESP32-S3 in Deep-Sleep und Peripherie aus; `RELAY_HOLD` darf dabei LOW sein, weil **ACC die Relaisansteuerung unabhängig von der MCU aufrechterhält**. Aufwecken mit geeigneter RTC-GPIO-fähiger Bestands-Taste. Bei ACC AUS im Standby öffnet Relais; nächstes ACC EIN löst einen normalen Boot aus.

## 2. Vorgeschlagene funktionale Versorgungsstruktur (noch keine Netzliste)

```text
M8 Pin 4 BAT+ --- Fahrzeug-Sicherung --- Eingangs-TVS / Verpolschutz
                                                  |
                                                  +--> geschuetzte BAT_AUX
                                                  |       |
                                                  |       +--> 5V_AUX-Buck (immer an)
                                                  |                    |
M8 Pin 1 ACC --- HV-sicherer ACC-Sense/Treiber ----+                    +--> 5V Relaisspule
                                                  |                         mit Low-Side-NMOS
ESP32 RELAY_HOLD --- Pulldown --- Watchdog/Timeout-+-[OR/Treiber] ----------^
     (nur aktiv, wenn Fahrzeugmodus zuvor ueber ACC aktiviert wurde)
                                                  |
BAT_AUX ------ NO-Kontakt Mikrorelais ------------+--> eFuse/Inrush/OVP --> 5V-MAIN-Buck
                                                                         |
                                                                         +--> 3V3 MCU/FRAM/SD
                                                                         +--> abschaltbare
                                                                              Peripherie-Rails

USB-VBUS --> gesondert rueckspeisefest entkoppelter USB-only MCU/SD-Pfad
```

**Das Diagramm zeigt Signalfluss, nicht reale Pin-Verbindungen.** Schutzreihenfolge, eFuse-Position, zusätzliche Sicherung/Current-Limit im AUX-Zweig und ideal-diode-/USB-Quellenlogik sind noch **auszulegen**. Besonders wichtig: Relaiskontakt ist sonst unmittelbar mit **Kapazitäts-Einschaltstoß, DC-Lichtbogen und Automotive-Pulsen** konfrontiert; eFuse **hinter dem Relais schützt nicht automatisch dessen erste Millisekunden**. Relaiskontaktlast durch Anlaufwiderstand/Softstart-/Inrush-Konzept sowie reale Schaltkurven nachweisen.

**Start-Henne-Ei vermeiden:** Relaisspule darf **nicht** nur aus 5V_MAIN versorgt werden, da 5V_MAIN erst **hinter** dem noch offenen Relais existiert. Der kleine 5V_AUX-Regler ist deshalb ein bewusst eingeplanter, batterieseitig immer verfügbarer Versorgungspfad. Im OFF verbraucht er ausschließlich eigenen IQ und die übrigen Wake-/Schutzschaltungen, **keinen kontinuierlichen Relaisspulenstrom**.

**Failsafe:** ACC-High darf das Relais immer starten. Nach ACC-Low darf `RELAY_HOLD` es nur während des geplanten Dateischlusses halten; MCU-Hänger oder festhängender HOLD-Pin darf **keine unbegrenzte Batterieentladung** ermöglichen. Ein **hardwareseitiges Zeit-/Heartbeat-Gate**, getrennt vom bloßen GPIO-Pegel, muss nach konkreter Bauteilwahl ausgelegt werden. Ein reiner RC-Kondensator an der Spule oder ein Firmware-Timeout allein zählt **nicht** als nachgewiesener Watchdog. Ein zusätzliches `VEHICLE_MODE_ARMED`-Interlock muss ein Aktivieren des Relais durch USB-only-Service verhindern.

## 3. Geprüfte Bauteilkandidaten; ausdrücklich noch keine Freigabe

| Aufgabe | Kandidat und Quellenstatus | Eckdaten und Vorteil | Ausstehende Prüfungen |
|---|---|---|---|
| Mikrorelais **RLY101** | **Omron G6S-2F DC5**, **LCSC C16707**, **JLCPCB Extended** ([JLCPCB](https://jlcpcb.com/partdetail/OmronElectronics-G6S_2FDC5/C16707), [Omron-Datenblatt](https://components.omron.com/eu-en/asset/datasheet_pdf/K093-E1.pdf)) | SMD 14,8 × 7,3 × 9,2 mm, Spule **5 V, 178 Ω, 140 mW**, Kontakt **2 A bei 30 VDC ohmsch**, **220 VDC maximale Schaltspannung**, Umgebung −40 bis **+85 °C**; 2 Wechsler, davon vorläufig ein Schließerkontakt erforderlich. | **Kontakt-Strom-Spannungs-Produktkurve** bei 36 V und tatsächlicher Einschalt-/Kondensatorlast, DC-Lichtbogen, Kontaktlebensdauer, −40/+85 °C, Vibration und Footprint-Padnummern. +85 °C Umgebungsgrenze muss zum geschlossenen ASA-Gehäuse passen. |
| Kleinere Relaisalternative | **Omron G6K-2F-Y-DC5**, **LCSC C326376**, **JLCPCB Extended** ([JLCPCB](https://jlcpcb.com/partdetail/OmronElectronics-G6K_2F_YDC5/C326376), [Omron](https://www.fa.omron.co.jp/product/item/G6K-2F-Y_DC5/)) | SMD **10 × 6,5 × 5,2 mm**, Spule **5 V / ca. 100 mW**, **1 A bei 30 VDC ohmsch**. | **Für V1 nicht erste Wahl**: nur **+70 °C**, geringere Kontaktreserve. Vergleich dient der Budget-/Baugrößenbewertung, nicht als freigegebener Footprint-Ersatz. |
| Immer aktiver Spulenregler **U_AUX** | **TI LM5164QDDARQ1**, **LCSC C2072225**, JLCPCB-Basic-/Extended-Status **ungeprüft** ([TI](https://www.ti.com/product/LM5164-Q1/part-details/LM5164QDDARQ1), [LCSC](https://www.lcsc.com/product-detail/C2072225.html)) | **AEC-Q100**, 6–100-V-Buck, bis 1 A, **10,5 µA typ. no-load-IQ**, Power-SOIC 8 (1,27-mm-Pinabstand), für handlötorientierten Aufbau günstiger als kleine QFN; Ausgang **auf 5 V auszulegen**, konkrete Induktivität/FB/Netzwerk noch offen. | **Keine fertige 5V-Auslegung**: TI-Anwendungsdaten, Pinout, Loop-/Ripple-Netzwerk, 6–9-V-Start, EN/PGOOD, Strom/EMV/Thermik, Gesamt-Ruhestrom und JLCPCB-Verfügbarkeit prüfen. 100-V-Eingang ersetzt keine Eingangstransientenfreigabe. |
| Kompakter Spulenregler-Vergleich | **TI LMR36506MSC5RPERQ1**, **JLCPCB C1882564**, **Extended**, als Fundstelle **ohne Lagerbestand** ([JLCPCB](https://jlcpcb.com/partdetail/1973384-LMR36506MSC5RPERQ1/C1882564)) | Fester 5-V-Ausgang, 3–65 V, 600 mA, 4 µA typ. IQ, **VQFN-9 2,1 × 2,1 mm**. | QFN wesentlich schlechter handlötbar, **65-V-Grenze** stellt höhere Anforderungen an Automotive-TVS; Preis-/Lieferfähigkeit gegen LM5164-Q1 prüfen. Noch **keine Entscheidung**. |
| Spulenschalter und Freilauf | Logikpegel-N-MOSFET + geeignete Freilauf-/Klemmdiode, 1206-Passive soweit sinnvoll | Schaltet voraussichtlich **28,1 mA** Spulenstrom; GPIO übernimmt nicht den Spulenstrom. | Reale Typen, Gateschutz, Ausgangs-/Eingangsspannungen, Induktions-/Abfallzeit sowie Hysterese und sichere Pulldowns bestimmen. |
| Hardware-Timer / Watchdog | **Funktion erforderlich, Bauteil noch offen** | Nach ACC AUS kein unbegrenztes HOLD bei Firmware-Blockade; zulässige Zeitspanne anhand SD/FRAM-Worst-Case. | Ob eigenständiger Watchdog/Monoflop oder andere fehlersichere Logik mit geringer BOM/Bestückungszahl besser ist; Boot-/Deep-Sleep- und USB-only-Interlocks prüfen. |

**BOM-Hinweis:** Diese Bauteile sind **Designkandidaten und noch nicht als bestückte bzw. eingezeichnete V1-Bauteile in der 21-Positionen-BOM enthalten**. Kein erfundener Preis, Hersteller-Pinout oder angeblich bestandener KiCad-ERC. Prüftag der oben verlinkten Angebotsdaten: **13.10.2026**; JLCPCB-Kategorien und Lager vor der Bestellung aktualisieren.

### Belastungs-Vorabschätzung (kein Test)

- **Spule G6S:** `I = 5 V / 178 Ω = 28,1 mA`, `P = 5²/178 = 0,140 W`. Bei ca. **85 % angenommenem** 5-V-AUX-Wirkungsgrad entsprechen **12 V ungefähr 13,8 mA** und **24 V ca. 6,9 mA** Batteriestrom, jeweils **nur für die Spule und noch ohne Regler-Verlust-/Ruhelastanteile**.
- **Kontakt (ungünstige Auslegungsannahme, nicht Messung):** 5V_MAIN **2 A = 10 W**, bei konservativ angenommenen **85 % Hauptbuck-Wirkungsgrad** etwa **1,31 A bei 9 V** und **0,327 A bei 36 V**. Zu beachten sind Spulen-Zweig, Einschaltstrom der Eingangskondensatoren und Kontakt-Worst-Case-Kurve; **2 A @ 30 VDC ohmsch ist keine pauschale Freigabe für beliebige 36-V-Kondensatorlast**.
- **OFF-Ruhestrom:** LM5164-Q1 **10,5 µA ist ein typischer IC-Datenblattwert**, **kein gemessener TripTracer-Gesamtruhestrom**. Die Batterie sieht außerdem Spannungsteiler, TVS-/Schutzleckströme, AUX-FB-/Spannungsreglerverluste und Wake-Schaltung. Das Ziel ist **deutlich unter 1 mA im OFF**, erst nach Messung als erreicht deklarieren.
- **ACC-Standby:** Relais bleibt wegen ACC angezogen. Deep-Sleep senkt MCU-/Peripherielast, aber Spulenversorgung benötigt weiterhin etwa **0,14 W plus Wandlungsverluste**. Kein microampere-Standby des Gesamtsystems behaupten.

## 4. Schnittstellenvertrag zu anderen Baugruppen

| Netz/Funktion | Quelle / Ziel | Verbindliche Eigenschaft |
|---|---|---|
| `BAT_RAW` | M8 Pin 4 → Sicherung, Schutz | Unabhängig von ACC immer vorhanden; 9–36 V, Automotive-Schutz vor empfindlicher Elektronik. |
| `ACC_RAW` / `ACC_SENSE` | M8 Pin 1 → HV-tauglicher Sense + Relais-Starttreiber | Nur Steuersignal, nicht 2-A-Geräteversorgung; Pin darf bei ACC AUS keine Rückspeisung erhalten. |
| `GND_VEHICLE` | M8 Pin 3 → geeigneter Stern-/Rückstrompfad | Gemeinsamer Bezugspegel, Schutzführung und Relais-/Buck-Rückstrom sorgfältig planen. |
| `5V_AUX` | always-on-Buck aus geschütztem BAT+ | Nur Relaisspule/Low-IQ-Wake-/Schutzlogik; keine unnötige GNSS/SD/ESP-Dauerlast. |
| `RELAY_HOLD` / `RELAY_WDI` | ESP32 → Timer/Low-Side-Treiber | Nach Boot aktiv setzen, vor Dateischluss nicht löschen, beim Deep-Sleep an ACC EIN keine dauerhafte HOLD-Ausgabe nötig; GPIO muss boot-/sleep-sicher sein. |
| `BAT_SW` | Relaiskontakt → Geräte-eFuse/5-V-Hauptbuck | **Nicht direkt auf USB/5 V/3,3 V**; Kontakt-Inrush und Lastspitzen schützen. |
| `USB_VBUS` | separater USB-C-Pfad → 3V3/SD-Service | USB-only-MSC/ROM-Flash weiterhin möglich; darf weder BAT_SW noch Spule/Relais einschalten. |
| `3V3_MAIN` / `5V_MAIN` | aus geschütztem Gerätpfad → Controller/Lasten | Stabil bis FRAM-/SD-Dateischluss, abschaltbare GNSS/TFT/Sensor/LED-Rails; keine ungesteuerten Backfeed-Pfade. |

## 4a. KiCad-Schaltplan-Teilstufe a1 – Relais und Spulentreiber

**Neue Dateien (13.10.2026):** Das bisher leere Blatt `01_Eingangsschutz.kicad_sch` enthält nun **K101 Omron G6S-2F DC5 (Pin 1 Spule+, 12 Spule−, 4 COM_A, 5 NO_A), Q111 Diodes DMN2056U-7 (Gate 1 / Source 2 / Drain 3), D111 SS36-Freilauf und R111 100-kΩ-Gate-Pulldown**. Das G6S-SMD-Footprint `Tripmaster.pretty/RLY101_Omron_G6S_2F.kicad_mod` ist aus der **Omron-Padzeichnung, Top View** erzeugt: Pad-Spalten −5,08/0/+2,54/+5,08 mm, Pad-Reihen −4/+4 mm, acht 1×2,2-mm-Pads. Der eigene `TripTracer_V1.kicad_sym` enthält **G6S_2F_DC5** sowie zusätzlich **LM5164_Q1** als Referenzsymbol mit TI-geprüften IC-Pin-Nummern 1–8 und EP. **LM5164 noch NICHT als elektrischer Schaltplan/Footprint implementiert.**

Die Teilbeschaltung besitzt absichtlich **offene Schnittstellen**: `5V_AUX_COIL`, `RELAY_ENABLE_5V` (Logikausgang aus noch zu bauender ACC-/HOLD-/Failsafe-Verschaltung), `BAT_PROTECTED_BEFORE_RELAY`, `BAT_SW_BEFORE_EFUSE`. Die DC-Schutzkette sowie MCU-/USB-Versorgung sind weiter OFFEN; diese Zwischenstufe darf **nicht** als funktionierendes Einschalt-/Shutdown-System oder bestandenes ERC bezeichnet werden.

**Nächster qualitätskritischer Schritt:** LM5164-Q1 als vollständigen 5V-AUX-Buck mit Feedback-/Ripple-Injektionsnetzwerk nach TI auslegen, dann 9–36-V-ACC-Detektor und HARDWARE-HOLD-Timer dimensionieren und in dasselbe Blatt einfügen; anschließend Schnittstellen, Footprints und **echten** KiCad-10-ERC prüfen. Derzeit **keine native KiCad-10-Öffnungs-, ERC- oder DRC-Prüfung**, kein getesteter 36-V-Inrush-/Kontaktlebensdauernachweis.

### AUX-Regler als hierarchisches KiCad-Schaltplanblatt – Vorentwurf a1.1

Die neue Unterseite `01A_AUX_5V.kicad_sch` ist **über das bestehende 01_Eingangsschutz-Blatt verlinkt**, also in KiCad 10 als Teil desselben Gesamtprojekts navigierbar. `U201` ist der LM5164-Q1, mit Pin 1 GND, 2 VIN, 3 EN, 4 RON, 5 FB, 6 PGOOD (absichtlich offen), 7 BST, 8 SW, **9 Exposed Pad** (im Symbol elektrisch auf GND). Das EP-Symbol wurde von `EP` auf padnummerierbares `9` korrigiert; **das finale thermische Pad und sein Land Pattern sind noch anhand der konkreten TI-DD[A] Zeichnung zu bestimmen**.

**Berechnete Vorabwerte** (TI SNVSB51C, 2025):
- `R203` 43,2 kΩ zwischen RON und GND: `f≈ 5×2500/43,2 = 289 kHz`, ideale Gleichung (15), tatsächliches Minimum-On-Time und VIN beachten.
- `R201` 316 kΩ / `R202` 100 kΩ: `VOUT≈1,2×(1+316/100)=4,992 V`, Gleichung des FB-Teilers. **Erst nach Ripple-/Last-Simulation als Sollwert freigeben.**
- `L201` **68 µH ausschließlich als Kandidat**, Saturationsstrom >=1,75 A des LM5164-Q1 Peak-Limits erforderlich, und DCR/Temperatur/Bauhöhe/Gehäuse noch offen. Ohne freigegebenen Footprint.
- `C201/C202` je 2,2 µF 100 V X7R (1210), `C204/C205` je 22 µF 16 V X7R (1210), `C203` Bootstrap 2,2 nF 50 V, R204/C206/C207 als **Type-3-Ripple-Injection**: SW→180 kΩ→AUX_RAMP→3,3 nF→5V_OUT; AUX_RAMP→100 pF (C0G)→FB. Elektrolyt-/Dämpfungspflicht erst aus Leitungslängen/EMV bewerten; das ist **kein großer 3-s-Shutdown-Puffer**.
- **Rechnerische Rippleabschätzung nur grob:** `tON≈VOUT/(VIN×f)`. `ΔV_FB≈tON×(VIN−VOUT)/(R204×C206)`: bei 9 V etwa 12,8 mV und bei 24 V etwa 22 mV; TI empfiehlt typ. 20 mV, mindestens 12 mV bei minimalem VIN. Teiletoleranzen und DCM/Light-Load-Verhalten bei lediglich 28 mA Spulenstrom bleiben offen.
- **Hardware-Schnittstelle:** `BAT_PROTECTED_BEFORE_RELAY` von vorgeschaltetem KFZ-Schutz → V_IN AUX (immer aktiv). `5V_AUX_COIL` → K101-Spule; keinerlei USB-Rückspeisung. `AUX_SW`, `AUX_RON`, `AUX_BST`, `AUX_FB` und `AUX_RAMP` sind innerhalb dieser Teilseite benannte elektrische Netze mit symbolischen Pads und Wire-Stubs. Die Haupt-GND-Netze sind gemeinsam.
- **NICHT fertig:** Vollständige Verpol-/TVS-geschützte BAT+-Quelle, ACC-Erkennung, HOLD-/Hardware-Timeout, eFuse/Relaiskontakt-Stoßstrom, Bauteil-Footprints U201/L201, nativer ERC, mechanischer/thermischer Layoutnachweis und Messungen fehlen. Die Vorgabe für <=100 µA gesamten BAT+-Ruhestrom ist ein **Wunschziel**, kein gemessener Wert. PGOOD und USB-Pfade sind separat zu prüfen.

### 01B – ACC-Einschaltstufe + galvanisch entkoppelter HOLD-Steuereingang (Teilstufe a2, 13.10.2026)

**KiCad-Datei:** `hardware/kicad/01B_ACC_WAKE.kicad_sch`, als Schwesterunterseite von 01A im vorhandenen Schaltplanblatt `01_Eingangsschutz.kicad_sch`. 9 Symbolinstanzen Q301 MMBT5551 NPN (LCSC C408396), Q302 MMBT5401 PNP (LCSC C408397), R301–R304 in 1206, C301 10 nF/1206, D301/D302 BAT54WS Schottky (C5251553, SOD323). Diese Kandidaten sind JLCPCB **Extended**, nicht Basic; Lager-/Preise erneut bei Bestellung prüfen. Q- und D-Footprints sind projektlokal, ihre endgültige Hersteller-Fertigungspadprüfung und 3D-Modelle fehlen.

**ACC-Pfad:** Geschütztes `ACC_PROTECTED_IN` → R301 220 kΩ → Basis Q301 mit R302 220 kΩ/10 nF nach GND. ACC=EIN zieht Q301 seine Kollektorseite gegen Masse; über R303 47 kΩ wird Q302-PNP eingeschaltet (R304 220 kΩ zieht Basis bei ACC AUS auf 5V_AUX); Q302 speist durch D301 den Relais-Enable-Eingang `RELAY_ENABLE_5V`. In der OFF-Stellung ist Q301 aus, Q302 gesperrt; **anders als bei einem permanent niedrigen NPN-Kollektor mit 10-kΩ-Pullup wird kein ständiger 5-V-Pull-up verheizt**. Die Verbraucher im OFF sind primär AUX-Buck, Protection, Leckströme und Rückspeisepfade; <100 µA gesamter BAT+-Ruhestrom ist **nicht nachgewiesen**.

**Vorläufige Ströme:** bei ACC=9 V und VBE≈0,7 V `I_R301≈(9−0,7)/220k=37,7 µA`; bei ACC=36 V ca. `160 µA`. R303 kann beim Einschalten mit 5 V AUX einen PNP-Basisstrom in der Größenordnung `(5−0,7)/47k ≈ 91 µA` liefern; die eigentliche D301-Gatelast setzt sich aus vorhandenem 100-kΩ-Pulldown R111 und MOSFET-Gate-Ladung zusammen. **Temperatur-, Transistor-Gain-, Gleichrichter-Dioden- und 9-V-Grenzfälle sind noch nicht simuliert oder gemessen.**

**HOLD-Pfad:** D302 verbindet `HOLD_TIMER_GRANTED_3V3` mit dem Gate-Enable **als Diode-OR mit dem ACC-Pfad**. Dieser Eingang ist derzeit **absichtlich unbeschaltet**: Er darf später **nur** von einem zusätzlichen, bei ausbleibenden MCU-Heartbeats auslaufenden Hardwaretimer/Watchdog **mit einem BAT_SW-ARMed-Interlock** gespeist werden. Keine direkte Verbindung von HOLD zu einem rohen ESP-GPIO, sonst wäre endlose Relaisselbsthaltung und unerlaubter USB-only-Start möglich. Die nächste Baugruppe ist deshalb der **reale, verifizierte HOLD-Failsafe und ACC-/BAT+-Frontendschutz**, nicht ein frei erfundener 555-Wert.

**Einzusetzende Produktquellen:** [MDD MMBT5551 Datenblatt](https://datasheet.lcsc.com/lcsc/2411211939_MDD-Microdiode-Semiconductor-MMBT5551_C408396.pdf), [MDD MMBT5401 JLCPCB](https://jlcpcb.com/partdetail/397622-MMBT5401/C408397), [MDD BAT54WS](https://jlcpcb.com/partdetail/5968241-BAT54WS/C5251553), [DMN2056U Spezifikation VGS=2,5V](https://www.diodes.com/part/view/DMN2056U). Dioden maximal 30 V rückwärts ausschließlich im 5-V-/3,3-V-Logikpfad verwenden; ACC selbst muss durch Automotive-Schutz und 220-kΩ-Eingang vor hohen Transienten gesichert werden.

**Elektrischer/Prüfstatus:** Zeichnung plus statische Symbol-/Netz-/S-Expression-Prüfung, **kein KiCad-ERC/DRC, keine SPICE-Simulation und kein Hardware-Nachweis**; Eingangsschutz, Interlock, Wake-up-/Timeout-Baustein, Batterieleitungs-/Spannungs-Priorisierung und Hauptkontakt-Inrush weiterhin offen.

### 01C – Hardware-Timeout als unabhängige maximale Relais-Nachlaufzeit (Teilstand a3, 13.10.2026)

**Neue KiCad-Seite:** `hardware/kicad/01C_HOLD_TIMER.kicad_sch`, als Unterblatt der Eingangsschutz-Seite neben `01A` und `01B`. Bauteile `U501` **TI TLC555-Q1 SOIC-8** (GND 1, TRIG 2, OUT 3, RESET 4, CONT 5, THRES 6, DISCH 7, VDD 8), `U502` **TI SN74LVC1G08-Q1 SOT-23-5** (A1/B2/GND3/Y4/VCC5), `R501`–`R504`, `C501`–`C505`, `D501/D502` Klemm-Schottkys. Die Symbole sind in der portablen Projektbibliothek, zwei lokale (vorläufige) Footprints sind vorhanden. `R305=100 kΩ` auf Seite 01B zieht den ACC-Treiber-Ausgang bei Zündung AUS nieder, damit die Flankenkopplung einen eindeutigen Zustand sieht.

**Hardware-Funktion:** `ACC_DRIVE_5V` fällt bei Zündung AUS → `C502=10 nF` koppelt eine **kurze negative TRIG-Flanke** ein, `R502=100 kΩ` zieht TRIG innerhalb ~1 ms wieder auf 3,3 V. `D501/D502` begrenzen Überschwinger auf die Logikschienen. **TRIG MUSS wieder High werden**, sonst kann ein 555-Monoflop die nominelle Zeit unbegrenzt verlängern. `TLC555-Q1` wird **nur aus geschalteten `3V3_MAIN` gespeist**, damit im Fahrzeug-OFF kein 555-Ruhestrom fließt. `RESET` mit R503/C503 hat eine Startup-Entprellung. `THRES/DISCH` am Timing-Netz `TIMER_RC`; `R501=2,2 MΩ` nach 3,3 V und `C501=10 µF/16V X7R` nach Masse. Zeitformel `t=1,1·R·C=24,2 s NOMINAL`; **MLCC-Kapazitätsverlust durch DC-Bias, Toleranz und Temperatur** kann das Zeitfenster bedeutend verkürzen, Leckstrom bei 2,2 MΩ verlängern/verfälschen. Erst nach Messung der minimalen/ maximalen Dauer ist der Timer eine belastbare Schutzschaltung.

`U502` bildet `HOLD_TIMER_GRANTED_3V3 = HOLD_TIME_WINDOW AND MCU_HOLD_REQ` und speist über die bereits vorhandene Diode D302 von 01B die Relay-Freigabe Q111. MCU muss **HOLD_REQ bereits während des regulären ACC-Betriebs HIGH setzen**, damit die Schaltflanke schnell überbrückt wird; nach erfolgreichem FRAM-/FAT32-/SD-Abschluss zieht sie HOLD_REQ LOW. Bei festhängendem HIGH begrenzt das Monoflop die Nachlaufzeit. **Das ist ein Hardware-Maximalzeitgeber, kein heartbeat-basierter Watchdog**. Vorteile gegenüber TPS3431-Q1 mit latch-basiertem Fehlergedächtnis: SOIC-8 handlötbar, weniger Logik-/Reset-Sonderfälle, bei ACC-Fahrbetrieb selbst stromlos abschaltbar.

**Status / Risiken:** Vor PCB-Freigabe **native KiCad/ERC**, echte Hersteller-Pad-/Thermalprüfungen, SW-/MCU-HOLD-GPIO, Reset-, ACC-Flatter- und USB-Stromquellenfälle sowie TRIG-Clamp-/Spannungsreihenfolge testen. BJT-Transistoren, Timer, Gate und Relais sind nur Teilschaltung; **der Schutz von ACC/BAT+ (TVS, Reverse Polarity, eFuse) fehlt weiterhin**. Schaltung ist derzeit nicht in hardware gemessen. Bauteilvarianten LCSC/JLCPCB Basic/Extended **nicht verifiziert**; keine geschätzten Preise als Beschaffungsfreigabe.
 
Quelle: [TI TLC555-Q1 Produkt und Datenblatt](https://www.ti.com/product/TLC555-Q1), [TI SN74LVC1G08-Q1](https://www.ti.com/product/SN74LVC1G08-Q1).

### 01D – Kfz-Eingangsschutz als neue Schaltplan-Baugruppe (Status: offen)

Der herstellerbasierte 20-polige **TPS26631-PWP-Symbolkandidat** ist als `U401` auf dem neuen KiCad-Unterblatt [01D_INPUT_PROTECTION.kicad_sch](../hardware/kicad/01D_INPUT_PROTECTION.kicad_sch) enthalten, jedoch **noch absichtlich nicht elektrisch verbunden**. Bevor eine sichere Eingangsversorgung aufgebaut wird, müssen der in [INPUT_PROTECTION_DESIGN_REVIEW.md](INPUT_PROTECTION_DESIGN_REVIEW.md) beschriebene separate Always-on-AUX-Schutz, das externe TPS26631-Reverse-BLOCKING-FET-Paar und das 24-V-Load-Dump-Profil dimensioniert werden. **Ein SMD-eFuse-IC allein ist noch kein Verpol-/Surge-Schutz.** Die TPS26631-Schaltschwellen (36-V-Dauerbetrieb!), Relaiskontakt-Inrush und der 12-V-Kaltstart bleiben Prüfungssperren. **Kein ERC/DRC/Hardwaretest ausgeführt.**

## 5. Abnahme-Gates – vor dem nächsten Baugruppenblatt

1. **Kontakt-/Relaisdaten**: G6S-2F DC5 **Schaltkurven**, Pin-Nummern/SMD-Footprint, Spulen- und Kontaktbelastung bei −40 bis +85 °C, Vibration, Real-Inrush, Dauerstrom und 36-V-Öffnen anhand Herstellervorgaben prüfen.
2. **AUX-Buck**: LM5164-Q1 5-V-Schaltung **vollständig** aus TI-Anwendungs- und Datenblattwerten auslegen, nicht frei erfunden; beide Plusleitungen und 100-V-/65-V-Grenzen unter Automotive-Pulsen dimensionieren.
3. **Boot/HOLD/Standby**: ACC-Hardware-Start unabhängig vom ESP; MCU-HOLD vor realem ACC-Ausfall gültig; Tiefschlaf/Wake-Taste auf sicherem RTC-GPIO; kein endloses HOLD bei MCU-Ausfall; kein USB-only-Selbststart des Fahrzeugs.
4. **eFuse/Relaiskontakt**: Relais vor eFuse nur zulassen, wenn Kontakt-Einschaltlast tatsächlich geschützt ist. Überstrom, Verpolung, TVS/Load-Dump und Eingangskondensatoren mit realen Bauteilen dimensionieren.
5. **Schaltplan**: Erst danach `01_Eingangsschutz.kicad_sch` mit korrekten KiCad-10-Symbolen, vollständigen Verbindungen, verifizierter Padnummerierung und herstellerbasierten Footprints erstellen. **Native ERC, projektweite Netz- und Kompatibilitätsprüfung** ausführen, sofern KiCad installiert/verfügbar; andernfalls **„nicht ausgeführt – Gate offen“**.
6. **Hardwaretest**: ACC EIN/AUS, ACC-Flattern, Wiederstart, M8+USB, 9/12/24/36 V, Motorstart/Brownout, Temperatur, SD-Timeout, manueller Standby und gemessener BAT+-OFF-Ruhestrom. Vollständiger M8-Abzug nur als **nicht abgesicherte Fehlergrenze** protokollieren.

**Nächster freizugebender Teil:** Relaiskontaktschalter samt Ansteuerung und immer aktiver AUX-5-V-Spulenversorgung. **Noch nicht** die gesamte Eingangs-/USB-/Regler-Baugruppe gleichzeitig als „fertig“ markieren.
