# TripTracer V1 – Kaufmodule zuerst: 12/24-V-Eingang und 5 V / 2 A

**Stand: 14.10.2026 · Status: COTS-Marktvergleich / elektrischer Konzeptkandidat, NICHT KiCad-integriert, NICHT ERC-/DRC-/Labor-/ISO-geprüft.**

## Verbindliche Entwicklungsstrategie (COTS first)

**Vor einer eigenen Schaltung prüfen wir erst fertig kaufbare, spezifizierte Lösungen.** Reihenfolge:

1. Vollständiges fertig bestücktes, dokumentiertes Modul mit passend spezifiziertem Eingangsbereich, Leistung, Temperatur, EMV, Schutz und Schnittstellen; inklusive Lieferbarkeit, Footprint und realer Kosten.
2. Integrierter Funktionsbaustein / Power-Modul oder Schutz-IC mit einem **nachbaubaren Hersteller-Referenzdesign**; die wenigen vom Hersteller vorgesehenen externen Bauteile übernehmen und prüfen.
3. Etablierte, bestellbare Schaltung aus Hersteller-EVM/Application Note (EVM-Preis und echter Teilepreis getrennt betrachten).
4. **Erst wenn diese Optionen nachweisbar nicht sinnvoll passen**, eigene Schutz-/Regler-Topologie entwickeln. Eigenentwicklung nur mit dokumentiertem Nutzen (Stückkosten, Abmessungen, Verfügbarkeit, Leistung, Safety).

**Vergleich gilt für jede Baugruppe**, nicht nur die Versorgung: Spannungswandler, Eingangsschutz, Lade-/Power-Path, USB, Anzeige, GNSS, Speicher, Taster, Beleuchtung, Gehäuse. Bei gleicher Funktion/Qualität sind geprüfte Lösungen mit weniger Bauteilen, Lötaufwand und Fehlerrisiken zu bevorzugen. Keine Hobby-Platine ohne Grenzwert-/Temperatur-/EMV-Daten als Fahrzeuglösung behaupten. Kostenvergleich immer auf gleichem Funktions- und Schutzumfang.

## Maßgebliche Anforderungen für diesen Vergleich

| Anforderung | Aktuelle Projektvorgabe |
| --- | --- |
| Fahrzeugnetze | 12 und 24 V, Normalbetrieb **9–30 V**, nicht historisch 9–36 V |
| Motorstart | **~9 V weiches Betriebsziel** (Beschluss 14.10.2026), **kein** garantierter 6-V-Dauerbetrieb; sicherer Reset unterhalb möglich |
| Geregelter Ausgang | **5 V / bis 2 A**, Reserve und Thermik noch mit realem Lastprofil prüfen |
| Fahrzeug-Eingang | Verpolung, ISO-16750-2-/ISO-7637-2-relevante Transienten, sichere Überstrom-/Kurzschlussbehandlung und Leitungsabsicherung |
| Load Dump | Zentral begrenztes **Test-B-Profil** und gesondertes ungedämpftes **Test A bis ~202 V** unterscheiden; A bleibt ungeprüft, nicht automatisch bestanden |
| Fahrzeugleitung | **BAT+ und ACC separat fahrzeugseitig geeignet abgesichert**; keine wartungspflichtige eingelötete Sicherung |
| Bedienung | ACC-Wakeup + MCU-HOLD/Abschalt-Nachlauf, BAT+-OFF-Ruhestromziel <100 µA |
| USB-C | 5 V nur für Flash-/Servicebetrieb ohne M8; keine Rückspeisung, M8 hat Vorrang |
| Nachweise | KiCad-10-Projekt mit projektlokalen Bibliotheken; ERC, DRC, Messungen, automotive Schutz-/EMV-/Thermiktests vor Freigabe |

Ältere Dokumente und KiCad-Blätter enthalten teilweise noch überholte 6-V-/36-V- oder frühere IC-Vorgaben. Im Konflikt haben die **jüngsten ausdrücklichen Nutzerentscheidungen vom 14.10.2026** Vorrang; bestehende Schaltungen aber nur nach eigener Revision tatsächlich ändern.

## Fertig verfügbare Kandidaten, zuerst vergleichen

