# TripPower C1 – Native-KiCad-Gates, statische Konsistenz und Kostenstand (15.10.2026)

**STATUS: ELEKTRISCHER ENTWURF; C1 NO-GO – keine Bestellung, keine Montage, keine Fahrzeugfreigabe.** Alle Dateien ausschliesslich Branch `design/trippower-c`. Historischer Stand C1 wird nicht als einsatzfertig bezeichnet. Auditergebnis siehe `C1_SURGE_AUDIT_2026-10-15.md`, alternative Architektur `C2_HV_80V_ALTERNATIVE_2026-10-15.md`.

## Tatsaechlich online durchgefuehrte Branch-Pruefung

Die ueber die GitHub-Schnittstelle gelesenen Daten der **aktuellen Branchdateien** wurden mit einem statischen Skript verglichen:

| Check | Tats. Ergebnis |
|---|---|
| `TripPower_C.kicad_sch` physische Ref-Anzahl | **28** |
| Eindeutige Ref-Designatoren | **28** |
| `BOM_C1_DRAFT.csv` Ref-Anzahl | **28** |
| `PRICED_BOM_C1_PARTIAL_2026-10-15.csv` Ref-Anzahl | **28** |
| Schaltplan/BOM/Preisliste Ref-Mengen exakt gleich | **Ja** |
| Schaltplan-MPN == BOM-MPN pro Position | **Ja, 28/28** |
| TPS26631 U2 SHDN Pin 13 nur `no_connect`, nicht `HV_PROTECTED` | **Ja, korrigiert** |
| AP U1 `C2` VCAP 220nF 100V MPN KEMET C1206C224K1RACAUTO in BOM und Schaltplan | **Ja, korrigiert** |
| Lokaler Diodes-SOT28-Footprint | Vorhanden, 8 Padnummern, Herstellerpadpitch 0.65mm, Y1 3.10mm angepasst |
| Lokaler TI-RDN11-Footprint | **Vorhanden**, 11 Padnummern, aber Landpattern **nicht** mit TI abgeglichen/freigegeben |
| KiCad 10 natives ERC | **NICHT DURCHGEFUEHRT – kicad-cli nicht installiert** |
| KiCad 10 native Netzliste | **NICHT DURCHGEFUEHRT – kicad-cli nicht installiert** |
| KiCad 10 PCB DRC | **NICHT MOEGLICH – KEIN PCB** |
| Reale 200-V-/350-ms-/+125C-Tests | **NICHT DURCHGEFUEHRT** |

**Achtung:** Vorherige Berichte erwaehnten teilweise 26 Positionen, die schon vor diesem Audit angelegte Branch-Erweiterung enthaelt jedoch zwei zusaetzliche **bestueckte** Kondensatoren: C10 4.7uF/50V und C11 22uF/16V. Deshalb sind es **28**, nicht 26. Die weiteren notwendigerweise fehlenden Eingangs-/Bulk-/Schutz-Teile werden die finale Zahl noch erhoehen.

Der TI-RDN0011B-Hersteller-Landpattern auf Seite 47 der TI TPSM336xx-Q1 Datenblattfassung 08/2025 zeigt nicht-gleichfoermige Pads und empfohlene SMD-Masken/Oeffnungen. Lokal `TI_RDN11.kicad_mod` ist nur ein unqualifizierter erster Entwurf. Einzelne z.B. Pad1 geometrische Ausdehnung/thermische Rechtecke weichen potenziell von der offiziellen Kontur ab. **Kein automatisches 11-Pad-Zaehlen ist ein korrekter Landpattern- oder Schablonennachweis.** 3D-Modell fehlt; fuer eine Bestellfreigabe Hersteller-CAD/praezise Geometrie und Pin1-Kennzeichnung kontrollieren.

## Exakter Ausfuehrungsweg fuer native KiCad10-Pruefungen (noch offen)

