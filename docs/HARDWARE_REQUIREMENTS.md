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
| SYS-04 | **Teilweise festgelegt** | Gehäuse soll **staubdicht** sein; **keine Wasserdichtigkeit/Regenschutz-Schutzklasse gefordert**. Temperaturbereich, Kondensations-/Spritzwasserfolgen und Vibrationsbelastung bleiben offen. | Staubschutz-Ziel hinsichtlich Festkörpern in Richtung **IP6X** entwickeln und später prüfen; keine ungeprüfte IP-Zertifizierung behaupten. |
| SYS-05 | **Offen** | Kosten-, Baugrößen- und Leistungsbudget | Zielpreis und maximale Gehäuseabmessungen festlegen |

## B. Stromversorgung und Schutz – erster Brainstorming-Block

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| PWR-01 | **Festgelegt** | Regulärer Betrieb sowohl an **12-V- als auch an 24-V-Fahrzeugbordnetzen**, ohne manuellen Spannungswahlschalter | Durchgängigen zulässigen Eingangsspannungsbereich, Motorstart-Unterspannung, Ladespannung und Transienten für beide Netze spezifizieren |
| PWR-02 | **Festgelegt** | **M8, 3-polig, A-codiert, Schraubverriegelung** als normaler Fahrzeug-Stromanschluss; keine einfache DC-Hohlbuchse | Einbaustecker am Gerät, Kabelbuchse fahrzeugseitig; Strombelastbarkeit, Orientierung und Schutzart prüfen |
| PWR-03 | **Festgelegt** | **Elektronischer Überstromschutz (eFuse) in SMD-Bauform direkt auf der Platine** im 12-/24-V-Bordnetz-Eingang; automatische Wiederherstellung nach einem geeigneten Fehlerfall | Stromgrenze, Einschaltstrombegrenzung, Spannungsbereich, thermische Auslegung und Verhalten bei dauerhaftem Kurzschluss erst festlegen; mögliche ergänzende Schmelzsicherung anhand Fehleranalyse prüfen |
| PWR-04 | **Festgelegt** | Ein **einfaches, selbst angefertigtes M8-Anschlusskabel** ohne integrierten gerätespezifischen Sicherungshalter | **Fahrzeugseitige Absicherung ist vom Nutzer bestätigt**: Anschluss an bereits abgesicherten Abgriff oder separate Sicherung nahe der Batterie; Leitungsquerschnitt/-länge und zur Zuleitung passende Sicherung festlegen |
| PWR-05 | **Festgelegt (Sicherheit)** | **Die Fahrzeugzuleitung wird fahrzeugseitig abgesichert.** Die eFuse im TripTracer kann keinen Kurzschluss im Kabel vor dem Gerät absichern. Bei direktem Batterieanschluss Sicherung nahe der Batterie; alternativ bereits abgesicherten Abgriff verwenden | Sicherungswert und Kabelquerschnitt aufeinander abstimmen, beide Bordnetzspannungen und maximalen Quell-Kurzschlussstrom berücksichtigen |
| PWR-06 | **Festgelegt** | **USB-C für Daten und Firmwareupdates; 5-V-Versorgung ausschließlich für den Flash-/Servicemodus ohne M8.** USB-C ist **keine alternative reguläre Betriebsversorgung** im Fahrzeug. | Firmware muss über USB-C am PC ohne angeschlossenen M8-Stecker aufspielbar sein. Strombedarf und ggf. Abschaltung nicht notwendiger Verbraucher im Flashmodus prüfen. |
| PWR-07 | **Festgelegt** | **Keine rohe 12-V- oder 24-V-Bordnetzspannung auf USB-C.** Externe Fahrzeugadapter müssen das Bordnetz außerhalb des TripTracers auf normgerechte USB-5-V-Versorgung wandeln | USB-Geräte-/Host-Schutz und CC-Beschaltung prüfen |
| PWR-08 | **Festgelegt** | **M8-Bordnetzeingang hat immer Vorrang vor USB-C-5-V.** USB bleibt bei gleichzeitiger Verbindung als Datenschnittstelle zum Flashen nutzbar. USB-5-V-Einspeisung darf nur ohne verfügbare M8-Versorgung den Flash-/Servicebetrieb speisen. Beide Quellen müssen rückspeisungssicher getrennt sein. | Sichere Quellenpriorisierung, USB-VBUS-/5-V-Erkennung, Strombudget sowie Umschalten bei Ein-/Ausstecken prüfen; kein allgemeiner USB-Ersatzbetrieb gefordert. |
| PWR-09 | **Festgelegt** | Bordnetzschutz für **12-V- und 24-V-Fahrzeuge** mit Überstromabschaltung durch eFuse; **Verpolschutz ist bei der konkret ausgewählten eFuse nachzuweisen** oder zusätzlich aufzubauen. Transienten/ESD, Load Dump, Spannungswandlung und sichere Masseführung bleiben gesondert zu lösen | Nicht jede eFuse bietet Verpolschutz oder ausreichend hohe Spannungsfestigkeit; Schutzfunktionen per Datenblatt und Tests für beide Bordnetze verifizieren |
| PWR-10 | **Festgelegt** | Vorläufige M8-Belegung: **Pin 1 = +12/24 V Bordnetz, Pin 3 = GND, Pin 4 = Reserve/NC** | Konkreten Gegenstecker und Kontaktansicht anhand Datenblatt verifizieren; 24-V-Tauglichkeit ergibt sich aus der gesamten Schaltung und nicht allein dem Steckertyp |
| PWR-11 | **Festgelegt** | **12-V- und 24-V-Fahrzeuge** unterstützen; automatisch nutzbar am selben M8-Eingang ohne Umschalten oder Umbau | Eingangsspannungsbereich und Schutz/Regler für beide Fahrzeugklassen erst auslegen und prüfen; die bisherige V0.3-Hardware erfüllt diese Vorgabe noch nicht nachweislich |
| PWR-12 | **Festgelegt** | **Kompakte SMD-eFuse mit automatischer Rückstellung**, statt steckbarer oder fest eingelöteter Schmelzsicherung als primärem Überstromschutz; kein von außen zugänglicher Sicherungshalter erforderlich | Auto-Retry-/Latch-Verhalten, sichere Reaktion bei Kurzschluss, zulässiger Fehlerstrom und ggf. notwendiger unabhängiger Schutz müssen für den ausgewählten Baustein verifiziert werden; eFuse ersetzt nicht die externe Kabelsicherung |
| PWR-13 | **Festgelegt** | **M8 vor USB-C:** Bei gleichzeitigem Anschluss versorgt der M8-Eingang das Gerät; USB-C liefert ausschließlich die Datenverbindung für Firmwareupdates. Ohne M8 versorgt USB-C ausschließlich den Flash-/Servicemodus. | Verhindern, dass USB-VBUS bei vorhandenem M8 in den Fahrzeugstrompfad einspeist oder ein angeschlossener PC aus dem Gerät gespeist wird. Keine automatische Übernahme des normalen Betriebs durch USB bei M8-Ausfall gefordert. |
| PWR-14 | **Bestand V0.3** | 12-V-Eingang J1 → Eingangsabsicherung/-schutz → 3,3-V-DC/DC; USB bisher nur Daten | Bei nächster Revision auch für 24-V-Fahrzeuge neu auslegen (PWR-01/09/11); an PWR-02/03/06/08 anpassen. Vorhandene V0.3-Schaltung nicht als 24-V-tauglich ausgeben |
| PWR-15 | **Festgelegt** | **Unterbrechungsfreier Betrieb beim Motorstart** in 12-V- und 24-V-Fahrzeugen: kein MCU-/GNSS-Neustart, keine Unterbrechung von Anzeige, Distanzzählung oder Streckenaufzeichnung durch den Startvorgang | Kritischen Spannungs-/Zeitverlauf beim Anlassvorgang, Mindest-Eingangsspannung und erforderliche Überbrückungszeit/Pufferenergie messen und festlegen; Funktionstest noch offen |
| PWR-16 | **Festgelegt** | **Variante B: Spannungseinbrüche beim Motorstart unterbrechungsfrei überstehen (PWR-15); bei vollständigem Verlust der M8-Eingangsspannung (0 V) ist ein automatischer Neustart zulässig.** USB-C wird dadurch nicht zur normalen Notstromversorgung. | Zulässige Unterspannungsgrenze und Dauer des Einbruchs separat festlegen. Nach Rückkehr der Versorgung muss das Gerät selbstständig und mit erhaltenen, konsistent gespeicherten Tripdaten wieder anlaufen. |
| PWR-17 | **Festgelegt** | **Variante A – ausgeprägte Kaltstart-Spannungseinbrüche ohne Neustart überstehen.** Vorläufiges 12-V-Auslegungsprofil: **3 V für ca. 15 ms**, danach **6 V für mehrere Sekunden**; vorläufiges 24-V-Auslegungsprofil: **6 V kurzzeitig**, danach **10 V für mehrere Sekunden**. Diese Werte sind **Planungsziele**, noch keine endgültig verifizierten Spannungs-/Zeitgrenzen. | Exakte Zeitdauer, Spannungsverlauf, Temperaturbedingungen und Wiederholungen je 12-/24-V-Netz anhand geeigneter Automotive-Anforderungen und Messungen festlegen. Wandler/eFuse müssen das Profil funktional unterstützen; für tiefe kurze Einbrüche darf ein Puffer erforderlich sein. **0 V muss gemäß PWR-16 nicht überbrückt werden.** |
| PWR-18 | **Festgelegt** | **Variante A:** Bei starken Start-Spannungseinbrüchen darf die Display-Hintergrundbeleuchtung automatisch gedimmt oder kurz ausgeschaltet werden; Anzeigecontroller, ESP32, GNSS, Distanzmessung und Streckenaufzeichnung laufen ohne Neustart weiter. | Bei wieder stabiler Versorgung ursprüngliche Helligkeit automatisch herstellen; unnötige Verbraucher priorisiert reduzieren. Schwellen/Hysterese, Zeitprofil und tatsächlich mögliche Energieersparnis im Test festlegen. |

