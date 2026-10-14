# TripTracer V1 – laufende Gesamtkostenkontrolle

## 14.10.2026 – Wiederverwendbares TripPower-Modul, LM74800 gegen LM74930

[Dokumentierter TI- und Bestandsvergleich](../hardware/modules/TripPower_5V2A/CONTROLLER_COMPARE_LM74800_LM74930_2026-10-14.md): Fuer eigenstaendige 9–30V/5V2A-Platine mit zusaetzlichem VIN_PROTECTED-Abzweig wird LM74930QRGERQ1 **fachlich bevorzugt, aber NICHT umgestellt oder bestellfreigegeben**. Grund ist integrierte einstellbare gemeinsame OCP-/Kurzschlussabschaltung statt LM74800 ohne eFuse-Funktion. Die separate Abzweigleitung braucht weiter eigenen Kurzschlussschutz und eine passende fahrzeugseitige Sicherung.

**Nur IC-Preissnapshot Mouser Deutschland 14.10.2026 (EUR Listenpreise, Steuer-/Versandbasis nicht abgeglichen):** LM74800 1/10/100: 2,58 / 1,94 / 1,59 EUR, LM74930 5,39 / 4,13 / 3,47 EUR; Aufpreis **2,81 / 2,19 / 1,88 EUR je Stueck**. Mouser-DE-Stock-Snapshot ca. 1.442 vs. 62; LM74930 bei LCSC als C22428070 in mehreren Tausend Einheiten gelistet. **Gleiche Schutzfunktion ist nicht ohne Rsense, TMR, RILIM und Footprint-/SOA-/9V-/VIN-Protected-Zweigschutz-Pruefung belegt.** Kein unverifizierter kompletter Preis, keine Lieferung/Bestellung, kein PCB-Swap.



## 14.10.2026 – neuer Beschaffungs- und Architektur-Gate: COTS zuerst

**Vor jeder weiteren eigenentwickelten Regler-/Schutzschaltung zuerst nach fertig kaufbaren Modulen und Herstellerreferenzen suchen.** Marktvergleich, technische Eignung, gleiche Schutzfunktionen und komplette Einkaufskosten vor einem neuen KiCad-Entwurf dokumentieren. Verbindliches Beispiel: [COTS_POWER_SUPPLY_EVALUATION.md](COTS_POWER_SUPPLY_EVALUATION.md).

**12/24-V → 5 V / 2 A – neuer Prototyp-Preisvergleich (keine Freigabe):**

| Kandidat | Nachprüfbarer Teilpreis | Zusatzaufwand |
| --- | --- | --- |
| RECOM R-78K5.0-2.0L (SIP3, 6,5–36 V) | Reichelt DE **5,35 € / 1 inkl. MwSt.**, zzgl. Versand | TI LM74800-Q1/LM74930-Q1 samt externen FETs, Transienten-/Überstromschutz; Modul ohne EN braucht echten ACC-/HOLD-Abschaltpfad |
| RECOM RPH-3.0-CT (SMD, 4,5–55 V, EN, 3 A) | Mouser DE **7,89 € / 1**, **7,76 € / 10**, zzgl. Steuern/Versand | Referenz-Peripherie, 47-Pad-QFN-Bestückung, Verpol-/Transienten-/Leitungsschutz |
| Bisheriger TI LMR38020FSQDDARQ1 (Automotive, 4,2–80 V, 2 A) | Mouser DE **4,01 € / 1**, **3,02 € / 10**, **2,50 € / 100**, zzgl. Steuern/Versand | Induktivität, passive Bauteile, Buck-PCB/EMV-Auslegung und Schutzpfad |

**Preis-/Linkstand:** Web-Recherche 14.10.2026; aktuelle Verfügbarkeit und individuelle Steuern beim Bestellen neu prüfen. **Die frühere geschätzte Spanne 11–14 € für „LM74800 + RECOM“ ist keine vollständige, geprüfte Gesamtkalkulation** (insbesondere Kurzschluss-/Brand-, ACC-/OFF-, USB-/M8-Schutz, FET-SOA und Fertigung unberücksichtigt). **Keinen Gesamtpreis aus Einzelpreisen verschiedener Währungen/Steuerarten konstruieren.** Aktuelle Bauteile im KiCad bleiben bis zum vollständigen Gegenvergleich unberührt; die Dokumentation ist kein Kauf-/Fertigungsnachweis.


