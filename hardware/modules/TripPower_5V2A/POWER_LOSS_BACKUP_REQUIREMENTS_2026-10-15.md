# TripPower ↔ TripTracer – Knopfzellen-Notversorgung bei Versorgungsverlust

**Verbindliche neue Nutzeranforderung vom 15.10.2026 – gültig für alle Architekturpfade A/B/C und das gemeinsame Baseline-/Review-Design.** Stellt eine **funktionale Anforderung**, keinen Nachweis oder eine freigegebene Zellenauswahl dar. Ältere Aussagen „kein Datennachlauf bei M8-/BAT+-Verlust“ in `docs/HARDWARE_REQUIREMENTS.md`, `AGENTS.md`, älteren Berichten oder der unveränderten elektrischen REV5-BOM werden dadurch **inhaltlich überholt**. Produktionsschaltplan, Schutzstufen und `REV5_DESIGN_BASELINE.json` bleiben konstruktiv eingefroren, bis technische Nachweise vorliegen.

## Ziel und Abgrenzung

TripTracer erhält eine **kleine Knopfzelle als lokale Notenergiequelle**, damit bei **unerwartetem vollständigem Wegfall der Fahrzeugversorgung** (z. B. BAT+ fällt aus, M8 wird abgezogen, Eingangsschutz trennt dauerhaft) kritische Daten **sicher persistent gemacht** und MCU/Dateisystem **geordnet heruntergefahren** werden können. Es wird **nicht** verlangt, während des Notbetriebs den Tripmaster weiter als Tripmaster zu betreiben.

**Normales ACC AUS bei BAT+ vorhanden** bleibt unverändert: normale ACC-/MCU-HOLD-Versorgung bis zum Dateischluss, kein unnötiger Verbrauch der Notzelle. Kurze Motorstart-Einbrüche sind ein dritter, separat zu testender Zustand und dürfen nicht unnötig die Knopfzelle entladen.

**Wichtig: Die bisher schon vorgesehene RTC-Knopfzelle (aktuelle Prüfung CR1220)** hat bisher ausschließlich die RTC-/Zeitpuffer-Aufgabe (`STO-25`). Eine übliche Primär-Lithiumknopfzelle ist **nicht** automatisch als Notstromquelle für ESP32-S3 + FRAM + microSD und deren SD-Schreibstromspitzen geeignet. Ob **eine gemeinsame** oder **zwei getrennte** Zellen, eine geeignete Hochstrom-Knopfzelle, ein kleiner zugeschalteter Energiepuffer oder ein anderes strombegrenztes Pufferkonzept notwendig ist, ist **offener Auslegungs-/Kostenpunkt**, nicht freigegeben. **Primärzellen niemals laden.** Keine pauschale Annahme, die Zelle könne 5 V / 2 A liefern.

## Zustandsautomat / Funktionskriterien

1. **Fahrzeug vorhanden, ACC EIN:** Fahrzeugversorgung betreibt normal; Notzelle idealerweise galvanisch/elektrisch entkoppelt, Ruhestrom minimieren. Lade-/Rückspeiseverbot bei Primärzellen. RTC-Funktion bleibt erhalten.
2. **ACC AUS, BAT+ vorhanden:** Bestehende HOLD-/Enable-Funktion schließt FRAM/GPX/CSV/microSD/FAT32 geordnet; Notzelle wird normalerweise nicht benötigt.
3. **BAT+/M8 fällt unerwartet aus, ggf. ACC noch EIN:** Versorgungsausfall oder drohendes Absinken einer kritischen Schiene **früh genug erkennen** (`PWR_FAIL`/Power-Good; Signalname/Polarität offen); aktive Lasten sofort ausschalten: Display/Backlight, Tasten-LEDs, GNSS/aktive Antenne, Radgeber/RAW-Ausgang und andere nicht essentielle Verbraucher. Danach nur **minimal notwendige MCU-, FRAM-, microSD- und zugehörige Logik-/Versorgungsschienen** bis zum *verifizierten* Datenabschluss sichern; danach Abschalten.
4. **Energiemangel, defekte/leere Zelle, SD-Schreibfehler oder MCU-Reset:** Sicherer definierter Ausfallzustand; FRAM-Zähler/Transaktionsmarker soweit möglich atomar sichern und beim Neustart konsistent wiederherstellen. Keine unzulässige Schreibunterbrechung oder absolute Dateischlussgarantie ohne Energie- und Fehlerfallnachweis behaupten; **das Produktziel bleibt vollständiger, geordneter Abschluss** bei spezifizierter und geprüfter Backup-Verfügbarkeit.
5. **Fahrzeug kommt zurück:** Keine unkontrollierten Einschaltzyklen, normaler Power-Path-Priorität und MCU-Zustandsübergang, kein USB-/Fahrzeug-/Zellen-Rückspeisen; Logging/SD-Mount nach Konsistenzprüfung fortsetzen.

## Zuständigkeiten / Hardware-Schnittstelle