| PWR-19 | **Festgelegt** | **Automatischer Start mit anliegender M8-Fahrzeugspannung**; kein zusätzlicher Einschaltknopf erforderlich. | Verhalten beim Anschluss an dauerhaft spannungsführende Fahrzeugklemmen beachten: Solange M8 Spannung liefert, bleibt das Gerät regulär eingeschaltet. USB-only startet ausschließlich Flash-/Servicemodus gemäß PWR-06. |
| PWR-20 | **Festgelegt** | **Kontrollierter Nachlauf mit lokalem Energiepuffer**, wenn die M8-Spannung wegfällt: kritische Betriebsdaten sichern, eine offene Streckenaufzeichnung/Datei konsistent abschließen und erst danach abschalten. | Pufferenergie, Abschaltschwelle, Reservierung für Dateisystem-Schreibspitzen sowie maximaler Nachlauf erst anhand Lastprofil festlegen; auch bei 0-V-Eingang sicher speichern, soweit innerhalb des dimensionierten Abschaltprofils. Keine fortgesetzte GPS-Messung im Nachlauf vorgeschrieben. |
| PWR-21 | **Festgelegt** | **Bordnetzspannung vor der Spannungswandlung überwachen und im Menü anzeigen**, für 12-V- und 24-V-Systeme. | Messpunkt/Messbereich, Schutz des ADC vor Transienten, Eingangsimpedanz, Filterung, Kalibrierung und Anzeigeauflösung später festlegen; keine ungeprüften Direktverbindungen zum ESP32-ADC. |
| PWR-22 | **Festgelegt** | **Variante A – geschaltetes Zündungsplus/ACC:** Die M8-Versorgung wird an einen fahrzeugseitig abgesicherten, mit Zündung geschalteten Stromkreis angeschlossen. Mit anliegender Spannung startet TripTracer automatisch (PWR-19); beim Ausschalten kontrollierter Nachlauf (PWR-20). | Für jedes 12-/24-V-Fahrzeug geeigneten, zulässig belastbaren und abgesicherten ACC-Abgriff wählen; keine zusätzliche Dauerplus-/Standby-Anforderung. |
| PWR-23 | **Festgelegt** | **Variante A – kürzestmöglicher kontrollierter Nachlauf:** nur so lange gepuffert weiterlaufen, wie zum konsistenten Speichern der Tripdaten und zum Abschluss offener Dateisystemoperationen notwendig. | Keine pauschale Mindestdauer von 5 oder 10 Sekunden; benötigte Energie und Sicherheitsreserve anhand realer Stromaufnahme, Speichermedien, Schreibzeiten und Spannungseinbrüchen bestimmen und testen. |
| PWR-24 | **Festgelegt** | **Variante A – im Nachlauf nur notwendige Elektronik versorgen:** ESP32 und für sichere Speicherung erforderliches FRAM/SD-/Dateisystem weiter betreiben; GNSS, Displaybeleuchtung und entbehrliche Verbraucher ausschalten. | Sichere Erkennung des M8-Spannungsverlusts und priorisiertes Abschalten der Verbraucher sicherstellen; Reserve für SD-Schreibspitzen vorsehen; keine Messfortsetzung im Nachlauf erforderlich. |
| PWR-25 | **Festgelegt** | **Variante A – Bordnetzspannung nur im Diagnosemenü anzeigen**, nicht permanent auf dem Hauptdisplay; Messung weiterhin für die Versorgungsüberwachung nutzbar (PWR-21). | Für 12-/24-V-Systeme korrekt skalieren/kalibrieren; Anzeigeauflösung, Aktualisierungsrate und Messschaltung später festlegen. |

