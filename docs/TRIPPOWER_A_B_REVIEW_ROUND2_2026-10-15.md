# TripPower A/B – unabhängiger Management-Review Runde 2 (2026-10-15)

**Vergleichsstand:** Weg A `3b88162a8afa5a4c2f46a8018158f22a7f1902f9`; Weg B `1fd96c7dbd43193beb907f6e51a7aa39902d765e`; gemeinsame Basis `2cafbf43e24aadc12ede10cd413b962c84579664`. Dieser Review ändert ausschließlich `design/trippower-review`.

**Freigabe:** KEINE Hardware-, Fahrzeug-, ISO-, Fertigungs-, 9-V-, 200-V-, PCB- oder Thermikfreigabe. Prüfaussagen sind nach Herkunft zu unterscheiden: im Repo verfügbare Quellen/Skripte, statische Auswertung, hergeleitete Szenarien, nicht vorhandene reale Messungen.

## 1. Fortschritt seit Review 1

| | Weg A | Weg B |
|---|---|---|
| Commits ggü. `design/solid-state-power-v1` | 16 | 6 |
| Branch-Änderungen | 1 Bericht alt, 1 neuer Bericht, 4 Python-Dateien + 1 GitHub-Workflow | 1 Bericht alt, 1 neuer Bericht, 2 Python-Dateien, BOM-Delta CSV + 1 GitHub-Workflow |
| Reproduzierbares Modell | Ja, VS-Precharge/Pump/FET, RVS/TVS/Zener/Energie/Sensitivitäten | Ja, OV-Schwellen, dynamische Szenarien, BOM-/Thermik-/Kostenabschätzungen |
| Native KiCad-Checks | A-Workflow **konfiguriert**, eigener Schutznetzlistenprüfer / KiCad-ERC; tatsächlicher erfolgreicher CI-Run hier **nicht** bestätigt | Kein KiCad-Layout/-Schema, bewusst wegen No-Go; Python-Workflow konfiguriert; erfolgreicher CI-Run nicht bestätigt |
| Physisches PCB/Messung | Nein | Nein |
| Geänderte elektrische REV5-Hardware | Nein | Nein |
| P01–P10 | offen | offen |

Ein vorhandenener Python-Test oder Workflow ist noch kein belegter CI-Pass. Die abgefragten GitHub-Commit-Statusobjekte für beide HEADs enthielten keine bestätigenden Statusmeldungen; das ist nicht gleichbedeutend mit dem Beweis eines fehlgeschlagenen Actions-Runs.

## 2. Review Weg A: Hauptpfad beibehalten

**A2-01 POSITIV: echte Prüfartefakte.** `tools/trippower_a_model.py`, `test_trippower_a_model.py`, `check_trippower_a_netlist.py`, `test_trippower_a_netlist.py` und Workflow liefern dokumentierte Rechnungen, Sensitivitätsfälle und Pin-Netzlistenregressionen. Schutzkette kontrolliert u.a. Q301 D2=VIN_FUSED/S3=SOURCE_A, D303 K1=VIN_FUSED/A2=TVS_STACK, D301 K1=VS_CLAMP, D302 K1=VS_CLAMP/A2=SOURCE_A und R313–R315. Mutationstest soll vertauschte D303-Pins und Kurzschluss von R314 erkennen. **Vor Übernahme nativen GitHub-Action-Run und Testartefakt prüfen; Tests hier nicht selbst in KiCad ausgeführt.**

**A2-02 KRITISCH: Q301 und TVS-Stack nicht gesichert.** Serieller TVS-Breakdownmin 167+36,7=203,7 V (unter jeweiliger Hersteller-I(V)-Prüfbedingung) bedeutet keine zugesicherte 200-V-Plateau-Klemmwirkung; unterschiedliche IPP-Klemmpunkte dürfen nicht addiert werden. Vishay Q301 250-V-VDS-Grenze lässt ideal 50 V zur 200-V-Spitze, aber keine garantierte SOA-Marge bei realer Quellenimpedanz, Kabel-L und thermisch heißem Abschalten. Das Modell lässt hot-SOA richtig offen.

**A2-03 KRITISCH NEUER EINZELFEHLER: D301 offen.** Unter explizitem Null-Last-/Ideal-Ceff-Modell steigt VS bei 200V-350ms /21µF aus VS0 auf rund 163V; die spezifizierte VS-Betriebsgrenze 65V wird modelliert nach ~82ms überschritten, bei VS0=56V bereits nach ~13ms. Zusätzlich sind C302/C308/C312 mit 100V spezifiziert. Dies beweist nicht den realen Pfad, zeigt jedoch, dass **F_MAIN wegen nur ca. 20mA über 9,9k kein garantiertes Einzelfehler-Mittel** ist. Die vollständige Hersteller-Pin/Schalt-/Fehlerpfadprüfung hat Priorität vor Komponentenreduktion.

**A2-04 PULS-Rechnung nur Screening:** Nominal 14,545mA, 0,244J pro 3,3k, 0,285J Zener /350ms bei angenommener fester 56V-Klemme. D301-Kurzschluss, RVS-Einzelkurzschluss und TCR-Ecken erweitert. **Noch keine** Verifikation der exakten Widerstands-350ms/125C-Puls-SOA, Zener-Zth und Wiederholung.

**A2-05 9V Modell nicht als Garantie missverstehen.** Nominales 21µF ist kein Ceff-min, `pre_ready_load_ua=35`, `additional_pump_ma=2`, `pump_interval_ms=2`, `timer_delay_ms=250` und SOURCE_A-Feed nach 2ms sind sensitivitätsbasierte Annahmen. Modell meldet korrekt Fehlschlag bei hypothetischen 155µA Last. Ein echtes Grenzwertmodell braucht die vollständige TPS38-CTR/RESET- und LM74930-CAP-/VS-Dynamik bzw. Hardwaremessung. `vin_v=0`-Fall ist **kein** Nachweis über RUN-Rückspeisung, weil `source_a_can_rise=False` vorgegeben wird.

