# TripPower – A/B/C Management-Review Runde 4 (2026-10-15)

**Status:** Engineering-Review, keine Freigabe für PCB-Bestellung, Fahrzeugbetrieb, 200-V-/350-ms-Survival, +125°C-/2-A-Volllast, 9-V-Start, ISO-Tests oder PCB-DRC. Nur dieser Review-Branch wurde bearbeitet. 

## GitHub-Stand (gegen `design/solid-state-power-v1`, SHA `2cafbf43e24aadc12ede10cd413b962c84579664`)

| Branch | geprüfter HEAD | Commits seit Basis | Zuwachs seit Review Runde 3 | Änderung |
|---|---|---:|---:|---|
| A `design/trippower-a` | `04cdcac359e062797867232959d600116385b481` | 46 | +15 | D302-Q307-R342-D306-Schutzblatt, Modell, Tests, BOM-Delta, CI-Dokumentation |
| B `design/trippower-b` | `914478710c497f2bb0c402ef6371ce41213e6e36` | 21 | +6 | AP74502HQ/TPS1HTC30-Referenzscreen, gerichteter MOSFET-Bodydioden-Faultgraph, Regressionen |
| C `design/trippower-c` | `d05ff038f185193d50f95309d39e2bbf494ea715` | 33 | +15 | C1 No-Go, Hersteller-/BOM-/KiCad-Text-Audit, C2-HV/LM70840-Q1-80V-Konzept, Testskript |
| Review `design/trippower-review` | Review Runde 3 vor dieser Änderung | 4 | – | Nur Reviews |

Die Basis-/Produktions-KiCad-Dateien sind durch A/B/C in ihrem Branch-Vergleich nicht verändert. **Keine belastbare fertige Bestück-/PCB-Alternative** in A/B/C. Commits ≠ elektrische Reife.

## A – Konstruktiver Fortschritt, aber der Ausfall Q301-KURZ ist NICHT behoben

- Native KiCad-10-Alternative `01_Protection_LM74930_Q301SHORT_CURRENTLIMIT_PROTOTYPE.kicad_sch`: `SOURCE_A -> D302 -> Q307 BSP135H6327XTSA1 Depletion MOSFET -> R342 1.5k -> VS_CLAMP`, Gate von Q307 auf VS, zusätzliche D306 56V SMC. 60 AUTO / 61 RUN bestückte Positionen **nur im Forschungsprototyp**, +3 zur unveränderten REV5-57/58.
- Q307/R342 als source-degeneration/current-limiter ist eine echte Verschaltungsalternative, aber der BSP135 `VGS(th)` bei 94µA ist **kein garantierter Stromgrenzwert über 0–200V, −40…+125°C, 350ms**. 9V-VS-Nachladestrom wird durch 1.5k plus Spannungsabfall reduziert. Q307-Hot-/Pulse-SOA und D306-Temperatur nicht freigegeben.
- **HARTER UND UNABHÄNGIGER PFAD:** Q301 D-S kurz: `SOURCE_A = VIN_FUSED`, damit LM74930 `A/Source pins2/15` und Q302 `Source pins1/2/3` direkt bei theoretischen 200V. **Kein D302-Q307-R342-Strombegrenzer begrenzt diesen Pinpfad.** 60V-Q302 und nachfolgender RAW/Buck-Pfad inklusive thermischer/failure-Ketten offen. Eine zweite Zener oder ein sicherer VS-Limiter alleine reicht nicht.
- 200V-Zenerstrom ohne Serien-R: idealisierte Quellimpedanz 5Ω ergibt `(200-56-0.7)/5 =28.66A` und `~562J` hypothetische Zenerenergie falls 350ms konstant, **kein realer oder garantierter Pulsstrom**. F_MAIN-Auslösung/200V-DC-Unterbrechung und Source-L/R unbekannt.
- **A-CI ausdrücklich nachgeprüft:** Actions `38742729871`, Job `116448323659` hat `completed/success`, einschließlich Modelltests, Basis ERC, D306- und Q307-Alternativ-ERC, nativen Netzlisten-Checks. A dokumentiert 41 erfolgreiche Unit-Tests und drei native ERC-Durchgänge ohne Violations. Der CI-Lauf war auf `9ec5fc90325b2c58cdff1b979bc5a80b1f1c5973`; **aktueller A-HEAD ist 1 Commit später**, dieser spätere Commit ergänzt *nur* `docs/TRIPPOWER_A_ROUND4_NATIVE_CI_EVIDENCE_2026-10-15.md`. Daher auf dem elektrischen Artefaktstand überprüfbar. Keine SOA-/HV-/Thermikfreigabe.

