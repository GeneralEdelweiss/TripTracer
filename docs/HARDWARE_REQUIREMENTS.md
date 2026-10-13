# TripTracer – Hardware-Anforderungen

**Status:** Arbeitsdokument für gemeinsames Brainstorming, nicht als freigegebene Fertigungsspezifikation zu verstehen.
**Erstellt:** 13.10.2026  
**Ziel:** Erst Funktionen, Betriebsbedingungen, Randbedingungen und Prüfkriterien festlegen; **danach** geeignete Bauteile, Schaltung und PCB-Layout auswählen.

## Vorgehensweise

1. Wir besprechen jeweils **einen Themenblock** und idealerweise nur eine offene Entscheidung auf einmal.
2. Bestätigte Wünsche werden als **Festgelegt** markiert; Annahmen bleiben **Offen**, vorhandene Bauteile **Bestand V0.3**, weitere Vorschläge **Wunsch**.
3. Nach jedem Gespräch die betroffenen Anforderungen und das Entscheidungsprotokoll aktualisieren.
4. Erst wenn die Anforderungen des Themenblocks hinreichend geklärt sind, konkrete Hersteller-/Teilenummern und die Schaltung festlegen.
5. Technische Prüfkriterien dokumentieren. Ein Schaltplan, eine erfolgreiche KiCad-Prüfung oder eine Bauteilauswahl allein ist noch keine elektrische oder Fahrzeugfreigabe.

**Status-Legende:**
- **Festgelegt** = vom Nutzer für die nächste Entwicklungsrevision bestätigt; kann noch technische Prüfung erfordern.
- **Bestand V0.3** = in der bisherigen KiCad-V0.3-Revision enthalten, nicht zwingend bereits für die nächste Revision freigegeben.
- **Wunsch** = Funktion aus der Ideensammlung, Umfang oder technische Lösung noch zu klären.
- **Offen** = keine Entscheidung getroffen.

## A. Einsatz und Gesamtkonzept

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| SYS-01 | **Festgelegt** | GPS-gestützter Tripmaster für unterschiedliche Fahrzeuge, Rallye- und Toureneinsatz | Umstecken ohne Änderungen am Gerät |
| SYS-02 | **Festgelegt** | Gerät zwischen mehreren Autos/Motorrädern einfach wechseln | Identische Stromanschlüsse und passende Halterungen je Fahrzeug |
| SYS-03 | **Festgelegt** | KiCad 10, transportable Projektdateien und Bibliotheken | ERC/DRC und 3D-Pfade vor Fertigung prüfen |
| SYS-04 | **Offen** | Gewünschter Temperaturbereich, Feuchte-/Staub-/Regenschutz und Vibrationsbelastung | Einsatzprofil festlegen |
| SYS-05 | **Offen** | Kosten-, Baugrößen- und Leistungsbudget | Zielpreis und maximale Gehäuseabmessungen festlegen |

