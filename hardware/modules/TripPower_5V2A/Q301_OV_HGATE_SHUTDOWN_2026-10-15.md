> **Fortsetzung / Korrektur C303 am 15.10.2026:** Der in Abschnitt 4 genannte alte 100nF-Stand und die dort erwogene 220nF-MPN-Suche sind ÜBERHOLT. Als neuer C303-Kandidat wurde **KEMET C1206C474K1RECAUTO7210 (470nF 100V X7R AEC-Q200)** ins eigenständige KiCad-01-Unterblatt übernommen. [Neue rechnerische Auslegung, Preise, offene K-SIM-Gates](C303_CAP_VS_SELECTION_2026-10-15.md). TI fordert **max(100nF Mindestwert, 95,7nF aus 10×Ciss) = 100nF effektive Kapazität**; altes Datum im ursprünglichen Text ist nur historische Analyse.

# TripPower Q301 OV-Abschaltung und HGATE-RC – Review 15.10.2026

**Scope:** Eigenständiges `TripPower_5V2A`, `design/solid-state-power-v1`. Nutzerentscheidungen unverändert: LM74930QRGERQ1, Q301 vorläufig Vishay SQM10250E_GE3 250V AEC-Q101, Q302 BUK7Y4R8-60EX, LMR38020SQDDARQ1, 9–30V Normal, ca. 9V Startziel, 5V/2A + 1A Ziel für `VIN_PROTECTED_UNFUSED`; nur eine **externe F_MAIN** (nicht 3A fix). **Nur Entwurf, kein freigegebener 202V/350ms- oder PCB-Schutz.**

## 1. Verbindlicher TI-Schaltungsvergleich und durchgeführter Schaltplan-Fix

