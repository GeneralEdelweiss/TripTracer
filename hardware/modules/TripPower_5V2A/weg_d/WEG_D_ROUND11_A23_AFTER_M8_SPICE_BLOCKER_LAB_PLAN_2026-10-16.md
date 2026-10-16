# TripPower Weg D – Round 11: A23-Eingangstransienten nach M8, 3-Knoten-Modell, SPICE-Blocker und Labor-Gate (2026-10-16)

**Entscheidung: FALL B – OFFEN. Keine PCB-/Fahrzeug-/Serienfreigabe.** TPS26631 bleibt die sparsame Labor-Hypothese, ist für die tatsächlich installierte 58-V-/350-ms-Grenze aber **noch nicht qualifiziert**. Nicht aus dem hypothetischen Sweep auf Ausfallwahrscheinlichkeit oder auf einen zwingenden Architekturwechsel schließen. Kein LTC4368-Projekt, kein neuer Schutz-IC und keine TripPower-Fuse/Holder/Einmal-Thermosicherung.

## 1. Quellenstand und korrekter aktueller Schaltplan

Aus den tatsächlichen GitHub-Branches gelesen (nicht aus alten Chats):
- A `design/trippower-a`, HEAD `3f3dd727452d61aa894ad2f03be03af10174eeec` (Round5): A23-Eingangsblatt `hardware/modules/TripPower_REV6_A/01_TPS26631_REV6_FACTORY_OVP.kicad_sch`, BOM `REV6_A_FACTORY_OVP_23_PART_ORDER_BOM_2026-10-16.csv`, A-Round4+Round5. Das A25-Blatt ist **nur historischer Vergleich**.
- B aktueller Round10 `hardware/modules/TripPower_5V2A/weg_b/WEG_B_ROUND10_TI_300K_FACTORY_OVP_UVLO_INDEPENDENT_DECISION_2026-10-16.md` auf `design/trippower-b`. B weist selbst ausdrücklich darauf hin, dass seine Round10-Pinbelege noch den älteren A25-Stand verifiziert hatten; nicht als nativen A23-Nachweis umetikettieren.
- C aktueller Round10 `hardware/modules/TripPower_5V2A/weg_c/REV6_ROUND10_A_COMPONENTS_COST_OPTIMIZATION_2026-10-16.md` auf `design/trippower-c`; historische A25-Baseline, A23-Vorschlag damals noch nicht in KiCad. Die A23-Umsetzung wurde danach durch A-Round4 geleistet.
- D vorheriger Round10-Bericht und `FINDINGS_LOG.md` dieses Branches.
- `AGENTS.md`, `docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md`, `docs/HARDWARE_REQUIREMENTS.md` PWR-44..56, `docs/TRIPPOWER_FUSE_PLACEMENT_DECISION_2026-10-16.md`, Powerloss-Backup-Vertrag.

**Tatsächlich gezeichnete A23-Netze und MPNs** nach A23-Sheet/23er-BOM:
| Position | A23-Ausführung / elektrischer Knoten |
|---|---|
| U201 | TI `TPS26631PWPR`. **IN1–3 vor Q201 auf `EFUSE_IN`**, **IN_SYS6 nach Q201 auf `VIN_FUSED`**. Diese beiden Knoten sind NICHT identisch! |
| Q201 | Vishay `SQM100N10-10_GE3`, Drain `EFUSE_IN`, Source `VIN_FUSED`, Gate am `R6_B_GATE`, AEC-Q101 100 V, VGS ±20 V; Q202 `BSS138LT1G` an DRV/BGATE/IN_SYS. |
| U201 Pin8,7 | OVP8 direkt GND → Factory OVP; UVLO7 nur über **R201 `AC1206FR-07330KL` 330 kΩ** von IN_SYS. Kein R202/R203 im A23. |
| U201 Pin12,16 | MODE12=GND → Overload/TSD Auto-Retry; PGTH16=GND → TPS-eigenes PGOOD LOW und **keine 2×IOL-Freigabe**; dVdT10 `C203=100nF`. Überstromlimit durch R204=6.04kΩ nominell ~3 A, NICHT 0.5 A RAW-selektiv. |
| Knoten C201, C202 | C201 `C1210C105K1RACAUTO` 1µF/100V **direkt an IN_SYS**; C202 dieselbe MPN 1µF/100V an U201 OUT (`VIN_PROTECTED_UNFUSED`). |
| Buck | U101 `LMR38020SQDDARQ1`, 2× C101/C108 `12101C475K4Z2A` 4.7µF/100V plus C107 100nF am **eFuse-OUT/Buck-Eingang**, L101 `SRP7050TA-150M` 15µH. Somit liegen Buck-CIN **hinter** U201, nicht als lokaler Parallel-CIN direkt an `EFUSE_IN` oder `IN_SYS`. |

