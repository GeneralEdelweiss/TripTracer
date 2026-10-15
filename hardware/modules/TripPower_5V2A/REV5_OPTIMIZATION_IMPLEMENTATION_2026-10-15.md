# TripPower REV5 – Bestueckungsoptimierung und 36V-Powermodul (2026-10-15)

**Im aktiven KiCad implementiert: zwei DNP-Einsparungen; kein Buck-Wechsel.** Entwicklungsziel bleibt 9–30V, 5V/2A, RAW-AUX 1A, -40..+125C und **200V/350ms ungedeckelter Load-Dump**. Die festgelegte externe, austauschbare F_MAIN bleibt erforderlich. Kein Hardware-/Fahrzeug-/PCB-Fab-Release.

## Verbindliche Aenderungen
- **R305 IMON 6.8k -> DNP:** TI LM74930-Q1 erlaubt ungenutzten IMON offen. In TripPower keine IMON-Diagnose am Steckverbinder; das Netz und der Footprint bleiben als spaetere optionale Laborbestueckung erhalten.
- **R321 FAULT_OC_N 47k Pullup -> DNP:** Open-Drain-FLT ungenutzt am Modulstecker. Externe Diagnose auf TripTracer noch abgleichen. Bei einer spaeteren Nutzung ist eine erneute Pullup-Dimensionierung erforderlich.
- Aktive BOM: **57 AUTO / 58 RUN** statt 59 / 60 REV5, bzw. 71 REV4. In KiCad (dnp yes) und der maschinenlesbaren REV5-Baseline enthalten; kein Einsparen des LM74930-eFuse-Strom-/Thermikschutzes.

## Die 36V-Kollision ist ein echter Design-Blocker
Automotive-Modul **TPSM33620S5QRDNRQ1** (3..36V IN, 5V/2A, integrierte Drossel und CBOOT) koennte auf der 5V-Stufe rund 7 Bestueckpositionen netto sparen, benoetigt jedoch einen belegten Regler-Eingangsschutz. Bestehende LM74930 OV-Topologie R307+R308=1.5M, R309=25.5k: steigende OV-Schwelle typisch **35.89V**, modellierte Worst-Case-Huelle **34.02..38.74V** inklusive TI-Schwelle, 1%-Widerstaenden, OV-Sense-Leck. Damit verletzt die OVP-Bandobergrenze schon statisch den **36V**-Betriebswert. 40V ist ABS MAX und keine Betriebsfreigabe.

**Ein einzelner R309-Tausch reicht NICHT.** Fuer 28.7k liegt das modellierte OV-UP-Fenster etwa **30.26..34.53V**; aber die fallende Schwelle zur Wiederfreigabe betraegt etwa **27.54..31.43V** und garantiert nach OV keinen Neustart bei VIN=30V. Darueber hinaus werden Spannungsspitzen durch Gate-Abschaltzeit, Kabelinduktivitaet und Kondensator-ESL nicht statisch begrenzt. Bei unserem 200V/350ms-Eingangspuls ist eine neue Worst-Case-VIN-Pad-Transienten- und SOA-Pruefung zwingend.

**Festlegung:** 36V-Modul **NICHT in aktive Schaltung eingebaut**; 80V-AEC-Q100 **LMR38020SQDDARQ1**, L101 und OV-R309 25.5k bleiben. Kein einfaches TVS-Rezept oder preiswerter Widerstand beseitigt die Schaltspitze und das Restart-Problem. Wenn ein 36V-Modul weiter verfolgt wird, braucht es eine neue, nachgewiesen praezise und schnelle OV-Abschaltung plus eigenen VIN-Pad-Ueberspannungsschutz mit Belastbarkeits-/Temperaturpruefung. Deren Teilezahl kann die ca. 7 gesparten Positionen aufheben.

