# TripPower ↔ TripTracer – Power-Fail, FRAM-first und optionale Knopfzellen-Notenergie (REV6)

**Aktueller Beschluss:** 15.10.2026, **REV6**, alle A–D-/Baseline-/Review-Branches. Verbindlicher Gesamtvertrag: [Praxisnahe REV6-V1-Anforderungen](../../../docs/TRIPPOWER_V1_PRACTICAL_REQUIREMENTS_REV6_2026-10-15.md) und [TripTracer-Hardwareanforderungen PWR-38–54](../../../docs/HARDWARE_REQUIREMENTS.md). **Diese Fassung ersetzt die ältere Verpflichtung, bei jedem abrupten M8-Abziehen mit einer gewöhnlichen Knopfzelle den ESP32-S3, FRAM und eine aktiv schreibende microSD sicher bis zum vollen FAT32-Unmount zu betreiben.** Ein **echter bereits nichtflüchtiger FRAM-Commit und nachweisbar sicheres Wiederherstellen** sind Pflicht; SD-Finalisierung aus Backup ist **nur bei nachgewiesener Energie** verpflichtend.

**Wichtig:** Weder eine Echtzeituhr-CR1220 noch ein vorhandener Power-Good-Pin sind ein SD-Shutdown-Energienachweis. Diese Datei allein ändert keine bestehenden elektronischen REV5-Prototypen und gibt kein Fahrzeug/PCB frei.

## 1. Datenintegritätsziele und Betriebszustände

1. **M8 vorhanden, 10–32 V und ACC aktiv:** TripTracer läuft im vorgesehenen REV6-Betriebs-/Temperaturfenster. Kritische Fahrt-/Distanz-/Session- und Transaktionsdaten werden während des normalen Betriebs in definiertem, messtechnisch passendem Intervall **atomar in FRAM** geschrieben. FRAM behält bereits gespeicherte Daten ohne Batterieversorgung.
2. **ACC AUS mit BAT+ weiterhin anliegend:** Der normale Mikrorelais-/MCU-HOLD-Pfad lässt die laufende SD-Schreibtransaktion fertig werden, führt Flush/Unmount der offenen GPX-/CSV-/FAT32-Daten aus und öffnet das Relais anschließend kontrolliert. Für defekte SD/MCU muss ein Timeout- und fehlergesicherter Zustand vorgesehen werden.
3. **Abrupter M8-/BAT+/GND-Verlust:** **0 garantierte Frühwarnzeit**. UVLO/PGOOD/PWR_FAIL dürfen ggf. nur den bereits laufenden Stromausfall melden. Die kritischen FRAM-Daten müssen **vorher** committed worden sein. Nach Neustart anhand FRAM-Journal und SD-Transaktionsmarker unvollständige Dateien erkennen und soweit tatsächlich möglich sicher reparieren/wiederherstellen; keine unqualifizierte Behauptung, jede unterbrochene FAT32-Schreiboperation könne immer verlustfrei repariert werden. Verlorene Messzeit oder beschädigte SD-Datei korrekt anzeigen/protokollieren.
4. **Optional qualifizierter Power-Fail-Backup-Pfad:** Nur wenn Echtmessungen von ESP32-S3/FRAM/microSD, SD-Schreibspitzen, Worst-Case-Flush-Zeit, Temperatur/Alterung und Zellen-/Speicherkondensator-Innenwiderstand einen **energetisch und strommäßig ausreichend dimensionierten** autarken Niedervolt-Puffer belegen, dürfen auch nach abruptem M8-Verlust MCU und microSD bis zum vollständigen Dateischluss betrieben und dieses Ergebnis garantiert werden.
5. **Unter10V, >32..≤36V, begrenzter Lastabwurf 58V/350ms oder Hitze:** Normaler 5V-Hauptbetrieb darf kontrolliert enden. Nach stabilem 10–32V-/Temperatur-Restart FRAM-/SD-Konsistenz prüfen. Flattern, Unterspannungsreset, Rückspeisung und gleichzeitiges USB-5V testen.
6. **Batterie/Backup fehlt, ist falsch gepolt oder gealtert:** RTC- und Zusatznotfunktionen dürfen ausfallen, ohne dass Hauptstrom in eine Primärzelle zurücklädt, ohne dass SD-Erfolg vorgetäuscht wird und ohne dass die vorher im FRAM committeden Daten ohne Bauteilfehler verloren gehen.

## 2. TripPower-Schnittstellenanforderung