TI TPS2663 Rev G §§6.1,6.3,6.5,8.3,8.4,9.4,9.5: Factory OVP rising 33.2..35.4 V / falling 32.7..35.0 V. 32 V statisch erlaubt Recovery, sofern **IN_SYS inklusive Ringing beim Zurückkehren tatsächlich unter 32.7 V** fällt. Eine 36-V-Garantie am M8 setzt zusätzlich ausreichend geringen spannungsabhängigen Drop bis IN_SYS voraus. R201 330 kΩ mit 1 % +100ppm/K bleibt zwischen -20..+85°C mit min ca 324.72 kΩ über TI-Minimum 300 kΩ. UVLO ist damit **kein** programmierter 10-V-Under-Voltage-Schutz. Der ältere D-Round10-Befund „R201100k und ungarantierter32V-Restart“ gilt **nicht mehr für A23**.

Die aktive TripTracer-V1-Haupthierarchie enthält A23 nach A-Round5 noch nicht als integriertes Blatt. RAW0.5A-selektiver Branch-Schutz, +85°C-Ambient-Safe-Off und System-Backfeed bleiben als getrennte Integrations-Gates **OFFEN**.

## 2. Exakter 58-V-Grenzpunkt und Modellarchitektur

Physikalische Kette und Modell-Gültigkeit strikt trennen:
1. **Generator und zentrale Fahrzeugklemme**: Quelle vor Fahrzeugleitung, ihre eigene Lastdump-Klemmregelung und Generator-Ri. Bei 58 V *an M8* gehören diese Upstream-L in das Gesamtfahrzeugmodell, aber **NICHT zusätzlich als lokale Serien-L**.
2. **Fahrzeugleitung bis zur M8-Gerätebuchse**: Kabellänge/Loop-L/R, BAT+- und ACC-Sicherung sowie ihre dynamischen Spannungsabfälle durch zweikanalige M8-Messung bestimmen.
3. **M8-Kontakt und TripTracer-Hauptplatine**: Kontaktzustand, Rückleiter, Host-Schutz-/HOLD-Pfad, Steckverbinder und Kupferbahn. Diese sind nach M8 elektrisch vorhanden, genaue Werte nicht aus KiCad-Sheet allein bekannt.
4. **Host→TripPower Leitungen/Stecker**: Länge/Loop-L/R/Kontakte als **lokaler post-M8-Anteil**, mit 3. zusammen.
5. **Q201 extern Reverse-FET**: zwischen `EFUSE_IN` und `VIN_FUSED`, reale Gate-Funktion, Coss(VDS,T), VGS und Schaltzeit; Q202 an Gate-Hilfe.
6. **U201 IN1–3 versus IN_SYS6**: vor/nach Q201 getrennt. U201-A23-Hochvolt-Pins empfohlen max60V, absolute max67V. Die TPS-eFuse schützt ihren **eigenen Eingang nicht durch die nachgelagerte OVP-Abschaltung**.
7. **C201 / C202**: C201 nach Q201 unmittelbar IN_SYS gegen lokale Masse; C202 nach U201, nicht als automatisch parallel wirksamer Eingangskondensator; die unbekannten effektiven Kapazitäten plus ESR/ESL sind eigene Parameter.
8. **U101 Buck**: C101+C108+C107 hinter U201, VIN max80V empfohlen/85V abs; SW, BOOT−SW, PGND und EN jeweils separate Datenblatt-Pingrenzen.

