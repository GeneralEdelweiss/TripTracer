# TripTracer V1 – Baugruppe 01, 80/20-Vorentscheid: Eingangsschutz mit LM74800-Q1

**Stand: 13.10.2026. Status: überprüfter Konzept-/Beschaffungsvergleich, KEINE elektrische/ISO-/KiCad-/Fertigungsfreigabe.** Ausgangspunkt: [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md), [COST_CONTROL.md](COST_CONTROL.md), [SOLID_STATE_POWER_ARCHITECTURE.md](SOLID_STATE_POWER_ARCHITECTURE.md). Die ursprünglichen Relais- und TPS26631-Schaltbilder bleiben vorerst unberührt; diese Datei ist die **bevorzugte neue Auslegungsrichtung**, nicht ein als fertig markiertes Schaltplanblatt.

## 1. Entscheidung: Fehler *sicher abschalten*, nicht bei 200 V zwanghaft weiterloggen

Bei 200-V-ungedämpftem 24-V-Load-Dump ist es **nicht erforderlich**, die aktuelle GPX/CSV-Aufzeichnung lückenlos fortzusetzen. Für die Schutzbewertung ist **Überspannungsabschaltung (OV cut-off)** gegenüber **linearer Ausgangsklemme (output clamp)** zu bevorzugen: Bei Cut-off wird der HV-MOSFET gesperrt; bei Clamp kann er über die Dauer des Impulses hohe lineare Verlustleistung aufnehmen. Weder die Abschalt-Schaltung noch diese Begründung ersetzen den MOSFET-SOA-/ESD-/Leitungsschutz-Nachweis. Die zulässige Funktionsunterbrechung nach gewählter ISO-16750-2-Prüfung **pro Test und Klasse** dokumentieren.

