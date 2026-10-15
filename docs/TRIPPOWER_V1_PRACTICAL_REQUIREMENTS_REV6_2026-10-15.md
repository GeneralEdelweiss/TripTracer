# TripPower / TripTracer – verbindliche praxisnahe V1-Anforderungen, REV6

**Beschlussdatum:** 15.10.2026. **Status:** verbindliche neue funktionale Auslegungsziele, **keine** Automotive-/KiCad-/Thermik-/Produktionsfreigabe. Ersetzt die strengeren früheren TripPower-9–30V-/200V-/125°C-Vollanforderungen **für die neu zu entwickelnde V1**. Die historischen REV5-Elektrodateien und `REV5_DESIGN_BASELINE.json` bleiben als nicht freigegebene Vergleichsbasis unverändert; ihre alten Zahlen sind **nicht mehr die autoritative Produktanforderung**. Verwendbar nur nach neuem REV6-Nachweis. Historische A–D-Berichte bleiben nachverfolgbar; keine alten 200V-STOP-Gates als erfüllte 58V-Gates umetikettieren.

## 1. Geltungsbereich / ausdrückliche Einschränkung

Ein einfaches Rallye-/Navigationsgerät für **12-/24-V-Bordnetze mit ausreichend zentral begrenztem Lastabwurf** im vorgesehenen Innenraum-Einbauort. **Nicht** universal für beliebige ungeregelte 24-V-Generatoren, ungedämpfte ISO-16750-2-Test-A-Pulse oder Anschlüsse ohne erforderlichen Fahrzeug-/Leitungsschutz. **58 V an der Gerätebuchse sind eine Installations-/Prüfbedingung**, kein automatisch gegebenes Fahrzeugmerkmal. Wenn ein Fahrzeug nicht nachweislich zentral begrenzt ist, ist vor TripPower ein eigenständig qualifizierter externer Load-Dump-Schutz erforderlich **oder** die Installation darf nicht als konform gelten. Dokumentation/Etikett und Anschlussanweisung müssen diese Einschränkung erklären. Kein Ersatz einer ausreichend dimensionierten fahrzeugseitigen Zuleitungssicherung.

## 2. Elektrische Betriebs- und Schutzfenster

| ID | Neuer V1-Wert / Verhalten | Abnahme- und Abgrenzungshinweis |
| --- | --- | --- |
| R6-VIN-01 | **10–32 V DC normaler Dauerbetrieb** für 12/24V ohne Spannungswahlschalter | Geregelte 5V, Sensor-/Logikbetrieb im qualifizierten Temperatur-/Leistungsfenster; Eingangsschutz und BAT-/ACC-Erfassung an beiden Plusleitungen auslegen |
| R6-UV-02 | **Unter 10 V darf kontrolliert abgeschaltet oder neu gestartet werden** | Kein Anspruch auf unterbrechungsfreies GNSS/MCU/Display/Radimpuls-Logging bei 3V/6V-Startkurven; FRAM-Persistenz und definierter Wiederanlauf statt verschwiegener Datenkorruption; Hysterese/Flattern messen |
| R6-OV-03 | **Oberhalb 32 V bis spätestens 36 V kontrolliert AUS** | 32V soll normal betrieben werden können; Shutdown-Schwelle inklusive Toleranzen/Hysterese zwischen >32 und ≤36V spezifizieren, keine ON-Garantie im Band; 36V/400ms ohne bleibenden gefährlichen Defekt |
| R6-OV-04 | **36 V / 400 ms temporärer Überspannungsprüffall** | Überleben und definierter Neustart nach Rückkehr, nicht 5V/2A während des Impulses; genaue Quellimpedanz/Form/Wiederholungen anhand anzuwendendem Prüfprofil vor Laborfreigabe definieren |
| R6-LD-05 | **Bis 58 V / 350 ms als begrenzter 24V-Load-Dump-Prüffall am TripPower-Eingang** | Schutzabschaltung während des Pulses zulässig, aber **keine** unsuppressed-200V/350ms-Test-A-Freigabe; Klemmung muss tatsächlich **vor der TripPower-Eingangsbuchse** wirken und auch Ringing/Leitungsinduktivität mit erfasst sein. Pulsform, Quell-R/L, Wiederholzahl und Padspitzen vor PCB-Freigabe festlegen. 58V-Nennzahl allein garantiert keinerlei SOA |
| R6-OPTION-06 | **90 V / 5 ms nur optionales Entwicklungsziel** | Kein Pflicht- oder Hersteller-ISO-/Automotive-Testnachweis, keine Auslegung anderer Blöcke auf diese Zahl ohne separate Quell-/Pulsdefinition und ausdrückliche spätere Freigabe |
| R6-FAULT-07 | **Verpol-/ESD-/Kurzschluss-/Überstromschutz, kein Brand und keine unzulässige Rückspeisung** | Sichere Abschaltung bzw. kontrollierter Totalausfall bei schweren Einzelfehlern erlaubt, aber Kabel/Stecker/F_MAIN/Masse/USB/RAW sicher; die externe fahrzeugseitige, austauschbare F_MAIN und geeigneter Kabelschutz bleiben Pflicht |
| R6-RESTART-08 | **Automatischer Wiederanlauf bei stabilen 10–32V nach UV/OV/Temperatur-Abschaltung** | Geeignete Hysterese und Shutdown-Latch, kein Einschaltflattern, unvollständige SD-Operation nur über FRAM-Transaktionsmarker/Recovery behandeln |

