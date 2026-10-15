# TripPower D Round 6 – vollständige Funktionsabdeckung und dokumentierte 1/10/100-BOM-Grenzen (15.10.2026)

**WICHTIG:** Keine der Architekturvarianten ist technisch freigegeben; daher kann keine vollständige, kaufbare Ersatz-TripPower-BOM mit seriösem Gesamtpreis erstellt werden. Das hier ist ein **vollständiges Register aller benötigten Funktionspositionen**, plus exakt gelistete vorhandene Herstellerbeispiel-Komponenten und **verifizierbare preisliche Untergrenzen**. Fehlende MPN/Preis = **TBD / kein Preisnachweis**, niemals 0€. Ein vermeintlicher Komplettpreis würde ein Sicherheitskonzept vortäuschen, das es noch nicht gibt.

## Einheitliche Vergleichsbasis

- REV5 57 bestückte AUTO/58 RUN Positionen auf Branch-Baseline; inklusive TI LM74930/250V-FET/UV-OV/VS-TPS38/LMR38020 80V Buck und ACC/HOLD, bis heute in OEM-Hot/200V nicht freigegeben. Externe F_MAIN nicht als Bestandteil der 57/58 zählen. Ein D-TVS **nur hinzugefügt** bedeutet **58/59** bestückte Positionen, wenn das Gesamt-Schutzkonzept ansonsten unverändert bliebe – die Sicherheitsgates sind weiterhin offen.
- Alle hier angezeigten EUR-Einzelpreise sind **netto ohne Versand**, sofern nicht als Reichelt brutto markiert. Stückpreise für Menge 10/100 sind Tierpreise **pro** Stück (nicht Zeilensumme); steuern und Versand erst in einer echten Bestellung zusammenziehen.
- Keine zusätzliche Platinen-Prototypfreigabe, kein natives ERC/DRC. Vollständige MPN-Liste der **bestehenden** REV5-BOM liegt in REV5_DESIGN_BASELINE.json nur teilweise als fixierte Schlüsselpositionen vor, nicht als vollständige 57/58-Positionen-Preisdatei. Keine unvollständige Liste als vollständige Serien-BOM ausgeben.

## A. Bekannte Einkaufspreise je Bauteil (1 / 10 / 100 Stück, EUR netto/Teil)

| Funktion | Exakte MPN | Händler / Beleg | 1 | 10 | 100 | Status |
|---|---|---|---:|---:|---:|---|
| TVS A | TLD8S36AH MAG | Reichelt: https://www.reichelt.de/de/de/shop/produkt/tvs-diode_unidirektional_36_v_6600_w_do-218ab-273917 | 1,5546 | 1,4454 | 1,3210 | Reichelt brutto 1,85/1,72/1,572 geteilt durch 1,19; Reichelt-SKU Restposten, Hersteller sonst aktiv; 125°C NO-GO |
| TVS B | SM8S36A-Q, unidirectional | DigiKey DE: https://www.digikey.de/en/products/detail/bourns-inc/SM8S36A-Q/9922432 | 3,7400 | 2,4530 | 1,6200 | aktiv und lagernd bei Abfrage; 10-Pulse-SOA @125°C nicht bestätigt |
| F_MAIN Musterteil | Schurter 0001.2509 3,15A 300VDC | DigiKey DE: https://www.digikey.de/de/products/detail/schurter-inc/0001-2509/639709 | 0,8800 | 0,6730 | 0,5158 | nur Musterkandidat; 33,7 A²s nominal *melting*, DC total-clearing bei 200V/125°C nicht validiert |
| Controller C | ADI LTC4366HTS8-2#TRMPBF | DigiKey DE https://www.digikey.de/en/products/detail/analog-devices-inc/LTC4366HTS8-2-TRMPBF/2825884 | 10,4200 | 8,1740 | 6,9960 | allein kein Schutz |
| OEM-Leistungs-FET C | IXTK90N25L2, 250V TO-264 | DigiKey DE https://www.digikey.de/en/products/detail/ixys/IXTK90N25L2/2117330 | 37,5700 | TBD | 23,5625 | 25er Staffel ≠ 10er Preis, aber 10 × 1er prinzipiell bestellbar |
| vorhandener Buck | TI LMR38020-Q1 MPN im REV5 | historische Repo-Kostenkontrolle, Mouser-Snapshot 14.10.2026 | 4,0100 | 3,0200 | 2,5000 | Teil des gemeinsamen Bestands, nicht als zusätzlicher D-Zukauf doppelt zählen |