**AKTUELLE ENTWICKLUNGSAUSWAHL (14.10.2026):** **TI LMR38020-Q1** (Automotive, 4,2–80 V, 2 A, synchroner 5-V-Buck) wird als neuer bevorzugter Hauptregler übernommen. Der vorherige LM74930-Q1 + LMR36520-Entwurf bleibt als bisheriger experimenteller Referenzstand erhalten und ist **nicht mehr die Kosten-Baseline**; keine ungetestete KiCad-Schaltung als funktionsfähig ausgeben. Ziel: einfache externe Verpol-/Eingangs-/ACC-HOLD-Schutzbeschaltung mit möglichst wenig Bauteilen. **Load-Dump nach ISO 16750-2:2023 differenzieren:** Test A (ungedämpft, 24V bis 202V, 350ms) und Test B (zentral begrenzt, typ. 58V bei 24V) sind unterschiedliche Prüffälle. Für den preiswerten Grundentwurf erst Test-B-Profil mit tatsächlichem Klemmpuls, TVS-Klemmspannung bei Strom/Temperatur und 80V-Grenzen des LMR38020-Q1 bewerten; Test A bleibt als eigenständige ungeprüfte Anforderung/Restrisiko zu dokumentieren und darf nicht stillschweigend als bestanden oder ausgeschlossen gelten. 9–30V Normalbetrieb, ~9V weiches Kaltstartziel, externe BAT+/ACC-Leitungsabsicherung, sicherer Kurzschluss-/Thermikschutz, USB-Rückspeisesperre und geordneter ACC-AUS-Nachlauf bleiben bestehen. **Keine ISO-/Fertigungs-/Fahrzeugfreigabe.**

**AKTUELLE KALTSTART-ENTSCHEIDUNG (14.10.2026, ersetzt 6-V-Hartgrenze):** Ziel ist **ungefähr 9 V** während des Motorstarts, **kein hartes Mindestspannungslimit**. Unterhalb davon sind Display-Dimmung/Abschaltung und bei Bedarf ein definierter Reset/Neustart zulässig. **Keine zusätzlichen teuren Buck-/Bootstrap-/Puffer-Bauteile allein zur garantierten Weiterfunktion bei 6 V vorsehen.** Die 9–30 V als nominaler Auslegungsbereich, 12-/24-V-Fahrzeugkompatibilität und elektrische/thermische Sicherheit bei Spannungseinbrüchen und Transienten bleiben erhalten. Frühere Forderungen nach garantiertem 6-V-Betrieb in diesem Repository sind **überholt**; bestehende technische 6-V-Sensitivitätsrechnungen sind nur noch Studien, keine verpflichtende Bestehensgrenze.

**NEUESTE SPANNUNGSENTSCHEIDUNG (13.10.2026):** Der Nutzer senkt die obere Dauerbetriebsgrenze von 36 V auf **ca. 30 V**. Fuer die Auslegung gilt jetzt **9–30 V Dauerbetrieb**, weiterhin 12-/24-V-Bordnetze und **6 V beim definierten Motorstart**. Die gewaehlten Automotive-/Load-Dump-Transientenziele sind davon getrennt und bleiben bestehen; Spannungen oberhalb 30 V sind keine zugesagte Dauerbetriebsbedingung. OVP-Schwelle mit Toleranzen oberhalb 30 V und unterhalb der nachgewiesenen Bauteilgrenzen dimensionieren. **Anforderungsentscheidung, kein Testnachweis.**

Aeltere 36-V-Rechnungen in diesem Dokument bleiben als historische Szenarien erkennbar; sie sind keine aktuelle Dauerbetriebsanforderung.

**Stand: 13.10.2026 · Status: KEINE belastbare Gesamt-BOM oder Fertigungspreiskalkulation.** Ziel ist der **günstigste nachweislich taugliche** Rallye-Tripmaster, nicht ein möglichst teures Automotive-Elektronikprojekt. Kein verbindliches Gerätebudget oder Verkaufspreis vom Nutzer festgelegt; **keine künstliche Budgetobergrenze** annehmen.

