# TripPower – Management-Review Runde 7 (15.10.2026, 22:12 Europe/Berlin)

**Review-Basis:** `docs/TRIPPOWER_A_B_C_D_REVIEW_ROUND6_2026-10-15.md` und die gemeinsame `POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md`. Vier separate Branches nach tatsächlich zusätzlichen Commits gelesen. Keine Änderung an Entwicklerbranches, REV5-Schaltung, aktuellen MPNs oder Konfiguration durch diesen Review.

## GitHub-Stand – exakt vs vorheriger Manager-Check

| Weg | Vorheriger Commit | Aktueller HEAD | Neue Commits | Neu gelesene Artefakte |
| --- | --- | --- | ---: | --- |
| A | `2f5469131f4cf16f1c5515a9a2c5e04c2719f8b0` | `13e9f8f4503b03c902cf95448d483043793a2196` | +18 | Round6 AP SRC/VIN/TLD/PG Bericht, PGOOD isolierter KiCad-Schaltplan, Kosten-CSV, CI und Tests |
| B | `7b6228a1a2b8b68e4b1d5135b5bb9473d92222d4` | `bbb77272c5a0547fc5778813ba67665ddeebe3f6` | +9 | A-vs-D-FMEA, PWR_FAIL-Schnittstelle, Fehlerenergie-Modelle, CI-Evidenz |
| C | `bb7cd43c79e42d1c60848da2b06c1e6b6c6a7f53` | `bfd9ffd01e854e0c899744975e5c2398477ac1e3` | +8 | drei COTS-Architekturen TLD/MAX16126/LTC4366, Preise, Scope, Tests |
| D | `0b3bf1bf52cee54f84a0ae9b0fbe0b754c89cb6e` | `8ade9adaa08ac3fb0cd94cbb62b987a4779710a6` | +8 | TLD/SM8S36A-Q/F_MAIN-Screen, LTC4366-Hot, BOM-Kosten-Matrix, Rechenmodell |

Die vier gemeinsamen Hardware- und Backup-Anforderungen sind in A–D vorhanden. **Keine der vier Architekturen ist produktions-, fahrzeug-, 200V/350ms-/125°C- oder Backup-Datensicherheitsfreigegeben.**

## A – wichtiger Go/No-Go-Fortschritt

**AP74502HQ-Q401-Hochvolt-Guard AS DRAWN = NO-GO:** Laut DS47093 abs max muss bei VIN>0 der AP-SRC-Pin ≤ AP-VIN liegen. Der zusätzliche VIN-Vorwiderstand 9,9kΩ/Controller-Ruhestrom kann AP-VIN unter die nahezu direkt angekoppelte MOSFET-SRC fallen lassen. A dokumentiert modellhafte SRC–VIN-Überschreitungen am 9V-Start und verwandten Zuständen; 10/11V beheben nicht den strukturellen Fehler. Diese Variante mit 69 AUTO/70 RUN nicht weiterbestücken, bis ein eigener datenblattkonformer VIN/SRC-Versorgungs- und Hot-Proof existiert.

**Positiv und real in KiCad:** isoliertes `02_5V_LMR38020_PGOOD_BACKUP_INTERFACE_PROTOTYPE.kicad_sch`; U101-PG Pin 6 -> 100k R501, 1M R502, Q501 BVSS123LT1G; fail-high/open-drain-ähnlicher Status: bei gesunder 5V LOW, bei Ausfall hochohmig mit Pullup auf TripTracer-Backup-Schiene HIGH. +3 fitted auf REV5 = **60 AUTO /61 RUN**; bekanntes Preisdelta ~0.552€/1 netto, nicht voller BOM-Preis. Konkrete CI https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38792761830 **completed/success** durch GitHub Job-API geprüft, inklusive KiCad 10 ERC/Netlist-Diff und Export REV5+PG BOM (Dokument nennt 58 erfolgreiche Tests und ERC fünfmal 0). **Nicht an eine RTC-Knopfzelle unmittelbar ziehen:** Host-Pullup und Pulslast müssen vom geeigneten Backup-PowerPath stammen und dürfen die Primärzelle nicht im Normalbetrieb leerziehen.