Reichelt-Umrechnung 19% USt nur **mathematische Normalisierung**; kein verifizierter steuerlicher Nettowarenkorb. Eine für 100 bestellte Reichelt-Restpostencharge nicht als verfügbar voraussetzen.

## B. Nachweisbar bezifferbare BOM-Untergrenzen, pro Gerät (EUR netto, *kein Vollpreis*)

| Architektur | 1 | 10 | 100 | In Summe enthalten | NICHT enthalten |
|---|---:|---:|---:|---|---|
| D1 TSC-TVS plus 3,15A F_MAIN | **2,4346** | **2,1184** | **1,8368** | 1× TVS, 1× Sicherung | Sicherungshalter, Verpol/OCP/PWR_FAIL/5V/RAW/ACC/BACKUP, PCB/Montage/VAT/Versand |
| D1b Bourns-TVS plus 3,15A F_MAIN | **4,6200** | **3,1260** | **2,1358** | 1× TVS, 1× Sicherung | gleiche nicht ausgelegten Pflichtteile |
| D2 LTC4366-2 + OEM-FET + 3,15A F_MAIN | **48,8700** | **nicht nachweisbar** | **31,0743** | 1× IC, 1× IXTK90N25L2, 1× Sicherung | mindestens 5×R+3×C, Halter, Verpol/OCP/PWR_FAIL/5V/RAW/ACC/BACKUP |
| D2 LTC4366-2 + OEM-FET + F_MAIN, 10 einzelne FETs zum Einzelstückpreis | – | **46,4170** | – | echte **konservative Einkaufsbudgetannahme**, NICHT Händler-10er-Preisstufe | gleicher Rest |

Vergleich: Mehrkosten von Bourns gegenüber TSC bei 1/10/100 nur **2,1854 / 1,0076 / 0,2990 €/St** im TVS-Beschaffungspreis. Ob die Bourns thermisch geeignet ist, bleibt offen; geringe Differenz allein ist kein Grund für Go.

## C. Vollständige physikalische Positionen des ADI-Herstellerbeispiels (keine 9V-Auslegung!)

| Ref | Anzahl | exakte Hersteller-Demo-Funktion | Wert / Teil | Preis 1/10/100 |
|---|---:|---|---|---|
| U_D2 | 1 | Controller | LTC4366HTS8-2#TRMPBF | siehe oben |
| Q_D2 | 1 | linearer Hochvolt-Serien-MOSFET | IXTK90N25L2 | siehe oben |
| R_D2_1 | 1 | Versorgung/RIN (Referenzwert) | 324kΩ, konkrete Automotive-MPN **TBD** | TBD |
| R_D2_2 | 1 | Gate-Serie | 10Ω, konkrete MPN **TBD** | TBD |
| R_D2_3 | 1 | Versorgung/Floating/Bias | 12,4kΩ, MPN **TBD** | TBD |
| R_D2_4 | 1 | Feedback | 422kΩ, MPN **TBD** | TBD |
| R_D2_5 | 1 | Feedback | 46,4kΩ, MPN **TBD** | TBD |
| C_D2_1 | 1 | Gate/Timer-Beschaltung, Referenzschaltbild | 2nF, MPN **TBD** | TBD |
| C_D2_2 | 1 | Versorgung | 0,47µF, MPN **TBD** | TBD |
| C_D2_3 | 1 | Versorgung/Ausgang | 1µF, MPN **TBD** | TBD |
| F_MAIN | 1 | externe Sicherung | 0001.2509 Kandidat | siehe oben |
| F_MAIN_HOLDER | 1 | externe, wartbare Aufnahme | Schurter FEU 0031.1751 600VDC, aber **Ta max85°C** | TBD; bei Ta125°C NO-GO |

**10 Herstellerbeispiel-Elektronikpositionen + externe Sicherung/Halter = 12 Positionen**, **OHNE** die unter D beschriebenen funktional nötigen Blöcke. Referenzwerte müssen für 9V-Anlauf / 30V / 200V / 2A / -40..125°C vollständig neu ausgelegt werden; Benennung einzelner R-Funktionen darf keinen qualifizierten Schaltplan suggerieren. Die 2nF-Zeitkonstante bedeutet nicht 350ms-Festigkeit.

## D. Vollständiges Block-Register für jede hypothetische Ersatz-Architektur