| STO-01 | **Festgelegt** | **Variante A: microSD-Karte** als entnehmbares Speichermedium für GPS-Trackaufzeichnung und Dateiexport. | Schnittstelle, sichere Schreibvorgänge, Erkennen von Kartenfehlern und Umgang mit plötzlichem Stromausfall prüfen. FRAM für Kilometerstände/Einstellungen bleibt unabhängig davon vorgesehen. |
| STO-02 | **Festgelegt** | **Variante A: microSD von außen erreichbar**, ohne Öffnen des TripTracer-Gehäuses. | Öffnung bei geschlossener Staubschutzkappe staubdicht ausführen (MEC-06/07). Mechanische Zugänglichkeit in der Fahrzeughalterung und sichere Entnahme ohne laufende Schreiboperationen berücksichtigen. |
| STO-03 | **Festgelegt** | **Variante A: externe GNSS-Antenne** außerhalb des TripTracer-Gehäuses, für guten Empfang günstig am Fahrzeug zu positionieren. | Robust zu trennende, staubgeschützte HF-Gehäuseschnittstelle für häufigen Fahrzeugwechsel definieren; die interne U.FL-Buchse ist **kein** direkt zu bedienender Außenanschluss. Kabel, Steckverluste, Antennenspeisung und Montage klären. |
| STO-04 | **Festgelegt** | **Variante A: separaten externen Anschluss und geschützten MCU-Eingang für späteren optionalen Radimpulssensor vorsehen**; Sensor selbst muss zunächst nicht vorhanden sein. | Für Reedschalter/Hallgeber geeignete elektrische Schnittstelle später definieren; Anschluss in unbenutztem Zustand mit Staubschutzkappe (MEC-07) versehen und mechanisch/elektrisch vom M8-Stromanschluss unverwechselbar ausführen. |

