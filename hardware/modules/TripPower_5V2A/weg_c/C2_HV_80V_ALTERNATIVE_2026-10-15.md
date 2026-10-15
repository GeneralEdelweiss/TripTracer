# Weg C2-HV — unabhaengige Alternative nach C1-No-Go (15.10.2026)

**Status:** Architektur-Kandidat, *noch kein KiCad-Schaltplan*, kein ERC, kein verifizierter 200-V-/350-ms-Test, kein Prototyp. Der C1-Entwurf bleibt als auditierter NO-GO-Referenzstand erhalten; keine Weg-A/B-Entwuerfe betrachtet.

## Warum C1 NO-GO ist

C1 koppelt einen 36-V-Buck (40V absolute maximum) ohne schnelle unabhaengige OV-Begrenzung an den AP74502HQ. Ueber seine garantierten OVLO-Toleranzen existiert kein passiver Teiler, der *garantierten* Neustart bei 30 V mit *garantierter* Abschaltung unter 36 V vereint. C1 1M/39k startet nach Ueberspannung im Worst Case erst unter 28.32V wieder; schneller Eingangsslew kann >40V am Buck erzeugen. Daneben bestehen Fehlerfall Q1 Drain/Source-Kurz, Schutzstromenergie, 125C-Thermik und komplette Verschaltung als Stopps.

## Neue Architektur C2-HV: HV-Schutz aus Herstellerreferenz + 80V-4A-Buck

```
 BAT_IN(9..30V; 200V/350ms surge)
    |
 F_MAIN extern, auswechselbar, auf Kabel/Stecker/PCB abgestimmt
    |
 AP74502HQ mit Diodes VIN/VCAP/Zener/OVLO-Referenzbeschaltung
    | 2x SQM35N30-97 300V, common-source, Drain-Seiten RAW/VIN
 HV_DISCONNECTED   [UVLO/OVLO auto-restart at <=30V; redundant FET fail gate offen]
    |
 TPS26631 60V eFuse (bis 67V abs) mit gemeinsamen elektronischen Fehlerstromschutz
    +-------------------> RAW_PROTECTED 1A NENNLAST (nicht separat 1A limitierend!)
    |
 TI LM70840-Q1 80V/4A integrierte Leistungsschalter + EXTERNE Standardinduktivitaet
    |
 5V/2A an TripTracer, auf Mainboard gegen USB rueckspeisefrei OR-ing
```

**80V statt 36V** loest nicht den 200V-Lastabwurf oder Fehlerfall, aber verbessert die Ueberspannungsreserve und beseitigt den mathematischen Zielkonflikt zwischen Wiedereinschaltpunkt bei 30V und normaler 36V-Buck-Grenze. TPS26631 bleibt der nachgeschaltete schwache Eingang (60V recommended, 67V abs). TI LM70840-Q1 ist Automotive AEC-Q100 Grade1, 4.5–80V, 4A, 6x6mm 29-pin VQFN, integrierte Low-/High-Side-Schalter, Auto-Mode, Hiccup/OTP/UVLO/PG; **Spule ist NICHT integriert**. Hersteller: https://www.ti.com/product/LM70840-Q1. MPN **LM70840QRRXRQ1** bei Mouser EU in stock 5,321 Stueck laut 15.10.-Recherche: https://eu.mouser.com/ProductDetail/Texas-Instruments/LM70840QRRXRQ1 . Preisstand 1/10/100 in EUR je Einheit muessen fuer Einkauf nochmals verifiziert werden; bekannte Orientierung ca. 6.30 / 4.86 / 4.11 EUR netto.

### Vorlaeufige OVLO-Vergleichsrechnung

Hersteller AP-Schwellen: steigende min1.165 / typ1.25 / max1.333 V; fallende min1.063 / typ1.143 / max1.222 V. Neuer *nur rechnerischer* Teiler Rtop=1M, Rbottom=35k, beta=35/1035=0.0338164:
- Einschalten nach vorheriger OV im Worst Case bei 1.063/0.0338164 = **31.434V** (damit 30V prinzipiell moeglich).
- Abschalten steigender Eingang im Worst Case bei 1.333/0.0338164 = **39.418V**.
- Widerstandstoleranzen, OVLO-Eingangsleckstroeme und Hysterese musst du vor Schaltungsfreigabe pruefen. 200V direkt am AP OVLO ueber Teiler -> 6.76V, aber Widerstandspulsfestigkeit 1M-Vorwiderstand pruefen.
- Unter angenommener 1us AP-Abschaltzeit und bei 10us 30V->200V steigen in 1us zusaetzlich 17V: rechnerisch **56.42V** bis zur Abschaltung (nur illustrative ideale Annahme, kein Nachweis). Dies laege zwar unter der 60V-Betriebsgrenze der eFuse und unter 80V des Buck, aber AP 1us wird beim realen 260nC-Qg-FET-Paar nicht garantiert und parasitaere Ueberschwinger fehlen; **keine Freigabe**.

