# TripPower V1 – REV6 Einbau-/Fahrzeug-Abnahme, Weg B independent (Entwurf)

**Nicht** für beliebige ungeregelte 24V-Generatoren, Motorraum-Steuergeräte, ISO16750-2 Test A 200V/350ms oder nachträgliche ungeprüfte Lichtmaschinenumbauten. **Kein Fahrzeug-/Einbaunachweis ist bereits bestanden.**

### Vor Installationsfreigabe auszufüllen

| Pflichtnachweis | Muss beim konkreten Fahrzeug dokumentiert sein | Ohne Nachweis |
| --- | --- | --- |
| Fahrzeug/Generator | Hersteller, Fahrzeugtyp, 12/24V-Version, Generator/Reglervariante und nachgewiesene zentrale Suppression einschließlich Reparatur-/Nachrüststatus | **NICHT INSTALLIEREN** oder eigener qualifizierter upstream Lastabwurfbegrenzer |
| Eingangsprüfung | Test B/äquivalenter tatsächlich repräsentativer Puls am **Gerätestecker** nach Sicherung und über dem lokalen Bezug, mindestens höchste Ausgangslast, unbelastet, ACC und USB; Vpeak≤58V inklusive positiver Ringspitzen, 350ms max im freigegebenen Testprofil | **NICHT INSTALLIEREN**; nominelles 58V an zentraler Klemme reicht nicht |
| Generator und Leitung | Rsrc,min/max, Leitungswiderstand, Kabel-L, ΔI/Δt, L/R, Kabellänge/Querschnitt, externe Sicherungsstelle, Masse und Masseverlust, negative Spannungsspitzen, Wiederholrate und Umgebung | **KEINE Lastabwurf-/FUSE-/Pin-Freigabe** |
| Sicherungsplatz F_MAIN | DC-Spannung über den Sicherungs-**Kontakten während des tatsächlichen Unterbrechens** ≤Nenn-DC-Rating; prospektiver I_fault inklusive Kurzschluss und Quellenimpedanz ≤Hersteller-Ausschaltvermögen | **KEINE 58V-Sicherungsfreigabe** bei Vbreaker>58V; höher geratetes austauschbares Set suchen, nicht den Moduleingang über 58V zulassen |
| Sicherung und Halter | Kandidat Littelfuse \`0997004.WXN\` 4A /58VDC/1kA in einem laut Hersteller 58VDC-zugelassenen MINI-Halter \`0FHM0001ZXJ-RED\`. Alternative 3A/5A nur nach Inrush/Hot-/Leitungsprüfung. BAT+ und ACC *beide* geeignet abgesichert; externer austauschbarer Zugang | **STOP** ohne Herstellerdaten, richtiger Einbaustelle, Wire-I²t und Holder-Thermik |
| Bordnetz-Betrieb | 10–32V am M8, bei V<10 zulässiger Reset; UV/OV-Latch prüft ab >32 bis spätestens36V AUS und Restart bei stabil32V; +70 Derating / +85 safe OFF | **STOP** |
| RAW/USB | RAW0.5A eigenständig kabelgeschützt, kein Rückfluss RAW/USB/RTC in BAT+, ACC, TripPower bei VIN0, GND open und versagendem Power-FET | **STOP**, Fahrzeugbrand- und Rückspeiserisiko |
| Montage | Nur dafür vorgesehener Innenraum-Einbau, wasser-/vibrations-/temperaturgeschützte Kabel, Leitungssicherung nahe Fahrzeugabgriff, eindeutige Leiterabschnitt-Kabeldimensionierung, Sicherungsauswahl nicht aus Spenderkiste | **STOP** |

**Gehäuse-/Handbuchtext (Vorschlag):** „TripTracer V1, 10–32V DC. Nur an geeignet abgesicherten 12-/24V-Bordnetzen mit nachweislich auf **maximal 58V am Gerätestecker einschließlich Überschwingern** begrenzter Versorgung verwenden. Nicht für ungeklemmten Lastabwurf. F_MAIN als externe, für vorhandene DC-Fehlerspannung und Kabelquerschnitt geeignete austauschbare Sicherung verwenden. Bei unbekannter Generatorbegrenzung vorgelagerten geprüften Lastabwurfbegrenzer einsetzen.“

**Wesentliche Klarstellung zum 58-V-Breaking-Rating:** Eine 58VDC-Nennspannung ist eine **Bauteil- und Prüfbedingung am unterbrechenden Sicherungshalter**, kein Freibrief bei lokaler Spannung \`58V + L*di/dt\`. Die tatsächliche Spannung über dem Sicherungselement während eines Lichtbogens hängt auch von der Quelle und dem Kabel ab. Dessen Rating darf nicht mit dem LMR38020 (80V Reglerbetrieb /85V VIN abs) oder LM74930 (65V Bereich /70V Pin-Abs) verwechselt werden. Wo Vbreaker>58V, muss die DC-Spannungsfestigkeit **des gesamten Sicherung-Halter-Sets** passend erhöht werden, während M8 dennoch ≤58V bleiben muss. Herstellerzeitkurven und Kabel-/Connector-Thermik auch für Fehler **unterhalb Nennstrom** nachweisen (zum Beispiel beschädigtes Silizium).

**Verbindliche Grundlage:** \`docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md\`, PWR-44–54 und [Weg B ausführliche Bewertung](WEG_B_ROUND7_REV6_PRACTICAL_SAFETY_AUDIT_2026-10-15.md). \`REV6_PRACTICAL_TEST_MATRIX_2026-10-15.csv\` ist die vorzunehmende Abnahmematrix. Das Blatt ist eine Vor-Ort-Dokumentationsvorlage, **keine** erfüllte Herstellerqualifizierung.