## C. Steuerung, Kommunikation und Speicher

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| MCU-01 | **Festgelegt** | **ESP32-S3-MINI-1-N8** als Prozessorplattform beibehalten | GPIO-Budget, RAM/Flash und Bootstrapping für alle Zusatzfunktionen vor PCB prüfen |
| MCU-02 | **Festgelegt** | Firmwareupdates direkt über **USB-C**, ohne zusätzliche 12-V-Stromquelle | USB-Boot-/Recovery-Prozedur in der späteren Hardware verifizieren |
| MCU-03 | **Bestand V0.3** | FRAM MB85RC256VPNF (I²C) für wichtige Zähler und Einstellungen | Schreibintervalle, Datenintegrität und benötigte Kapazität bestimmen |
| MCU-04 | **Wunsch** | Streckenaufzeichnung mit Export in gängige Dateiformate | GPX/KML/CSV, Datenrate, Datenmenge und Exportweg abstimmen |
| MCU-05 | **Festgelegt** | Entnehmbare **microSD-Karte mit äußerem Kartenzugang** (siehe STO-01/02). | Schnittstelle, FAT/Dateisystem, sicherer Auswurf und Datensicherheit später auslegen. |
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
| MEC-04 | **Teilweise festgelegt** | Position und Zugänglichkeit von USB-C, M8, äußerer microSD, externer GNSS-Antennenbuchse sowie optionalem Radsensoranschluss | Nicht ständig benötigte Öffnungen mit Staubschutz gemäß MEC-07 abdecken, auch wenn das Gerät in der Fahrzeughalterung steckt. Konkrete Positionen noch offen. |
| MEC-05 | **Offen** | Einbaulage, Sturz-/Vibrationsfestigkeit, Temperatur, Kondenswasserverhalten und Gehäusewerkstoffe | **Keine Wasserdichtheitsanforderung**; Staubdichtheit gesondert in MEC-06 festgelegt. Fahrzeugtypen und Montagesituationen sammeln. |
| MEC-06 | **Festgelegt** | **Gehäuse staubdicht auslegen**, auch an Fugen und bei geschlossenen Anschlussabdeckungen; keine Wasserdichtheit gefordert. | Entwicklungsziel **IP6X hinsichtlich Festkörper-/Staubschutz**; nicht zertifiziert, Staubprüfung bei der Prototypenvalidierung vorsehen. |
| MEC-07 | **Festgelegt** | **Alle optionalen, nicht ständig benutzten Anschlüsse und Öffnungen mit passenden Staubschutzstopfen/-kappen** (z. B. Gummi/Silikon) abdecken. | Insbesondere USB-C, microSD und nicht belegter Radimpulsanschluss; unbenutzte externe GNSS- und M8-Buchsen bei Lagerung/Transport ebenfalls schützen. Bevorzugt unverlierbar befestigte Abdeckungen. |