### Kostenvergleich auf 5 aktiven Halb-/Leistungsbauteilen (keine Vollkosten)

| MPN / Anzahl | 1 St. EUR netto | 10 St. | 100 St. |
|---|---:|---:|---:|
| AP74502HQTA8-7 x1 | 0.636 | 0.450 | 0.352 |
| SQM35N30-97_GE3 x2 | 8.960 | 5.926 | 4.212 |
| TPS26631PWPR x1 | 3.890 | 2.960 | 2.460 |
| TPSM33620S5QRDNRQ1 x1 (nur C1) | 1.990 | 1.960 | 1.860 |
| LM70840QRRXRQ1 x1 (nur C2-HV) | ~6.300 | ~4.860 | ~4.110 |
| **C1 Halbleiter-Summe** | **15.476** | **11.296** | **8.884** |
| **C2-HV Halbleiter-Summe** | **19.786** | **14.196** | **11.134** |

**Die Vergleichssummen sind nicht die Gesamt-BOM-Kosten.** C2-HV benoetigt mindestens eine zusaetzliche gepraegte Induktivitaet und einige Hersteller-Passiva. Beide brauchen eingangsseitiges 200V-taugliches HF-C, AP VIN-Klemmung/pulsfeste Widerstaende, ausreichend Bulk, Schutz der ACC/RUN-Signale, passende MPN/Stecker, F_MAIN plus Fassung. Fracht/MwSt/PCB/Bestueckung sind nicht enthalten. Alte Tabelle der reinen IC-Kosten ohne 2 FETs deshalb niemals als reale Teilekosten bezeichnen.

## Liste der offen zu schliessenden Bedingungen

1. **FATAL SINGLE FAULT:** Q1 Drain–Source-Kurz kann bei 200V per Q2-Bodydiode direkt HV_DISCONNECTED auf 200V heben und sowohl TPS26631 als auch LM70840 zerstören. Abhilfe muss als einfacher herstellerreferenzierter COTS-Baustein bzw. physisch nachweisbarer passiver Grenzschutz benannt werden. Nicht automatisch 2. MOSFET-Paar ohne Konzept!
2. **200V/350ms mehr als bloss 200V-Peak:** definierte ISO-Kurven/Quellimpedanz, externer F_MAIN, 200-V-CIN, MOV/TVS-Energien und Abschalt-/Wiederein-Laborpruefung. Keine Datenblatt-Pulsuebertragung auf alle Wellenformen.
3. **+125C/2A/RAW1A:** MOSFETs je bis ~1.07W bei RDSon hot (ohne Stromfeedback), LM70840 thermische Verlust- und theta-Messung auf tatsaechlichem PCB statt EVM/PR Marketing. Externe Induktivitaet und eFuse thermisch ebenfalls pruefen.
4. **Pin-/Pad- und KiCad10-Schaltung erst nach konkreter Alternative:** Hersteller 29-Pin-QFN-Landpattern/Schaltplan und 5V-Referenzwerte, native ERC/Netlist. Kein nicht-geprueftes Generator-Symbol.
5. **AUTO/RUN und USB:** MCU-HOLD pegel- und ausfallfest, <100uA @125C, kein Rueckspeisen.
6. **RAW stromlimit:** bei gemeinsamem 3.2A-eFuse-Limit und kurzen 2x/3x Fehlstroemen fuer den RAW-Abgang keine separate 1A-Sicherung, RAW-Port muss komplette Belastung abkoennen oder preiswerter eigenstaendiger 1A-Schutz hinter eFuse vorgeschaltet werden.

## Entscheidung

**C1 nur als Fehleraudit konservieren; C2-HV als vorlaeufige kuenftige Entwicklungsrichtung.** Das ist kein erfuellter 200V/350ms-/Fertigteil-Anspruch. Weil Herstellerdaten des C1 Sicherheitsanforderungen widersprechen, ist ein unsicheres Blind-Ergaenzen und Layouten keine verantwortbare Fortsetzung. Folgend: C2-HV Referenz-Buck aus TI-Datenblatt konkret dimensionieren und 200V-/Single-Fault-Gate vor PCB und Bestell-BOM schliessen.

