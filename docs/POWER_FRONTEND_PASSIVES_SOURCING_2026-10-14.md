# Standard-SMD-Teile der LM74800-Q1-Schutzstufe – Beschaffung 14.10.2026

**Status: Bauteil- und Hersteller-MPNs festgelegt. Keine KIcad-Integration/Fahrzeug-/Fertigungsfreigabe.** Die verbindliche maschinenlesbare Auswahl ist [power_frontend_design_freeze.json](../hardware/kicad/power_frontend_design_freeze.json); [CSV für Stücklistenabgleich](../hardware/kicad/power_frontend_order_bom.csv).

## Konkret neu ausgewählte 1206-Standardbauteile

| Funktion | Qty | Hersteller / MPN | Eigenschaften | DigiKey Bestand (Momentaufnahme) | EUR netto /1 | EUR netto /10 je Stk |
|---|---:|---|---|---:|---:|---:|
| OV oberer Teil A/B | 2 | [Yageo RC1206FR-07330KL](https://www.digikey.de/de/products/detail/yageo/RC1206FR-07330KL/728823) | 330kΩ, 1%, 0.25W, 1206 | 24.347 | 0,10 | 0,044 |
| OV unten | 1 | [Yageo RC1206FR-0723K2L](https://www.digikey.in/en/products/detail/yageo/RC1206FR-0723K2L/728700) | 23,2kΩ, 1%, 0.25W, 1206 | **514 (regionale Momentaufnahme)** | ~0,09* | offen |
| C_CAP | 1 | [KEMET C1206C224K5RACTU](https://www.digikey.de/de/products/detail/kemet/C1206C224K5RACTU/411250) | 220nF, 50V, X7R, 1206 | 7.931 | 0,32 | 0,183 |
| R_SLEW | 1 | [Yageo RC1206FR-07100RL](https://www.digikey.de/de/products/detail/yageo/RC1206FR-07100RL/731438) | 100Ω, 1%, 0.25W, 1206 | 462.929 | 0,09 | 0,040 |
| C_SLEW | 1 | [KEMET C1206C103K1RACTU](https://www.digikey.de/de/products/detail/kemet/C1206C103K1RACTU/411511) | 10nF, 100V, X7R, 1206 | 265.220 | 0,20 | 0,112 |

`*` **23,2kΩ-Sonderfall:** Die exakte Yageo-MPN existiert und wurde in DigiKey-Regionaldaten als lagernd geführt; EUR-Einzelpreis von 0,09€ ist ein ähnlich gelisteter DigiKey-EUR-Preis, **nicht direkt auf einer aktuellen DE-Einzelartikel-Seite verifiziert**. Der 10-Stück-Preis bleibt absichtlich leer. Vor Bestellung Region/Lagerstand/Pricing bestätigen; ggf. [Bourns CR1206-FX-2322ELF](https://www.digikey.in/en/products/detail/yageo/RC1206FR-0723K2L/728700) nur als dort aufgeführter Alternativkandidat prüfen (nicht ohne Review automatisch tauschen).

**Für die sechs konkret ergänzten Positionen** ergeben sich aus den bestätigten EUR-Einzelwerten plus 0,09€ nur als *Platzhalter* für R_OV_BOTTOM ungefähr **0,90€ netto pro Einzelgerät**. Die bekannte 10er-Staffel ist **0,423€ pro Gerät zuzüglich des noch zu verifizierenden 23,2-kΩ-Widerstands**. Keine unbestätigten Lagerpreise in die Vollkosten-BOM hochrechnen, kein Versand enthalten.

## Kritische Schaltungsprüfung aus TI-Referenz (nicht nur Teile)
- TI [LM74800EVM-CS, Abb. 3-1 und BOM Tab. 6-1](https://www.ti.com/de/lit/pdf/slvubu4): Das RC-Glied **R2/C4 = 100Ω / 10nF** ist ein **dv/dt/Gate-Steuerelement**; Position nur entsprechend tatsächlicher EVM-Netzknoten, nicht als beliebiges RC-Glied über Gate/Source verdrahten.
- Der EVM-Schaltplan enthält zusätzlich **C10 = 15nF 100V**, dessen Notwendigkeit und Netze im späteren reduzierten TripTracer-Schutzschaltplan zu prüfen sind. Ein bestellbarer Referenz-MPN-Kandidat ist [Yageo CC1206KRX7R0BB153](https://www.digikey.de/de/products/detail/yageo/CC1206KRX7R0BB153/8025568), 15nF 100V X7R 1206; ca. 3.798 Stück lagernd, 0,24 EUR netto pro Stück. **Noch NICHT in der festen Stückliste** (keine unbestätigte Zusatzbeschaltung).
- **OV-Werte:** 2×330kΩ oben in SERIE und 23,2kΩ unten. Nach TI LM7480-Q1 rising OV-Pin-Schwelle 1,233V ergibt sich nominell `1.233*(1+660/23.2) = 36.31V`, beim 24-V-Netz 35,1µA und bei 30V 43,9µA Teilerstrom. Die 330k oben sehen bei 200V nominal ~96,6V pro Widerstand. 1%-Toleranz, Eingangsleckstrom (Datenblatt bis ca. 1µA), Temperatur und Abschaltposition SW/VSNS müssen als echte Worst-Case-Berechnung folgen.
- Die restlichen (bereits fixierten) Kondensatoren und 56V-Diode bleiben in der design-frozen JSON/CSV. **R_VS mit 0,7J konservativer 200V/350ms-Energie noch nicht freigegeben.**
- **Sicherheit:** LM74800 bietet KEINEN programmierbaren VIN-Hauptstrom-Kurzschlussschutz; externe Quellen-Sicherungen plus Leitungsschutz/Fehleranalyse sind erforderlich. ACC/MCU-HOLD <100µA, USB kein Rückspeisen, 9–30V und 200V-ISO-Profil sind nachzuweisen.
- Bestehender Live-KiCad-Schaltplan **01G_SIMPLE_INPUT** behält D901/D902. Die JSON/CSV sind **bevorzugte nächste Einkaufs-/Schaltplanstückliste**, **kein KiCad-Netlist-BOM**. DRC/ERC sind nicht fertig.

## Preis-/Bestandsmethode
Momentaufnahmen verschiedener Regionen und Abrufzeitpunkte **nicht** gleichsetzen. EUR netto ist hier DigiKey DE Gurtabschnitt, soweit explizit genannt; 23,2k ist gesondert markiert. Keine MwSt, Versand, Kleinmengenaufschläge, Gehäuse, Montage, Leitungsicherung oder bisherige MOSFET/Reglerkosten in 0,90€ enthalten. Regelmäßige Neubewertung vor Bestellung.
