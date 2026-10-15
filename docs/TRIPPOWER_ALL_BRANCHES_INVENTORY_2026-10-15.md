# TripTracer – vollständiges Branch-Inventar und TripPower-Gate-Check (2026-10-15, 19:17 Europe/Berlin)

**Umfang:** Repository `GeneralEdelweiss/TripTracer`, alle über `search_branches` gelieferten **12 Branches** (zweite Seite leer). Dieses Inventar dokumentiert einen GitHub-Snapshot und **keine neue elektrische Freigabe**.

## Was hat sich seit dem vorherigen A–D-Management-Review geändert?

Exakte GitHub-Commits des letzten Reviews wurden gegen die heutigen Branch-HEADs verglichen:

| Branch | HEAD (verifiziert) | Neue Commits seit A–D-Runde-5-Review |
|---|---|---:|
| `design/trippower-a` | `2f5469131f4cf16f1c5515a9a2c5e04c2719f8b0` | 0 |
| `design/trippower-b` | `7b6228a1a2b8b68e4b1d5135b5bb9473d92222d4` | 0 |
| `design/trippower-c` | `bb7cd43c79e42d1c60848da2b06c1e6b6c6a7f53` | 0 |
| `design/trippower-d-load-dump` | `0b3bf1bf52cee54f84a0ae9b0fbe0b754c89cb6e` | 0 |
| `design/trippower-review` | vor Anlegen dieser Datei `c66b52b6163bbbdd0d700b7dbb78bc775170daf3` | 0 |

**Keiner** der vier technischen Chats hat seit dem letzten Review neue **committete** technische Ergebnisse. Das sagt nichts über laufende/uncommittete Chat-Arbeit. Keine weitere No-Go-/Go-Entscheidung ohne neue Evidenz.

## Vollständige Branch-Karte

| Branch | Rolle / Einordnung | Empfohlene Handhabung |
|---|---|---|
| `main` | Standard-/Produktbasis; seit der TripPower-Abzweigung unabhängig weiterentwickelt; neue Backup-Dokumentation hier vorhanden | Aktive Projektbasis, aber Änderungen aus Entwicklungsbranches keinesfalls blind mergen |
| `design/solid-state-power-v1` | Gemeinsame **REV5-Engineering-Baseline**, 57 AUTO/58 RUN; eigene neue Dokumentationscommits | Baseline eingefroren, nicht als fertige Platine bezeichnen |
| `design/trippower-a` | A: unabhängige AP74502HQ-Eingangs-Guard/LM74930-Forschung, isolierte KiCad-Prototypen, native ERC/Netzlistentests | Haupt-KiCad-Forschungsweg; AP VIN/SRC 9V, 200V-SOA, +12 Teile und Backup-PWR_FAIL ungeklärt |
| `design/trippower-b` | B: unabhängige FMEA/F_MAIN/Fehlerenergie | Sicherheitsgate-Prüfer; kein fertiger abgeleiteter Produktionsentwurf |
| `design/trippower-c` | C: C1 (36V-TPSM) & C2-HV (80V LM70840) als Gesamtkonzept **No-Go**, alte C1-KiCad-Draft vorhanden | Neuer COTS-Ansatz erst nach vorigem Gesamtkonzept-Stopp |
| `design/trippower-d-load-dump` | D: TLD8S36AH-Load-Dump-TV S / LTC4366-2-Research, kein fertiger KiCad-Entwurf | Preis-/Teilezahl-Option mit vorrangigem Hersteller-Ri-/SOA-Gate |
| `design/trippower-review` | Unabhängige Entscheidungen, Vergleiche und Schnittstellenanforderungen | Dort Bericht halten; nicht als Entwickler-/Produktbranch verwenden |
| `design/trippower-80v` | **Eigener alter, echter 80V-Buck-Branch:** `WEG_A_80V_ENGINEERING_2026-10-15.md`; echte REV5-Standalone-KiCad-/Baseline-Anpassungen **L101 = Bourns SRP7050TA-150M**, **C306 = Panasonic EEHZC1J470P**, neuer Spulen-Footprint, Regression/Workflow | Wertvolle Teilequalifikation; **nicht automatisch** in A übernehmen, Thermik/Induktivitäts-Derating und 2A/30V-Peak-Limit zuerst belegen |
| `design/trippower-36v` | Seit altem Merge-Base 4 **nur gemeinsame Backup-/Dokumentationscommits**, **kein** 36V-KiCad-Deltanachweis | Historischer Vergleich, nicht als aktuelle Variante bezeichnen |
| `design/01d-input-protection-review-20261013` | Historische Schutzprüfung vor solid-state-Baseline | Historisch/Read-only, nicht current |
| `snapshot/2026-10-13-before-solid-state` | Historischer Zustand | Archiv, nicht verändern |
| `snapshot/2026-10-13-with-01d-review` | Historischer Zustand mit 01d-Review | Archiv, nicht verändern |