**A-Entscheid:** Prototyp- und Sicherheitsforschung positiv; nicht einfach Q307+D306 als Produktionslösung übernehmen. Statt weiterer Einzelbauteil-Patches die vollständige Risiko-/Kostenabwägung gegenüber COTS-Gesamtschutz vornehmen.

## B – Beste neue unabhängige Gefahrenfeststellung

- Diodes AP74502HQ Herstellerdatenblatt Seite 15 zeigt wirklich ein 200V-**unsuppressed**-Load-Dump-Beispiel mit Zweifach-MOSFET und `VIN`-Vorwiderstand (10k), 60V-Zener, OVLO 100k/3.5k. **Nicht** 200V/350ms, +125°C, 9V, F_MAIN/I²t oder Single-Fault freigegeben. Direkte Datenblattquelle: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf
- **B-Fault-Graph:** Zwei common-source N-MOSFETs verhindern Rückstrom im gesunden OFF. Bei *Eingangs-FET Q1 D-S kurz* liegt VIN am gemeinsamen SOURCE/MID und gelangt **über die Vorwärts-Bodydiode des zweiten FET** an den Ausgang. Dieser Fehler kann 200V nach `TPS1HTC30-Q1` (max 60V empfohlen) und `LMR38020-Q1` (max 80V) durchlassen. `2 MOSFETs` sind **nicht 2 unabhängige Schalter gegen einen einzelnen Q1-Kurzschluss**.
- Unabhängiger Einzelfehler `Dz OPEN`: das AP-VIN-Pin erreicht im idealen 1µF/10k/200V-Modell die 80V-absolute Grenze nach ca 5.1ms (VS0=0) bzw 1.54ms (VS0=60V). `Dz SHORT`: 10k sieht ideal 4W/1.4J bei 350ms; F_MAIN mit Ampere-Nennstrom ist keine Garantie, das abzusichern. OVLO-Top-100k bei 200V ebenfalls Pulse/Hot-derating offen.
- B4-Kandidat `AP74502HQTA8-7 + TPS1HTC30AQPWPRQ1 + LMR38020SQDDARQ1` ist **ein Bewertungs-/Sicherheitskonzept**, kein KiCad-Schaltplan; zusätzliche IC-Teilmengenkosten gegenüber altem LM74930+LMR circa 0.61/0.43/0.33€ pro 1/10/100, **ohne** FETs, Pulse, Extra-Fault-Protektion. Kein Gesamt-BOM-Vorteil bewiesen.
- Neue B-Python-Tests und CI-Konfiguration sind **keine unabhängig bestätigte erfolgreiche Native-KiCad-Ausführung**.

**B-Entscheid:** Als adversarialer Qualitätsprüfer höchster Nutzen, nicht nochmals generische Kauf-IC-Suche. Neueste Risiken eigenständig priorisieren und Anforderungen an akzeptablen Einzelbauteilausfall spezifizieren.

## C – C1 zu Recht gestoppt, C2-HV bleibt unbewiesene Option