**Neuer Komponenten-Preischeck (13.10.2026):** [POWER_INPUT_80_20_DECISION.md](POWER_INPUT_80_20_DECISION.md) vergleicht die **OV-Cut-off-Variante** mit Ti LM74800 (2,58 €/1) und lieferbarem **onsemi 250-V-FET FQD16N25CTM (0,9493 USD/1 bei LCSC)**. Im Unterschied zur teuren Altstudie ist keine aktive lineare 200-V-Ausgangsklemme vorgesehen. **Keine gemischten USD-/EUR-Summierungen, keinen angeblichen fertigen BOM-Preis**; relevante Zener-/TVS-/Fuse-/ACC-Logik und Prüfkosten sind noch offen. Die preisgünstigen 250-V-FETs sind **noch nicht 6-V-Gate-/Temperatur-/SOA-freigegeben**.

**VERBINDLICHE NEUE ENTSCHEIDUNG (13.10.2026):** Variante **C mit LM74930-Q1 + LMR36520 + elektronischer ACC-/HOLD-Selbsthaltung** ist ausgewählt. **Keine separate TPS26631 und keine eingelötete Schmelzsicherung, für deren Wechsel Lötarbeit nötig ist.** ACC- und BAT+-Fahrzeugzuleitungen bleiben getrennt quellseitig abgesichert, ggf. durch ohne Löten wechselbare Sicherungen. **Beschaffungspriorität: Reichelt und andere deutsche Lieferanten**, soweit Preis/Verfügbarkeit stimmen. Kostenvergleich immer inklusive MwSt., Versand, Mindestbestellwert, Lagerbestand, Lieferzeit und Eigenbestückungsaufwand; Mouser/DigiKey/LCSC bleiben zulässige Alternativen. JLCPCB-PCBA und Basic/Extended sind kein Muss. Frühere Variante-B-Kalkulation nur Archiv, nicht mehr als aktive Alternative zur Entscheidung. **Der endgültige BOM-Gesamtpreis ist noch offen.**

## Q401-Preisentscheidung 14.10.2026 – umgesetzt im KiCad-Entwicklungsbranch

Auf ausdrücklichen Nutzerwunsch ist der kostengünstige **onsemi FQD16N25CTM, LCSC C415866 (250V, DPAK)** wieder Q401-Entwicklungskandidat statt des teureren **Infineon IPB17N25S3-100 (250V, D2PAK)**. In `01D_INPUT_PROTECTION.kicad_sch` und der tragbaren Projekt-Symbolbibliothek ist Q401 tatsächlich umgestellt und der Pinout-Regressionstest entsprechend angepasst. Kostenbasis LCSC **0,9493 USD/1, 0,8064 USD/10, 0,6652 USD/100**, ohne Mehrwertsteuer/Versand; **keine EUR-Gesamtsumme durch Mischen von Währungen**. Die aktuelle V1-KiCad-BOM-DRAFT enthält noch historische/stückweise Teilkalkulationen, ist **keine validierte aktuelle Einkaufs-BOM**.

**Sicherheits- und Physikvorbehalt:** 270 mΩ max bei VGS=10V statt rund 100 mΩ des vorigen Infineon-Kandidaten; bei 2A erhöht dies die Verlustleistung am Q401 von etwa 0,4W auf **1,08W** (nur 25°C/10V Gate, keine Hot-/6V-Garantie). FQD16N25CTM ist nicht als Automotive AEC-Q101 qualifiziert nachgewiesen; 6V Cold-Crank, 200V-Load-Dump-SOA, thermischer Strom-/PCB-Sicherheitsnachweis, VS-Bootstrap und finale BOM bleiben offen. Günstiger heißt ausdrücklich **nicht ungeprüft fahrzeugtauglich**. Ein geeigneter 250V-Typ mit nachgewiesener niedrigeren VGS-/Temperatur-SOA kann trotz höherem Teilepreis wirtschaftlicher sein.

**Verbindliche Regeln bleiben:** Variante C **LM74930-Q1 + LMR36520**, 9–30V normal, 6V definiertem Start, 200V Transientenziel, einfacher relaisloser ACC/HOLD, keine zweite TPS26631, keine auszulötenden Sicherungen, 80/20 Preis-/Brandsicherheitsoptimierung, KiCad-10-Portabilität, keine Hersteller-/ERC-/DRC-/Fertigungs-/Fahrzeugfreigabe ohne Nachweis.

## Übergeordnete 80/20-Sicherheitsentscheidung (13.10.2026)