**TripPower (jeder Entwicklungsbranch):**
- Nicht mehr voraussetzen, dass bei Versorgungsverlust alle nachfolgenden Schienen sofort folgenlos auf 0 V gehen dürfen. Frühzeitige, sauber spezifizierte **Power-Fail-Erkennung** bzw. ein entsprechend geeigneter Spannungsstatus und eine elektrische Schnittstelle zur TripTracer-Backup-Steuerung berücksichtigen; bei Architekturvarianten mit Vorschaltschutz muss das Ereignis auch bei elektronischer OV/UV-Abschaltung erkannt bzw. antizipiert werden.
- **Rückspeisung aus lokaler Backup-Energie in Fahrzeug-BAT+/ACC, RAW_PROTECTED, defekte TripPower-Schutzstufen, USB-VBUS oder die normalen 5-V-/2-A-Hauptlasten verhindern**; möglichst eindeutige Power-Domain-Trennung. Die Standby-Last der Schnittstelle darf das bisherige BAT+-OFF-Systemziel unter 100µA nicht ungeprüft verletzen.
- Falls TripPower den Not-Power-Path konstruktiv übernehmen soll, gelten dafür dieselben Nachweise. **Keine fixe Knopfzellenzelle oder ungeregelte Verbindung zu +5V_MAIN in TripPower vorsehen**, bevor die Schnittstelle mit der TripTracer-Hauptplatine und dem Strombudget festgelegt wurde.

**TripTracer (Hauptplatine und Firmware):**
- Lokale Notenergiequelle/Knopfzellenhalter, Schutz/Verpolung, Entkopplung und ggf. passender DC/DC bzw. Hold-up-Schalter auf **die kritische Lastdomäne** auslegen; Versorgung und Reset/Unterspannungsschwellen von ESP32-S3, FRAM und SD gemeinsam koordinieren.
- Frühzeitige Power-Fail-IRQ / Zustandsmaschine: Datenaufnahme stoppen, kritische Zähler/Sessions atomar in FRAM persistieren, offene GPX-/CSV-Schreibvorgänge und FAT32-Metadaten sicher abschließen, SD unmount, Versorgung kontrolliert freigeben. Falls Energie nur für FRAM reicht, darf die Firmware keine bereits gesicherte SD-Konsistenz vortäuschen; Recovery im nächsten Boot ist dann ein **unqualifizierter Not-/Fehlzustand**, kein Ersatz für das Ziel der geordneten Abschaltung.
- USB-only-MSC und RTC-Backup von der Notversorgungsfunktion funktional und elektrisch entkoppeln. Bereits vorgesehene RTC-Backupversorgung ist kein Beleg für SD-Shutdown-Energie.

## Erforderliche Nachweise – verbindliche offene Gates

- **Strom-/Leistungsmessung** der tatsächlich minimalen Shut-down-Domäne (MCU, FRAM, SD) mit SD-Peaks, RTC, Supervisor, Power-Path und Wirkungsgrad. **Energie** >= Integral der Leistungsaufnahme über den *Worst-Case*-Speichervorgang inklusive Spannungsabfall/Temperatur/Alterung/Zelleninnenwiderstand und Reserve. Die bisherige ~3-s-Zeitannahme bei ACC AUS ist ein **erster Testansatz**, **keine** nachgewiesene Knopfzellen-Backupzeit.
- **Knopfzelle fachlich qualifizieren:** MPN, Chemie (Primär/aufladbar), Entladekurve, max Puls- und Dauerstrom, Kapazität/Innenwiderstand bei tiefen und hohen Temperaturen, Alterung, Selbstentladung, mechanischer Halter, Vibrationssicherheit, Polarität, **Temperaturfähigkeit im TripTracer-Gehäuse** und sichere Wechselbarkeit. Normale CR1220/CR2032-RTC-Zellen **nicht als bereits ausreichend** annehmen.
- Messung **PWR_FAIL→IRQ**, Umschaltzeit, minimale Versorgungsschiene unter maximalen SD-Schreibspitzen, Ende der SD-Transaktion, Abschaltzeit und Wiederanlauf. Tests bei Fahrzeugabzug, 9/12/24/30V, USB gleichzeitig, schwacher/fehlender/verkehrt eingesetzter Zelle, MCU-Hänger, SD voll/fehlerhaft und Schutzabschaltung.
- Ruhestrom/BAT+-OFF<100µA, Batterie-Lebensdauer, sichere Schalter-/FET-Fehlermodi. Kein höheres 200V-/350ms- oder −40..+125°C-Qualifikationsprädikat, nur weil Backup existiert.

**Abgrenzung 9-V-Vmin:** Diese neue Backup-Anforderung **ändert nicht automatisch** das bisherige 9–30V-TripPower-Betriebsziel. Ein Wechsel auf 10V/11V erfordert eine separate Entscheidung; im Backupzustand gilt statt Rallye-Dauerbetrieb nur der geprüfte geordnete Shutdown.

## Umsetzung / Fortschritt

Alle A/B/C-Chats müssen die Backupschnittstelle in ihren Architekturvergleichen berücksichtigen; Platzierung/Hauptplatinenverantwortung ist als offener Interface-Entscheid zu markieren. Keine stillschweigende Aufstockung ihrer normalen 5-V/2-A-Dauerlastanforderung auf Batteriebetrieb. Erst bei geklärter Energiebilanz und Hersteller-MPN kann eine Zelle als funktionsfähig freigegeben werden.