| Option | Regler | Schutz-/Schaltweg | Potenzial / wesentliche offenen Punkte |
| --- | --- | --- | --- |
| **A: günstiger THT-Kaufwandler** | **RECOM R-78K5.0-2.0L**, 6,5–36 V auf 5 V / 2 A, SIP3 | **TI LM74800-Q1** mit back-to-back MOSFETs nach TI-200-V-Load-Dump-Referenz und zusätzlichem *nachgewiesenem* Überstrom-/Kabelschutz | Minimiert Buck-Entwicklungsaufwand, gut handlötbar. **Kein EN-Pin am 3-Pin-Modul**, daher ACC/MCU-HOLD und <100 µA mit vorgeschaltetem Abschaltpfad erst nachweisen. **LM74800 ist keine eFuse**. Bei 30 V normaler Obergrenze reichen pauschal 33-V-OVP und 36-V-Maximalrating nur nach Toleranz-/Transientenrechnung aus. |
| **B: Kaufwandler + integrierter elektronischer Schutz** | Gleicher **RECOM R-78K5.0-2.0L** | **TI LM74930-Q1**, geeignete externe MOSFETs, Shunt und Referenzbeschaltung für Überstrom-/Kurzschlussschutz | Teurerer Controller; Gegenwert ist ein spezifizierbarer elektronischer Leistungsschutz. Externe Quell-Sicherungen bleiben nötig. Wieder ACC-/OFF-Pfad und 36-V-Modulgrenze prüfen. |
| **C: flaches SMD-Power-Modul** | **RECOM RPH-3.0-CT**, 4,5–55 V Eingang, auf 5 V einstellbar / 3 A, **ON/OFF-Eingang** | Wie A oder B, entsprechend gefordertem Sicherheits-/Fehlerumfang | Funktionell attraktiv: EN vereinfacht HOLD, größerer Eingangsspannungs-Spielraum. **47-Pad-QFN**, Zusatzbeschaltung und thermisch sauberes PCB erforderlich; Eigenbestückung und Moduleffizienz/Thermik überprüfen. |
| **D: bisheriger integrierter Automotive-Buck** | **TI LMR38020-Q1**, 4,2–80 V, 2 A, AEC-Q100, mit EN und integrierter Strombegrenzung | Bestmöglich einfacher, validierter Verpol-/Transienten-/Leitungsschutz nach dem tatsächlichen Testprofil | Kein fertiges Komplettmodul; externe Spule, Kondensatoren und Layout/EMV-Nachweis. Kann **preiswerter und platzsparender als Module** sein und bleibt bis zum Vergleich die aktuelle aktive Entwicklungswahl im Branch. Seine 80 V sind **kein** Beweis für Überstehen des ungedämpften 202-V-Test-A. |

**Empfohlene Prüf-Reihenfolge:** A als handlötbaren Budget-/Entwicklungsreferenzpunkt und C als SMD-Alternative vermessen/preisen; B mit dem tatsächlich nötigen Kurzschluss-/Brand-Schutz vergleichen; D anhand kompletter Stückkosten statt nur IC-Preis als Gegenprobe weiterführen. **Noch kein Hardware-Swap und keine Änderung der freigegebenen Anforderungen aus dieser Marktstudie ableiten.**

## Exemplarischer Teilekorb für Option A – KEINE freigegebene Bestell-BOM

| Funktion | Hersteller-MPN / Referenz | Stück | Bemerkung |
| --- | --- | ---: | --- |
| Buck-Modul | RECOM **R-78K5.0-2.0L** | 1 | 5 V / 2 A; SIP3; evtl. externe Ein-/Ausgangsfilter |
| Ideal-Diode-/OV-Controller | TI **LM74800QDRRRQ1** | 1 | **Ohne** eigene Überstromabschaltung |
| Load-Dump-Leistungstransistor | **250-V-MOSFET** wie onsemi **FQD16N25CTM** | 1 | Nur Kandidat; RDS(on), VGS, SOA, 202-V-Puls, Verlustleistung und Footprint prüfen. Nicht den zuvor grob genannten 200-V-FET ungeprüft verwenden. |
| Zweiter MOSFET | z. B. IRLML0060TRPBF (60 V) | 1 | Nur Kandidat; 60-V-VDS, Gate, Impuls und Temperatur mit konkreter Klemme verifizieren |
| Transienten/Zener/Dioden | Beispiel aus dem **TI LM74800-Q1 200-V-Referenzdesign**: SMBJ33CA, SMBJ150A und passende weitere Dioden | nach Design | Kein DIY-Neu-Design; reale Hersteller-BOM, Polung, Impulsfestigkeit, Kondensator-/Widerstandwerte erst gegen Datenblatt übernehmen |
| Eingangsspeicherung, HF-Filter und R/C | Nach Referenzdesign, EMV-/Layout-Validierung | nach Design | Spannungsklasse, Derating, Leckstrom bei warm/heiß, Lastsprünge |
| Überstrom-/Leitungsschutz | Fahrzeugseitige BAT+/ACC-Sicherungen plus ggf. elektronischer Geräteschutz | nach FMEA | **Fehlt** in der bloßen Kombination LM74800 + RECOM; ohne Nachweis keine Freigabe |
| ACC/MCU-HOLD und USB-Power-Path | Bestehende TripTracer-Anforderungen | nach Design | Modul ohne EN braucht echte Eingangstrennung, damit AUS-Ruhestromziel eingehalten wird |

**Kostenvergleich, ausdrücklich noch nicht vollständig:**