**Gefahr vor Verfügbarkeit:** Ein Tripmaster darf bei seltenen Extremtransienten ausgehen, neu starten oder im Einzelfall einen laufenden GPX-/CSV-Datensatz verlieren; diese Folgen sind akzeptabel, wenn der Zustand **elektrisch und thermisch sicher** bleibt. **Nicht akzeptabel:** Fahrzeugkabelbrand/-überlast, dauernder gefährlicher Kurzschluss, thermisch überlastete Leistungsteile oder unkontrollierter Dauerbetrieb unter einem Fehler. Für Schutzmaßnahmen nur dann zusätzliche Bauteile vorsehen, wenn sie **erforderliche elektrische Sicherheit**, normale Funktion oder einen erheblichen Nutzwert belegen.

**Kostenfragen ab jetzt nach Risiko:** 1. Verhindert die Komponente Brand/gefährliche Überlast? 2. Ist sie für 9–36 V normal, ≥6 V während definiertem Motorstart oder für das tatsächlich gewählte ISO-Testprofil nötig? 3. Verhindert sie nur einen seltenen Datenfehler? **Punkt 3 allein rechtfertigt keine teure Redundanz.** Normalen ACC-AUS-Dateischluss weiterhin kostengünstig anstreben; Auto-Retry/eFuse-Ausstattung und unabhängige zweite Abschaltung auf tatsächliche Gefahren, Heizzyklen, Kabelsicherung und Mehrkosten prüfen, **nicht vorzeitig ohne Zustimmung streichen**.

**Verbindliche Konzeptänderung vor weiterem Schaltplan:** Die ältere pauschale Forderung nach *zwei unabhängig fehlersicheren Hauptstromabschaltkanälen* gilt **nicht mehr als automatische Randbedingung**; nach FMEA über gefährliche Einzelfehler entscheiden, ob und wozu ein zweiter Pfad gebraucht wird. Der LM74800-Q1 bleibt kostengünstiger Erstkandidat, ohne eine implizite Brandsicherheitsgarantie oder Normfreigabe.

## Neue Anforderung: ISO-16750-2:2023-Testziele wirtschaftlich abdecken

**Entscheidung 13.10.2026:** Elektrische Belastungsprüfungen für 12-/24-V-Straßenfahrzeuge nach den relevanten Teilen von **ISO 16750-2:2023** als Designmaßstab; für schnelle Spannungspulse zusätzlich die relevante **ISO 7637-2** prüfen. Die Ausführung des **TI LM74800-Q1-Referenzdesigns für 200 V ungedämpften 24-V-Load-Dump** hat Vorrang als **kostensparender technischer Ausgangspunkt** vor einer unbegründeten zweiten Surge-Stufe. Es ist keine fertige Normfreigabe und ersetzt keine getrennte Überstromschutz-/eFuse-Funktionsbewertung.

**Kostenentscheidung:** Den Schutz pro Prüfprofil nur einmal dort einbauen, wo er technisch wirksam ist; Mehrkosten für redundante/zusätzliche ICs nur bei nachgewiesenem Fehlerfall-Nutzen freigeben. Preisvergleiche weiterhin **auf identischem Funktions- und Prüfumfang** anstellen. Fehlende Messungen und fehlende Einzel-BOM-Preise kennzeichnen. ISO 16750-2:2023 umfasst keine EMC-Prüfung und gilt nicht direkt für Motorräder/Mopeds; Tests dieser Fahrzeuge gesondert definieren.

**Neue IC-Auswahlprüfung 13.10.2026:** Der **LM74930-Q1** bringt den bislang in einer zweiten TPS26631 gesuchten Überstrom-/Kurzschlussschutz **integriert** mit und unterstützt den TI-200-V-Load-Dump-Aufbau mit externen MOSFETs. Netto Mouser Deutschland: **5,39 €/1, 4,13 €/10, 3,47 €/100** gegenüber den früheren **6,80 / 5,15 / 4,26 €** für LM74800-Q1 + TPS26631 zusammen (nur ICs). **Betriebs-/Shunt-/R/C-/VQFN-Bestückungs- und Sicherungskosten noch NICHT enthalten**; siehe [POWER_INPUT_80_20_DECISION.md](POWER_INPUT_80_20_DECISION.md). LCSC/JLC PCB C22428070, **Extended**. Sicherheitsvorteil gegen unkontrollierten Kurzschluss ist plausibel, aber noch nicht nachgewiesen. Keine fertige Gesamt-BOM.