- C1: `AP74502HQ + 2x 300V NMOS + TPS26631 + TPSM33620S5-Q1` mit 28 aktuellen bestückten Entwurfspositionen (J1/J2 und zwei Reserve-Cs inklusive, **noch fehlende Schutz-/Bulk-Bauteile nicht mitgezählt**); 36V-Buck mit 40V abs & 30V-autorestart nicht dynamisch abgesichert. C1 als NO-GO behandelt.
- `C1_STATIC_VALIDATION_AND_COST_2026-10-15.md`: 28 Symbole/BOM/preisbezogene refs auf Textbasis konsistent, TPS26631 U2 SHDN Pin13 berichtigt, AP-VCAP auf 220nF, SOT28-Pitch korrigiert, RDN11 vorhanden aber **vorläufig**. Nur **13 von 28** Positionen mit Stückpreis (1 St), **11/28** bei 10/100; Teilsummen 20.206€/13.133€/10.145€ ohne restliche Teile, PCB/F_MAIN etc. `check_kicad10.sh` vorbereitet, **aber kicad-cli in verwendeter Laufzeit fehlte**. Kein native ERC/Netzlistenpass, kein Layout/3D/DRC.
- C2-HV bevorzugt nun `LM70840QRRXRQ1` Automotive 4,5–80V 4A (TI bestätigt; VQFN29, **externe Spule**), zusätzlich zum AP74502HQ, 2 HV-FET und TPS26631 eFuse. Der größere VIN-Spielraum beseitigt **die enge 36V-Schwellenreserve**, nicht das 200V-Fehlerproblem. Der TPS26631 bleibt 60V empfohlen (67V abs laut C/B); **OVLO-/FET-off-Wellenform** bis Pad muss auch hierfür belegt werden.
- `OVLO Rtop=1M/Rbottom=35k` C2 nom. Rückkehr bei >31.4V und steigende Worst-Case-Abschaltung rund39.4V **nur statisch ohne 1%-R/Temperatur/leak + Flanken**. Beispiel 10µs Eingang 30→200V und optimistische 1µs Offannahme: theoretisch Eingang bis rund 56V vor Trennung, noch keine validierte eFuse-Pad-Obergrenze.
- Bei 9V+RAW1A+5V2A und angenommen 90% Buck wird `I≈2.235A`, zwei 97mΩ-FETs bei 125°C rund2.14W zusammen; +125°C-Buck-/FET-/PCB-Thermik bleibt offen. C2 macht echte Kosten-/Bestückpositionsersparnis noch nicht verbindlich: C1 Halbleiter inkl 2 FET ≈15.48€ bei 1St, C2≈19.79€ **ohne Induktor / passive Teile / zusätzliche Fehlerbehandlung**, A ist damit nicht gleichartig verglichen.
- B's Input-FET-Q1-short→Q2-Bodydiode-VOUT-Fehler gilt **auch** für C2, sofern gleiche common-source-Anordnung. Deshalb hoher Single-Fault-/I²t-Stop vor C2-KiCad-Integration.

**C-Entscheid:** C2 nur als Konzept mit besseren Spannungsreserven weiterverfolgen; keine voreilige neue KiCad-Leiterplatte. Native KiCad-10-Prüfung für aktuellen C1-Screen bei Verfügbarkeit nachholen, jedoch keinen wertlosen Vollausbau einer gesperrten C1-Hardware erzwingen.

## Manager-spezifische Sicherheitsentscheidung: Nicht unnötig überkonstruieren

**Pflichtziel:** Gefährliche Überhitzung, PCB-/Kabelbrand, unkontrollierte Kurzschlüsse und unzulässige Fahrzeugrückspeisung verhindern; die 5V-Versorgung und das gesamte Modul dürfen beim schweren Fehler ggf. beschädigt werden bzw. ausfallen, wenn der Fehler energiemäßig und mechanisch beherrscht ist. **Nicht ohne Nutzerentscheidung zum strengeren Ziel erklären**, dass alle nachgeschalteten ICs nach JEDEM Einzel-MOSFET-Short bei 200V ihre Maximalspannung ohne Schaden einhalten müssen. Ein zweiter HV-Schalter ist eine mögliche Sicherheitsmaßnahme, **nicht logisch die einzige**: Sicherung/F_MAIN mit realer 200V-DC-Unterbrechung, definierter Quellenimpedanz, I²t/Fehlerenergie, thermisch kontrollierter/sicher ausfallender Klemme oder anderer integrierter Schutz können Alternativen sein. Ohne belastbare Quelle + FMEA + Grenztemperatur ist auch ein zerstörter IC keineswegs automatisch unkritisch.

