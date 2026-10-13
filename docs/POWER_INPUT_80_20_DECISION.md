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


## 4.1 Nachgereichte Q1-Suche: verfügbarer 250-V-FET, niedrigere Kosten

Die erste Kostenprobe war noch zu pessimistisch: Bei LCSC finden sich **lagernde 250-V-N-MOSFETs** als Q1-Kandidaten, darunter:

| Kandidat | Preis 1 / 10 / 100 Stück (USD, LCSC) | Datenlage | Entscheidung |
|---|---|---|---|
| **Truesemi TSD16N25M** / LCSC **C2829043**, 250 V, TO-252 | **0,319 / 0,2501 / 0,1837** | günstig, derzeit lagernd; max. RDS(on)/Gate-Kennlinie bei 6 V, Original-SOA und Qualität/AEC unbekannt | **Nur Preisreferenz**, kein blindes „billig = sicher“ |
| **onsemi FQD16N25CTM** / LCSC **C415866**, 250 V, DPAK | **0,9493 / 0,8064 / 0,6652** | offizielles onsemi-Datenblatt, RDS(on) max **270 mΩ bei VGS=10 V**, **kein** spezifiziertes RDS(on) bei 5 V, Qg max 53,5 nC, ±30V VGS, derzeit lagernd | **Bevorzugter zu untersuchender 250-V-Prototyp-Kandidat**, vor 6-V-Cold-Crank-/SOA-/Temperaturtest **nicht freigegeben** |
| **onsemi FDD18N20LZ** / LCSC **C903557**, 200 V, DPAK | DigiKey EUR **2,55 / 1,648 / 1,134** (*nicht vergleichbare Währung und Vertriebssituation*) | bessere VGS=5V-RDS(on)-Spezifikation (max. 130mΩ); LCSC gerade Bestand 0; nur 200-V-VDSS | **Preis-/Gate-Vergleich**, nicht aktueller JLC-Bestückungskandidat |
| **Infineon AUIRFR4292TRL** / LCSC **C533343**, 250 V, DPAK | Preis noch ungeprüft | AEC-Q101, aber **Last Time Buy**, RDS(on) max 345mΩ @ VGS=10 V; Threshold max. 5V | **Nicht** als neue serienfähige Standardwahl übernehmen |

**Wirtschaftliche Konsequenz:** Beim 250-V-onsemi-FET statt 200-V-FDD kann der Materialpreis **unter ~1 USD** in Einzelmenge liegen, jedoch hat der FQD ein **2- bis 3-fach höheres RDS(on) bei spezifizierten 10 V** und keine garantierte 5-V-RDS(on)-Angabe. Es ist erst nach realem **6-V-Eingang/Temperatur-/Gate-Charge-/Dauerstrom-Test** zulässig, die Ersparnis mitzunehmen. Bei 6 V Fahrzeug-BAT+ ist **die MOSFET-Gate-Spannung nicht identisch mit der Bordnetzspannung**, da LM74800-Q1 über Charge Pump treibt, aber der tatsächliche VGS-/Treiber-Einregelverlauf unter Starttransienten bleibt zu messen.

**Zum Leitungsschutz:** Eine **58-V-DC-Nennsicherung** ist für normalen 36-V-Dauerbetrieb geeigneter als eine typische 32-V-Blade, stellt aber **keinen automatischen Nachweis sicheren Abschaltens eines harten Kurzschlusses während eines 200-V-Load-Dump** dar. Ein 200-V-Transient und die reale Quellimpedanz erfordern eine gesonderte Prüfung des Verhaltens von Sicherung/TVS/Q1, keine stillschweigende 200-V-Fuse-Rating-Unterstellung. Damit ist die gewählte Priorität **kein Brand im Fehlerfall** auch bei Pulsbeanspruchung einzuhalten.