**MegaSquirt-V3.57-Benchmark (13.10.2026):** [MEGASQUIRT_POWER_BENCHMARK.md](MEGASQUIRT_POWER_BENCHMARK.md) zeigt **erhebliche Einsparungen durch Vereinfachung der Topologie**, ohne Brandschutz zu opfern. **TI LMR36520ADDAR** 5V/2A-Buck inkl. internem Short-/Thermal-Schutz bei Mouser DE **2,80 €/1, 2,11 €/10**, lieferbar; bei LCSC **1,5894 USD/1**, soweit Händlerstand. **Diese IC-Preise sind KEIN Gesamtversorgungspreis.** 9–36V + 6V-Kaltstart sowie 200-V-ISO-Test A brauchen geeignete Eingangsstufen; Original-MegaSquirt-MOV hat nur 18V DC, der LM2937-LDO max. 26V/0,5A. **Präferenz neu: lieferbare, preiswerte, möglichst handlötbare Teile von beliebigen seriösen Distributoren; JLCPCB Extended/automatisierte Bestückung nur als optionalen realen Angebotsvergleich**. Frühere JLC-Basic-Priorität in den verbindlichen Anforderungen überholt. Selbsthaltung zuerst einfach per ACC/MCU-HOLD am Buck-EN prüfen; ZusatzeFuse/Watchdog nur falls gefährliche Fehlerfälle oder gemessene Anforderungen es verlangen.

**Aktueller 80/20-Entscheidungsvergleich (13.10.2026):** [POWER_VARIANTS_COST_SAFETY.md](POWER_VARIANTS_COST_SAFETY.md) stellt **MegaSquirt-inspirierte Labor-Minimallösung, LM74800 + geeignete SMD-Schmelzsicherung und LM74930 mit integriertem elektronischen Circuit Breaker** gegenüber. Verbindliche Empfehlung als **Entwicklungsrichtung**: **LM74930 + LMR36520** ohne zweite TPS26631; ca. **2,81 € reine Mehr-IC-Kosten pro Einzelsatz** gegenüber LM74800, zusätzliche Rsense/R/C-/Bestückungskosten offen. Dieser Aufpreis soll **gefährliche Teilüberlast und Kurzschluss**, nicht Datenkomfort adressieren. Eine billigere **LM74800+Sicherung**-Variante bleibt als Pareto-Alternative offen, wenn dieselben thermischen Fehlerprüfungen bestanden werden. Alle vollständigen Materialkosten/Teileanzahlen sind grobe Schätzspannen ohne vollständige Freigabe-BOM; PCB/Versand/MwSt. fehlen.

**Neuer echter Buck-Schaltplanstand a1 (13.10.2026):** `02_5V_Buck.kicad_sch` samt `Tripmaster.pretty/L_Bourns_SRP6030VA_100M.kicad_mod` und der Entwurfs-BOM wurde **tatsächlich aktualisiert**, nicht nur geplant. Verifizierte Online-Einzelteile Mouser Deutschland: **U101 LMR36520 2,80 €/Stück netto**, **L101 Bourns SRP6030VA-100M 1,25 €/Stück netto** = **4,05 € netto** nur für diese zwei Positionen, nicht vollständiger Buckpreis. Neue C106/C107 und korrigierte R/MLCC-Werte noch ohne verbindliche Einkaufspreise; bei Reichelt vorhandene Kondensatoroptionen anhand DC-Bias/Verfügbarkeit noch auf MPN freizugeben. Bourns Isat typ 5A >= TI maximale High-Side-Stromgrenze 3,6A; Spulenthermik/Layoutprüfung bleibt offen. Diese Auslegung ersetzt **nicht** die noch fehlende LM74930-Eingangsstufe oder USB/ACC-HOLD.

## Systemstatus der Kalkulation

- Bestehendes `hardware/kicad/TripTracer_V1_BOM_DRAFT.csv` umfasst derzeit **21 vorläufige Positionen** und unvollständige Hardware; die Felder `Einzelpreis_1/10/50/100` sind noch leer. **Eine gesamte V1-Stückkostensumme ist dadurch derzeit nicht seriös berechenbar.**
- Die historische, überdimensionierte LTC4380-/TPS26631-/250-V-FET-Eingangsschutz-Variante ergibt bei einer Teil-BOM **21,92 €/Gerät** im Einzelbezug; **nicht als neues Kosten-/Sicherheitsminimum übernehmen**. Die detaillierte, uneinheitlich verifizierte Preisschätzung ist in [SOLID_STATE_POWER_ARCHITECTURE.md](SOLID_STATE_POWER_ARCHITECTURE.md) archiviert.
- LM74800-Q1-Eingangsschutz-Forschung deutet auf ca. **9,13–10,13 €/Gerät für eine vereinfachte Teil-Surge-Schutz-BOM** hin (Einzelmengen, netto, teilweise Schätzmaterial, **ohne** elektronische Strombegrenzung/Auto-Retry, unabhängige Abschaltung, ACC/HOLD, USB, Fertigung). **Das ist kein vollständiger Vergleich der Gesamtsystemkosten**. Kein Kosten- oder Funktionsvorteil behaupten, ehe beide Varianten denselben Schutzumfang und Prüfnachweis liefern.