- RECOM R-78K5.0-2.0L bei Reichelt DE: **5,35 € / 1 Stück inkl. 19 % MwSt.**, zzgl. Versand (Anzeige im Recherchezeitpunkt 14.10.2026).
- RECOM RPH-3.0-CT bei Mouser DE: **7,89 € / 1 Stück**, **7,76 € / 10 Stück**, zzgl. maßgeblicher Steuern/Versand (Recherchezeitpunkt).
- TI LMR38020FSQDDARQ1 bei Mouser DE: **4,01 € / 1 Stück**, **3,02 € / 10 Stück**, **2,50 € / 100 Stück**, **nur der Regler-IC** (Recherchezeitpunkt).
- LM74800, FETs, TVS, Ausgangsfilter, Überspannungs-/Leitungsschutz, ACC-HOLD, USB-Entkopplung, Montage, Leiterplatte und Versand **nicht zu einer belastbaren Gesamtsumme kalkuliert**. Die in der vorigen Unterhaltung genannte Spanne **11–14 € war eine unvollständige Schätzung**, kein verifizierter Komplettpreis. Preise in USD und EUR, brutto und netto **nicht addieren**.
- Die teure TI **LM74800EVM-CS** ist eine Entwicklungs-/Referenzplatine, nicht die preisgünstige Kleinserienlösung. Das TI-Referenzdesign ist nutzbar, die Schaltungsübernahme muss gegen Herstellerrevision, MOSFETs und Automotive-Profile geprüft werden.

## Nachweise vor Auswahl und Umsetzung im KiCad-Projekt

- [ ] Marktcheck aktualisieren: vollständige Module und Schutz-ICs, aktive Hersteller-MPN, verfügbare Menge 1/10/100, End-to-end BOM inkl. Beschaffung/Bestückung.
- [ ] 9/12/24/30 V bei 5 V / 2 A unter Temperatur; Effizienz, Thermik, Output-Ripple, Lastsprünge, 3,3-V-Folgeregler und GNSS-EMV prüfen.
- [ ] ~9-V-Startprofil und definierte Unterspannungsfolge; 30-V-Dauergrenze + Toleranzen / OVP-Maximalwert des 36-V-Moduls prüfen.
- [ ] Hersteller-200-V-Referenzschaltung mit **belegtem** MOSFET-SOA und thermischen Sicherheitsgrenzen übernehmen; zentral begrenztes Test B und ungedämpftes Test A getrennt bewerten.
- [ ] Gefährliche Kurzschlüsse vor und hinter Regler, defekten FET, Sicherungs-Auslöseverhalten und Brandrisiken per FMEA prüfen; LM74800 ersetzt **keine** eFuse.
- [ ] BAT+-AUS-Strom <100 µA inklusive Modul-Abschaltpfad, TVS, OVP-Teiler, MCU-HOLD und ACC-Fehlerfälle prüfen.
- [ ] USB/M8-Power-Mux und Rückspeisung, Firmware-Service, SD-Flush/ACC-AUS durchtesten.
- [ ] Projektlokale KiCad-10-Symbole/Footprints/3D-Modelle, ERC/DRC, reale Prüfungen; erst **danach** BOM- und Fertigungsfreigabe.

## Quellen / direkt kaufbare Lösungen

- [RECOM R-78K5.0-2.0L – Herstellerdaten](https://recom-power.com/de/products/switching-regulators/switching-regulators-sip/rec-p-R-78K5.0-2.0L.html)
- [RECOM R-78K5.0-2.0L – Reichelt](https://www.reichelt.com/de/en/shop/product/r-78_dc_dc_converter_6_5_-_36_vin_single_5_vout_2000_ma_sip-422394)
- [RECOM RPH-3.0-CT – Hersteller-Serie](https://recom-power.com/en/rec-s-RPH-3.0.html)
- [RECOM RPH-3.0-CT – Mouser](https://www.mouser.de/de/ProductDetail/RECOM-Power/RPH-3.0-CT)
- [TI LM74800-Q1 – 200-V-Load-Dump-Referenz im Datenblatt](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf)
- [TI LM74800EVM-CS – Evaluierungsboard](https://www.ti.com/tool/LM74800EVM-CS)
- [TI LM74930-Q1 – integrierte Überstromschutzfunktionen](https://www.ti.com/product/LM74930-Q1)
- [TI LMR38020-Q1 – Automotive-Reglerdaten](https://www.ti.com/product/LMR38020-Q1)
- [TI LMR38020FSQDDARQ1 – Mouser-Preis und Verfügbarkeit](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LMR38020FSQDDARQ1)
- [Bestehende Kosten- und Sicherheitsvergleiche](POWER_VARIANTS_COST_SAFETY.md), [aktive Kostendokumentation](COST_CONTROL.md), [offene Punkte](OPEN_ITEMS.md).

**Entscheidungsstatus:** Kaufteile-/Referenzdesign zuerst ist **verbindliche Methode**. Die Option **LM74800-Q1 + RECOM R-78K5.0-2.0L** wird ausdrücklich als kostengünstiger **Prototyp-Kandidat** aufgenommen, **nicht** als bereits geprüfte oder schon in KiCad verbaute endgültige Versorgung. Die aktuelle LMR38020-Q1-Baseline bleibt vorläufig bestehen, bis ein funktional gleichwertiger, sicherer, vollständiger Vergleich die Umstellung begründet.
