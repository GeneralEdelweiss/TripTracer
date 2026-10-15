# TripPower Weg D – REV6 58-V-V1-BOM / 1–10–100 Kosten- und Vollständigkeits-Audit (2026-10-15)

**Stand: Engineering-Screen, KEINE bestellfertige schaltungsscharfe Gesamt-BOM und kein Freigabe-Schaltplan.** Der Kostenvergleich enthält **sämtliche funktionalen Blöcke**, teils mit noch offenen exakten MPN/Footprints und daher **KEINE** vorgetäuschte Vollkostenangabe. Die ersten Preis-Teilgruppen sind konkrete Hersteller-MPNs mit Menge1/10/100 **€/Gerät NETTO ohne Versand, MwSt., Leiterplatten und Fertigung**. Tatsächliche Lagerstände schwanken. Externe F_MAIN ist in jeder Teilpreisgruppe mit 4A-MINI-58V berücksichtigt, zugehöriger **zertifiziert kompatibler >=58VDC-HALTER IST OFFEN**.

## Kandidatenmatrix / genaue Quellen

| Ref / Funktion | MPN und Hersteller / Beleg | €/St 1 | €/St 10 | €/St 100 | Hinweis |
|---|---|---:|---:|---:|---|
| U_PROT (V3) | **LTC4368HMS-2#WPBF**, ADI **AUTOMOTIVE #W** https://www.mouser.de/ProductDetail/Analog-Devices/LTC4368HMS-2WPBF | 7,5700 | 5,8800 | 4,9900 | Lager-Snapshot 833, MSOP10, H-Grad, 100V Schutz/60V Betrieb. Andere #PBF nicht AEC identisch. |
| Q_PROT1 + Q_PROT2 (V3) | **SIR870DP-T1-GE3**, Vishay 100V, 6mΩ, PowerPAKSO8, https://www.digikey.de/de/products/detail/vishay-siliconix/SIR870DP-T1-GE3/3748958 | **2×2,9300** | **2×1,9100** | **2×1,3256** | **Nur expliziter ADI-Forschungs-/Preis-Platzhalter**; Automotive-Quali, Lager-/PCN-Risiko, Hot-Inrush-SOA noch ungeprüft. Muss vor PCB MPN-seitig ersetzt/validiert werden. |
| U_PROT (V2) | TI **TPS26631PWPR** https://www.digikey.de/de/products/detail/texas-instruments/TPS26631PWPR/12165168 | 3,8700 | 2,9380 | 2,4466 | integriert OCP/OVP-PFET, VIN60V operating/ABS67V, bei +58V ungeklärtem Ringing **NO-GO ohne qualifizierte Zusatzbegrenzung**. |
| U_PROT (Ref C) | TI **LM74801QDRRRQ1**, https://www.digikey.de/de/products/detail/texas-instruments/LM74801QDRRRQ1/13531282 | 2,4600 | 1,8350 | 1,5077 | VIN65V Betrieb, benötigt 2 MOSFETs; kein separater gemeinsamer eFuse-Strommesspfad. |
| U_BUCK (V1/2/3) | TI **LMR38020SQDDARQ1** 80V, https://www.digikey.de/de/products/detail/texas-instruments/LMR38020SQDDARQ1/18177286 | 3,9100 | 2,9650 | 2,4703 | ausgelegt 5V/2A; vollständige Induktor-/Eingangs-/Ausgangs-C-/Feedback-BOM TBD |
| D_TVS (optional V2) | Littelfuse **SMBJ58A**, https://www.digikey.de/de/products/detail/littelfuse-inc/SMBJ58A/688286 | 0,4400 | 0,2720 | 0,1717 | VRWM58V; Clamping bis93.6V bei spez. Kurzpuls, schützt TPS26631 unter67V **NICHT garantiert** |
| D_TVS (V3 optional, NICHT in Preisgruppen) | TI **TVS5800**, https://www.ti.com/product/TVS5800 | TBD | TBD | TBD | speziell niedriges Clamp 75V max bei25A/8-20us, 58V-Standby, Katalog statt AEC; NICHT für350ms-Shuntstrom angenommen |
| F_MAIN externe | Littelfuse **0997004.WXN** 4A/58VDC, https://www.digikey.de/de/products/detail/littelfuse-inc/0997004-WXN/701056 | 0,8900 | 0,6790 | 0,5194 | nur unter **nachweislich bis58V an der Sicherung** gültigem Quellen-/Halterprofil, HOT-Derating, 1000A DC-Ausschalt-/I2t prüfen. |
| F_MAIN-Halter | hersteller-/Spannungs-/Temperaturgeprüfter Halter mind.58VDC | **TBD** | **TBD** | **TBD** | Die im Shop für 997 vorgeschlagenen Standard-MINI-Halter nur 32VDC, dürfen nicht ohne Beleg verwendet werden. |