## Pflichtstruktur je Baugruppe

| Prüffeld | Immer ausweisen |
|---|---|
| Pflichtfunktion / Prämisse | Exakt welche HW-/PWR-Anforderung und welchen Fehlerfall erfüllt das Teil? |
| Preisgünstige Basisoption | Vollständige, norm-/lastgerecht dimensionierte funktionale Option, ggf. Automotive-Referenzdesign |
| Teurere Alternative | Konkreter zusätzlicher Nutzen, was entfällt, welche Zusatzbauteile sind zwingend? |
| Gesamte Bauteilkosten | MPN, Menge, Quelle/Datum, **2/10/100 Stück**, Steuer-/Versand-/Bestückungsstatus |
| PCB-/Fertigungsfolgen | Mehrfläche, nötige Kupferfläche, thermische Anbindung, 2/4 Lagen, JLC Basic/Extended, zweite Seite, manuelle Arbeit |
| *Inkrementelle* Mehrkosten | €/Gerät und Gesamtkosten für jeweilige Stückzahl, gegenüber der **gleichen Funktionsspezifikation** |
| Technische Entscheidung | günstigere nachweislich ausreichende Variante bevorzugen; teurere nur mit konkretem Nutzen |
| Unsicherheit | Endpreise/Verfügbarkeit, Automotive-/SOA-/EMV-/ERC-/DRC-Prüfung explizit „offen“ |

**Keine künstliche Redundanz:** Zwei in Serie geschaltete teure Controller sind nicht allein durch das Wort „Sicherheit“ gerechtfertigt. Zuerst gemeinsame Fehlerfälle, unabhängige Abschaltanforderungen und bereits integrierte Schutzfunktionen betrachten. Die Pflichtfunktionen Kurzschluss-/Leitungsschutz, Kfz-Transienten, Verpolung, sichere SD-Abmeldung, USB-Entkopplung bleiben erhalten; der preisgünstigste Weg zu **nachweisbar** sicheren Funktionen gewinnt.

## Motorstart-Kostenentscheidung (13.10.2026)

**Neue verbindliche Untergrenze:** 6 V statt 3 V beim Motorstart (PWR-17). Keine zusätzlichen Bauteile oder Energiespeicher allein zur Überbrückung eines 3-V-/15-ms-Einbruchs einkalkulieren. **Unmittelbare Ersparnis noch unbekannt**, da Regler-/MOSFET-/eFuse-Kette bei 6 V und Last erst geprüft werden muss; keine pauschale Einsparzahl erfinden. Wandler mit geeigneter UVLO, ausreichend geringem Spannungsabfall und Backlight-Lastabwurf kostengünstig priorisieren. 9–36 V Dauerbetrieb und ISO-16750-2-Ziel bleiben unverändert.

## Kostenrisiken für die Gesamtrechnung, derzeit priorisiert