**HARTES Timingproblem:** LMR38020-PG informiert nur über bereits gesunkenen Buck-FB und hat internes Filter, im Modell ~12,7µs nutzbarer C_OUT-Drain vor 92% statt PG-filter mindestens ~40µs: **PG allein kann nicht als rechtzeitiger Backup-Starttrigger dienen**, wenn kritische AON/SD-Domäne nicht schon gestützt ist. TripTracer-UV-Supervisor, Backup-Power-Mux und Frühwarnung vor gefährlichem Spannungseinbruch unabhängig auslegen.

**TLD als Zusatz zu REV5 kostet zunächst +1 Teil = 58/59; zusammen mit PG 61/62. Kein Beleg, dass sie als alleiniger neuer Schutz 125°C passt oder Schutz-BOM reduziert.**

## B – unabhängige Fehlermatrix und konkrete Pin-Zeit-Schnittstelle

Neue `weg_b/PWR_FAIL_INTERFACE_R6_2026-10-15.md`: vorgeschlagen **LOW = main power good**, **HIGH = Fehlersituation**, NC/TripPower-0V→HIGH über Pullup100k an getrennt versorgtem 3V3_Backup. LOW ≤0.30V bei ≤36µA, OFF-Leck ≤1µA, VOH≥2.90V als **Designziel**, kein garantierter Bauteil-/MCU-Parameter. PWR_FAIL release≤100µs, lokaler UV≤100µs, Power-Mux≤100µs, IRQ≤1ms nur vorläufige Zielwerte. Bei abruptem M8-Abziehen **0 µs Vorwarnzeit**: Notversorgungsquelle muss physikalisch bereits verfügbar sein. Stuck-LOW-PWR_FAIL erfordert *separaten* lokalen UV-/IRQ-/Power-Mux-Mechanismus, parallele LOW=good-OD-Signale sind nicht fail-safe-Wired-OR.

Energie **nur Rechenbeispiel**: 3.3V × 0.1A ×3s plus 3×0.2A×20ms zusätzliche Peaks, η80% und 1.25 Reserve ⇒ ~1.61 J an der Backupquelle. Reiner idealer Kondensator über 3.6→2.9V ~0.707F. Das beweist ausdrücklich **NICHT**, dass eine CR1220 oder einzelne Standard-Knopfzelle ausreichenden Strom/Energie für ESP32-S3/SD liefert. Messen: Spannungs-/Stromspitzen/T_flush mit FAT32-WorstCase, Quellinnenwiderstand, Temperatur/Alterung, Reset, Rücklauf und USB.

Vergleich A-Guard gegenüber TLD betont zunächst bessere physische zweite HV-Sperre *wenn* sie gültig gesteuert wird, berücksichtigt aber AP-SRC/VIN-Gate. **Round7 korrigiert die Management-Priorität:** A hat Guard inzwischen selbst als gezeichnet NO-GO eingeordnet. Die hypothetisch bessere Redundanz ist keine zulässige Entscheidung pro A-Guard; beide A-Guard und D-TVS bleiben STOP.

CI https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38792391844, Job 116619986879, **completed/success** direkt geprüft: modellierte Fehlerfälle und **geerbte** REV5 ERC/Netlist, kein neues B-Schaltplan-Pin-Design oder realer 200V-/Backup-Test. B meldet 44 Python-Regressionen.

## C – drei neue Herstellerstrategien, aber kein Produktkandidat