**A2-06 Qualitätslücke für nächste Runde:** Modelltests überprüfen überwiegend eigene Konstanten/Ergebnisse des Modells. Ein erfolgreiches Unit-Test-Ergebnis validiert die Rechnungsimplementierung, **nicht** die Modelladäquatheit oder Bauteilsicherheit. Datenblattkurven und reale Messungen fehlen.

## 3. Review Weg B: No-Go des 36V-Einfachtausches anerkennen

**B2-01 POSITIV:** `verify_b_feasibility.py`, Regressionen, CSV-Positionsvergleich, GitHub-Workflow. Die ausgewiesene No-Go-Entscheidung ist transparent begrenzt: kein Nachweis einer **einfacheren/sicher qualifizierten** TPSM33620-Architektur, **kein universeller Beweis** dass ein 36V-Modul physikalisch nie geschützt werden könnte.

**B2-02 Statische Schwellen sind keine dynamische Garantie.** TPS3760-Teiler 940k/23,2k liefert kalkuliert Rising 32,153..34,302V und Falling 31,499..33,628V. Statisch mögliches 30V-Restart; aber unter Hersteller-Testbedingungen nur partielle Sensorzeit bekannt, kein Max `t_EN→Q301_OFF`, kein garantierter Default-Off vor Supervisor-POR, kein VIN-Pad-Klemmwert bei Leitungstransienten. Für TPSM gilt 36V empfohlen und 40V absolut maximal (TI). Die im Bericht verwendeten 0,1Ω/4,7µF-Stufenszenarien sind ausdrücklich **hypothetische Gegenbeispiele**, keine bewiesene ISO-Wellenform. Auch 24us=17us Sense + angenommene 7us ist **kein Hersteller-Maximalwert** für den gesamten FET-off-Pfad.

**B2-03 Keine echte Teileersparnis belegt.** Aktiver Buck A=12 Plätze, B-Referenz=6 plus 5 Positionen für OV = 11, somit nur **-1 bestückter Platz** *vor* zusätzlichem fail-off, Padschutz, Dämpfung. Ein beispielhaftes +3 würde +2 Plätze ggü. A verursachen. Preisbelegte IC-Teilmengen B gegenüber A +0,51€/+0,738€/+0,81€ für Stückzahl 1/10/100 vor fehlenden Passiven, Leiterplatten- und Bestückkosten; kein belastbarer Gesamtpreis. B ist daher kein nachgewiesener Netto-Vorteil.

**B2-04 125°C/2A nicht qualifiziert.** Aus dem rein hypothetischen 22K/W- oder 35K/W-Gesamtheat-Ansatz ergibt sich ein Wirkungsgradbedarf ~89,8% oder 93,33%; echte Layoutverluste und TJ hängen von Board ab. A ist thermisch ebenfalls noch ungeprüft. B muss dafür kein Fake-PCB anlegen.

## 4. Managerentscheidung und nächster technischer Schritt

1. **Weg A = Hauptpfad**, aber P01–P10 bleiben gesperrt. Bevorzugter Fortschritt ist jetzt ein **konkreter, abgesicherter** Vorschlag zur Begrenzung der VS-Domain bei D301-OFF sowie Q301 hot-SOA/TVS-Verifikation. Danach reale 9-V-Startmargen mit Hersteller-Ceff/I(VS,t) oder testbarem Bench-Plan schließen.
2. **Weg B = TPSM-Einfachtausch als NO-GO archivieren**; keine weiteren generischen TPSM-Berichte oder zeitintensiven Footprints. Sinnvolle unabhängige Aufgabe: einen tatsächlich verfügbaren, überprüfbar einfacheren COTS-Schutz-/Buck-Alternativpfad mit ausreichend hoher VIN-Reserve **oder** einen adversarialen Fakten-/Fehlerreview der A-200-V-Sicherheitskette liefern. Kein Rückschreiben auf Weg A.
3. **Nächstes Akzeptanzkriterium:** messbar weniger offene Sicherheitsunsicherheit durch Hersteller-Bounds, ausführbare unabhängige Grenztests oder einen isolierten KiCad-Änderungsvorschlag mit ERC/Netzliste. Keine unbelegte Freigabe aus CI, kein Hardware-Order-Gate.
4. **Plan zur nächsten Review:** von beiden Branches die konkreten GitHub-Action-Run-URLs, Logs und Prüfartefakte anfordern; falsche Pass-Claims nicht zulassen. Kein physischer Test ohne sichere HV-geeignete Prüfeinrichtung.

## Grundlage / Herstellerquellen

- Weg A: `hardware/modules/TripPower_5V2A/WEG_A_EXECUTABLE_P03_P04_P01_EVIDENCE_2026-10-15.md`; `tools/trippower_a_model.py`.
- Weg B: `hardware/modules/TripPower_5V2A/weg_b/WEG_B_ROUND2_TECHNICAL_NO_GO_2026-10-15.md`; `weg_b/verify_b_feasibility.py`.
- REV5-Baseline: `hardware/modules/TripPower_5V2A/REV5_DESIGN_BASELINE.json`.
- TI TPSM33620-Q1: https://www.ti.com/product/TPSM33620-Q1 (36V empfohlen, 40V absolute).
- TI TPS3760-Q1: https://www.ti.com/product/TPS3760-Q1.
- Vishay SQM10250E: https://www.vishay.com/docs/75035/sqm10250e.pdf.
- TI LM74930-Q1: https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf.