**Neues ausgeführtes Rechenmodell:** [`tps26631_a23_after_m8_linear_nodes.py`](tps26631_a23_after_m8_linear_nodes.py), [Tests](test_tps26631_a23_linear_nodes.py). Nur **post-M8**: geregelte M8-Trail 32→58V (Anstiegszeit parametrierbar), 350ms plateau, 58→32V; R+L auf lokalen `EFUSE_IN`-Knoten mit angenommener Cpre gegen GND; Q201 als KONSTANT voll leitender Widerstand parallel zu angenommener **differenzieller Coss**, auf `IN_SYS` wirkt nur C201eff; U201-Eingangsstrom als unabhängig vorgegebene Stromlast. Differentialgleichungen für Leitungsstrom, V(IN), V(IN_SYS) als lineares Drei-Zustands-Netzwerk; stückweise lineare Quelle/Last und Matrixexponential numerisch integriert (SciPy). **KEIN TPS26631/TI-SPICE, kein realistischer Q201-Gate-Transient, keine echten eFuse- oder LMR-/OCP-Modelle, keine ESR/ESL-abhängige HF-Messung.**

Eingaben **SENSITIVITÄTSWERTE, keine belegten A23-Parameter**: nach M8 L=20/50/200nH (getrennt von Generatorleitung), R=80mΩ, Cpre=2nF, C201eff=0.2/0.5/1.0µF, Coss=655pF (Vishay Datenblatt **typ bei VDS=25V**, **nicht** bei58V!), R_Q201=20mΩ als vollständig angesteuerter FET, Anstieg0.2/1/20µs, Abfall20µs. Der in der Hersteller-PDF bei25V genannte Coss-Typ ist keine validierte nichtlineare Coss(V,T)-Kennlinie bei58V. Modellstrom wird beim Eingangsstufenschritt **nicht** durch realen Generator-/Stecker-HF-Stromlimit begrenzt. Spannungsresultate dürfen nur als hypothetische sensitivitätsbezogene Vergleichswerte genutzt werden.

**Lokal tatsächlich gerechnete Resultate (SciPy, keine Hersteller-/Hardwaremessung):**
| Hypothese (alle nach M8) | Spitze TPS-IN vor Q201 | Spitze IN_SYS nach Q201 | idealisierte Spitzenleitung |
|---|---:|---:|---:|
| Basis L50nH/R80mΩ/C201eff0.5µF/Rise1µs/eFuse zuvor OFF | 59.987V | 59.982V | 20.94A |
| Gleiche Basis, Rise0.2µs | 72.725V | ca72.7V | 61.44A |
| Rise0.2µs, Rlocal0.35Ω **nur rechnerisch** | 60.515V | näher an 60V | 38.94A |
| Rise0.2µs, Rlocal0.65Ω **nur rechnerisch** | 58.0V | nahe58V | 27.32A |
| L50nH/R80mΩ/C201eff0.5µF, Rise1µs, abgeschaltete Last1.75A nach **angenommen**14µs | 59.847V | <59.847V | 22.69A |

Zusätzlicher ausgeführter **27-Fälle-Sweep** (L 20/50/200nH × C201eff0.2/0.5/1.0µF × Rise0.2/1/20µs bei übrigen genannten Parametern und `mode=already_off`): **14/27 theoretisch >60V**, **10/27 ≥67V**. Dies sind absichtlich verschiedene Eingaben, keine empirischen Fahrzeughäufigkeiten und nicht mit Round10s 288 Passivfällen oder Round9s 144 Lastfällen statistisch zu addieren. Große errechnete Einschaltströme bis mehrere zehn Ampere zeigen gerade die Grenzen einer ideal steifen Quelle und idealen linearen Gate-/ESL-Annahme. **Weder Fall A noch C** kann daraus abgeleitet werden.