**Zeitpunkt/Quellen:** 15.10.2026, Abfrage Händlerseiten; Einkauf muss erneut geprüft werden. Vishay 100V PowerPak-MPN ist kein Nachweis für AEC-Q101. Die alte grosse TLD8S36AH-TVS, Bourns SM8S-Q, 250V-FET, LTC4366 und 200V-Zenerzüge erhalten **keine** Serienposition in REV6.

## Rechenbare bekannte Teilpreisgruppen, €/Gerät NETTO (nicht Total-BOM!)

| Variante | 1 Stück | 10 Stück | 100 Stück | Eingerechnete Teile | Entfallene, aber UNBEDINGT noch nachzutragende Posten |
|---|---:|---:|---:|---|---|
| **V1 Buck direkt** | **4,8000** | **3,6440** | **2,9897** | 1× Buck und 1× externe 4A-Sicherung | OVP+Reverse+RAW-Fehler+PWR_FAIL+Temp + passives Buck-BOM + Halter: FEHLT |
| **V2 TPS26631+SMBJ58A** | **9,1100** | **6,8540** | **5,6080** | eFuse+TVS+Buck+F_MAIN | externe Reverse-FET/Schutz, OV-Teiler, PG, Buck-BOM, RAW/Temp/Halter: FEHLT; TVS KEINE 67V-Pad-Sicherheitsgarantie |
| **V3 LTC4368HMS#W + 2x SiR870 + Buck + F_MAIN** | **18,2300** | **13,3440** | **10,6309** | 1× Automotive-Controller +2×100V FET + Buck + F_MAIN | Sense-R, 4 precision R, C_retry, R/C_inrush, PG, RAW/85C/BUCK-L/C, Halter + PCB: FEHLT; MOSFET-Quali offen |
| **TI LM74801Q1+2x SiR870+Buck+F_MAIN** | **13,1200** | **9,2990** | **7,1486** | Controller +2 FET + Buck + F_MAIN | OCP/eFuse/Fault + passive und Thermal fehlt; maximal65V VIN hilft nicht bei unbekanntem Ringing |

**Unterscheidung:** Preisgruppen sind **BOM-Untergrenzen**. Keine Variante ist im derzeitigen Materialstand als vollständiges sicheres Gerät preislich vergleichbar; besonders billige V1/2 stehen nur deshalb niedriger, weil funktional erforderliche Nachweise/Bauteile fehlen. Nicht vorhandene Posten sind **nicht 0€**.

## Exaktes Bauteilpositionsregister V3 / Isolation von Scope