## B. Stromversorgung und Schutz – erster Brainstorming-Block

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| PWR-01 | **Festgelegt** | Regulärer Betrieb sowohl an **12-V- als auch an 24-V-Fahrzeugbordnetzen**, ohne manuellen Spannungswahlschalter | Durchgängigen zulässigen Eingangsspannungsbereich, Motorstart-Unterspannung, Ladespannung und Transienten für beide Netze spezifizieren |
| PWR-02 | **Festgelegt** | **M8, 3-polig, A-codiert, Schraubverriegelung** als normaler Fahrzeug-Stromanschluss; keine einfache DC-Hohlbuchse | Einbaustecker am Gerät, Kabelbuchse fahrzeugseitig; Strombelastbarkeit, Orientierung und Schutzart prüfen |
| PWR-03 | **Festgelegt** | **Elektronischer Überstromschutz (eFuse) in SMD-Bauform direkt auf der Platine** im 12-/24-V-Bordnetz-Eingang; automatische Wiederherstellung nach einem geeigneten Fehlerfall | Stromgrenze, Einschaltstrombegrenzung, Spannungsbereich, thermische Auslegung und Verhalten bei dauerhaftem Kurzschluss erst festlegen; mögliche ergänzende Schmelzsicherung anhand Fehleranalyse prüfen |
| PWR-04 | **Festgelegt** | Ein **einfaches, selbst angefertigtes M8-Anschlusskabel** ohne integrierten gerätespezifischen Sicherungshalter | **Fahrzeugseitige Absicherung ist vom Nutzer bestätigt**: Anschluss an bereits abgesicherten Abgriff oder separate Sicherung nahe der Batterie; Leitungsquerschnitt/-länge und zur Zuleitung passende Sicherung festlegen |
| PWR-05 | **Festgelegt (Sicherheit)** | **Die Fahrzeugzuleitung wird fahrzeugseitig abgesichert.** Die eFuse im TripTracer kann keinen Kurzschluss im Kabel vor dem Gerät absichern. Bei direktem Batterieanschluss Sicherung nahe der Batterie; alternativ bereits abgesicherten Abgriff verwenden | Sicherungswert und Kabelquerschnitt aufeinander abstimmen, beide Bordnetzspannungen und maximalen Quell-Kurzschlussstrom berücksichtigen |
| PWR-06 | **Festgelegt** | **USB-C** dient sowohl für USB-Daten/Firmwareupdates als auch zur alternativen Versorgung mit **5 V** (PC oder externer Zigarettenanzünder-auf-USB-C-Adapter) | Gerät muss zum Flashen über USB allein funktionieren; 5-V-Strombudget prüfen |
| PWR-07 | **Festgelegt** | **Keine rohe 12-V- oder 24-V-Bordnetzspannung auf USB-C.** Externe Fahrzeugadapter müssen das Bordnetz außerhalb des TripTracers auf normgerechte USB-5-V-Versorgung wandeln | USB-Geräte-/Host-Schutz und CC-Beschaltung prüfen |
| PWR-08 | **Festgelegt** | Sichere Entkopplung von USB-5-V- und Bordnetz-Eingang; keine Rückspeisung bei gleichzeitigem Anschluss | Umschalt-/Prioritätsverhalten und Ausfallfälle festlegen |
| PWR-09 | **Festgelegt** | Bordnetzschutz für **12-V- und 24-V-Fahrzeuge** mit Überstromabschaltung durch eFuse; **Verpolschutz ist bei der konkret ausgewählten eFuse nachzuweisen** oder zusätzlich aufzubauen. Transienten/ESD, Load Dump, Spannungswandlung und sichere Masseführung bleiben gesondert zu lösen | Nicht jede eFuse bietet Verpolschutz oder ausreichend hohe Spannungsfestigkeit; Schutzfunktionen per Datenblatt und Tests für beide Bordnetze verifizieren |
| PWR-10 | **Festgelegt** | Vorläufige M8-Belegung: **Pin 1 = +12/24 V Bordnetz, Pin 3 = GND, Pin 4 = Reserve/NC** | Konkreten Gegenstecker und Kontaktansicht anhand Datenblatt verifizieren; 24-V-Tauglichkeit ergibt sich aus der gesamten Schaltung und nicht allein dem Steckertyp |
| PWR-11 | **Festgelegt** | **12-V- und 24-V-Fahrzeuge** unterstützen; automatisch nutzbar am selben M8-Eingang ohne Umschalten oder Umbau | Eingangsspannungsbereich und Schutz/Regler für beide Fahrzeugklassen erst auslegen und prüfen; die bisherige V0.3-Hardware erfüllt diese Vorgabe noch nicht nachweislich |
| PWR-12 | **Festgelegt** | **Kompakte SMD-eFuse mit automatischer Rückstellung**, statt steckbarer oder fest eingelöteter Schmelzsicherung als primärem Überstromschutz; kein von außen zugänglicher Sicherungshalter erforderlich | Auto-Retry-/Latch-Verhalten, sichere Reaktion bei Kurzschluss, zulässiger Fehlerstrom und ggf. notwendiger unabhängiger Schutz müssen für den ausgewählten Baustein verifiziert werden; eFuse ersetzt nicht die externe Kabelsicherung |
| PWR-13 | **Offen** | Was passiert bei gleichzeitig eingestecktem USB und M8? | Versorgungsvorrang und Umschaltunterbrechung |
| PWR-14 | **Bestand V0.3** | 12-V-Eingang J1 → Eingangsabsicherung/-schutz → 3,3-V-DC/DC; USB bisher nur Daten | Bei nächster Revision auch für 24-V-Fahrzeuge neu auslegen (PWR-01/09/11); an PWR-02/03/06/08 anpassen. Vorhandene V0.3-Schaltung nicht als 24-V-tauglich ausgeben |
| PWR-15 | **Festgelegt** | **Unterbrechungsfreier Betrieb beim Motorstart** in 12-V- und 24-V-Fahrzeugen: kein MCU-/GNSS-Neustart, keine Unterbrechung von Anzeige, Distanzzählung oder Streckenaufzeichnung durch den Startvorgang | Kritischen Spannungs-/Zeitverlauf beim Anlassvorgang, Mindest-Eingangsspannung und erforderliche Überbrückungszeit/Pufferenergie messen und festlegen; Funktionstest noch offen |