Die Varianten `mode=assumed_trip` mit selbst gewählter 14µs-Stromunterbrechung und `mode=fet_short` (durchgehend Laststrom) sind nur Laststrom-Wirkhypothesen. Letzterer emuliert einen **U201-internen Serien-FET-Short**, nicht den Q201-Drain-Source-Kurz; Q201-Short und Coss-/Gate-Änderung benötigen weitere echte Modelle. `MODE=GND,PGTH=GND` werden im Python-Netz nicht physikalisch hergeleitet: TI sagt Auto-Retry und PGOOD-LOW/kein 2×IOL-Betriebsmodus, aber nicht, dass Kurzschlussstromspitzen stets ≤3A sind. Dies ist gerade ein Labor-/Hersteller-SPICE-Gate.

### Auswirkungen der passiven Dämpfung

Für das einzelne effektive L50nH/C201eff0.5µF gilt als **grobe Zweipol-Näherung** `Rcrit=2 sqrt(L/C)=0.632Ω`. Diese Näherung trifft weder Cpre/Coss noch parasitäre zweifache Knoten exakt. Mehr **Serien-R** reduziert die modellierte 0.2µs-Spitze, ist aber **keine Teilempfehlung**: 0.65Ω würde bei 10V/1.75A ca1.14V DC abfallen und ca2.0W erwärmen, den 10V-Start gefährden; Kontaktalterung darf nicht als Dämpfer eingeplant werden. **Zuerst** Induktivität und lokale Stromschleifen minimieren, C201-Ceff/ESL/Coss belegen; bei Bedarf gezielt RC-Snubber ohne permanenten hohen DC-Durchlass-R. Größenordnung eines allein auf L/C basierenden Serien-R für ein lokales Snubber-C wäre ~sqrt(L/C)=0.316Ω, aber **Snubber-C, RMS-/Pulsleistung, Ladeenergie, ESR und Wirksamkeit zwischen IN und IN_SYS sind NICHT aus diesem Sweep dimensioniert**. Solange der reale HF-Verlauf unbekannt ist, keine unqualifizierten zwei neuen 100V-Bauteile verpflichtend hinzufügen. Kleine TVS erst nach nachgewiesenem `V_C(I,T,t)<` zulässiger **Pin**-Grenze mit Unsicherheit, Pulsenergie/Follow-on/Failure-Mode; eine übliche 58V-TVS hat keine automatische <60V-Klemme.

### Fehlende belastbare Ceff/ESR/ESL-Daten

C201/C202 `C1210C105K1RACAUTO` und Buck-C101/C108 `12101C475K4Z2A` sind wirkliche A23-MPN. **Keine originalen temperatur- und spannungsaufgelösten DC-Bias-Kurven dieser MPN bei58V in einer hier tatsächlich lesbaren und dokumentierbaren Form gewonnen**; deshalb keine erfundenen numerischen Ceff- oder ESR/ESL-Werte. KEMET/KYOCERA AVX herstellerseitige Sim-/SPICE-/Bias-Datenblatt-Tools oder Vierleitermessung mit DC-Bias und Tieftemperatur/Hot-Losen erforderlich. Ebenfalls Coss(VDS,T) für Q201 und Q202 Ciss/Coss prüfen. Bei sehr schnellen Flanken können die verwendeten quasi-konstanten C und die fehlenden ESL/Gatepfade das Ergebnis stark ändern.

## 3. Originales TI-TPS2663-PSpice: konkreter reproduzierbarer Blocker

