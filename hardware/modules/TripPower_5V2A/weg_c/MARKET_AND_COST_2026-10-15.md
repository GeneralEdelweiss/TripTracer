> **KORREKTUR 15.10.2026: Die folgende fruehe C1-Bevorzugung gilt nicht mehr als Fertigungsempfehlung.** C1 muss bis zur Schliessung der NO-GO-Gates gesperrt bleiben, siehe [C1_SURGE_AUDIT_2026-10-15.md](C1_SURGE_AUDIT_2026-10-15.md) und [C2_HV_80V_ALTERNATIVE_2026-10-15.md](C2_HV_80V_ALTERNATIVE_2026-10-15.md). Vorherige IC-Teilpreise lassen 2x teure 300V MOSFETs weg und duerfen **nicht** als echte BOM-Preise verstanden werden. Qualifizierte 200V-/125C-Loesung weiter ausstehend.

# Weg C — Markt-, Architektur- und Vollkostenvergleich (15.10.2026)

Recherche ausschliesslich auf Basis der Anforderungen, ohne Berichte/Schaltungen aus Weg A/B auszuwerten. **Preise sind Momentaufnahmen in EUR/Stueck netto (ohne MwSt./Versand), keine Angebote.** Verfuegbarkeitsstatus aendert sich. Nicht bestueckte Lieferantenartikel zaehlen nicht als fuer 100 Stueck sicher erhaeltlich.

## Konkrete aktive Kandidaten

| MPN / Hersteller | Daten / Grenze | Stand der Bezugsquelle | EUR 1 / 10 / 100 | Quelle |
|---|---|---|---|---|
| AP74502HQTA8-7, Diodes | 3.2..75 V normal, 2x externe MOSFETs, Verpol/OVLO, 200-V-Demo nur mit Zusatzklemmung; −40..125 C | Mouser EU gelistet/Bestand im EU-Listing; DigiKey DE 0 | 0.636 / 0.450 / 0.352 | https://www.mouser.lt/en/ProductDetail/Diodes-Incorporated/AP74502HQTA8-7 |
| TPS26631PWPR, TI | 4.5..60 V, 31mOhm eFuse, einstellbar ~0.6..6 A, Auto-Retry | Mouser DE 57 lieferbar, 100 nicht sofort | 3.89 / 2.96 / 2.46 | https://www.mouser.de/de/ProductDetail/Texas-Instruments/TPS26631PWPR |
| TPSM33620S5QRDNRQ1, TI | 3..36 V, integrierte Spule/Boot, 5 V / 2 A, AEC-Q100 Grade 1; Tj max 150 C | Mouser AT EU 5,286 lieferbar | 1.99 / 1.96 / 1.86 | https://www.mouser.at/en/ProductDetail/Texas-Instruments/TPSM33620S5QRDNRQ1 |
| LMR43620RS5QRPERQ1, TI | 3..36 V, 5V/2A Buck, separate Spule, einstellbare Frequenz; -40..125 C TA | Mouser EU 0 Lager, Bestellung | 3.67 / 2.79 / 2.31 | https://eu.mouser.com/de/ProductDetail/Texas-Instruments/LMR43620RS5QRPERQ1 |
| LTC4366HTS8-2#TRMPBF, ADI | >500V Surge-Stopper, erneuter Anlauf nach Schutz-/Timerzyklus; **H-Grade** fuer +125C | DigiKey DE gelistet, aktuell Bestand erneut pruefen | 9.74 / 7.622 / 6.509 | https://www.digikey.de/ (gezielt MPN suchen) |
| AUIRFS6535TRL, Infineon | Automotive AEC-Q101, N-MOS 300V, 185mOhm max @10V, D2PAK, 175C | MPN aktiv, Grosshaendlerbestand/Einzelpreis **noch nicht belastbar verifiziert** | kein belastbarer EUR-Preis | https://www.infineon.com/part/AUIRFS6535 |
| R-78K5.0-2.0L, RECOM | integriertes DC-DC-Modul 5V/2A | Marktuebersicht; bei +125C Vollast **keine Freigabe** | nicht vergleichbar/ungeeignet | https://recom-power.com |

## Rechnerisch nachvollziehbare **IC-Teilsummen** ohne FET und Passiva

| Architektur | 1 St. | 10 St. | 100 St. | Einheit |
|---|---:|---:|---:|---|
| C1 AP74502HQ + TPS26631 + TPSM33620S5 | **6.516** | **5.370** | **4.672** | EUR/Geraet netto |
| C2 AP74502HQ + TPS26631 + LMR43620RS5 | 8.196 | 6.200 | 5.122 | EUR/Geraet netto |
| C3 LTC4366H-2 + TPS26631 + TPSM33620S5 | 15.620 | 12.542 | 10.829 | EUR/Geraet netto |

**Nicht als Vollkosten verkaufen:** Die obigen Betraege enthalten **nur die drei Haupt-ICs**. Fuer einen fairen Vollkostenvergleich muessen MOSFETs (C1/C2 mindestens 2x, C3 mit Rueckpolschutz ebenfalls), HV-Pulswiderstaende, HV-Zener/TVS, Versorgungskapazitaeten, Widerstaende, Induktivitaet (C2), Buchsen, externe Sicherung/Fassung sowie PCB/Montage eingepreist werden. Keine erfundenen Livepreise fuer diese offenen MPNs.

### Transparentes indikatives Budget (NICHT Lieferangebot)