C1/C2 NO-GO beibehalten. Round6 Konzepte:
1. **TLD8S36AH TVS Shunt** + LMR38020-Q1 80V/2A + TPS26631 60V eFuse: Hot-TV S, V(PAD), TVS-OPEN/SHORT und Sicherung ungeklärt.
2. **MAX16126** (+ HV-NMOS, TVS/Zener) mit echter ADI-Referenz 202V/400ms/Rsource1–8Ω und beispielhafter 1A Last, aber **nicht** 200V/350ms/+125°C/5V2A+RAW1A und keine Einzelfehler/F_MAIN-Zusage; **sinnvoller nächster COTS-Recherchepfad**.
3. **LTC4366-2** Controller + linearer FET, Zeitabschaltung möglich, 9V am unteren Systemlimit, thermisch/ökonomisch NO-GO bis andere FET-/Timerkonfiguration.

Nur Teilpreis-/Bauteilfunktions-Scope, **kein** kaufbarer Endpreis und keine real bestückbare neue PCB: jeweilige 39/49/46 *Scope-Platzhalter*, nicht validierte Bauteilzahl. Rechnung zwei heiße 300V-FETs + eFuse bei 9/10/11V liefert 2.502/2.158/1.911W reine FET-Verluste; *kein* Einsparnachweis durch neues VINmin. CI https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38792445057 completed/success direkt geprüft, 11 modellierte Regressionen, **kein nativer KiCad-ERC** für diese Round6-Ideen.

**C-Nächster Forschungsschritt:** Hersteller-MAX16126-Referenz gegen tatsächliche OEM-Bauteil- und Fehlergrenzen auswerten und nur weiterverfolgen, wenn vollständig vergleichbare 5V/2A + RAW1A + F_MAIN + ON/OFF + Backup-/USB-Entkopplung und Hot-125C-BOM gegenüber REV5 wirtschaftlich belegbar sind; nicht bei bloßem Herstellerartikel-Go.

## D – Alternative Bourns, erster HV-DC-Fuse-MPN

**TLD8S36AH** bleibt als **alleiniger** 200V/350ms/125°C-Schutz **NO-GO**: Originalhersteller AN-1003 bei 25°C widersprüchlich Ri-Fig ~4.5Ω vs Tab 3.5Ω, 61.2V clamp bei25°C nicht Hot-V(PAD) max. Neuer Vergleich **Bourns SM8S36A-Q** AEC-Q101, aktive Beschaffung, OEM ISO16750-2 Test-A **10-Puls-Diagramm** mit 202V/350ms; D liest 350ms-Punkt bei etwa Ri2Ω, noch **keine +125°C-Garantie**, auch nicht garantiert ≤60V hinter Shunt. Hersteller-BOM-Snapshot SM8S36A-Q 3.74/2.453/1.620€ pro 1/10/100 netto, gegenüber TLD ca1.555/1.445/1.321€ netto (Reichelt-USt herausgerechnet, Restposten Händler ≠ Hersteller EOL). **Noch keine Endentscheidung** pro Bourns ohne Hot-125C/Clamping-/Safe-Fault-Daten.

**F_MAIN-Schritt:** Schurter `0001.2509`, 3.15A, 300VDC, MPN zur Herstellerprüfung. Melting I²t 33.7A²s ist **NICHT** total-clearing oder garantiert 200V/350ms DC-Arc bei realem Quell-R/L. Gefundener Holder `0031.1751` nur max +85°C, **No-Go für +125°C-Einbauort**. Bei 9V Normalvollast und 125°C muss 3.15A außerdem thermisch/Alterung korrekt abgeleitet werden. Unter-Fusenennstrom-Faults bleiben ungelöst.

D untersucht LTC4366-2 mit ADI-Referenz-250V-MOSFET IXTK90N25L2: allein Controller+FET ≈47.99€ netto/1, ca30.56€ netto/100, +Rest, für Kleinmodul teuer und mechanisch unpraktisch; Timer früh aus statt 350ms linearer FET-Verlust ist offen. **D hat keine neue KiCad-10-Schaltplan-/ERC-/PCB-Prüfung**, sondern ein Python-Szenario-/Unit-Testmodell ohne hier independently geprüften GitHub-Actions-Echtlauf.

## Wichtigste fachliche Querfeststellungen