| Baugruppe / Kostenthema | Nachweisbarer Stand / Risiko | Kostenkontrolle vor Festlegung |
|---|---|---|
| **Eingangsschutz, ACC-HOLD** | In bisheriger Designstudie **21,92 € Teil-BOM** für Doppelcontroller, neue alternative Teil-BOM **9,13–10,13 €** unvollständig | vollständige Funktionsvergleichs-BOM mit realen Lieferartikeln, SOA und Test-A-Ziel; zweiten Controller nur bei unverzichtbarer Funktion |
| **6 FILN-Leuchttaster** | Projektanforderungen nennen ca. **3,20 USD je Taster**, FILN-Versand **28 € pro Bestellung** als bisherigen Ansatz | Alternative mit vergleichbarer Haptik/Lebensdauer, Versandbündelung; Kosten der Taster **plus** Auslösekabel/Ring-LED berücksichtigen |
| **Riverdi-Display + Beleuchtung** | Hochwertiges 3,5-Zoll-Display, Boost-/LED-Treiber und Einbau; noch kein finaler Gesamtpreis | komplettes Modul inkl. Versand und Backlight-Treiber bepreisen; keine Displayänderung ohne Bewertung des Nutzerwerts |
| **GNSS/Antennenpfad** | MAX-M10N, aktive GNSS-Antenne und HF-Steckverbindung | Gesamtmodul-/Antennen- und Assemblierungspreis inkl. Steck-/Koaxteile erheben |
| **Platine 2 vs. 4 Lagen** | 2 Lagen bevorzugt, 4 erlaubt bei technischer Notwendigkeit | JLCPCB *konkretes* Angebot für 5 PCB/2 PCBA vergleichen, nicht pauschalen Kostenfaktor erfinden |
| **JLCPCB Basic/Extended** | BOM unvollständig, Kategorien noch nicht verifiziert | auch Bestückung/Feeder-/Extended-/Mindestmengen- und Non-Stock-Kosten einrechnen |
| **Mechanik/Service** | 3D-Gehäuse, M8-Kabel/Stecker, USB, Taster, Halter, Dichtung | Gehäuse-/Befestigungs-/Kabellängen und Versand/Steuern nicht außerhalb der „Teilekosten“ vergessen |
| **Lieferantenvielfalt** | LCSC/JLCPCB, DigiKey, Mouser, FILN möglich | Mindestbestellwerte, getrennte Fracht, Zoll/MwSt. und Nachbestellrisiken berücksichtigen |

## Entscheidungsschwellwert ohne erfundenes Euro-Budget

Jede neue Baugruppe startet mit **„Welchen Schutz oder welche Funktion brauchen wir wirklich?“**. Wenn die bevorzugte Lösung **wesentlich teurer** ist als eine ebenfalls spezifikationskonforme Alternative, vor Auswahl **Mehrpreis pro Gerät und technisches Alleinstellungsmerkmal** ausweisen; gegebenenfalls zurückstellen. Ein vermeintlicher Sicherheitsgewinn muss mit Datenblatt, Fehlerbaum und erforderlichem Test nachweisbar sein.

### Nächste konkrete Arbeitsschritte

1. Gesamte V1-Hierarchie aus KiCad in eine **vollständige vorläufige BOM** überführen, nicht bei den 21 Legacy-BOM-Positionen stehenbleiben.
2. **Einkaufskosten pro Stück und per 2/10/100 Geräte**, getrennt nach verifizierten Händlerpreisen, Schätzpreisen und unbekannten Preisen, vollständig gegenrechnen. Fehlende Preise **nicht als 0 €** verrechnen.
3. Preislich dominierende Baugruppen (Displays, Taster samt Versand, GNSS, Versorgung, PCBA, Gehäuse) nach Gesamteinfluss priorisieren und Angebote/Austauschbarkeit prüfen.
4. Vor KiCad-Auslegung neuer Eingangsschutz-Topologie die vollständig funktional **vergleichbare**, kostenoptimierte BOM auslegen; Sicherheits-/Ruhestrom-/SOA-Gates weiterführen.
5. Laufende Zwischenstände und Änderungen nach jeder Baugruppe hier dokumentieren; Änderungen an `main` erst nach Review/Merge.

**Keine Freigabe vor:** ERC/DRC, Pin-/Package-Kontrolle, Fahrzeugstörprofil, SOA/thermisches Derating, realer USB-Bordnetz-Rückspeiseschutz, SD-Flush, Mess- und Fertigungskostenbewertung.


## 2026-10-14: repair ACC-only buck EN overstress

[Implemented discrete startup correction](validation/2026-10-14-acc-vin-source-fix.md): +2 SOT23 BJT (Nexperia PMBT5551,215; Diodes MMBT5401-7-F), +3 1206 resistors (2x Panasonic ERJP08F1002V; 1x ERJP08F4701V); reuse D911/R912 and change R911/R913/R915 values. Native BOM now 58 power components. No new supply IC, auxiliary regulator, footprint file or PCB change. Alternatives: direct divider invalid at ACC live/BAT absent; simple diode clamp has no assured VIN+0.3V bound; second opto would add an unqualified low-current CTR dependency. Actual complete 2/10/100-device delta including VAT/shipping/assembly remains **NICHT BELASTBAR**. Exact stock, Reichelt equivalence, LCSC IDs and JLC categories ungeprüft; no prices invented and no purchase. Manufacturer confirms Panasonic P08 1206 resistors at 0.66W nominal; temperature derating and circuit pulse tests still required.