**Nicht als neue Testpflicht wieder einführen:** 9V garantierter Vollbetrieb, 200V/350ms **ungedämpft**, −40..+125°C Umgebung unter Volllast. Sie bleiben historische strengere Vergleichsanforderungen und dürfen optional als **eigenständige höhere Ausbauvariante**, niemals als automatisch zertifiziertes V1, weiter untersucht werden.

## 3. Umgebung, Leistung, RAW und Ruhestrom

| ID | Neuer V1-Wert | Prüfung / Interpretation |
| --- | --- | --- |
| R6-TEMP-09 | **−20 bis +70 °C Umgebung** als vorgesehenes Einsatz-/Funktionsfenster | **5V/2A bei Ta −20..+60°C** als Regler-Auslegungsziel; **+60..+70°C thermische Leistungsreduzierung oder geordnete Abschaltung zulässig**. Nicht zwischen Ambient, PCB und Halbleiter-Sperrschicht-Temperatur verwechseln |
| R6-TEMP-10 | **Bis +85 °C Umgebung sicher ausschalten / keinen gefährlichen Zustand erzeugen** | Keine 2A-Funktion oberhalb +60°C vorgeschrieben; Lagerung **−40..+85°C** nur, wenn **alle** Zellen, Display, Elektrolyte und Kunststoffteile gemäß Hersteller für diese Lagerung freigegeben sind |
| R6-5V-11 | **5,0 V / 2,0 A bei 10..32V und Ta −20..+60°C** | Vorläufige Worst-Case-Versorgungsdimensionierung; Geräte-Lastbilanz (ESP32, Display, GNSS, SD, LEDs) messen, nicht 2A automatisch als reale Dauerlast deklarieren |
| R6-RAW-12 | **Geschützter RAW-/Hilfs-Ausgang mit 0,5 A als Entwicklungsziel**, 1A optional | Kein garantierter 1A RAW gleichzeitig mit 5V2A bei VINmin/Tmax; RAW-Leitungs-/Stecker-/Teilkurzschutz gesondert prüfen; **0,5A ist ein Ziel, nicht schon sicherer frei verwendbarer Ausgang** |
| R6-OFF-13 | **Fahrzeugseitiger BAT+-OFF-Ruhestrom <1mA**, **Ziel <0,5mA** | Messen an 12V/24V und beim warmen Leckstrom. Relais-aktiv/DeepSleep ist ein anderer Zustand; RTC-Primärzellenentnahme separat. Nicht die frühere <100µA-Forderung als Pflicht fortschreiben |

## 4. Datenerhalt und neue Backup-Strategie

**Priorität 1:** Kritische Distanz-, Fahrzustands-, Zeit-/Session- und Transaktionsmarker werden **laufend atomar im nichtflüchtigen FRAM** gesichert, so dass der vollständige Stromabbruch oder ein Reset möglichst nur den jüngsten noch nicht verpflichtend gespeicherten Datensatz betrifft. Schreibintervalle/Verlustfenster, Strombudget und FRAM-Lebensdauer verifizieren; *FRAM benötigt zum Halten seiner gespeicherten Daten keine Batterie.*

**Priorität 2:** Bei normalem ACC AUS und weiterhin vorhandenem BAT+ bleibt der geordnete microSD-/FAT32-/GPX-/CSV-Abschluss inklusive MCU-HOLD Pflicht. Bei überraschendem M8-/BAT+-Ausfall dürfen SD-Flush/Unmount und MCU-Shutdown **nur** als garantiert versprochen werden, wenn eine unabhängig gespeiste Backupdomain plus gemessenes Worst-Case-Energie-/Strom-/Zeitbudget unter Zellalterung/Temperatur dies tatsächlich ermöglicht.

**Priorität 3:** Bei fehlender Backupenergie oder unvollständiger SD-Transaktion erfasst ein FRAM-Transaktionsjournal den unsauberen Abschluss; **sichere Erkennung/Wiederherstellung beim nächsten Start**, keine unqualifizierte Zusicherung stets geschlossener FAT32-Dateien. Software/Filesystem-Design muss gegen Power-Loss-Korruption robust geplant werden (z.B. periodisch begrenzte atomare SD-Commit-Blöcke; tatsächlich erreichbares Recovery gesondert testen).