Quellen: [LCSC TSD16N25M C2829043](https://www.lcsc.com/product-detail/C2829043.html), [LCSC onsemi FQD16N25CTM C415866](https://www.lcsc.com/product-detail/C415866.html), [onsemi FQD16N25C-Datenblatt](https://www.onsemi.com/pdf/datasheet/fqd16n25c-d.pdf), [Infineon AUIRFR4292-Datenblatt](https://www.infineon.com/assets/row/public/documents/10/49/auirfr4292.pdf?fileId=5546d462533600a4015355b59f38148b).

## 4.2 Neuer starker 80/20-Kandidat: **LM74930-Q1 integriert Circuit Breaker**

**Wichtiger Fund bei der Überprüfung der Zusatz-eFuse:** TI hat mit dem **LM74930-Q1** bereits einen für den **200-V-ungedämpften 24-V-Load-Dump** vorgesehenen Automotive-Controller, der im **gleichen einen IC** Verpol-/Rückstromschutz, OVP/UVLO, elektronische Lastabschaltung **sowie einstellbaren Überstrom- und Kurzschlussschutz** einschließlich Fault-Signal und **Auto-Retry oder Latch-Off** bietet. Anders als beim **LM74800-Q1** ist eine separate TPS26631 möglicherweise nicht nötig. [TI-Bauteil](https://www.ti.com/product/LM74930-Q1), [TI-Anwendungsbeschreibung](https://www.ti.com/lit/ab/snoaaa1/snoaaa1.pdf), [Abschn. 7.3.4/7.3.5 Auto-Retry/Latch](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf).

**Plausible Systemvorteile:** 4–65-V-nomineller Vin-Bereich, 6-V-Motorstart prinzipiell möglich, AEC-Q100, **OV cut-off** statt erzwungener linearer Clamp, 200-V-Load-Dump-HV-FET-Topologie; Sensestromwiderstand zwischen MOSFET und VOUT ermöglicht näher am Eingang einen definierten Überstromschutz. Die TI-Referenz dimensioniert **45 W und 3 A nominal / 5 A Peak**; das ist **nicht** unser automatisch richtiges Stromlimit. TripTracer nach echtem Lastbudget und den Folgen von USB-/5-V-Abzweigen **deutlich kleiner** dimensionieren. Q1/Q2, OVP-/UVLO-R und TVS sind weiterhin notwendig; zusätzlich Rsense sowie TMR/ILIM/ISCP-Beschaltung; weniger ICs heißt nicht null externe Bauteile.

### Nur die IC-Einkaufskosten (netto, Mouser DE, unverbindlicher Stand 13.10.2026)

| Variante | 1 Gerät | 10 Geräte | 100 Geräte | Funktionsabgrenzung |
|---|---:|---:|---:|---|
| **LM74800-Q1 + TPS26631** | **6,80 €** | **5,15 €** | **4,26 €** | zwei ICs, zusätzlichen eFuse-Blocking-FET und weitere R/Cs prüfen |
| **LM74930-Q1** | **5,39 €** | **4,13 €** | **3,47 €** | ein IC, **zusätzlicher Shunt und Timer-/Limiter-R/C**, 24-QFN- statt 12-WSON-IC |
| **Reine IC-Ersparnis** | **1,41 €** | **1,02 €** | **0,79 €** | *keine komplette Stückkosteneinsparung*: Shunt, Layout, PCBA/Extended-Fees, Kabelsicherung, Lieferanten und Test können das Delta verändern |
| LM74800-Q1 **ohne** eFuse | 2,58 € | 1,94 € | 1,59 € | auf Stückpreis günstiger, **Überstrom-/Kurzschluss-Risiko muss dann durch externe Sicherung/Buck- und Leiterbahnschutz nachgewiesen sein** |

[LM74930 QRGERQ1 bei Mouser](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74930QRGERQ1), [LM74800 QDRRRQ1 bei Mouser](https://www.mouser.de/de/ProductDetail/Texas-Instruments/LM74800QDRRRQ1), [TPS26631 bei DigiKey](https://www.digikey.de/de/products/detail/texas-instruments/TPS26631PWPT/12165640).

**Beschaffung:** LM74930QRGERQ1 = **LCSC/JLC C22428070, Extended**, VQFN-24-EP **4×4 mm**, LCSC derzeit als vorrätig gemeldet (Einzelpreis **4,4426 USD**, ab 100 **3,2765 USD**). [LCSC](https://www.lcsc.com/product-detail/C22428070.html), [JLCPCB](https://jlcpcb.com/partdetail/TexasInstruments-LM74930QRGERQ1/C22428070). Einbau/Handlötbarkeit **schwieriger** als SOT/SOIC, aber 12-WSON-LM74800 ebenfalls mit Unterseitenpad; JLC-SMT-Bestückung bevorzugt und bei Kostenvergleich mitrechnen. Das zusätzliche Shunt-Layout muss eine verlässliche Kelvin-Anbindung bieten.

**Auto-Retry vs. Latch-Off:** Der LM74930 unterstützt beides. Wegen Nutzerpriorität **Brand vermeiden, Datenverlust tolerieren** ist **Latch-Off bei dauerhaftem Überstrom** als sicherheitsorientierte Voreinstellung zu prüfen; normaler Neustart über ACC-Zyklus. Ein automatisches Retry im dauerhaften Kurzschluss könnte dagegen thermische Pulsbelastungen wiederholen; Betriebsmodus erst aus Temperatur-/Fehlerprüfung freigeben. [TI-Datenblatt 7.3.4–7.3.5](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf). Wegen der **bestehenden PWR-12-Anforderung (Auto-Retry)** ist dies **noch keine stillschweigende Änderung**, sondern ein zu entscheidender Trade-off.

**Stand nach der neuen Suche:** **LM74930-Q1 als priorisierter Schaltungs-Kandidat** für Eingangsschutz *mit explizitem Kurzschlussschutz*. **LM74800-Q1 als kostenarme Vergleichsvariante** bei nachgewiesener Sicherheit ohne eigene eFuse. Vor Bevorzugung einer Variante die vollständige R/C-/Shunt-/FET-/Fuse-/PCBA-BOM und die fatalen Fehlerfälle rechnen; kein „LM74930 löst alles“ behaupten. Insbesondere ist die **~100-µA-OFF-Zielvorgabe** mit jeder immer-verbundenen HV-/OV-Teilerstufe zu verifizieren und 200-V-Gate-/FET-/Sicherungsstress zu messen.

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