Standalone-Baugruppe im Clone des Branch:
```bash
cd hardware/modules/TripPower_5V2A/weg_c
bash check_kicad10.sh
```
Das Skript verlangt **KiCad 10**, fuehrt `kicad-cli sch erc --exit-code-violations --severity-all`, anschliessend `kicad-cli sch export netlist --format kicadsexpr` und dann `python3 -m unittest protection_budget` aus. Abbrechen bei jedem Fehler. Das hier verwendete Modell hat `kicad-cli` in seiner Laufzeit nicht zur Verfuegung, GitHub Actions Runs gab es zum Branch beim Abruf keine. **Niemals aus fehlender Fehlerausgabe einen bestandenen Test ableiten.** Auch ein gruener ERC wuerde die gezeigten Sicherheitsfehler nicht freigeben.

## Kostenbasis: 28 bestueckte Positionen, davon nur Teilpreise verifiziert

Quelle: `PRICED_BOM_C1_PARTIAL_2026-10-15.csv`, mit exakten Links, MPN und Fehler-/Qualifikationsspalten. Stand 15.10.2026, **EUR netto pro fertiger theoretischer Baugruppe**, ohne MwSt., Fracht, PCB, Schablone oder externe Sicherung. Mengenpreis = verifizierter Einheitspreis bei Einkaufsmenge 1/10/100; fehlende Positionen absichtlich **nicht** erfunden.

| Bekannte Teilpreise | 1 Stueck | 10 Stueck | 100 Stueck |
|---|---:|---:|---:|
| Verifizierte Einzelpositionen | 13 von 28 | 11 von 28 | 11 von 28 |
| **Bisherige Preis-Teilsumme** (nicht Gesamtkosten!) | **20.206 EUR** | **13.133 EUR** | **10.145 EUR** |
| Noch unbepreiste Positionen | 15 | 17 | 17 |

**Warum keine komplette endgueltige BOM?** J1 und J2 haben keine feste MPN und waren als vorlaeufige Header eingezeichnet. Nicht verifizierte Puls- und Hochvolt-Schutzteile duerfen nicht durch beliebige guenstige Widerstaende/TVS/Stecker ersetzt werden. Zusaetzliche Herstellerreferenzteile fuer 200V-CIN, effektiv >=1uF AP VIN, VCAP/Bulk, ACC-Surgeschutz und eventuell Einzel-RAW-Stromlimit fehlen noch. Eine exakte Stueckkostenbehauptung waere deshalb irrefuehrend; die hier angegebenen Summen sind **nur Untergrenzen anhand bekannter Preise der bereits vorgesehenen Positionen**, keine Einkaufsangebote.

### Vier Sicherheitsstopps

1. 200V/350ms Pulsform, Quellimpedanz, Schaltspitzen, echte AP-VIN-Klemme und Ceff, FET-SOA und F_MAIN-Koordination;
2. Worst-Case OVLO-Hysterese macht 30V-Restart und 36V-Buckbetrieb in C1 widerspruechlich, und schnelle Transienten koennen 40V abs ueberschreiten;
3. 125C/5V2A/RAW1A Thermik bei 9V: HV-MOSFETs ~2.14W zusammen, TPSM33620 1.11W bei optimistisch 90% eta und 150C-Tj-Grenze;
4. Q1 D-S-KURZ -> Q2-Bodydiode -> HV_PROTECTED 200V trotz AP-EIN/AUS: **sicherheitsrelevanter Einzelfehler ohne nachgewiesene Schutzkoordination**.

## Naechste reale Entwicklung

Nicht am C1-36V-Buck mit zusaetzlichen ungeprueften diskreten Komparatoren herumdoktern. C2-HV mit **TI LM70840QRRXRQ1 (80V, 4A, integrierte FETs, externe Spule)** als Herstellerreferenz nachvollziehen; 30V-Restart/OVLO und das weiterhin kritischste Q1-Short->eFuse-Single-Fault verifizieren **vor** neuem KiCad10-Bauversuch. Erst danach Voll-BOM/Footprints, ERC/Netlist, PCB, DRC, echte +125C/200V/ISO-Tests.