**A = passive TVS direkt als einziger Transientenschutz; B = passive TVS zusätzlich zu REV5; C = LTC4366-2 Serie.**

| Pflichtfunktion / bestückbare Position | A | B | C | heutiger Preis/MPN |
|---|---|---|---|---|
| Eingang BAT+ und GND + realer Hochstrom-Shunt-Pfad | neu auszulegen | bestehender Block + neue TVS-Pads | neu auszulegen | TBD Stecker/PCB |
| Externe DC-Sicherung F_MAIN samt Halter/Kappe und Kabelschutz | notwendig | notwendig | notwendig | SPT 0001.2509 als Kandidat; Halter Ta125°C OFFEN |
| 200V/350ms Transientenbauteil | 1x TVS | 1x zusätzlicher TVS | 1x IC plus 1x HV-MOSFET, 5R/3C | TVS/IC/FET siehe oben |
| Verpol-/Rückstromschutz (auch mit TVS-Kurz-/Open) | **fehlt**, MPN TBD | REV5 muss geprüft werden | **fehlt**, MPN TBD | TBD |
| 9V/30V UVLO/OVLO und Restart auch in Cold/Hot | **fehlt**, MPN TBD | REV5 Status **nicht validiert** | **neu dimensionieren**, MPN TBD | TBD |
| 5V/2A Buck inklusive L/C/R/Filter | ggf. REV5-LMR38020 nur, wenn Padmax erfüllt | REV5 vorhanden, Hot-Gate offen | ggf. bestehender Buck, Schutz-Pad OFFEN | Gesamtpreis TBD |
| RAW1A-Abzweig mit sicheren Kurzschluss-/Fehlerstromgrenzen | **fehlt**, MPN TBD | LM74930-REV5-Schutz, ungeprüft | **fehlt**, MPN TBD | TBD |
| ACC/RUN/HOLD, OFF<100µA, USB/M8-Isolation | **fehlt**, MPN TBD | REV5 Status ungeprüft | **fehlt**, MPN TBD | TBD |
| Fruehes fail-high-PWR_FAIL mit hochohmig bei VIN=0 | **neu**, MPN TBD | **neu**, MPN TBD | **neu**, MPN TBD | TBD |
| TripTracer-Lokalnotzelle, Power-Mux, MCU/SD/FRAM-Only-Switchover | extern und zwingend | extern und zwingend | extern und zwingend | eigene TripTracer-BOM **TBD**; nicht Teil von TripPower |
| Sicheres Verhalten TVS-OPEN oder FET-D-S-SHORT | **NICHT GELOEST** | **NICHT GELOEST** | **NICHT GELOEST** | Prüfnachweis fehlt |
| Laborpunkte, Clearance, Hot-/Leitungs-/Sicherungstransienten | notwendig | notwendig | notwendig | Test-/PCB-Budget TBD |

**Belegbarer Bauteilzahlvergleich:** B gegenüber REV5 = **+1 Elektronikposition**; A gegen REV5 = **unbekannt**, weil keine sicher vollständige Alternative existiert; C gegen REV5 = **unbekannt**, da LTC-Demoboard nicht Verpolung/5V/RAW/HOLD/PWR_FAIL/FMAIN abdeckt. Kein Einsatz für einen Produktiv-BOM-Tausch.

## E. Bedingungen zur Finalisierung einer „wirklich vollständigen“ bestellbaren BOM

Erst wenn TSC/Bourns die max Hot-SOA und worst-case Vpad sowie F_MAIN/TVS-OPEN-FMEA erfüllen oder der LTC4366-Gate-OFF plus FET-short durch geeignetes einfaches System abgesichert ist, werden alle offenen Positionen durch exakte MPN, Pinout, Footprint, 3D-Modell, 1/10/100-Preisstufen, Kälte-/Hitze-Lastwerte und ERC-verifizierte Nets ersetzt. Dann 57/58-REV5 und Kandidat mit gleicher 5V/RAW/ACC/USB/Backup-Funktion, SMD-Bestückzeit, PCB-Fläche, isoliertem F_MAIN-Halter, Steuer/Versand und Prüfdienstleistung vergleichen.

**Gesamtkosten jetzt: NICHT BELASTBAR.** Eine vollständige Liste *fehlender* Pflichtpositionen ist kein vollständiger Serien-BOM-Preis. Dies ist die fachlich ehrliche Antwort auf die Preis-Anforderung statt erfundener Kleinteil-Summen.