## C. Steuerung, Kommunikation und Speicher

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| MCU-01 | **Festgelegt** | **ESP32-S3-MINI-1-N8** als Prozessorplattform beibehalten | GPIO-Budget, RAM/Flash und Bootstrapping für alle Zusatzfunktionen vor PCB prüfen |
| MCU-02 | **Festgelegt** | Firmwareupdates direkt über **USB-C**, ohne zusätzliche 12-V-Stromquelle | USB-Boot-/Recovery-Prozedur in der späteren Hardware verifizieren |
| MCU-03 | **Bestand V0.3** | FRAM MB85RC256VPNF (I²C) für wichtige Zähler und Einstellungen | Schreibintervalle, Datenintegrität und benötigte Kapazität bestimmen |
| MCU-04 | **Wunsch** | Streckenaufzeichnung mit Export in gängige Dateiformate | GPX/KML/CSV, Datenrate, Datenmenge und Exportweg abstimmen |
| MCU-05 | **Wunsch** | Entnehmbarer Speicherdatenträger (z. B. microSD) | Schnittstelle, Kartenzugang, Dateisystem und Datensicherheit abstimmen |
| MCU-06 | **Offen** | Erweiterungsreserve bei freien GPIOs, Energie und Einbaufläche | Nach kompletter Pinplanung festlegen |

## D. GNSS und Messfunktionen

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| GPS-01 | **Bestand V0.3** | u-blox MAX-M10N-00B mit externer Antenne über U.FL | Antennentyp, aktive Versorgung und RF-Layout prüfen |
| GPS-02 | **Wunsch** | Gesamtdistanz, Teilstrecken, manuelle Korrektur und weitere typische Tripmaster-Funktionen | Konkrete Bedienabläufe und Genauigkeitsziele festlegen |
| GPS-03 | **Wunsch** | Anzahl verwendeter/empfangener Satelliten anzeigen | Gewünschte Kennzahl und Anzeigeformat festlegen |
| GPS-04 | **Offen** | Genauigkeit bei Stillstand, Tunneln oder schlechter GNSS-Abdeckung | Optionaler Radsensor, Logging und Fehlerindikator? |
| GPS-05 | **Offen** | Gewünschte GNSS-Aktualisierungsrate und Kaltstartverhalten | Nach Messanforderungen bestimmen |

## E. Anzeige und Bedienelemente

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| UI-01 | **Bestand V0.3** | EA DOGL128W-6, 128 × 64 Pixel, transflektiv, Amber-Hintergrundbeleuchtung | Ablesbarkeit, Verfügbarkeit und mechanische Maße evaluieren |
| UI-02 | **Bestand V0.3** | Fünf Fronttaster sowie Reset/Boot und externer Trip-Reset | Anordnung, Bedienung mit Handschuhen, Schutz vor Fehlbetätigung |
| UI-03 | **Wunsch** | Piepser als optional abschaltbare Tastenrückmeldung | Lautstärke, Frequenz und Montage-/Dichtheitskonzept |
| UI-04 | **Wunsch** | Automatische Displayhelligkeit mit Menüoption zum Deaktivieren | Umgebungslichtsensor und Regelverhalten festlegen |
| UI-05 | **Offen** | Anzeigeinhalte, Schriftgrößen, Ablesbarkeit bei Sonne/Nacht | Nutzerführung und Sichtabstand festlegen |

## F. Gehäuse, Stecker und Montage

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| MEC-01 | **Festgelegt** | Pro Fahrzeug eine feste Aufnahme; TripTracer ohne Werkzeug schnell einschieben, lösen und umsetzen | Rastung, Sicherung gegen unbeabsichtigtes Herausfallen und universelle Halterungsgeometrie entwickeln |
| MEC-02 | **Festgelegt** | M8 mechanisch über die Gehäusewand abstützen; keine nennenswerte Steckkraft auf PCB-Lötstellen | Zugentlastung und Dichtung definieren |
| MEC-03 | **Bestand V0.1** | Referenzgehäuse aus 3D-Druck, etwa 126 × 76 mm Front, PCB-Konzept etwa 118 × 68 mm | Maße sind Ausgangsstand, keine finale Begrenzung |
| MEC-04 | **Offen** | Position/Zugänglichkeit von USB-C, M8, microSD und Antenne | Erreichbarkeit im montierten Zustand, Kappen und Abdichtung |
| MEC-05 | **Offen** | Einbaulage, Sturz-/Vibrations-/Wasserschutz und Werkstoffe | Fahrzeugtypen und Montagesituationen sammeln |

