# TripPower Weg A — REV6 KiCad-10-Prototyp

**Aktueller Arbeitsstand 16.10.2026 – maßgebliche Entwicklungsentscheidung:** [Round3: Werks-OVP NO-GO / 32V-Restart / 25-MPN-BOM](REV6_A_ROUND3_FIXED_OVP_25MPN_COMPLETE_2026-10-16.md). Führende 25-Positionen-REV6-Grundschaltung: OVP R201100k/R20212k **Panasonic ERA-8AEB123V**/R2034.22k, 0.1%/25ppm, rising32.223..33.880V, falling29.864..31.833V, 32V Wiederanlauf **nur statisch** 0.167V Headroom, 10V UVLO8.821V worst. TI werkseitige OVP-falling 32.7..35.0V und UVLO rising15.1..15.9V **nicht geeignet**; drei Widerstände bleiben. L101 Bourns **SRP7050TA-150M** AEC-Q200 15uH/6A Isat mit portabler Hersteller-Footprint; R204 Vishay **CRCW12066K04FKEAHP** AEC-Q200. EOL 22uF Murata zuvor mit Taiyo Yuden MCAST32MSB7226KPNA01 ersetzt. **25/25 Modul-BOM-Linien nun bepreist**, netto EUR 20.763/13.991/11.0217 pro Modul bei1/10/100 Stück, **ohne PCB/Bestückung/Versand, Host-Bauteile und Fahrzeug-F_MAIN**. TP502 dient nur zur 5V-Signalprobe, nicht als 2A-Steckverbinder. Separat belegte Thermal- und RAW-PPTC-Forschungsblätter enthalten je26 Positionen, **beide weiterhin NO-GO**. Ausnahmslos **keine Sicherung oder Halter** auf TripPower. **+85°C ambient safe-off und 58V-Eingangspin-Ringing sind nicht qualifiziert; kein PCB/DRC, NO FAB.**

**Projekt öffnen:** `TripPower_REV6_A.kicad_pro` (KiCad 10). Das **eine** Root-Schaltblatt `TripPower_REV6_A.kicad_sch` führt im Hierarchie-Navigator zu **01 TPS26631 Eingangs-/Überstrom-/Verpol-/UV-/OV-Schutz** und **02 TI LMR38020 5V/2A + PGOOD**. Original-REV5-Dateien im Nachbarverzeichnis bleiben unverändert und sind **nicht** Teil dieses Projekts.

## Was bereits konkret vorliegt
- 25 native, bestückte KiCad-Netzlisten-Bauteile in 2 Schaltblättern. Plus nicht bestückte PWR-/Testpads. Eigene portable Symbol-/Footprint-Bibliotheken liegen hier.
- Bei TI abgeglichener TPS26631PWPR 20-Pin PWP-Pinout, GND-EP21, reverse N-MOSFET 100V und Q202-Gate-Driver; SHDN13 **floating** (absolut maximal5,5V, Hersteller bestätigt internes Pull-up), R201/R202/R203 im führenden Plan mit präziser Anstieg-/Abstiegshysterese modelliert: OV-ON 32,334–33,996V; Freigabe 29,967–31,943V; nur 57mV statische 32V-Restart-Marge.
- LMR38020SQDDARQ1 80V-Buck mit vorheriger passiver Baseline, fail-HIGH Status via Q501.
- `REV6_A_25_PART_ORDER_BOM_2026-10-15.csv`: tatsächliche 25 Positionen und einzeln nachweisbare Einkaufspreise; die frühere Murata-22uF-MPN `GRM32ER71E226KE15L` **wurde durch Taiyo Yuden `MCAST32MSB7226KPNA01` ersetzt** (C104–C106). Der echte Ceff bei5V DC-Bias muss noch geprüft werden.
- `REV6_A_ARCHITECTURE_BOM_SAFETY_REPORT_2026-10-15.md`: Architektur/FMEA und **offene** Grenzen.

