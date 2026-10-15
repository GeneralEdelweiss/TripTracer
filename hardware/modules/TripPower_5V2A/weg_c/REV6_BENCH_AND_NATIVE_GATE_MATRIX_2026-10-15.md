# Weg C — REV6 Hersteller- und Abnahmematrix (stand 15.10.2026)

**Alle Prüfungen außer den unten genannten automatisierten Rechenregressionen sind OFFEN.** Hersteller-/Schaltungsdaten = kein ISO-Prüflauf. Keine Fertigungs-/Fahrzeugfreigabe. Neue abgespeckte Produktziele laut docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md PWR-44–54 haben Vorrang vor altem 200V-REV5.

## A. Bevor ein fertiger KiCad-10-Schaltplan freigegeben werden darf

| Gate | Konkreter Prüfstand, Beobachtung, harte Grenze | Status |
|---|---|---|
| A1 OVLO ACC nach 32V | 0.1% 100k/3.78k TPS26631: statisch bei IC rising32.210..33.685V, falling max31.649V. Mit vorgeschalteter 100V-Diode nach realer Vf(T,I) und OVP-Leckstrom rechnen; **32.000V VIN auch nach Überspannung garantiert wieder EIN** | Rechenhülle in CI, Diode-Vf(T/I) offen |
| A2 Factory-OVP vermeiden | TPS26631 default OVP rising33.2..35.4, falling32.7..35.0V erlaubt NICHT garantierten 32V-Neustart. OVP=GND allein **No-Go**, externen OVP-Teiler verwenden | Nach Herstellerdatenblatt entschieden |
| A3 B integrated alternative | TPS26600 external divider 100k/3.74k 0.1%: rising32.381..34.055V falling max31.275V, 32V re-enable statisch; factory trip min31V unpassend | Rechenhülle in CI, dynamischer Pad-Stress offen |
| A4 10V-Kaltstart / brownout | Prüfe VIN10 (10V vor Schutz), 2A 5V und RAW0.5A, worst-case diode Vf and buck eta, eFuse UVLO, eFuse current limit pulse, inrush Ceff, mainboard ACC/HOLD, Release sobald stabil 10V; darunter wiederholbar reset erlaubt | Offen |
| A5 Dauer32V | 32V/DC 5V2A bei Ta−20/25/+60°C, RAW0.5A als gleichzeitiger Entwicklungszustand, Ausgangsgenauigkeit, eFuse power and dropout, ripple, eFuse thresholds & pg false | Offen |
| A6 OFF-BAT | Batterie 12V &24V ACC LOW MCU hold LOW, BAT OFF <1mA Ziel0.5mA, eFuse SHDN low (5.5V abs), OVP+UVLO dividers, all PG pulls and leakage @+60/+70; USB-only cannot source BAT | Offen |
| A7 36V/400ms | Bei Vin36 für400ms keine unsichere Bauteilreaktion, eFuse OUT OFF, RAW OFF, PGOOD/Fault; VIN32 nach Puls automatisch stabil ON, ohne flatternden Hysterese-Kreis | Offen |
| A8 58V/350ms | Nur bei nachweislich ZENTRAL geklemmtem Fahrzeug. 58V maximal **inklusive Ringing an M8**, plus Leiterbahninduktion an IC-Pads instrumentiert. TPS26631 VIN & IN_SYS ≤60V OPER und ABS<67V; TPS26600 <62V ABS; Buck VIN <80V recommended, max SW/BOOT/EN/PG analog pins per datasheet; 100V MLCC rated & effective C | **P0 OFFEN, keine garantierte Reserve bei schnellen Flanken** |
| A9 Fehler / shorts | Seriendiode open/short, eFuse internal FET short, mode resistor & ILIM open/short, 100V capacitors short/open, input+/- reversed, BAT vs ACC swapped, RAW full fault and GND cable break; F_MAIN and 58V-source DC rating/clearing; keep mainboard safe and no fire | P0 Offen |
| A10 60C full power | Vin10/12/24/32, continuous 5V/2A up to +60°C, thermal LMR38020 TJ max150C, Schottky D1 TJ, inductor hot DCR, eFuse chip & thermal pad at +60C board | Offen |
| A11 +70 Derating and +85 OFF | -20..70 operate or derate safe 60..70. +85 ambient **safe OFF** verify real auto temperature control path, sensor with MCU/backup and hardware condition on temp sensor fault, no smoke, no source backfeed; never assume silicon own +150C-TJ threshold = guaranteed safe 85C-ambient shutdown | Offen |
| A12 RAW0.5A branch | With common eFuse current limit>2A RAW branch is *not* independently 0.5A limited. Check auxiliary connector/leads carrying full 2x/3x pulse fault or add low-current eFuse TPS26621 with current limit and independent OV stress analysis | Offen |
| A13 ACC RUN / USB | SHDN control low at ACC OFF/no HOLD while battery available, high on ACC startup, MCU RUN hold after ACC0, no VIN-high (>5.5V) at SHDN, no VIN at 3V3 GPIO; USB-only off BAT/RAW and service 5V; M8 wins; no diode/ESD backfeed at VIN0 | Offen |
| A14 PWR_FAIL and FRAM-first | In TripTracer/mainboard 3V3 domain: fail-HIGH at MAIN5V lost or low, independent of powered TripPower. Complete M8 unplug gives zero guaranteed early warning; pre-committed CRC/sequence FRAM journal plus boot recovery (SD finish only optional proven energy). Do not source RTC coin cell into 5V2A | Offen |
| A15 native KiCad10, PCB DRC | Exact TI PWP20 and DDA8 pin-to-pad mapping, complete electrical wires, genuine KiCad 10 ERC+netlist from GitHub CI, no unconnected fault flags; local relative footprints and 3D; then PCB/DRC and Vmax pad checks | **NOT RUN – design not yet electrically qualified** |

## B. Reproducible successful checks done this turn

- Run on GitHub: https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38812555462
- 13 passed Python tests: manufacturer OVP thresholds, both precision dividers, voltage margins, basic thermal and brownout budgets, no falsely claimed primary-cell power, draft BOM set.
- Three honest scope BOMs: 35/34/23 preliminary required positions, cost lower bounds only because 23/23/19 positions still TBD, including essential interface/safety protection. The actual KiCad count is **not** determined.
- No native KiCad ERC/netlist or manufactured board, no 58V pulse or +60C hot-load test. This file is a preparation, not qualification.

## C. Deployment label (proposed draft, NOT proof)

TripPower V1 REV6: **For centrally load-dump-limited 12V/24V vehicle electrical systems ONLY**. Device-input load dump up to **58V/350ms only in verified qualified source configuration**; normal 10–32V. Do not connect to non-clamped alternators/unsuppressed 24V systems without separately qualified load-dump protector. External replaceable vehicle-side F_MAIN and safe harness are mandatory. Battery RTC/USB must not back-feed M8 or RAW.