- `MAIN_5V`, geschützter RAW-AUX-Ausgang, GND und ggf. `PWR_FAIL`/Power-Good in klaren Power-Domains. **Keine Verbindung der Knopfzelle an den normalen 5V/2A-Hauptausgang**.
- `PWR_FAIL` ist vorzugsweise **fail-HIGH**, TripPower zieht über geeigneten Open-Drain-Schalter nur bei nutzbarer Versorgung LOW. Der Pullup liegt auf einer **separat und im Normalbetrieb aus Fahrzeugversorgung gespeisten** TripTracer-Logikdomäne, nicht dauerhaft auf einer entladen werdenden RTC-Primärzelle.
- Vollständige Trennung von TripPower oder Kabelunterbrechung darf keinen unversorgten Halbleiter auf TripPower nötig machen, um HIGH zu erzeugen. Eine fest auf LOW kurzgeschlossene Signalleitung wird durch **unabhängige lokale UVLO-/5V-Überwachung** erkannt. Signalpegel, Leckstrom bei Temperaturen, Flanken/Filter, ESD, Massebezug, Leiter-/Steckerführung und Hochvolt-Einzelfehler erst nach Datenblattprüfung festlegen.
- **Buck-PGOOD fällt unter Umständen erst nach bereits abgesenktem 5V-Ausgang und internem Filter ab**; nie als garantierte Vorwarnung vor sofortigem M8-/GND-Abriss ausgeben. Ein vollständiger SD-Notabschluss erfordert **vor dem Ausfall vorhandene** Energie, selbst wenn PWR_FAIL zuverlässig wäre.
- Keine Rückspeisung aus RTC-Zelle, USB, MCU-GPIO, 3V3-AON, internem RAW, Notkondensator oder abgeschalteter TripPower in ACC/BAT+, Fahrzeugleitung, Haupt-5V oder fremden USB-Host; Dioden- und ESD-Pfade bei VIN=0 gesondert prüfen.
- Fahrzeug-BAT+-OFF-Ruhestrom **<1mA, Ziel <0,5mA**, jeweils 12/24V und Temperatur. Batterie-Ruheentnahme separat gegen Zellkapazität/Lebensdauer prüfen. **Primärzellen niemals laden.**
- Testfall 58V/350ms gilt nur wenn der Puls am realen TripPower-Anschluss **begrenzt** ist; die Knopfzelle legitimiert **keine** ungeschützte 200V-Test-A-Installation.

## 3. TripTracer-Hauptplatine / Firmware

- Regelmäßige atomare Zähler-/Sessions-/Config-Commits mit Zeit-/Sequenzkennung, CRC und Transaktionsmetadaten ins FRAM; definierte maximal mögliche Datenlücke zwischen Commits messen. Kein Wunsch nach langlebiger RTC-Zelle als Ersatz für laufende Persistenz.
- MicroSD-Schreibstrategie mit kontrolliertem Commit und Recovery bei plötzlich wegfallender Energie; Dateisystem-/GPX-/CSV-Wiederherstellung beim Booten anhand konsistenter FRAM-Transaktionsmarker und SD-Prüfergebnissen. Gewöhnliches FAT32 garantiert nicht automatisch Crash-Konsistenz, deshalb Fehlerfälle explizit testen.
- RTC mit kleiner auswechselbarer Knopfzelle als eigene Last. Eine zusätzliche MCU-/microSD-Notenergie ist **optional**, braucht echtes I(t)/P(t), Worst-Case T_flush, ESR/Zellchemie, Temperatur/Alterung, geeigneten Power-Mux und sichere Freigabe. Keine 3-s-Garantie aus frei gewähltem Modell ableiten.
- Falls der Zusatzpuffer belegt ist: nichtkritische Verbraucher (Display/Backlight, LEDs, GNSS, RAW) sofort abschalten, nur sichere MCU-/FRAM-/SD-Powerdomäne bis zum verifizierten Flush und Shutdown betreiben; bei unzureichender Energie transparenter Recovery-Fallback.

## 4. Konkrete offene Tests / Freigabe-Stopp

1. Reales vollständiges M8-Abziehen unter microSD-Schreiblast, bei normalem Abschalten ACC und während 58V-OV-Abschaltung; FRAM-Commit-Dauer, Recovery, SD-Dateizustände inklusive absichtlicher Dateisystemfehler und Full/Read-only SD.
2. Kommutierte Quelle 10–32V, <10V Reset, >32..≤36V Off, 36V/400ms, begrenzt 58V/350ms, USB-only/-gleichzeitig, VIN0/RUN-High, GND-Unterbruch; kein gefährlicher Backfeed und kein EEPROM-/SD-Datenverlust aus vorzeitigem Commit-Versprechen.
3. Tatsächlicher Zelltyp, RTC-Lebensdauer, mechanische Halterung, mögliche Rückladung/Fehlpolung und gesamte Lager-/Betriebstemperatur; Lagerung −40..+85°C nur wenn die Zelle es erlaubt.
4. Für SD-Notabschlussoption: `E_backup_usable >= integral(P_required(t) dt) / eta_path` plus klarer Energie-/Strom-/Temperatur-/Alterungs-Reserve; SD-I_peak, Supervisor-Umschaltzeit, Spannungsbodengrenzen, Worst-Case-FAT32-Abschlussdauer und Hardware-Power-Mux real messen.
5. Teste sicheren Wiederanlauf nach Fehler, Versorgungseinbruch und stromlosem TripPower. Keine implizite 200V-Test-A- oder +125°C-Volllastzulassung aus bestandenem REV5-ERC ableiten.

**Status:** funktional beschlossen, **elektrische Implementation, Datenintegritätsversuch, PWR_FAIL-Signallage und Zell-/Puffer-Auswahl** offen. Jede A–D-Architektur muss nur die Schutz-/Schnittstellenfunktionen anbieten, die im gewählten REV6-Einsatzprofil wirklich nötig sind. Kein unnötiger 200V-/125°C-Überbau im neuen V1-Entwurf.