- [TI LM74930-Q1 SNOSDF6, 7.3.2.1, Fig. 7-2 und Fig. 8-1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): Q301-Gate **direkt an HGATE (U301.14)**, Source direkt an OUT (U301.15). Der **100-Ω-Widerstand liegt nicht in Serie zum Q301-Gate**, sondern mit **CdVdT 10nF in einer RC-Reihenschaltung HGATE → 100Ω → 10nF → GND**. Die TI-Referenz verwendet 100Ω und 10nF.
- Vorher: `U301.HGATE → R320(100Ω) → Q301.G`, **kein** `CdVdT`. Diese Konfiguration ist nicht mit der TI-Referenz identisch und limitiert bei hohen Stromspitzen die Gate-Entladung; sie ließ den Einschaltstrom ungelöst.
- Jetzt im echten eigenständigen `01_Protection_LM74930.kicad_sch`: `U301.14/HGATE → Q301.1/G` direkt; `R320.1/HGATE → R320.2/DV_DT_RC_NODE → C307.1/10nF → C307.2/GND`.
- **Neues C307**: KEMET `C1206C103JARECAUTO`, AEC-Q200, 1206, 10nF ±5%, 250V, X7R, -55..+125°C [DigiKey DE](https://www.digikey.de/en/products/detail/kemet/C1206C103JARECAUTO/16680107) (15.10.2026 Preisindikator netto 0,31 € / 1pc, 0,178 € / 10pcs, 0,114 € / 100pcs; gelistet rund 3900–4000 verfügbar; MwSt./Versand, Lager und 202V-Bias-Kennlinie erneut prüfen). **MPN/Footprint nur Kandidat:** 250V DC-Nennwert ist nicht der Nachweis effektiver 10nF oder Pulsfestigkeit bei beliebiger Gate-Absolutspannung. Keine JLCPCB-Basic-Behauptung.
- Der Netzlistenprüfer `tools/check_trippower_native_netlist.py` fordert nun Q301.1/U301.14 auf `HGATE`, R320 auf `HGATE ↔ DV_DT_RC_NODE`, C307 auf `DV_DT_RC_NODE ↔ GND` und verbietet den alten direkt eingeschleiften 100Ω-Gatepfad.

## 2. Überstrom beim EINSCHALTEN: TI Eq.2 ist nur eine Näherung

Nach U301 hinter dem gemeinsamen R301 und parallel zum Buck an `VIN_PROTECTED_UNFUSED` liegen **C306 = 47µF nominal**, Buck **C101+C108 je 4,7µF**, HF-Buck **C107=0,1µF**: Summe **56,5µF nominal** (nicht unter Bias garantiert). TI Fig.7-2/Gl.2:
`CdVdT = COUT × IHGATE_SRC / I_INRUSH`; nach `I= COUT× IHGATE_SRC/CdVdT`:

| HGATE Ladestrom | Nominaler Einschaltstrom allein zum Laden dieser Kapazität |
|---|---:|
| 39µA (TI Min) | 0,220 A |
| 55µA (TI typ) | 0,311 A |
| 75µA (TI Max) | 0,424 A |

Dies ist **nicht** der gesamte Startstrom, da 5V-Buck, Ausgangskondensatoren, parallel angeschlossene Rohlast, MLCC-DC-Bias, Quellimpedanz, Induktivitäten, Einschaltspannung, Chargepump-Stabilität und Fehlerszenarien hinzukommen. Bei 9V Volllast **2,39A** plus nominell ~0,31A ergibt sich 2,70A, aber das ist keine Zusage unterhalb der berechneten OCP-min.-Schwelle ~3,10A. Anlauf unter Buck-Volllast/Motorstart ist zu prüfen.

## 3. Ausschalten bei OV → HGATE: Zeitbudget und MOSFET-Stress

**U301-Ereignis:** Bei RAW oberhalb nominell 35,89V (historisch berechneter OV-Teiler; Toleranz ~34–39V), `OVCLAMP=GND` wird **OV Cut-Off** ausgeführt: HGATE gegen SOURCE_A; Q301 sperrt. **Keine lineare 202V-Ausgangsklemme**; Q302 kann wegen gemeinsamer Quelle das Abschalten von Q301 nicht überbrücken. Der Rohabgriff und 5V verschwinden, sobald die Nachlaufkapazitäten entladen sind.

**TI-Datenblatt (6.5/6.6):** HGATE-Sinkstrom **≥128mA, typ 180mA**, Quelle 39–75µA, typ 55µA. Überspannungs-De-Glitch **4µs typ / 7µs max**, bei den TI-Prüfbedingungen. Dies ist der De-Glitch bis *HGATE fällt*, **nicht** die garantierte Stromunterbrechungszeit bei Q301 und 202V.

**Vishay [SQM10250E](https://www.vishay.com/docs/75035/sqm10250e.pdf):** Qg max 75nC bei VGS 10V, VDS125V, ID10A; Qgd typ 15nC; Ciss max 4050pF (VDS25V); VGS max±20V. Die Rechnung `75nC/128mA=0,586µs` ist nur eine **illustrative Q/I-Ratio**: kein garantierter Gate-Off-Wert, weil (a) Strom zeitlich variiert, (b) Qg unter anderen Bedingungen spezifiziert, (c) C307 gegen **GND** geladen wird (absolute Gate-Spannung im Betrieb), (d) Miller/Landpattern/Temperatur/Source-Induktivität Effekte erzeugen. Beispielrechnungen `(75nC + 10nF × VGabs)/128mA` für VGabs=40/100/200V sind nur **Sensitivitäten**, keine Schaltzeiten.

**Spannungs-/SOA-Gate:** Q301 `VDS(max)=250V`; 202V nominal nur **48V Differenz ohne TVS-/Leitungsüberschwinger und Bauteiltoleranzen**. TI stellt echten **OV-cutoff** der *VOUT clamp*-Regelung gegenüber. Bei einem schnell ansteigenden 202V-Puls kann `VIN_FUSED` zunächst hochspringen, bevor OV-Erkennung+Gateentladung wirken. Zur Illustration: `202V×2,39A×10µs ≈ 4,83mJ` **nur bei** unterstelltem konstantem 2,39A und 10µs überlappendem 202V-Spannungsabfall; nicht die reale Energie und **keine** SOA-Garantie. Ausgangs-Ladestrom, Leitungsinduktivitäten, Gate-Millerplateau, HIGH VIN vor Ausschaltung, Überstrom/Latch-Off, Gatefehler und thermischer Vorzustand sind noch nicht berücksichtigt. Vishay SOA-Diagramm Seite 5 gilt **Tc=25°C / Einzelpuls**; keine belegte 202V-/Heiß-SOA in TripPower.

## 4. Wichtiges Neben-Gate: C303/CAP-Ladungspumpe

TI [Datenblatt Abschnitt 8.2.2.2](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): `C(CAP) ≥ 10 × [Ciss(Q1)+Ciss(Q2)]`. Vishay SQM10250E **Ciss max4050pF**, Nexperia [BUK7Y4R8-60EX](https://www.nexperia.com/products/mosfets/automotive-mosfets/BUK7Y4R8-60E.html) **Ciss max5520pF**. Summe 9570pF → Empfehlung ≥**95,7nF effektive Kapazität**. Aktuell C303 **100nF nominell/100V X7R**: 10%-Untertoleranz **90nF** unterschreitet den Empfehlungswert, selbst **ohne** DC-Bias/Temperatur-/Alterungsabzug. Daher **C303 ist nicht endgültig ausgelegt**. Für den nächsten MPN-Vergleich **220nF/100V X7R** oder angemessene C0G/Hybrid-Option gegen tatsächliche Ceff bei VCAP–VS ca. 11–14V auslegen, keine blind freigegebene BOM.

## 5. Prüfstrategie / Freigabe-Sperren

1. **Native KiCad10 ERC + Netzliste am HEAD**, R320/C307-Pinplan inkl. analoger Funktionen prüfen (CI-Run nach Commit), 3D-/Footprint-Pins nachkontrollieren; **noch kein PCB/DRC**.
2. **Simulation/Labor:** 9/12/24/30V; kalt/heiß; 0/2A 5V und 0/1A Roh; HGATE, Q301 Gate–SOURCE_A, `VIN_FUSED`, `VIN_PROTECTED_UNFUSED`, `VS_CLAMP`, `CAP_PUMP`, `OV_DIV` und Shuntstrom synchron messen; Hochspannungs-Differenzialprobes und dafür geeignete Strommessung. Einschalt-Stromspitze und OCP/SCP-Interaktion.
3. **202V/350ms-Load-Dump Test A** als eigenständiges, noch offenes Gate. Mit sicherer Prüfumgebung und Strom-/Energiebegrenzung aufbauen; Ausgang/Steckverbinder, R313–315 Puls, D301-D304, 60V Q302, 63V C306, FET `VDS` und kurzzeitige SOA bei Worst-Case Tj prüfen. Test B getrennt; keine Normkonformität behaupten.
4. **Gefährliche Fehler:** OV-Pin-Unterbrechung, D301 Zener kurz/offen, Q301 stuck-ON, Q302 stuck-ON, HGATE kurz/unterbrochen, C307/R320 offen oder kurz, Dauer-LASTKurzschluss und externe `F_MAIN`-I²t/PCB-Kupfer; Abschaltung darf kein Brandrisiko auslösen.
5. **Gate-A/B**, bevor PCB geroutet wird: C303 effektive Kapazität unter Bias + Temperatur, HGATE/C307-Stress unter 202V, Q301 heißen Schalt-SOA, C306 Einschaltstrom + TVS und Hauptsicherung. Geometrie/Q301/Pin/Pad/3D offen.

**Keine Fertigungs-/Fahrzeug- oder ISO-Freigabe, solange diese Gates offen sind.** Nach jedem KiCad-Pin-/Netzwechsel müssen nativ ERC, Netlist und die systematische Schnittstellenprüfung erneut laufen.