In jeder Architektur vor Schlussurteilen unterscheiden:
- Hersteller-Datenblatt-Grenzen / echte garantierte Maxima
- Szenario-Rechnung / idealisierte Wellenform / hypothetischer Quellwiderstand
- Netzlisten-Topologie / CI-Pass
- Labor-ISO-Prüfung / PCB-Fertigungsgate

## Nächste Meilensteine (priorisiert)

**A:** Den Q301-short→U301-A/Q302-Source-Pfad ohne unnötige teure zweite komplette Schutzarchitektur beherrschen. Erstelle FMEA als *Gefahrenenergie und F_MAIN*-Entscheid, prüfe mindestens zwei ganzheitliche Lösungen (z. B. sichere begrenzte Fehlerenergie durch Sicherungskoordination vs unabhängige HV-Trennung). Nur wenn eine echte Funktion/Schutzstufe entsteht, isolierter KiCad-Prototyp, vom Hersteller belegte Pulsgrenzen, qualifizierbare 9V/30V/125C-Marge. Alten Q307-Forschungsprototyp weder einfach aufblasen noch freigeben.

**B:** Reviewer für A/Q301 und C/Q1-bodydiode. Unabhängig Datenblatt-Pin/SOA- und Fuse/I²t-Prüfkette; ob zerstörbare ICs sicher versagen, nicht behaupten, sondern messbare Limits und Prüfplan. B4 ohne belegbaren Preis-/Teile-/Fehlervorteil NICHT zu Vollschematic zwingen. Tatsächliche GitHub Actions Run-URLs (falls vorhanden) prüfen.

**C:** C2 mit LM70840-Q1/TPS26631/AP74502HQ als gesamtes schaltungsarchitektonisches *Fehler-/Transientenbudget* überprüfen. Benötigte Quelle/Flanken + TOFF/Qg/Pad Vmax, OVLO cold/restart, FET Q1-short und AP VIN-Zener-open, Hot-125C und Kosten + komplette Bestückpositionenzahl berechnen. Erst falls alle harten Punkte plausibel sind, KiCad-10-C2-Standalone mit echten TI/Diodes-Referenzblättern und Hersteller-Landpatterns bauen, native ERC/Netzlisten- und Teilezahlregression mit GitHub Actions KiCad10 betreiben (kein Code-Textcheck als ERC ausgeben).

**Review-Exit:** Ein konkreter, herstellerbelegter Entscheidungspfad für *gefährliche Fehlerenergie* plus Start/Wiederanlauf/Temp mit aktivem Test-Gate; nicht alle drei aufwändig neu bauen. Vor PCB-Auslösung: 200V/350ms Testgeneratorparameter (nicht allein Spitze/Zeit), Quellimpedanz, F_MAIN DC-breaking/SOA, 9V/30V/Lebensdauer/Temperatur und echte Designvalidierung dokumentieren.

### Quellen
- A: `hardware/modules/TripPower_5V2A/WEG_A_ROUND4_Q301_SHORT_FAILSAFE_PROTOTYPE_2026-10-15.md`; `docs/TRIPPOWER_A_ROUND4_NATIVE_CI_EVIDENCE_2026-10-15.md`; GitHub Actions https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38742729871 .
- B: `hardware/modules/TripPower_5V2A/weg_b/WEG_B_ROUND4_AP74502_REFERENCE_GATES_2026-10-15.md`.
- C: `hardware/modules/TripPower_5V2A/weg_c/C1_SURGE_AUDIT_2026-10-15.md`, `C1_STATIC_VALIDATION_AND_COST_2026-10-15.md`, `C2_HV_80V_ALTERNATIVE_2026-10-15.md`.
- Diodes official ref: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf p15. TI LM70840-Q1 official: https://www.ti.com/product/LM70840-Q1 .