- **Knopfzellen-Anforderung ist inzwischen bei A+B wirklich als Signal-/Funktionsprototyp bzw. Spezifikation umgesetzt, aber NICHT als nachgewiesener lokaler Backup-PowerPath.** PWR_FAIL-Logik allein kann bei sofortigem M8-/GND-Verlust keine Energie speichern; TripTracer-Projekt muss reale RTC-/PowerPath-/SD-Energiequalifizierung selbst leisten.
- **9–30V bleibt verbindlich**; 10/11V reduzieren im Modell Leitverluste, beseitigen nicht die 200V-Single-Fault- und AP-SRC/VIN-Frage. Keine ungefragte Umspezifikation.
- **Keine Branche derzeit sicher genug für eine PCB-Bestellung oder reale Fahrzeugfreigabe.** Insbesondere ERC=0 ist Schaltplan-Syntax-/Pinnetzprüfung, keine SOA-/I²t-/Isolationserprobung. 200V/350ms fehlen Quell-R/L, Flanken, Pulsform, Wiederholungsanzahl und HOT.
- **Konsistenzpunkt für nächsten Review:** A/B-`PWR_FAIL` tatsächlich beobachteter *geschützter Hauptversorgungsstatus* vs nur Buck-FB/PG; benötigte Prognose beim OVLO und ausreichende Pufferung; Rückstrom-/ESD-/Fail-stuck-Test, User-Primärzelle nicht in RUN-Dauerverbrauch entladen.

## Management-Folgegates (nicht als Freigabe missverstehen)

1. **D**: OEM-Bourns-SM8S36A-Q 125°C-TVS-LoadDump-SOA plus F_MAIN-300VDC-Halter und Testgenerator real herausarbeiten; TLD nur bei schriftlicher SOA-Klärung. Wenn keine scharfen Daten: konditional NO-GO statt Endlosloop.
2. **C**: MAX16126-ADI-Referenz als neue Vergleichschance systematisch Pin/SOA/fuse- und BOM-komplett qualifizieren; mit D-Bourns und A-Gateway fair vergleichen, Kosten 1/10/100 nur echte MPN-Kassen.
3. **B**: separate **TripTracer**-Power-Mux-/SD-Energie-Messspezifikation und 200V-PWR_FAIL-Single-Fault-Audit, wenn user den Auftrag erweitert; 0µs-Warnfall zwingend abdecken.
4. **A**: Nicht AP-Guard wiederbeleben; PG-Prototyp als **Statussignal** behalten, aber unabhängigen, schnelleren VIN-/UV-Detektor/Backup-PowerPath definieren; echte Serien-MPN/PG-Leckage und Schnittstellen-Isolation prüfen.

**Review-Freigabe:** nur Forschungsfortsetzung. Keine Kosten-/Stückzahl-/Sicherheitsvorteile einer kompletten D-/C-Ersatzarchitektur bereits bewiesen.

### Gelesene Hauptquellen
- A: `hardware/modules/TripPower_5V2A/WEG_A_ROUND6_AP_SRC_TLD_PGOOD_BACKUP_DECISION_2026-10-15.md`, `docs/TRIPPOWER_A_ROUND6_NATIVE_CI_EVIDENCE_2026-10-15.md`.
- B: `hardware/modules/TripPower_5V2A/weg_b/WEG_B_ROUND6_A_GUARD_VS_D_TVS_BACKUP_DECISION_2026-10-15.md`, `weg_b/PWR_FAIL_INTERFACE_R6_2026-10-15.md`, `weg_b/WEG_B_ROUND6_VERIFIED_ACTIONS_EVIDENCE_2026-10-15.md`.
- C: `hardware/modules/TripPower_5V2A/weg_c/R6_COTS_RESET_DECISION_2026-10-15.md`.
- D: `hardware/modules/TripPower_5V2A/weg_d/WEG_D_ROUND6_CONDITIONAL_STOP_DECISION_2026-10-15.md`, `ROUND6_BOM_COST_MATRIX_2026-10-15.md`.