## Markt-Screen fuer echten 60/65/80V integrierten Buck
- TI **TPSM65620SVCGR**, 65V/2A, Spule integriert: aktuell **Catalog (kein AEC-Q100)**, DigiKey DE Lager 0 (Stand Recherche 15.10.2026). [TI](https://www.ti.com/product/TPSM65620). Nicht als Automotive-Substitut festgelegt.
- TI **TLVM65030VCGR**, 65V/3A, Spule integriert: **Catalog, nicht Automotive**, DigiKey und Mouser zuletzt Lager 0, ab Hersteller lange Lieferzeit. [TI](https://www.ti.com/product/TLVM65030), [DigiKey DE](https://www.digikey.de/de/products/detail/texas-instruments/TLVM65030VCGR/29796470).
- MPS **MPM3901-AEC1**, 60V mit integrierter Spule und AEC-Q100, aber **nur 1A**, damit fuer geforderte 5V/2A ungeeignet. [MPS](https://www.monolithicpower.com/en/mpm3901-aec1.html).
- ADI **LTM8050**, 58V/2A, BGA, deutlich teurer und AEC-Q100 nicht belegt; kein gleichwertiger Handbestueckungsersatz. [ADI](https://www.analog.com/en/products/ltm8050.html).
**Kein fuer unsere aktuellen Anforderungen qualifizierter, zugleich verfuegbarer 60/65V-2A-Automotive-Modul-Ersatz nachgewiesen.**

## Verworfen bzw. OFFEN – nicht entfernen
- R303 ISCP und C301 TMR: Kurzschluss-/SOA-/Retry-Verhalten wuerde sich aendern.
- R307/R308/R310/R311 in der 200V-Ueberwachung: kein bestaetigtes robustes 200V-Array.
- C308/C312: Ceff(V,T,aging) und 9V-Startup nach wie vor P01/P06 offen.
- R103 des LMR38020: RT/SYNC darf nicht floaten.
- Weiterer TPS38A-Schwellwertvarianten-Tausch: genaues lieferbares Automotive-OPN/Hysterese/READY-RUN-Interlock fehlt.

## Nachweise vor irgendeiner Fertigung
GitHub KiCad-10-Standalone-Workflow kann Schematic ERC und Netlist pruefen. Die Baseline prueft 57 AUTO/58 RUN sowie DNP von R305/R321. Kein eigenstaendiges geroutetes PCB/DRC. **P01–P10 weiterhin nicht freigegeben** (insbesondere 9V erster Start, hot-Q301-SOA 200V/350ms, R313–315/Zener, Ceff, VIN0-RUN, F_MAIN und EMV). Vor einer neuen IC-Festlegung erst reale MPN/Footprint/3D-Modelle, Verfuegbarkeit, Schaltplan- und dynamische Worst-Case-Tests.

## Weiterer real beschaffbarer 36V-Kandidat: MPM3551-AEC1 (noch NICHT eingebaut)
Bei erweiterter Suche identifiziert: **Monolithic Power MPM3551GQWE-AEC1-Z** (AEC-Q100, 5V feste Ausgangsvariante je exakter MPN zu pruefen, 3A, integrierte Spule, 36V empfohlener Dauerbereich, 42V spezifizierter Load-Dump-Widerstandswert nur im gekennzeichneten Testkontext). **Mouser DE 3.241 lagernd zu 5,19 EUR/1 Stk** als Recherche-Snapshot vom 15.10.2026: https://www.mouser.de/en/ProductDetail/Monolithic-Power-Systems-MPS/MPM3551GQWE-AEC1-Z . Herstellerdatenblatt https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/document_type/Datasheet/lang/en/sku/MPM3551GQWE-AEC1/ .

Das MPM3551 ist wegen seiner integrierten VIN-OVP (Rising min/typ/max 35.5/37.5/40V; Falling 34.5/36.5/39V) und der 42V-Load-Dump-Toleranz **ein besserer zu evaluierender 36V-Kandidat als das 40V-Abs-Max-TPSM**, der 42V-Wert ist aber **ABSOLUTE MAXIMAL / Sonderpruefbereich, NICHT garantierte Dauerbetriebs-Freigabe**. LM74930-OFF rechnerisch max 38.74V, jedoch nicht inkl. dynamischem Kabelringing/200V-Impuls. Bei 30V ist MPM3551 ebenfalls thermisch/elektrisch neu zu qualifizieren, 42V nicht als undefinierten transienten Puffer verwenden. Dies ist **keine nachgewiesene Loesung fuer die 36V-Schnittstelle**. Naechster Nachweis: echte Eingangsspannung am Modul bei 200V/350ms mit worst-case LM74930-OVP+Q301-Gateoff, und vom Lieferanten bestaetigte 42V-Testform, Revision / exakte 5V-OPN und alle VIN/EN-Ratings. Ohne diese Messung bleibt LMR38020 aktiv.
