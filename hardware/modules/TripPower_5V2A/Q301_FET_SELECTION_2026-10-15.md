# TripPower Q301 – Automotive HV-MOSFET-Auswahl (15.10.2026)

**Aktiver Bauteilkandidat in eigenstaendiger TripPower-01-Unterseite:** Vishay **SQM10250E_GE3**, 250V N-MOSFET, AEC-Q101, D2PAK TO-263-3. Dieser Bauteil- und Footprintwechsel ist ein **Schaltplanentwurf**, KEINE 202V-Load-Dump-, PCB-, Automotive- oder Fertigungsfreigabe.

## Herstellervergleich

| Q301-Kandidat | VDS | RDS max 25C bei 10V Gate | RDS max 125/175C | AEC | Gehaeuse | Urteil |
|---|---:|---:|---|---|---|---|
| ST STD17NF25 alt | 250V | 165mOhm | 175C nicht zulaessig | nicht ausgewiesen | DPAK | thermisch schwaecher |
| Infineon IPB17N25S3100ATMA1 | 250V | 100mOhm | 175C RDS nicht garantiert | Q101 | D2PAK | robust, gute 2. Wahl |
| **Vishay SQM10250E_GE3** | **250V** | **30mOhm** | **65/86.8mOhm** | **Q101** | D2PAK | **vorlaeufig gewaehlt** |
| Infineon AUIRFS6535 | 300V | 185mOhm | pruefen | Q101 | D2PAK | Reserve 300V, sehr hohe Waerme |
| Infineon IPB64N25S3-20 | 250V | 20mOhm | pruefen | Q101 | D2PAK | EOL, keine neue Serie |

Quellen: [Vishay Datenblatt Rev. A, S.1-2 (RDS, Tj, Leckstrom)](https://www.vishay.com/docs/75035/sqm10250e.pdf), [Infineon IPB17N25S3-100](https://www.infineon.com/part/IPB17N25S3-100), [Infineon AUIRFS6535](https://www.infineon.com/part/AUIRFS6535), [ST](https://www.st.com/resource/en/datasheet/std17nf25.pdf), [abgekuendigter IPB64](https://www.infineon.com/part/IPB64N25S3-20).

## 9-V-Vollast: ehrliche Datenblattrechnung

Bis 5V/2A und 1A `VIN_PROTECTED_UNFUSED`: I = 10W/(9V x 0.8) + 1A = **2.389A**, bezogen auf *angenommene* 80% Buck-Effizienz. I^2 = 5.707A². Q301-Verlust mit RDS-max bei 10V Gate:

- ST bisher @25C 165mOhm: **0.942W**.
- Infineon @25C 100mOhm: **0.571W**.
- Vishay @25C 30mOhm: **0.171W**; @125C 65mOhm: **0.371W**; @175C 86.8mOhm: **0.495W**. Letztere sind Herstellerangaben fuer gepulste Widerstandsmessung, keine garantierte 202V-SOA.
- Vishay RthJA=40K/W ist NUR die Referenzmessung auf 1-Zoll-Quadrat-FR4 mit 2oz Kupfer. Bei 85C Umgebung und 0.495W waeren rechnerisch 105C Tj auf genau dieser Referenzplatine, **nicht nachgewiesen fuer unser kompaktes 35um/1oz PCB**. Fuer Ziel Tj≤125C bei 85C muss RthJA≤80.8K/W sein, beim spezifizierten 175C-Maximalwiderstand und dauerhaft vollen 2.389A.

## Konkrete KiCad-Umstellung und offene Sicherheitsgates

`Q301` hat im aktiven `01_Protection_LM74930.kicad_sch` die neue MPN, den Hersteller-Datenblattlink und den **Standard-KiCad-10-Footprint** `Package_TO_SOT_SMD:TO-263-3_TabPin2`, statt bisher DPAK. Symbolpinfolge **G1/D2+Tab/S3**; Vishay [TO-263-Gehaeusedaten](https://www.vishay.com/docs/71198/to263d2.pdf) und [Padempfehlung AN826](https://www.vishay.com/docs/73397/73397.pdf). **Noch kein nativer PCB-Footprint-/Pad- oder 3D-GUI-Nachweis.** Hersteller-Padzeichung gegen KiCad-Standard pruefen.

1. **202V Test A/B:** 250V VDS laesst nominell nur **48V Abstand** zu 202V (ohne Kabelinduktions-Ueberschwinger, Kaelte/Temperatur und Messreserve). LM74930 ist als **OV-Abschalter**, nicht als 202V/350ms linearer Spannungsregler vorgesehen. Tatsaechliche OV-Reaktionszeit, HGATE-Abschalten, Strom-/VDS-Ueberlappung beim Ausschalten und bei Einschaltspitzen mit [Vishay SOA, S.5](https://www.vishay.com/docs/75035/sqm10250e.pdf) bei heisser Sperrschicht pruefen. Voll belastet bei 202V fuer 350ms wurde **nicht** nachgewiesen und ist nicht die Schaltungsidee.
2. **Gateantrieb:** Qg typisch 50nC / max. **75nC**, statt 29.5nC beim alten ST und max. 19nC beim Infineon. **R320=100R** und Gate-Slew-C, 9V-Ladungspumpenstart sowie VGS 10V unter realem Worst Case verifizieren.
3. **OFF-Strom:** Datenblatt **IDSS max 600uA bei 250V und Tj=175C**; damit ist **<100uA** BAT-Off-SYSTEMLIMIT nicht automatisch gegeben. 30V und heisse Sperr-/Zener-/EN-Pfade messen/bewerten (250V-Wert nicht unzulaessig auf 30V umrechnen).
4. **F_MAIN extern** bleibt einzig vorgesehene Quelle-Fuse, noch ohne Nennstrom; Kurzschluss mit Q301 durchlegiert, Kabel-, Stecker- und 35um-Kupfer-I²t offen.

**Preissnapshot (15.10.2026, unverbindlich, EUR netto, zzgl. Versand/MwSt.):** [Mouser DE SQM10250E_GE3](https://www.mouser.de/de/ProductDetail/Vishay-Siliconix/SQM10250E_GE3): ca. 13.730 St. lagernd, **1/10/100 Stück 3.85/1.98/1.80 €/St.**; [DigiKey DE](https://www.digikey.de/de/products/detail/vishay-siliconix/SQM10250E-GE3/9341559): etwa 13.906 lagernd, **3.93/2.587/1.8237 €/St.**; [Infineon DigiKey DE](https://www.digikey.de/de/products/detail/infineon-technologies/IPB17N25S3100ATMA1/5960205) 2.88/1.875/1.2974 €/St. mit mehr Lager. Keine erfundenen LCSC-/JLC-Basic Angaben.

**Naechster Schritt nach CI ERC/Netlist:** TI HGATE/EN und OV-202V-Umschalt-SOA mit Gate-Ladung auslegen, Vishay TO-263 Pad und thermische 35um-Kupferflaeche verifizieren, danach erst PCB-Layout. **NO FAB**.