| Ref | Menge | Funktion / nominelle Geometrie / PCB-Bedingung | MPN / Preisstand |
|---|---:|---|---|
| J_VIN | 1 | M8-Typ / Anschluss-Lötpad, 58V inkl Ringing | TBD (TripTracer system, nicht BOM doppelt zählen) |
| F_MAIN + HOLDER | 1+1 | extern austauschbar, >=58VDC DC-Break und gültig bei Einsatztemperatur | 0997004.WXN + HALTER TBD |
| U201 | 1 | LTC4368HMS-2#WPBF, MSOP10 automotive | bekannt |
| Q201+Q202 | 2 | back-to-back N-MOSFET, >=100V, D-S short und reverse current, Hot-SOA | SiR870 Forschungs-MPN, NICHT bestätigt |
| R201 | 1 | ca **15mΩ**, 1% temperaturstabil, Kelvin-Shunt SENSE-VOUT, nominell 2512 | MPN/Preise TBD |
| R202/R203/R204/R205 | 4 | **475k / 1.5M / 121k / 30.2k Ω**, je effektive ≤±0.25% inkl. TCR/Temperatur – 0.1% präzise Typen | Hersteller/MPN/Preis TBD, 30.2k E192 |
| R206/C201 | 1+1 | RGate/RInrush-Cgate aus Hersteller 22k/2.2–3.3nF, Zeitkonstante/SOA | MPN/Preis TBD; nicht blind dimensionieren |
| C202 | 1 | RETRY-Latch-/Cooldown-Dauer (maximale Wiederholenergie) | TBD (alternativ latched RETRY-Anschluss nur nach FMEA) |
| U101 | 1 | LMR38020SQDDARQ1, 80V Buck/2A | bekannt; aus REV5 Stand nicht als neu zahlen |
| L101 | 1 | Buck-Spule; AEC-/Isat/Peak/thermisches Layout bei VIN32/Ta60 | REV5-L101 FCH0650-150M als Vergleich, thermische Bestätigung TBD |
| Buck-Passives | >=6 | HF-Cin 100V, Cout, CBOOT, Feedback-Teiler, RT/SYNC-R, EMV-/Dämpfungsnetz | exakte vollständige 5V-Referenz-BOM aus freizugebendem REV6-KiCad TBD, nicht >=6 als garantierte Stückzahl behandeln |
| J_RAW / RAW OCP | >=1 | 0.5A Kurzschutz auch bei Kurzschluss nur RAW | TBD (Sicherung im Ausgang/Highside-Switch/FMAIN-Leitung) |
| PWR_FAIL / PG-Interface | >=1 | fail-high bezogen auf tatsächlich MAIN_5V/PGOOD, keine GPIO-Backfeed, kein RTC-Dauerpullup | TBD (ggf TripTracer Board statt auf TripPower) |
| HOT_OFF | >=2 | +70°C-Derating/AUS, Ta+85°C unabhängige Temperaturabschaltung über SHDN (NTC/Switch + Bias/Hysterese) | TBD, muss sensor-OPEN/SHORT fail safe prüfen |
| USB/BAT/ACC-Isolation | >=1 | USB-only und Backup-Domain nicht in Fahrzeug/RAW/5V_MAIN rückspeisen | überwiegend TripTracer-Board; exakter Schnittstellen-/Fehlergraph TBD |
| Testpunkte | >=4 | LTCVIN/OV, VOUT/SENSE, buck VIN, PG/FAULT, VIN_FUSED, RAW | PCB-/Fixturekosten TBD |

**Minimaler Vergleich nach echter Architektur:** V3-Schutz-Mindestbauteilzahl mit 1 IC+2FET+1Shunt+4R+2 Inrush +1 Retry = **11 Positionen** (ohne PG/Temp/RAW/FMAIN/Buck), ADI Referenzschema hat sinnvolle Stellplätze und ist relativ 200V-REV5-Schutz viel einfacher. Für PCB-Erstellung müssen alle Schnittstellen vollständig definiert sein; eine symbolische Dummy-Schaltung ohne thermischen OFF-/Rückspeisepfad darf nicht als geeignete V1-Alternative verkauft werden.

## Offene Freigabekosten und thermische Rechnung

- Thermal: bei 10W 5V out und beispielhaft η=90% ≈1.11W Wandlerverlust (ohne RAW, EMV, Kupfer), bei 80% ≈2.5W. Bei +60°C Umgebung muss TI-LMR80V/2A reale TJ,max mit PCB-Kupfer, Schaltfrequenz, 32V, Drosselverlust, SW-Spitzen und 2A Last nachgewiesen werden; +85°C sicher AUS benötigt eigenen Temperatursensor.
- Reverse: Zwei common-source-FETs blocken ohne Defekt, aber INPUT-FET D-S SHORT kann über zweite Bodydiode Spannung an Buck liefern. Da 58V innerhalb 80V Buck-Bereich liegt, ist das **nicht automatisch katastrophal**; muss Kurz-/Temperatur-/Rückspeisefolge trotzdem nachgewiesen werden. RAW steckerseitig mit 0.5A-Ziel abgesichert dimensionieren.
- Installationsanweisung: NUR 12/24V mit zentral *am Gerät* gemessenem Limit58V/350ms und frei geschalteter F_MAIN-Koordination, ungedämpfter200V darf nur externe vorgelagerte zertifizierte Erweiterung behandeln.

**Abschluss BOM: Gesamtpreis NICHT BELASTBAR**, deshalb aktuell keine abnahmefähige PCB-Order-BOM. Die tabellarischen Stückpreise sind transparent und reproduzierbar, nicht imaginäre 0€ für Pflichtteile.