## 2026-10-14: prearmed ACC-off HOLD, without another IC
[Electrical change and alternatives](validation/2026-10-14-prearmed-acc-hold.md): reuse TLC555/AND/opto; remove seven obsolete edge/inversion parts, add BAS116Q D503, BAT54WS D912 and 10k R505. Net four fewer parts. R501/C501 change to 1M/22uF in their existing footprints for leakage margin. A separate RC-reset transistor was rejected for hot leakage; TMUX1101 at listed EUR 1.84/1, 1.37/10, 1.12/100 plus passives is avoided by using the unloaded Q912 inverse node. No invented savings: capacitor/resistor sourcing and complete landed 2/10/100-device delta remain **NICHT BELASTBAR**, LCSC/JLCPCB ungeprüft. No PCB work or purchase.

Native KiCad 10.0.6 run 38561884651 verified the resulting **54-component** active power BOM at 623171d9; topology/state regressions pass, full ERC/DRC and hardware release remain open.


## 2026-10-14: complete MCU ignition-off interface
R207 100k/1% uses the existing 1206 symbol/footprint; candidate Panasonic ERJP08F1003V. One passive connects the existing protected ACC detector to GPIO34 and isolates a stuck-low MCU output from the hardware timer trigger. Direct connection saves one resistor but can defeat the timer on that fault; another sensing IC/transistor is unnecessary for this interface. Expected native power BOM55 parts, including R207 on the MCU sheet. Actual price, Reichelt availability, LCSC/JLC category and landed2/10/100-device delta remain ungeprüft; no fabricated saving or purchase. [Circuit and qualification limits](validation/2026-10-14-acc-shutdown-interface.md).


## 2026-10-14: input clamp above central58V limit
[Implemented candidate and procurement limits](validation/2026-10-14-input-flat-clamp.md): replace D901 with S5MC-13-F1000V and D902 with TVS5800VEBR58V flat clamp; R911/R915 change to30.1k for forward-drop headroom. No added parts, controller chain, PCB change or order;55 power parts expected. Retrieved DigiKey US1/10/100 prices are USD1.03/.637/.4126 for S5MC and USD.72/.512/.4025 for TVS5800; no tax/shipping/FX/assembly assumptions. TVS5800 currently lacks confirmed stock, so not a released procurement BOM. Bigger SLD8S43A USD4.53/2.981/2.1012 still clamps below the central58V bus and is not an automatic electrical solution. New tiny VEB package increases reflow/microscope effort; new1000V diode increases forward dissipation. These costs and TestA/ISO/thermal/fuse gates remain explicit. Reichelt equivalence, complete2/10/100-device landed costs, and JLC category unverified.

Native KiCad10.0.6 at8374f624 confirmed55 power parts and all input/buck/HOLD/mux topology/envelope checks; complete node-to-net mapping unchanged by the following label cleanup. ERC33/DRC5 remain unresolved; no PCB edits. [Verified evidence and report hashes](validation/2026-10-14-input-flat-clamp.md).


## 2026-10-14: full-load wiring loss and external fuses
[Implemented circuit and bounded calculations](validation/2026-10-14-vehicle-harness-hold.md): R911/R91524.9k, R914154ohm; no added PCB parts or IC. Add two explicitly offboard replaceable fuse candidates, BAT3A0997003.WXN and ACC2A0997002.WXN, with installation tags in the native BOM. Qualified existing source fuse positions are preferred over new source-side holders. Optional58V FHM holders add real cost (retrieved USD10.33/7.55/5.40 each at1/10/100); do not swap in a cheap32V holder without qualification. R914 YAGEO154ohm candidate USD.10/.047/.0247; Panasonic1206 alternative exists but unquoted. F902 Mouser DE EUR.886/.668/.501, F901 DigiKey USD1.04/.792/.6063, catalog observations only. TVS5800 small-quantity supply remains unconfirmed; no electrical-protection downgrade for a claimed in-stock substitute. Reichelt58V MINI holder, complete landed2/10/100-unit totals and JLC category ungeprueft. No order or PCB change.

The diode may dissipate2.75W in the conservative9V case; actual PCB heat removal is unproven. Copper/cooling, crimps, holders and M8 qualification are real costs, not zero-cost assumptions. 2A/70C, fuse clearing and vehicle tests remain gates.