Die drei historischen 01d/Snapshot-Branches sind laut Compare lediglich Vorfahren des gemeinsamen Engineering-Ausgangspunkts; `main` ist vom damaligen Commit stark **divergiert**, daher **keine** Gleichsetzung von `main` und `design/solid-state-power-v1`.

## Technische Statuspunkte / Sicherheitsgates

**A:** zusätzliches AP74502HQ-Guard vor Q301 kostet +12, **69 AUTO/70 RUN** (Baseline 57/58). Echter nativer KiCad-10-CI-Pass https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38749865263. Bei 9V mögliches Hersteller-Abs-Max-Verhältnis `SRC ≤ VIN` nicht geklärt; Single-Fault-SOA, 200V/350ms, 125C/Fuse nicht freigegeben.

**B:** Der sichere Geräte-Totalausfall wird als Option geprüft, aber kein Sicherungs-/Halter-Nachweis für alle unter-Nennstrom-Fault-Energien. Mersen MEV55C5 550V/5A hat Min-Breaking-Current 10A, kein schneller Schutz bei 1–3A garantiert; kein unterschriebener Power-Fail-Gate.

**C:** AP+2FET+TPS26631+LM70840 als komplette C2-HV-Architektur **No-Go**, u.a. Q1-short → Q2 body diode. Erfolgreicher rein mathematischer Run https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38748545904. Keine Native-C2-Schaltplan- oder PCB-Freigabe.

**D:** Hersteller-TLD8S36AH hat 202V/350ms Herstellerbeispiel bei 25C; Hersteller-Anwendungshinweis Grafik ~4.5Ω, Rechnung/Tabelle 3.5Ω für ähnlichen Puls, Widerspruch offen, Hot-SOA, V(Pad), Einzelfehler OPEN/SHORT und F_MAIN unbekannt. LTC4366-2 als teurere Alternative ohne FET-SOA-Freigabe.

**80v alt:** Gleiche 57/58 Bauteile, aber `L101` AEC-Q200 mit höheren DCR/kleinerem Irms als alte FANGCHENG, und `C306` 47µF/63V AEC-Q200. 30V/2A Peak Ripple bei konservativ 12µH/320kHz = ca 2.543A vs 2.6A minimum high-side current limit, d.h. nur 57mA idealisierte Reserve vor zusätzlichem DC-bias/Hot-Abfall. Hersteller-Temperatur-/Kennlinien fehlen. Kein PCB-DRC/Fahrzeugnachweis.

**Backup:** Neue `POWER_LOSS_BACKUP_REQUIREMENTS_2026-10-15.md` und geändertes `HARDWARE_REQUIREMENTS.md` PWR-38–43 liegen auf main, Baseline, allen aktuellen A–D-/Review- und beiden Legacy-36V/80V-Branches. RTC-CR1220 ist für ESP32-S3/FRAM/microSD-Backup **nicht automatisch geeignet**; gemessene Stromspitzen/Shutdownzeit, Not-Energiequelle, PWR_FAIL/PGOOD, Rückstrompfade und Trennung der Haupt-5V-Domäne sind weiterhin **keine Hardware-/Software-Implementierung**. Relevante Projekt-Anforderungswidersprüche älteren Textes (z.B. `PWR-30` 9–36V trotz „9–30V“ sowie PWR-15 vs PWR-17) sollen vor Produktfreigabe konsolidiert werden; nicht stillschweigend umdeuten.

## Operative Entscheidung

1. **Keine Branch-Zusammenführung jetzt.** Führe die Entwicklungszweige getrennt, sonst verschwimmen freigegebene Hersteller-MPNs, Varianten und Proof-Gates.
2. B und D haben den höchsten Informationswert für die nächste *Sicherheits-/Kostenentscheidung*. A wartet vorrangig auf konkrete AP-SRC/VIN-Datenblatt-/HOT-Validierung; C braucht neues Gesamtkonzept statt Ausbau der verworfenen C2-Kette.
3. Backup-Aufgabe als **separaten TripTracer-Integrationsarbeitsschritt** priorisieren: echte MCU+microSD-Spitzenströme und Worst-Case-FAT-Flush -> Zell-/Puffertechnologie entscheiden; TripPower-Signal/GND-/Power-Path-Schnittstelle definieren. Ohne diese Messung wäre jedes „Knopfzelle sichert alles“-Versprechen falsch.
4. Für künftige Reviews konkrete Commit-SHA vs vorherigen Review-HEAD prüfen (nicht bloß Ahead-by gegen divergierte Basis), belegte KiCad-CI-Jobs sowie Fehlerenergiebelege anführen.

Keine Änderungen an A, B, C, D, `main`, den historischen Branches oder der REV5-BOM durch diese Inventur.