## Elektrische REV6-Abgrenzung und unbelegte Punkte

**10–32V normal, unter10 Reset zulässig, OV-Abschaltung spätestens36, 36V/400ms, nur extern zentral begrenzt 58V/350ms.** Kein unsuppressed-200V-ISO-Test A, kein 9-V-Vollbetrieb, keine +125°C-Vollast. 2A 5V bis+60°C, -20..+70C Einsatzbereich, sichere Abschaltung bis+85C. F_MAIN und Fahrzeugeinbau in zentral begrenzten 24V-Systemen bleiben Pflicht.

**KEINE Fertigungsfreigabe**, weil:
- eFuse max60V empfohlen, **67V abs**: Bei58V im 350ms-Profil sind nur2V Betriebs-/9V Absolute-Margen vor Ringing, Hot-SOA/MCU nicht bewiesen.
- Bis+85C besteht **noch kein qualifizierter Ambiente-Temperatur-Abschaltkreis**. Die integrierte 165°C-Tj-Notabschaltung des eFuse reicht als +85°C-Umgebungsschutz nicht automatisch.
- Buck 5V2A+60°C, reale PCB-Kupfer-/Induktivitäts-Thermik und Ceff nach DC-Bias/Alterung, negative Pulse, 36V/400ms, Restart-Hysterese, unter1mA-Off-BAT nicht im Prüfstand verifiziert.
- RAW 0,5A ist nur als vom OCP gemeinsam gespeister Kandidat abgegriffen, **nicht selektiv abgesichert**. Fehlen echter passender 2A-/0,5A-Stecker/Leiterbahnen/F_MAIN-Coordination und M8-GND-Reverse-/USB-Service-Mux.
- PGOOD kann *nicht* vor dem sofortigen M8-Abziehen warnen; TripTracer muss FRAM-first committen und SD-Recovery durchführen, RTC-Zelle ist keine SD-Backup-5V-Quelle.
- PWP20/TPS26631-Landpattern in `Tripmaster.pretty/TI_TPS26631_PWP_EP.kicad_mod` ist **provisorisch**; TI-PWP-Normlandpattern/EP-Pasten-/Thermal-Via-Fenster vor PCB-Auftrag geometrisch abgleichen. Der bestehende `L_FANGCHENG_FCH0650_150M` Footprint ist ebenfalls provisorisch und benötigt echte Hersteller-Abmessungen und Lieferbarkeit. **Kein PCB existiert**, PCB-DRC daher unmöglich.

## Reproduzierbare Entwicklungstests

Aus Repository-Root:

```bash
python3 tools/trippower_a_rev6_limits.py
python3 -m unittest discover -s tools -p 'test_trippower_a_rev6.py' -v
# GitHub Actions: .github/workflows/trippower-a-rev6.yml
kicad-cli sch erc --severity-all --exit-code-violations --format json -o rev6-erc.json \
  hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_sch
kicad-cli sch export netlist -o rev6-a.net hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_sch
python3 tools/check_trippower_a_rev6_native_netlist.py rev6-a.net
kicad-cli sch export bom -o rev6-bom.csv hardware/modules/TripPower_REV6_A/TripPower_REV6_A.kicad_sch
```

**Erster erfolgreich beobachteter historischer Basislauf (aktuelle 3-Varianten-CI siehe Bericht oben):** [KiCad-10 GitHub Actions Run 38813768801](https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38813768801), SHA `17318999a066a2ac511f59eaf256ce154045157b`, Job `116693210258`: **9/9 Python-Regressionstests**, native KiCad 10 **0 ERC-Verstöße**, native 25-Pinpositions-/FET-Orientierungs-/PGOOD-Topologie validiert, nativer BOM-Export 25 Positionen, Aktions-Artefakte hochgeladen. Die spätere reine Einkaufslisten-Aktualisierung verändert weder Schaltplan, Bibliothek noch Tests; aktueller Workflow-Status pro GitHub Actions separat prüfen.