## G. Fertigung und Verifikation

| ID | Status | Anforderung / Ziel | Offene Details oder Prüfkriterium |
|---|---|---|---|
| Q-01 | **Festgelegt** | Portables KiCad-10-Projekt, schlüssige Symbole, Footprints, STEP-Dateien und Stückliste | Keine absoluten lokalen Pfade; Bauteile anhand Herstellerunterlagen verifizieren |
| Q-02 | **Offen** | Leiterplattenfertiger, Lagenaufbau, Dicke, Bestückungs-/Lötverfahren | Nach mechanischem und elektrischem Bedarf entscheiden |
| Q-03 | **Festgelegt** | ERC/DRC und Datenblatt-/Pinprüfung vor Bestellung; Fahrzeugschutz und reale Funktion zusätzlich testen | Prüfberichte revisionsbezogen speichern |
| Q-04 | **Offen** | Wartbarkeit, Prüfanschlüsse, Debug-/Firmware-Recovery | Zugang ohne Zerstörung des Gehäuses |

| MEC-08 | **Festgelegt** | **Variante A – verschraubte SMA-Gehäusebuchse** für die externe GNSS-Antenne; trennbares Antennenkabel und passende Staubschutzkappe bei Nichtbenutzung. | Konkrete SMA-Polarität, Antennenkabel, HF-Impedanz (50 Ω), mechanische Wandmontage, interne Verbindung zum GNSS-Modul und ESD-Schutz vor Bauteilauswahl prüfen. |
| MEC-09 | **Festgelegt** | **Variante A – unverlierbar am Gehäuse befestigte Gummi-/Silikon-Staubschutzkappe** für den außen zugänglichen microSD-Steckplatz. | Dichtender Sitz im geschlossenen Zustand (Staubschutz), Auswurf-/Entnahmefreiraum, Haltbarkeit der Befestigung und Bedienbarkeit bei montiertem TripTracer prüfen. |
| MEC-10 | **Festgelegt** | **Variante A – eigener, kleiner, steckbarer Anschluss für den optionalen Radimpulssensor**, bei Nichtbenutzung mit Staubschutzkappe versehen. | Steckgeometrie eindeutig verschieden vom M8-Versorgungsanschluss; erforderliche Kontakte, Sensor-Versorgung, Schutz und mechanische Robustheit erst nach Definition des Sensors festlegen. |
| MEC-11 | **Festgelegt** | **Variante A – unverlierbar befestigte Gummi-/Silikon-Staubschutzkappe** für USB-C, im normalen Fahrzeugbetrieb geschlossen. | Staubdichter Verschluss im unbenutzten Zustand, USB-Steckerfreiraum beim Flashen, Befestigung und mechanische Beständigkeit prüfen. |
| MEC-12 | **Offen** | Schnellwechselhalterung: Schiebeaufnahme mit Rastverriegelung oder Bajonettverschluss | Vibrationssicherheit, Werkzeuglosigkeit und Montage in mehreren Fahrzeugen prüfen. |
| MEC-13 | **Offen** | Gehäusefertigung: 3D-Druck (z. B. ASA) oder anderes Verfahren/Material | Mechanische Robustheit, Temperatur, Alterung, Gewindeeinsätze und Fertigungskosten beurteilen. |
| MEC-14 | **Offen** | Gehäuse wiederholt servicefähig zu öffnen oder dauerhaft geschlossen zu fertigen | Staubdichte Fuge, Wartbarkeit von Platine/Anschlüssen und Verschraubung. |
| MEC-15 | **Offen** | Haptisches Bedienkonzept: gut fühlbare Handschuhtaster oder flache Membrantasten | Staubschutz und zuverlässige Betätigung unter Vibration; fünf Tasten im V0.3 nur Bestandsinformation. |

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
| 13.10.2026 | PWR-06/08/13 | **M8 hat Versorgungsvorrang; USB-C-5-V ausschließlich zum Flashen ohne M8** | Mit M8 bleibt USB-Datenübertragung möglich, aber keine reguläre USB-Versorgung vorgesehen |
| 13.10.2026 | PWR-16 | **Variante B: Unterbrechungsfrei bei Start-Spannungseinbrüchen; Neustart bei 0 V M8 zulässig** | Ergänzt PWR-15; kein Bedarf für vollständige Nullvolt-Überbrückung |
| 13.10.2026 | PWR-17 | **Variante A: auch ausgeprägte Kaltstart-Spannungseinbrüche überstehen** | Vorläufig: 12 V → 3 V/ca. 15 ms und 6 V/mehrere Sekunden; 24 V → 6 V kurzzeitig und 10 V/mehrere Sekunden. Exakte Prüfprofile noch festzulegen. |
| 13.10.2026 | PWR-18/19/20/21 | **Gebündelte 4er-Runde:** Display bei Motorstart dimmbar; Start automatisch mit M8; kontrollierter gepufferter Nachlauf; Bordnetzspannung im Menü messen/anzeigen | PWR-16 bleibt bestehen: vollständiger 0-V-Ausfall muss keinen laufenden Messbetrieb garantieren; der Nachlaufpuffer ist stattdessen für gesichertes Herunterfahren zu dimensionieren. |
| 13.10.2026 | PWR-22/23/24/25 | **Gebündelte 4er-Runde:** geschaltetes Zündungsplus; minimal notwendiger Speichernachlauf; nur notwendige Elektronik im Nachlauf; Spannungsanzeige nur im Diagnosemenü | Keine feste Nachlaufdauer; Pufferung und Datensicherheit vor PCB-Layout dimensionieren und testen. |
| 13.10.2026 | STO-01/02/03/04 | **Gebündelte 4er-Runde:** microSD, von außen zugänglich; externe GNSS-Antenne; Anschluss für optionalen Radsensor | Bauteile, geeignete HF-Stecker, Abdichtung und GPIOs noch offen. |
| 13.10.2026 | SYS-04, MEC-04/05/06/07 | **Gehäuse staubdicht, aber nicht wasserdicht gefordert; Staubschutzkappen für optionale Anschlüsse/Öffnungen** | Schutz bei verschlossenen Öffnungen; IP6X nur als Entwicklungsziel, kein nachgewiesener Prüfstatus. |
| 13.10.2026 | MEC-08/09/10/11 | **Gebündelte 4er-Runde:** SMA-Gehäusebuchse mit Staubkappe, außen liegende microSD mit unverlierbarer Gummikappe, separater steckbarer Radsensoranschluss, USB-C mit unverlierbarer Gummikappe | Hersteller-/Bauteilnummern und mechanische Prüfung stehen aus. |