## G. Fertigung und Verifikation

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| Q-01 | **Festgelegt** | Portables KiCad-10-Projekt, schlüssige Symbole, Footprints, STEP-Dateien und Stückliste | Keine absoluten lokalen Pfade; Bauteile anhand Herstellerunterlagen verifizieren |
| Q-02 | **Offen** | Leiterplattenfertiger, Lagenaufbau, Dicke, Bestückungs-/Lötverfahren | Nach mechanischem und elektrischem Bedarf entscheiden |
| Q-03 | **Festgelegt** | ERC/DRC und Datenblatt-/Pinprüfung vor Bestellung; Fahrzeugschutz und reale Funktion zusätzlich testen | Prüfberichte revisionsbezogen speichern |
| Q-04 | **Offen** | Wartbarkeit, Prüfanschlüsse, Debug-/Firmware-Recovery | Zugang ohne Zerstörung des Gehäuses |

## Entscheidungsprotokoll

| Datum | ID(s) | Entscheidung | Bemerkung |
|---|---|---|---|
| 13.10.2026 | SYS-01/02, MEC-01 | Ein TripTracer für mehrere Fahrzeuge, separate Halterungen | Vom Nutzer bestätigt |
| 13.10.2026 | PWR-02/10 | M8, 3-polig, A-codiert als Fahrzeugeingang | Endgültige Bestellnummer und Pinansicht offen |
| 13.10.2026 | PWR-06/07/08 | USB-C: 5 V + Firmware; separater 12-V-Eingang | Bei V0.3 noch nicht umgesetzt |
| 13.10.2026 | PWR-03/04 | **Sicherung auf der Platine**; einfach selbst anzufertigendes Fahrzeugkabel | Zuleitung braucht dennoch quellseitigen Kurzschlussschutz |
| 13.10.2026 | MCU-01 | ESP32-S3 beibehalten; kein CH32X035 im TripTracer | Prozessor bereits im V0.3-Projekt |
| 13.10.2026 | PWR-01/09/10/11 | **12 V und 24 V gleichermaßen unterstützen**, ohne Umstecken oder Spannungswahlschalter | Nachträgliche verbindliche Anforderung; Eingangsschutz, DC/DC und Sicherung neu dimensionieren |
| 13.10.2026 | PWR-15 | **Variante A: unterbrechungsfreier Motorstart** | Gilt für beide Bordnetze; Spannungs-/Zeitgrenzen und Pufferung sind noch auszulegen und zu prüfen |
| 13.10.2026 | PWR-12 | Zunächst Variante C: fest eingelötete Schmelzsicherung | **Durch spätere Entscheidung für eFuse ersetzt**; historische Zwischenentscheidung, nicht mehr aktuell |
| 13.10.2026 | PWR-03/04/05/09/12 | **SMD-eFuse mit automatischem Wiederanlauf als primärer Geräteschutz**; Fahrzeugzuleitung ist fahrzeugseitig abgesichert | Verpolschutz und Fehler-/Transientenfestigkeit nach konkretem Datenblatt prüfen; keine Bauteilnummer festgelegt |

## Nächste gemeinsame Entscheidung

**Block B – Stromversorgung, Frage 4 (PWR-13):** Wenn **M8 (12/24 V) und USB-C (5 V) gleichzeitig angeschlossen** sind, welcher Eingang soll das Gerät vorzugsweise versorgen?

- **A (Vorschlag): M8 hat Vorrang.** USB-C bleibt für Daten/Flashen verbunden. Fällt M8 aus, übernimmt USB-C nach Möglichkeit ohne Neustart, sofern die USB-Quelle genug Leistung liefert.
- **B: USB-C hat Vorrang.** Beim Anschluss an PC/USB-Adapter läuft das Gerät vorzugsweise daraus. Fällt USB-C aus, übernimmt M8 nach Möglichkeit ohne Neustart.

In beiden Fällen sind sichere Entkopplung, keine Rückspeisung und eine funktionsfähige Versorgung bei einzeln angeschlossenen Quellen zwingend. Die konkrete Schaltung wird erst nach Klärung des Leistungsbudgets festgelegt.

Anschließend legen wir den realistischen Spannungs-/Zeitverlauf beim Motorstart fest. Konkrete Bauteile wählen wir später.

## Quellen / Verbindlichkeit

- [IDEAS.md](IDEAS.md) – freie Funktionen und zukünftige Wünsche; nicht automatisch freigegeben.
- [ARCHITECTURE.md](ARCHITECTURE.md) – dokumentierter Bestand V0.3 und jüngste technische Entscheidungen.
- [OPEN_ITEMS.md](OPEN_ITEMS.md) – konkrete Entwicklungs-/Validierungsaufgaben.
- [AGENTS.md](../AGENTS.md) – Arbeitsregeln für KI/Codex.

**Dieses Dokument ist die zentrale Hardware-Anforderungsspezifikation der nächsten Revision.** Die Kennzeichnung »Festgelegt« bedeutet eine Projektentscheidung, **keine elektrische oder mechanische Prüfung**.