Annahme nur zur Architekturentscheidung: Zwei HV-MOSFETs zusammen 4–12 EUR, sonstige zwingende Schutz- und Passivbauteile zusammen 3–9 EUR bei 1 Stueck bzw. 2–6 EUR bei 10 und 1.5–5 EUR bei 100; C2 zusaetzliche Spule mit 0.8–3 EUR/Stk. C3 zusaetzlicher Verpolschutz mit 1–4 EUR/Stk. **Diese Spannen sind unbestaetigte Budgetannahmen und duerfen nicht fuer Einkauf/Produktkalkulation verwendet werden.** Annahme bei 10 Stueck fuer MOSFETs 3–9 EUR; bei 100 Stueck 2–8 EUR.

| Architektur | 1 St. EUR netto indikativ | 10 St. EUR netto indikativ | 100 St. EUR netto indikativ |
|---|---:|---:|---:|
| C1 | 13.52–27.52 | 10.37–20.37 | 8.17–17.67 |
| C2 | 16.00–32.20 | 12.00–24.20 | 9.42–20.12 |
| C3 | 23.62–40.62 | 18.54–31.54 | 15.33–27.83 |

Alle diese Budgets **ohne** PCB, Loetpaste, Schablone, Stecker, F_MAIN, MwSt. und Versand. Erst nach MPN/Footprint-Fixierung und tatsaechlichen Warenkorbpreisen gibt es echte Vollkosten.

## Technische Bewertungsmatrix

| Kriterium | C1 Module | C2 Regler mit Spule | C3 HV-Surge-Stopper |
|---|---|---|---|
| Anzahl Versorgungshaupt-IC | 3 + 2 FET | 3 + 2 FET + L | 3 + HV FET + zusaetzliche Reverse-Sperre |
| 200V / 350ms mit IC-Datasheet allein bewiesen? | NEIN | NEIN | NEIN |
| 9V Start / 30V Relaunch plausibel? | JA, noch messen | JA, noch messen | JA, noch messen |
| RAW/eFuse mit Kurzschlussabschaltung | gemeinsam | gemeinsam | gemeinsam |
| +125C / 2A / 30V **gesichert**? | NEIN | NEIN | NEIN |
| Handmontage | SOT28 + HTSSOP + 11Pin QFN-Modul | SOT28 + HTSSOP + QFN-Regler + Spule | TSOT8 + HTSSOP + Modul |
| Mindestzahl externer Reglerteile | ca. 4 bei C1 | Induktivitaet + Ein-/Ausgangs-Cs + VCC/Boot + RT | ca. 4 |
| Schutz-IC-HV-Marge | Externe VIN-Klemmung erforderlich | dito | >500V-Controllerfestigkeit |
| Entscheidung | **Vorlaeufig bevorzugt** | Thermik-Backup | teure HV-Backup-Variante |

**Wichtiger Einzelbefund:** Mit 9 V Eingang, 10 W an 5 V / 2 A, angenommen η=90% und 1 A RAW fliessen am gemeinsamen Eingangs-Pfad bereits 10/(9×0.9)+1 = 2.235 A, bevor Eigenverbrauch/Verlust der beiden HV-FETs eingerechnet werden. Bei z.B. 185mOhm pro FET waere P = 2×I²×0.185 = 1.85 W bei 25-C-RDSon. Bei 125C ist die thermische Lage schlechter. Ein 300-V-MOSFET ist allein wegen seiner Spannungsfestigkeit **nicht** automatisch freigegeben.

## Referenzen

- Diodes: https://www.diodes.com/datasheet/download/AP74502Q_AP74502HQ.pdf
- TI eFuse: https://www.ti.com/lit/ds/symlink/tps2663.pdf
- TI Modul: https://www.ti.com/lit/gpn/TPSM33620-Q1
- TI Buck: https://www.ti.com/lit/ds/symlink/lmr43620-q1.pdf
- ADI Surge: https://www.analog.com/media/en/technical-documentation/data-sheets/436612fe.pdf

## Nachtrag: 50-V-/16-V-Passivbauteile (15.10.2026)

Konkrete tatsaechliche MPN-Kandidaten: C3 **C1210C105K5RACAUTO** 1uF/50V AEC-Q200, C4 **C1210C475K5RACAUTO** 4.7uF/50V AEC-Q200, C5/C9 **C1206C104K5RACTU** 0.1uF/50V (nicht AEC), C6 **C1206C105K4RACTU** 1uF/16V (nicht AEC), C7/C8 **C1210C226K4RACTU** 22uF/16V (nicht AEC). Handelslisting DigiKey DE bestaetigt bis 125 C (C4 C3 Automotive; die drei CTU Commercial-Grade). C3/4/5/6/7/8/9 sind nun mit realen MPNs hinterlegt, ihre DC-Bias-Kapazitaet, Loetprozess und Toleranzreserve sind nicht freigegeben.

- C3 DigiKey 1 St. 0.48 EUR, 10 St. 0.295 EUR, 100 St. 0.1985 EUR (https://www.digikey.de/de/products/detail/kemet/C1210C105K5RACTU/502005 ist nicht C3; fuer C3 exakter AEC-Artikel: https://www.digikey.de/de/products/detail/kemet/C1210C105K5RACAUTO/3314552; Preis vor Bestellung separat bestaetigen.)
- C4 DigiKey in stock 131,393, 0.88 EUR pro St. (https://www.digikey.de/de/products/detail/kemet/C1210C475K5RACAUTO/3315039).
- C5/C9 DigiKey 2,290,423 stock, 0.12/0.066/0.0394 EUR bei 1/10/100 Stueck (https://www.digikey.de/de/products/detail/kemet/C1206C104K5RACTU/411524).
- C7/C8 DigiKey 65,209 stock, 0.70/0.439/0.3065 EUR bei 1/10/100 Stueck (https://www.digikey.de/de/products/detail/kemet/C1210C226K4RACTU/5023254).

Tabellenwerte C2/C3 100 St. korrigiert: Induktivitaet und zusaetzlicher Verpolschutz waren vorher in der Untergrenze uebersehen worden.