**Knopfzelle:** Klein, austauschbar, **für RTC weiterhin geplant**. Ob dieselbe Zelle überhaupt mehr als RTC/kleine stromarme Backup-Aufgaben übernehmen kann, ist offen. Die CR1220 ist **nicht** ohne Datenblatt-Pulsstromnachweis für ESP32-S3 + microSD geeignet. Ein unabhängig bemessener Niedervolt-Puffer (z.B. geeigneter Supercap mit strombegrenztem Pfad oder geeignete Sekundärversorgung) kann nötig werden, muss aber nicht ohne Messdaten als Pflichtstückzahl in TripPower aufgenommen werden. Primär-Lithiumzelle nie laden. Keine Backfeed-Pfade in Fahrzeug-BAT+, ACC, RAW, 5V MAIN oder USB.

**Schnittstelle:** TripPower liefert einen fehlersicheren Versorgungsstatus (z.B. `PWR_FAIL` fail-HIGH bzw. PG) oder TripTracer überwacht den ungesicherten Fahrzeugpfad und die MAIN-Schiene zusätzlich autonom auf seiner bereits verfügbaren Hilfsdomäne. **Plötzlicher M8-/Masseabriss hat 0 garantierte Vorwarnzeit:** bloßes spätes Buck-PG sichert kein SD-Flush. Geeignete permanente Energie-/Backup-Verfügbarkeit bzw. FRAM-Konsistenz ist erforderlich. Keine Entladung der Primärzelle im normalen Betrieb für permanenten GPIO-Pullup. Eigene schriftliche Hardware-/Firmware-Schnittstelle und Tests bestimmen.

## 5. Verantwortung, Migration, Prüfgates

- **TripPower A/C/D:** vorhandene Branch-REV5-Schaltpläne sind Vergleichsartefakte. Für REV6 neue isolierte, einfachere 10..32V / 58V-begrenzt Designs nach echten IC-Referenzen entwickeln. Keine alte 200V-/125°C-Schutzstufe allein aus Angst um historische Spezifikation beibehalten, solange sie nicht konkret für das neue, deklarierte Installationsprofil erforderlich ist. Eine eFuse ist nur dann Pflicht, wenn ihre Schutzfunktion nicht durch eine einfachere nachgewiesene Alternative zuverlässig abgedeckt wird; äußere Zuleitungssicherung bleibt. Nicht eigenmächtig 90V/5ms obligatorisch machen.
- **TripPower B:** unabhängige Fehlerfall-/Leitungs-/F_MAIN-/32–36V-/58V-Überlebensprüfung und Kontrollfragen zur Fahrzeuginstallation, keine grenzenlosen 200V/125°C-Überbauanforderungen an V1, keine Kopplung der Primärzelle an Hochvolt. Power-Fail-/Backup-Fail-Status prüfen.
- **TripTracer-Hauptplatine:** FRAM-Commit-Zyklen, SD-Powerloss-Recovery, zeit-/energiebegrenztes Shutdown-Verhalten, RTC-Zelle und Rückspeise-/Powerpath-Design sowie RAW-Lastvermessung. MCU-/SD-Powerloss bleibt zu testen; Baugruppe ist nicht allein mit TripPower-Prototyp freigegeben.
- **Altdateien:** `REV5_DESIGN_BASELINE.json` enthält weiter alte 9–30V / 200V/350ms / -40..125°C. **Nicht** als aktuelle Produktspezifikation verwenden oder ohne explizite neue Schaltungsrevision still überschreiben. `AGENTS.md`, `HARDWARE_REQUIREMENTS.md`, Backup-Schnittstelle und `START_HERE_NEXT_CHAT.md` verweisen auf diese REV6-Datei.
- **Freigabe noch OFFEN:** konkrete Test-B-Wellenform/Quell-R/L an Moduleingang, echte Maximal-Pinspannungen, Short-/TVS-OPEN/SHORT-/fuse-safe-FMEA im eingeschränkten Einsatzbereich, UV/OV-Hysterese, 2A@+60°C Thermik, 32V-Dauerbetrieb, RAW 0.5A-Sicherheit, M8/USB-Isolation, Batteriezellen-/FRAM-/Dateisystemtests, native KiCad10 ERC/PCB-DRC/BOM/Footprints, Hersteller-/Laborbelege und Einbauvorschrift. Eine dokumentierte Einschränkung schützt **nicht** gegen falsche Installation; klare Kennzeichnung und Warn-/Prüfroutine erwägen.

### Versionsentscheidung

**Vorher REV5:** 9–30V Dauer; 200V/350ms ungedämpft; -40..+125°C Umgebung mit 5V2A+RAW1A als Worst-Case; sehr niedriger OFF-100µA; vollständiger SD-Backupabschluss als Ziel. **Neu REV6:** 10–32V Dauer; bei >32..≤36V AUS; 36V/400ms und max 58V/350ms **nur als konditionierter, vom Fahrzeug begrenzter Prüfpunkt**; -20..70°C, 2A nur bis+60°C, +85°C safe-off; RAW 0.5A Ziel; Fahrzeug-BAT-OFF <1mA (Ziel 0.5mA); FRAM-First und SD-Notabschluss nur bei qualifizierter Notenergie, sonst nachvollziehbare Wiederherstellung. **200V-Version bleibt gesonderte zukünftige Produkt-/Schutzoption**, nicht die V1-Pflicht.