## Nächste gemeinsame Entscheidung

**Nächste Vierer-Runde – Gehäuse und Bedienbarkeit (MEC-12 bis MEC-15):**

1. **MEC-12 – Schnellwechselhalterung:** A: universelle Schiebeaufnahme mit mechanischer Rastverriegelung und separatem Lösen des M8-/SMA-Kabels (Empfehlung). B: Bajonett-/Vierteldrehverschluss mit mechanischer Rastung. Beide Varianten sollen das Gerät sicher gegen Vibration halten.
2. **MEC-13 – Gehäusefertigung:** A: 3D-druckbares ASA-Gehäuse für Prototyp und kleine Stückzahlen, bei Bedarf mit Einpressgewinden (Empfehlung). B: zunächst anderes Fertigungsverfahren/Material, z. B. CNC-Gehäuse; thermische und mechanische Anforderungen bleiben zu prüfen.
3. **MEC-14 – Gehäuseservice:** A: geschraubter, wiederholt zu öffnender Deckel mit Staubdichtung (Empfehlung). B: dauerhaft verklebtes/verschweißtes Gehäuse ohne reguläre Öffnung. Der äußere microSD-Zugang bleibt in beiden Varianten bestehen.
4. **MEC-15 – Tastenbedienung:** A: große mechanisch klar fühlbare Tasten, auch mit Handschuhen nutzbar, gegen Staub abgedichtet (Empfehlung). B: besonders flache Tasten/Membranbedienung zugunsten einer glatten Front. Anzahl/Funktionen bleiben bis zur Bedienkonzeptentscheidung offen.

**Noch keine Auswahl getroffen:** Diese Optionen sind Vorschläge für die nächste gemeinsame Entscheidungsrunde; sie beeinflussen Gehäuseabmessungen, Staubschutz, Haptik und mechanische Stückliste.

## Quellen / Verbindlichkeit

- [IDEAS.md](IDEAS.md) – freie Funktionen und zukünftige Wünsche; nicht automatisch freigegeben.
- [ARCHITECTURE.md](ARCHITECTURE.md) – dokumentierter Bestand V0.3 und jüngste technische Entscheidungen.
- [OPEN_ITEMS.md](OPEN_ITEMS.md) – konkrete Entwicklungs-/Validierungsaufgaben.
- [AGENTS.md](../AGENTS.md) – Arbeitsregeln für KI/Codex.

**Dieses Dokument ist die zentrale Hardware-Anforderungsspezifikation der nächsten Revision.** Die Kennzeichnung »Festgelegt« bedeutet eine Projektentscheidung, **keine elektrische oder mechanische Prüfung**.