**TI LM74800-Q1 Rev. C, Abschnitt 10.3** zeigt **200-V/24-V ungedämpften Load-Dump** mit **common-source back-to-back N-MOSFETs**: **Q1 mindestens 200 V**, **Q2 60 V**, ein **60-V-VS-Zener** und **85-V-Zener**, negative/positive TVS sowie **OV-Kriterium etwa 37 V**, außerdem **6 V Kaltstart**. Hersteller-Referenz nennt einen **25-W**-Anwendungsfall; dies belegt weder diesen Chip als eigenständigen Überstromschutz noch unsere spezifischen FETs, PCB oder IEC/ISO-Gesamtprüfungen. Siehe [TI Rev. C Abschnitt 10.3](https://www.ti.com/document-viewer/LM7480-Q1/datasheet/GUID-4F98E915-57FC-497B-9AAC-F5F521CDA769) und [OV cut-off vs. clamp, 10.3.2.4](https://www.ti.com/document-viewer/LM7480-Q1/datasheet/GUID-89138DDE-D941-44D3-840D-FF47FB28C0DC).

**Wichtige Einschränkung am FET:** TI nennt für Q1 mindestens 200 V bei *echter Abschaltung* und empfiehlt **±20 V V_GS-Nennfestigkeit**; FDD18N20LZ erfüllt nominell beides, aber **200 V genau am angenommenen Impulsmaximum ohne Zusatzreserve**, unbekannte Layout-Überschwinger und noch nicht bewertete SOA machen es zu einem **nicht freigegebenen** Kosten-Proxy. FET mit >200-V-Rating kann wirtschaftlicher sein als späterer Schaden/Rework. **Die scheinbare 25-W-Gate-/Schutz-Kompatibilität der TI-Referenz ist nicht automatisch für jeden Austausch-FET gültig.**

## 2. Minimale elektrisch plausible Funktionsblöcke, ohne Doppelcontroller

```text
  Fahrzeugseitig separat abgesicherter BAT+ (M8 Pin 4)
           |
           +-- 58-V-geeignete 24-V-extern sitzende Sicherung / Leitungsschutz
           |   (Amperewert nach PCB-/Kabel-/Inrush-Budget, NICHT blind 2 A)
           |
           +-- TI-Referenz: Vortransienten-/Zener-/TVS-Netz
           |
           +-- Q1 (HV-FET >=200 V, wahrscheinl. >200-V-Typ besser)
           |   + Q2 (60-V-FET), gemeinsame Source
           |   an LM74800-Q1:
           |   - DGATE: Rueckwaertsstrom-/Verpolschutz
           |   - HGATE: getrennte Lastabschaltung
           |   - OV: Eingang-Ueberspannung --> AUS bei ~37 V (nicht Clamp)
           |   - EN/UVLO: ACC + zeitbegrenzter MCU-HOLD, fail-off
           |   - VS: gegen Load-Dump nach TI-Zener-Design geschützt
           |
           +--> HV_PROTECTED (nur nach korrektem Entwurf)
                   |
                   +--> zentraler 5-V-Buck (LMR36520-A1 als Kandidat)
                   |       -> 3V3_CORE / GNSS / FRAM / MCU / SD
                   +--> andere aktive Verbraucher
                   
   ACC Pin 1 -> eigene Sicherung und Transienten-/Reverse-Beschaltung
                   -> ACC-Start + MCU-HOLD + USB-only-Sperre
   USB-C VBUS -> separate geschützte Service-Schiene (keine BAT-Rückspeisung)
```

**Nicht als fertige Netzliste verwenden.** OV-Eingangsdividerspannung, VS-Zener, Gate-Überspannung, Einschaltsequenz, Enable-/HOLD-Bootstrap, ACC-Pulse, common-source-Source/Drain-Richtungen, USB-Rückspeisung, Inrush und tatsächlicher MOSFET-Datenblatttyp benötigen einen **vollständig verdrahteten Schaltplan**. Die **interne VSNS/SW-Schalterfunktion** trennt einen entsprechend beschalteten Spannungsteiler bei IGN_OFF; bei der **200-V-Auslegung und OV-Abschaltung** darf aber der direkt an VBATT angeschlossene Teiler **nicht ohne Prüfung** an VSNS/SW umgehängt werden: absolute Pinspannungen und Surge müssen stimmen.

**OV-Teiler bei TI-Beispiel:** 100 kΩ + 3,48 kΩ (ca. 37-V-Schaltschwelle). Wenn die obere Teilerspeisung dauerhaft an BAT+ hängt, fließen nominal **116 µA bei 12 V, 232 µA bei 24 V, 348 µA bei 36 V** – *weit mehr als* die etwa **2,87 µA** Chip-Shutdown-Strom. Das übertrifft bei 36 V das projektierte OFF-Ziel unter 100 µA bereits ohne weitere Blöcke. Ein geeigneter **SURGE-fester, im OFF-Zustand geschalteter OVP-Messpfad** bzw. eine herstellerkonforme Nutzung von VSNS/SW ist deshalb ein **echtes Gate**, nicht mit frei gewählten Megohm-Widerständen ohne Leakage-/Störsicherheitsprüfung lösen. An 200 V fallen in 100 kΩ rechnerisch ~**0,4 W Momentanleistung** und ~**0,14 J in 350 ms** bei konstanter Spannung an; echte Impulsform und **pulsfeste Serienwiderstände** prüfen. Quelle: [TI 10.3.2.4](https://www.ti.com/document-viewer/LM7480-Q1/datasheet/GUID-89138DDE-D941-44D3-840D-FF47FB28C0DC) und [TI integrierte Divider-Abschaltung](https://www.ti.com/document-viewer/LM7480-Q1/datasheet/GUID-928AE6E6-E06D-4DD7-A976-53321BC2CAD9).

## 3. Überstrom- und Brandschutz: eFuse-Entscheidung steht bewusst noch aus

**Ein LM74800-Q1 ist KEINE eFuse und hat keine frei einstellbare Hauptstrombegrenzung.** Die früheren PWR-03/12-Funktionen („eFuse, Auto-Retry“) dürfen **nicht stillschweigend** entfallen. Benutzerpräferenz nach neuer 80/20-Bewertung: **gefährlicher Kurzschluss/Überhitzung ausschließen**, seltenen Logging-Abbruch/geräteeigenen Defekt ggf. akzeptieren.

Zwei zu messende Alternativen:

- **Einfache Variante ohne zusätzliche eFuse (prüfen):** Beidseitig/je Fahrzeugleiter passende **fahrzeugseitige Leitungssicherung** mit realer **DC-Nennspannung, ausreichendem Abschaltvermögen und Kennlinie**; PCB-Eingangsleiterbahnen und lokale Lastzweige für die Zeit bis zum Sicherungsansprechen dimensionieren. Zentraler Buck **LMR36520** mit **cycle-by-cycle current limit, thermischem Schutz und Hiccup bei Ausgangskurzschluss**. Die 5-V-Sensor-/Antennenausgänge weiterhin passend begrenzen, weil ihr Kurzschluss **nicht** automatisch von einer BAT+-Hauptsicherung beherrscht wird. **Nur freigeben, wenn die Fehleranalyse den Wegfall der eFuse als gleichwertig sicher beurteilt**; bei hartem PCB-Kurzschluss **vor** dem Buck kann nur die vorgeschaltete Sicherung helfen. [TI LMR36520](https://www.ti.com/product/LMR36520), [Littelfuse 58-V-MINI-Serie](https://www.littelfuse.com/assetdocs/automotive-passenger-car-catalog?assetguid=613475c5-28ce-4646-a46e-0a9344b7a944).
- **Volle bisherige eFuse-Funktion (Vergleich):** zusätzliche **TPS26631** hinter der LM74800-Hochvoltstufe; sie braucht Zusatzbeschaltung und ca. 4,22 € im Einzelbezug. Wichtig sind 60-V-Spannungsgrenze am Eingang, Verpol-FET-Funktion nicht doppelt bezahlen, Stromlimit/Softstart/Auto-Retry nicht zu hoch setzen; ein thermisch ungünstiger Retry-Dauerkurzschluss wäre **kein** Sicherheitsgewinn. [TI TPS2663](https://www.ti.com/product/TPS2663).

**Vorentscheidung:** weder „eFuse MUSS weg“ noch „zweites IC MUSS hin“. Entscheidung allein anhand *tatsächlicher Fehler-/Leitungsschutzfälle und Zusatzkosten*. Ein gewöhnlicher **32-V-Kfz-Stecksicherungstyp** ist bei **36-V-regulärem Eingang** nicht ohne Weiteres zulässig; für 24-V-Fahrzeugkreise gibt es **58-V-rated MINI-Blade-Varianten** (ca. 2–30 A), deren **Kennlinie, Temperatur-Derating und DC-Abschaltvermögen** zum 36-V-Dauerbetrieb und realen Kurzschluss passen müssen.

## 4. Beschaffungs-Kandidaten und tatsächliche Quellenlage (13.10.2026)

| Funktion | MPN | LCSC/JLCPCB | Preis / Beschaffung | Freigabe |
|---|---|---|---|---|
| Controller | TI **LM74800QDRRRQ1** | **JLC C3215600 Extended**, SON-12 / 3×3 mm, Thermalpad | **2,58 €/1; 1,94 €/10; 1,59 €/100**, netto Mouser DE; JLC-Bestückungskosten extra | TI-Referenzschaltung bestätigt; Footprint/Pad/Ansteuerung offen |
| Q1 200 V HV-FET **nur Kostenkandidat** | onsemi **FDD18N20LZ** | **JLC C903557 Extended, aktuell Bestand 0** | **2,55 €/1; 1,648 €/10; 1,134 €/100**, netto DigiKey DE | nicht automotive-qualifiziert nachgewiesen; SOA, ≥6-V-Gatebetrieb und Spitzenreserve offen; lagernder Alternativtyp zwingend |
| Q2 60 V N-FET, günstiger Alternativkandidat | Nexperia **BUK9Y43-60E,115** | **LCSC C456113: aktuell Bestand 0**, Referenzpreis 0,56 USD/1, 0,459 USD/10, 0,360 USD/100 | bei DigiKey US in USD lieferbar (kein gemischter USD/€-Zwischensummenwert!) | AEC-Q101, RDSon max. 43 mΩ @5V; Pin-/Footprint/SOA testen |
| Q2 60 V TI-Referenz-FET | Nexperia **BUK7Y4R8-60E/EX** | **LCSC C503619**, Status variiert, zuletzt ab 1,67 USD/1 | keine bestätigte wirtschaftliche JLC-PCBA-Lieferbarkeit | unnötig niedrige 4,8-mΩ bei unserer Last, teurer als 43-mΩ-Kandidat |
| 200-V-Surge-TVSpaar | **SMBJ150A + SMBJ33CA** | genaue lieferbare MPN-/C-Nummern offen | Preise je nach Hersteller/Distributor getrennt prüfen | ISO-Puls-/Spannungskoordination und 1206/SMB-Geometrie offen |
| Vor-Sicherung BAT+/ACC | 58-V-geeignete, fahrzeugseitig absichernde DC-Fuse | extern zum PCB; Fahrzeugkabelanfertigung | **unbepreist**, Abschaltstrom/Spannung/Einbau noch auswählen | 32-V-Typ nicht automatisch zulässig |
| Hauptbuck | TI **LMR36520** (bestehender Kandidat) | `hardware/kicad` enthält frühen Entwurf | Gesamtpreis inkl. Spule/MLCC/PCBA unvollständig | TI-typ. 90% @24V/5V/1A; **6-V-/5-V-Regelung im gesamten Lastprofil** nicht freigegeben |

**Kostengrenze heute:** Die verifizierten **LM74800 + FDD-Kandidaten** alleine kosten **5,13 € / Gerät einzeln, 3,59 € bei 10 und 2,724 € bei 100 Stück**, *ohne* Q2, TVS, Zener, Eingangs-/Gate-Widerstände, Cap, Sicherung, ACC-/HOLD-/USB-Logik, PCBA/Versand/MwSt. Deshalb **keine fertige „5-€-Schutzschaltung“ behaupten**. Die frühere 21,92-€-Doppelcontroller-BOM ist kein notwendiger Standard und die früheren 9–10-€-Schätzungen sind noch kein vollständiger Funktionsvergleich.

## 5. Nächste Baugruppenschritte in sinnvoller Reihenfolge

1. **Brand-/Kurzschluss-FMEA** mit BAT+-Kurzschluss vor/nach Q1/Q2, FET D-S stuck ON, Buck-Eingang kurz, 5-V- und externe Sensorleitung kurz, 24-V-Transient, TVS selbst kurz, Masseausfall und USB-Rückspeisung. Leiter-/Sicherungskette zuerst freigeben; konkret Sicherung und Leiterbahnen gemeinsam festlegen.
2. **TI-Load-Dump-Topologie als echte KiCad-10-Unterseite** in 01D/01_Eingangsschutz überführen: **nicht die alte eFuse nur beschriften**. Pin-Belegung und Footprints vom Hersteller prüfen; zwei passende lieferbare Q1-MOSFETs mindestens 200 V sowie günstigen Q2 60 V vergleichen; *OV CUT-OFF*, nicht output clamp.
3. **ACC-Bootstrap/MCU-HOLD** (inkl. Fahrzeug-only-Interlock) und die **OFF-Verlustleistung des tatsächlich angeschlossenen OV-Teilers** lösen, bevor Ruhestromziel ≤100 µA behauptet wird.
4. **Lastbudget 6 V:** Buck-Ein-/Ausgänge unter realem Display/SD-Lastsprung prüfen; bei ≥6 V Kernsystem stabil, Beleuchtung darf aus; darunter definierter Brownout. Kein teurer 3-V-Hold-up-Puffer.
5. **eFuse-Funktionsentscheidung** und realer Gesamtkostenvergleich inkl. Steck-/Leitungssicherung, PCB/Bestückung, ggf. Ausfall-/Schutztests. Kein Backup-/Redundanzteil ohne belegten gefährlichen Fehlermodus.
6. KiCad-10-ERC/DRC sowie Labor-Fault-Injection/Norm-Testmatrix; **Status bis dahin: NICHT GETESTET / NICHT FREIGEGEBEN**.

## Herstellerquellen

- [TI LM7480-Q1](https://www.ti.com/product/LM7480-Q1), [Abschnitt 10.3 (200-V-24-V-Load-Dump)](https://www.ti.com/document-viewer/LM7480-Q1/datasheet/GUID-4F98E915-57FC-497B-9AAC-F5F521CDA769), [Abschnitt 10.3.2.4 (Cut-off/Clamp)](https://www.ti.com/document-viewer/LM7480-Q1/datasheet/GUID-89138DDE-D941-44D3-840D-FF47FB28C0DC).
- [JLCPCB LM74800QDRRRQ1 C3215600](https://jlcpcb.com/partdetail/TexasInstruments-LM74800QDRRRQ1/C3215600), [JLCPCB FDD18N20LZ C903557](https://jlcpcb.com/partdetail/onsemi-FDD18N20LZ/C903557), [LCSC Nexperia BUK9Y43-60E C456113](https://www.lcsc.com/product-detail/MOSFETs_Nexperia_C456113.html).
- [TI LMR36520](https://www.ti.com/product/LMR36520), [TI TPS2663](https://www.ti.com/product/TPS2663).
