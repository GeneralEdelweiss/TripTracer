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

## 5. Abnahme-Gates – vor dem nächsten Baugruppenblatt

1. **Kontakt-/Relaisdaten**: G6S-2F DC5 **Schaltkurven**, Pin-Nummern/SMD-Footprint, Spulen- und Kontaktbelastung bei −40 bis +85 °C, Vibration, Real-Inrush, Dauerstrom und 36-V-Öffnen anhand Herstellervorgaben prüfen.
2. **AUX-Buck**: LM5164-Q1 5-V-Schaltung **vollständig** aus TI-Anwendungs- und Datenblattwerten auslegen, nicht frei erfunden; beide Plusleitungen und 100-V-/65-V-Grenzen unter Automotive-Pulsen dimensionieren.
3. **Boot/HOLD/Standby**: ACC-Hardware-Start unabhängig vom ESP; MCU-HOLD vor realem ACC-Ausfall gültig; Tiefschlaf/Wake-Taste auf sicherem RTC-GPIO; kein endloses HOLD bei MCU-Ausfall; kein USB-only-Selbststart des Fahrzeugs.
4. **eFuse/Relaiskontakt**: Relais vor eFuse nur zulassen, wenn Kontakt-Einschaltlast tatsächlich geschützt ist. Überstrom, Verpolung, TVS/Load-Dump und Eingangskondensatoren mit realen Bauteilen dimensionieren.
5. **Schaltplan**: Erst danach `01_Eingangsschutz.kicad_sch` mit korrekten KiCad-10-Symbolen, vollständigen Verbindungen, verifizierter Padnummerierung und herstellerbasierten Footprints erstellen. **Native ERC, projektweite Netz- und Kompatibilitätsprüfung** ausführen, sofern KiCad installiert/verfügbar; andernfalls **„nicht ausgeführt – Gate offen“**.
6. **Hardwaretest**: ACC EIN/AUS, ACC-Flattern, Wiederstart, M8+USB, 9/12/24/36 V, Motorstart/Brownout, Temperatur, SD-Timeout, manueller Standby und gemessener BAT+-OFF-Ruhestrom. Vollständiger M8-Abzug nur als **nicht abgesicherte Fehlergrenze** protokollieren.

**Nächster freizugebender Teil:** Relaiskontaktschalter samt Ansteuerung und immer aktiver AUX-5-V-Spulenversorgung. **Noch nicht** die gesamte Eingangs-/USB-/Regler-Baugruppe gleichzeitig als „fertig“ markieren.