- TI selbst listet **TPS2663 PSpice Transient Model (Rev. A)** `SLVMD03A.ZIP` ca317KB, https://www.ti.com/lit/zip/SLVMD03 und https://www.ti.com/product/TPS2663.
- **In dieser Sitzung erneut geprüft:** Direktabruf der ZIP im Web-Textwerkzeug → kein nutzbarer Binärinhalt; im Container `requests.get('https://www.ti.com/lit/zip/SLVMD03')` → `ConnectionError: NameResolutionError ... Failed to resolve 'www.ti.com'`; derselbe DNS-/Netzzugangsfehler für GitHub raw. Binärdatei fehlt, darum **kein Original-Hash und kein extrahiertes .LIB/.CIR/.OLB**, **keine identifizierte .SUBCKT-TPS26631-Variante**, **kein Pinmapping aus Originalmodell**, **kein Parser-/Konvergenz-Log**. `command -v ngspice` und `command -v kicad-cli` liefern in dieser Ausführungsumgebung keinen Pfad. Dass ngspice das TI-Modell tatsächlich ablehnen würde, ist **NICHT nachgewiesen**.
- TI bewirbt [PSpice for TI](https://www.ti.com/tool/PSPICE-FOR-TI) als Windows-/Cadence-OrCAD-Capture-basierte Simulationssuite **nach Antrag/Installation**; nicht bereits auf GitHub-hosted Linux/Windows-Runnern installiert. `apt-get install ngspice` auf Linux-GitHub-Actions grundsätzlich als Container-/Runner-Testpfad geeignet, aber keine PSpice-Kompatibilität ohne die Original-.LIB behaupten; GitHub-Windows-Runner mit interaktiv zu registrierendem Hersteller-Tool nicht als autonom nachweisbar annehmen. Selbst gehosteter rechtmäßig lizenzierter Windows-Runner ist ein möglicher, noch nicht ausgeführter Pfad.
- **Reproduktion auf autorisiertem internetfähigen Windows-PC:**
  1. `Invoke-WebRequest -Uri 'https://www.ti.com/lit/zip/SLVMD03' -OutFile SLVMD03A.zip` (ggf. Browser-Download mit TI-Cookies). Prüfen, dass ZIP gültig, Produkt TPS2663 Rev A, Dateigröße und Header stimmen.
  2. `Get-FileHash .\SLVMD03A.zip -Algorithm SHA256`; `Expand-Archive .\SLVMD03A.zip -DestinationPath .\ti_model`; Dateiliste, Original `*.LIB/*.CIR/*.OLB/*.OPJ` und `.SUBCKT`-Zeilen protokollieren.
  3. Die tatsächliche **TPS26631**-Variante, Modell-Pinreihenfolge und die offizielle **Hersteller-Referenztestschaltung** aus den extrahierten Dateien ermitteln, über Pin-Labels des KiCad-A23 (IN1..3, IN_SYS, BGATE, DRV, OVP, UVLO, ILIM, dVdT, PGTH, MODE, OUT) auf realen Schaltplan abgleichen. Bis dahin **KEIN PINMAPPING erfinden**.
  4. PSpice for TI Versionsnummer, Modelldatei-SHA256, Testbench, `tstep/maxstep`, Bode/TRAN/Currentlimit/OVP-Logs und Differenz zu obigem lokalen M8-Modell zusammen mit Waveform-CSV speichern; nur falls zulässig Modellteile nach Lizenz in GitHub ablegen.
  5. Zulässigkeit der redistributierbaren TI-/Cadence-Modellinhalte **vor Commit ausdrücklich klären**. In GitHub standardmäßig nur Skript, Quellen-URL, Hash, selbst erzeugte Kurven/Protokolle; kein TI-LIB-ZIP-Commit.
- **Status: Hersteller-SPICE NICHT ausgeführt, konkreter technischer Zugriffblocker belegt.** Eine Inkompatibilität wäre erst mit originalem Parserlog ein Befund.

## 4. Praktischer Laborprüfplan (einsetzbare Testanweisung)

**Aufbau / Freigabe für Test:** Fachkundiger HV-/Automotive-Elektronikprüfstand, abgeschirmter Strompfad, Netzteil/ISO16750-2-kompatibler programmierbarer DC-Transientengenerator **mindestens 58V/350ms** und definierbare 10/32/36V, aktive einstellbare Strom- und Energiebegrenzung, Not-Aus/Remote-Abschaltung, berührungsgeschützte und gegen Lichtbogen/Überhitzung abgeschirmte Prüfadapter. Externe, quellnahe, für Gleichstrom/Kabelstrom dimensionierte BAT+- und ACC-Leitungssicherungen in geprüften Haltern; **keine Fuse/Holder/Einmal-Thermosicherung auf TripPower**. Vor Kurzschlussversuchen Aufbau bei ungefährlichem, niedrigem Spannungs-/Strom-Limit validieren; LMR, MLCC, MOSFET und Last ggf. an eine strombegrenzte Fehlerfixture statt Fahrzeugleitung hängen. `58V*5A*0.35s=101.5J` ist nur eine obere Quellen-Energieabschätzung, nicht tatsächlich im Bauteil umgesetzte Energie; Labor-Hochenergieversuche wurden **nicht durchgeführt**.

**Kalibrierung / Boundary:** Sowohl **Quellklemmen vor Fahrzeugleitung als auch M8 Pin4/BAT+-Pin3/GND differenziell zeitgleich** messen. Für 58V als garantierten *M8*-Grenzwert muss die **gesamte** gemessene M8-Wellenform inklusive HF-Ringing/Ungewissheit ≤58V bleiben; sonst Quelle/Installation außerhalb des REV6-Einschlusses und P0-Test stoppen. M8-Abschwächung/kontaktbedingter Abfall gehört in Zuleitungsdaten, **nicht noch einmal in `L_after_m8`**. Testleiter 0.5m/3m einschließlich Rückleiter als getrennte Installationsfälle; DC-Vierleiter-R und Schleifen-L (M8 zu Q201 D, Return GND, Host→Modul) mit geeigneter Frequenz und Adapter messen. Kabelkontaktzustand kalt/warm/vibriert prüfen. Tatsächliche Quellflanken 0.2/1/5/20/100µs (nur wenn technisch darstellbar) und 32→36 400ms / 32→58 350ms / 58→32 Recovery gemeinsam aufzeichnen, nicht nur Setpoint oder Generator-Frontend-Peak.

**Messmittel:** zunächst ≥100MHz-DSO, ≥500MS/s, plus auflösbare differentiell isolierte Hochvoltsonden mit überprüfter **realer** Bandbreite, Overshoot-/Common-mode- und Phasenfehler; für0.2µs und ns-HF höhere Bandbreite dokumentiert verifizieren. GND nur Kelvin an jeweiligem Pad; keine Scope-Masseklemme an BGATE, DRV, Q201-G oder SW. ≥5MHz DC-fähige Stromsonde mit Kalibrierung/Offset oder entsprechend spezifizierter Kelvin-Shunt und Sicherheits-Isolation, vor jedem Test 4-kanalige Zeitsynchronisierung, Probenkapazität und Tip-loop-Induktivität messen. Messunsicherheitsbudget `U_total=Probe/DSO+Kalibrierung+CommonMode+Ringing-Auflösung+Temperatur+Quelle+Lose` dokumentieren, konservativ nicht nur RMS kombinieren, wenn einzelne unbekannte Fehler vorliegen.

**Differenzielle Pflichtpunkte mit Signal-/Messgrenze:** M8 BAT–GND; Q201 D(`EFUSE_IN`)/S(`VIN_FUSED`)/G, **VGS und VDS**, Q202 G/D/S; TPS26631 **IN1–3 einzeln**, IN_SYS6, UVLO7, OVP8, PGTH16, MODE12, SHDN13, BGATE4, DRV5, FLT15, OUT18–20, **BGATE−IN_SYS und DRV−IN_SYS**, dVdT10, ILIM11; C201 positive/negative Pad direkt, C202 ebenso; LMR38020 VIN, PGND, SW, BOOT−SW, EN, PG, FB und C101/C108; RAW und 5V Lastströme, USB-VBUS, PWR_FAIL, FRAM-Persistenz, Modulmasse relativ M8-GND. Weitere relevante Fußnoten/Vmax erst am Herstellerdatenblatt und tatsächlichem Herstellerpinout abhaken.

**Vorläufige Datengrenzen, tatsächliche Einzel-Pin-Tabelle bleibt verbindlich:** TPS `IN/IN_SYS` empfohlen bis60V, ABS67V; BGATE-GND ABS81V / BGATE−IN_SYS ABS14V; DRV-GND ABS72V / DRV−IN_SYS ABS20V; OVP/MODE/dVdT/ILIM und SHDN-HV-fremde Pins dürfen **nicht** wie IN mit67V belastet werden; Q201 VDS100V/VGS±20V, Q202 VDS50V/VGS±20V; LMR VIN empfohlen80V/ABS85V, SW/BOOT spezifisch Datenblatt. MLCC 100V NENN, **DC-Bias-Ceff/Hot/ESR/ESL separate Gates**. Bereits empfohlenes TPS60V-Max mit Unsicherheits-/Engineeringreserve prüfen; **67V ABS ist kein freigegebener Wiederholbetriebspunkt**. Beispiel einer Prüftoleranz: nur wenn nachgewiesener vollständiger `U_total=1V`, intern `V_IN_peak≤59V` als Ziel; das ist **kein** Hersteller-Rating.

**Matrix und Reihenfolge (jede Abweichung von Hersteller-/Grenzprofil dokumentieren):**
1. Bei +25°C, RAW0 und 5V0A → RAW0.5A/5V1A/2A, 10V-Kaltstart mit worst leitungsbedingten Drops/Quelle Stromlimit; dann −20°C, +60°C 2A/RAW0.5A und +70°C derating, +85°C **aktiv sicher OFF** (hierfür fehlt derzeit der gesamte Ambient-Hardwarepfad). Tatsächliche 10V-Startspannung am **Modul** festhalten.
2. 32→36V für400ms →32, bei 0A/2A Buck und RAW0/0.5A, prüfe reale Ausgangs-Off-Zeit, Nichtschädigung, Q201-Drop, U201-IN_SYS wirklich≥Factory-OVP-Threshold und Wiederanlauf.
3. 32→58V für350ms →32, gleiche Lastfälle, Flanken-/Kabel-/Ceff-Corners; Scope triggert auf IN/IN_SYS >58.5/59/60V vorläufig, nicht allein auf Generator. **Zunächst Einzelpuls**, danach **10 Pulse mit mindestens60s Abstand oder bis Bauteiltemperaturen auf spezifiziertes Ausgangsniveau zurückkehren**. Das ist ein Engineering-Anfangsplan, keine behauptete Automotive-Standardpulszahl; größere Pulsstichprobe erst nach ersten Ergebnissen und OEM-Profil vereinbaren.
4. Beim `58→32V` Rücksprung ausreichende Factory-OVP-Hysterese überprüfen: IN_SYS-Rauschen stets <32.7V bis zum Neustart; Buck 5V-PG, Current-Inrush, PGOOD(LOW durch PGTH), PWR_FAIL-Reaktion und Auto-Retry/thermische Ruhebedingungen mit Zeitstempel dokumentieren.
5. Bei 10/32V 5V- und RAW-Zweig-Kurzschluss **getrennt** mit kontrollierten Fehlermodulen testen (Soft-/Hard-short, 0.5A RAW-Schutzziel offenes Systemgate). Bei bereits anliegendem58V-Puls zunächst OVP-OFF-Baseline; dann extern erzwungene Kurzschlussfehler **nur** unter reduzierter strom-/energiebegrenzter Testquelle, gestufter Erhöhung nach SOA-Nachweis. 58V + Gate-/FET-Kurz ist nicht automatisch mit normalen 58V-Pulsen identisch.
6. Q201-Drain–Source-SHORT und U201-interner FET-SHORT **getrennt** ersetzen/überbrücken (nur geschützte Fehlerfixture): Q201-SHORT beseitigt Reverse-Funktion und verändert die Pre/Post-Resonanz; U201-SHORT kann Buck-CIN/RAW bis58V exponieren. Separate −Polung, fehlende Masse, USB eingesteckt, HOST/PWR_FAIL-Backfeed nur unter sicherer niedriger Stromgrenze. Fehlerteile nicht live am Energieschrank überbrücken.
7. −20/+25/+60/+70°C und +85°C-OFF sowie mindestens zwei MLCC-Batches, Ceff(V,T), Loop-L/R und Coss(V,T) dokumentieren. Jedes Pulse-CSV benötigt `VIN_M8(t), V_IN1..3(t), V_IN_SYS(t), I_IN(t), OUT(t), 5V(t)` plus alle übrigen kritischen Pins in synchronisierten Wiederholungen, Setup/Bandbreite/Probe, Temperatur, DUT-Revision, Quelllimit und Pulse-ID.

**Pass/fail und Abbruch:** Ein *tatsächlich gemessener*, nach Messunsicherheitsbereinigung nachweisbar über60V liegender TPS-Betriebspunkt ist für den geplanten normalen58V-Puls ein **NO-GO ohne Layout/Dämpfung-Neuqualifikation**; ≥67V (oder irgendein anderer absolut überschrittener Pin) sofort FAIL/Abbruch. Sofort stoppen bei Hot-Retry ohne thermische Stabilität, Q202>50V, Q201 VGS>±20V, kritischem SW/BOOT-Stress, 32V-Wiederanlaufversagen, RAW-Leitungsüberlast oder unerwartetem Rückspeisen. Ein nicht gemessener Punkt bleibt **OFFEN**, nicht „PASS“. Schutzmaßnahmen nur nach quantifiziertem Mess-Gewinn ergänzen.

## 5. Nächste zielgerichtete Entscheidung

**FALL B – OFFEN** wegen fehlendem originalem herstellermodelliertem Gate/Pin-Timing, realem Q201-Coss/verschiedenem Gate-Zustand, C201eff@58V, lokalem M8→IN R/L samt Host-Topologie, echter spannungsbegrenzter M8-Quellflanke und Hardware-Kurzschluss/Temperatur-Wiederholbarkeit. Keine begründete Fall-A-Fertigungsfreigabe, aber auch kein belastbarer Fall C. A23-Prototyp mit 23 Positionen ist bis zur gezielt begrenzten Laborprüfung die **führende zu untersuchende** günstige Variante. Reihenfolge: (1) sichere post-M8-Loops/Buchse messen (2) MLCC-/Coss-Kurven und TI-Originaltestbench verfügbar machen (3) Labormessung mit vorhandener A23-Schaltung (4) falls PIN-MAX verletzt: Layout, lokale MLCC und gezielten RC-Snubber quantifizieren (5) nur wenn nicht beherrschbar, höheren Schutzcontroller samt Mehrpreis-/Positionen-/SOA-Kosten neu bewerten.

**Evidenzstatus:** lokales SciPy-Rechenmodell und 27 Sensitivitätsfälle tatsächlich gerechnet; Hersteller-Originalmodell **nicht ausgeführt**; kein physischer Hochenergie-/Fahrzeugversuch, kein KiCad10-ERC/DRC in Weg D; neue GitHub Actions nach Commit nur dann PASS, wenn Run-Job-ID/Log konkret abgefragt wird. A-natives ERC auf anderem Branch ersetzt keine P0-58V-Qualifikation.

## Offizielle Herstellerquellen

- Texas Instruments TPS2663 Datenblatt Rev G: https://www.ti.com/lit/ds/symlink/tps2663.pdf (besonders §9.5.1, Gleichung14).
- Texas Instruments TPS2663 Modell Rev A: https://www.ti.com/lit/zip/SLVMD03
- Texas Instruments PSpice for TI: https://www.ti.com/tool/PSPICE-FOR-TI
- Texas Instruments LMR38020-Q1 Rev B: https://www.ti.com/lit/ds/symlink/lmr38020-q1.pdf
- Vishay SQM100N10-10: https://www.vishay.com/docs/67027/sqm100n1.pdf
- onsemi BSS138L: https://www.onsemi.com/pdf/datasheet/bss138lt1-d.pdf
