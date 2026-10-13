# TripTracer V1 – Feldstudie: relaislose Automotive-Stromversorgung (Variante 3)

**Stand:** 13.10.2026, **elektrische Vorstudie ohne Fertigungsfreigabe**. Ausgangsstand unveränderlich gesichert: `07b6ae6c82a02aa866dadd50f507025a7d0c8587` (`snapshot/2026-10-13-before-solid-state`); der vorangegangene 01D-Designreview separat unter `snapshot/2026-10-13-with-01d-review`. Diese Studie **ersetzt keinen KiCad-Schaltplan**, keinen Schaltungs-/Pincheck, kein ERC/DRC und keinen Fahrzeugtest.

## 1. Beschluss, Ziel, Einschränkungen

Nach Vergleich der relaisgesteuerten Variante 2 mit der elektronischen Variante 3 soll **Variante 3 prioritär entwickelt werden**. Entscheidung gilt für die **Entwicklungsrichtung**, **nicht** als elektrische, Automotive-, funktionale oder fertigungstechnische Freigabe. Bei Versagen wichtiger Sicherheitstests darf auf Variante 2 mit kleinem monostabilem Signalrelais zurückgegriffen werden.

Unverändert aus `HARDWARE_REQUIREMENTS.md`: **M8: Pin 1 ACC, Pin 3 GND, Pin 4 BAT+; ACC/BAT+ fahrzeugseitig getrennt absichern**; 9–36 V Dauerbereich; getrennt ausgelegte negative/positive Transienten; USB-only betreibt ESP32 und SD für MSC/Flash, nie normalen Rallyebetrieb; M8 hat beim gleichzeitigen USB-Anschluss Strompriorität und darf USB nicht rückspeisen. Bei **ACC AUS + BAT+ vorhanden** müssen FRAM/GPX/CSV/FAT32 abgeschlossen werden, danach harte Ausschaltung. Bei **vollem M8-Abzug** kein garantierter Notflush. Gewollter manuell aktivierter **ACC-Standby** bleibt möglich. USB-only darf die Fahrzeug-Versorgung *nicht* über MCU-HOLD einschalten.

**Sicherheitsdefinition:** „sicherer als das Relais“ ist **eine Hypothese**, erst nach FMEA (inklusive Common-Cause-Fehler), Schaltplan- und Bauteilprüfung sowie realen Messungen feststellbar. Zwei physische Schalter sind nur dann eine glaubwürdige Redundanz, wenn ihre Fehler-/Ansteuerpfade hinreichend getrennt und die Schaltzustände gemessen sind.

## 2. Zwei relaislose Topologien

### S1 – empfohlene erste Labor-Topologie: eFuse vor unabhängigem Abschalt-MOSFET

```text
   M8 Pin 4 BAT+  ---- Fahrzeug-Sicherung (extern) ----> Schutz gegen Transienten
                                                     / Verpolung / neg. Pulse
                                                             |
                                                    BAT_PROTECTED, 9–36 V
                                                             |
                                          Q401 Blocking-FET / Q402 Treiber
                                                             |
                                      U401 TPS26631 eFuse: ILIM / OVP / UVLO
                                               dVdT / FLT / SHDN
                                                             |
                                               Q601 separater HIGH-SIDE-FET
                                         (normally OFF; eigener Steuerpfad)
                                                             |
                                              HV_MAIN -> 5V_MAIN -> 3V3_VEH
                                                             |
                                  Hauptsystem: ESP32/GNSS/FRAM/SD/Datenpfade

   M8 Pin 1 ACC -- eigene Sicherung -- ACC-Surge-/Reverse-Schutz -->
        ACC_QUAL --> ACC-Wake- und Hardware-HOLD-Logik --> SHDN & Q601
                             ^                            (getrennte Treiber)
                       MCU_HOLD_REQ, car-only Timer

   USB-C 5V --> getrennte, rückspeisegeschützte USB-ONLY-Logik/SD-Versorgung
        (kein ACC/HOLD-Anlauf und kein Rückweg in BAT_PROTECTED)
```

**Pluspunkte:** U401 begrenzt den Einschaltstrom zur nachgelagerten Hauptlast; kein stromschaltender Relaiskontakt und **kein dauerhaft arbeitender 5-V-AUX-Wandler für eine Relaisspule**. Q601 kann als zweiter, **separat angesteuerter** Abschalter wirken, wenn die eFuse intern leitend ausfällt. U401 behält ihre externe Q401/Q402-Verpol-/Rückstromfunktion; Q601 ersetzt diese **nicht**.

**Risiko:** U401 liegt permanent an BAT+ und zieht im SHDN-Zustand **21 µA typ., 60 µA max.** (über spezifizierte Datenblattbedingungen). Die externe U401-OVP/UVLO- und ACC-Logik benötigt einen eigenen Ruhestrometat. Q601 kann im OFF-Zustand über die Body-Diode **rückwärts** vom USB-versorgten Ausgang speisen: reale USB-Rückspeisesperre ist weiterhin zwingend. Ein FET kann leitend ausfallen; **keine** Behauptung eines sicherheitszertifizierten zweikanaligen Systems.

### S2 – nur als Reserve für zu hohen Ruhestrom: eigener MOSFET *vor* der eFuse

```text
   M8 BAT+ -> Fahrzeug-Sicherung -> vollwertiger Kfz-/Verpol-Schutz
         -> Q601 HIGH-SIDE (default OFF, unabhängiges Gate)
         -> möglichst kleine C_IN -> Q401+Q402 / U401 eFuse -> 5V_MAIN
```

**Plus:** Wenn Q601 sperrt, sind U401 und ihr OVP-Teiler grundsätzlich spannungsfrei; der BAT+-Ruhestrom kann deutlich kleiner als S1 sein. **Aber:** Q601 schaltet die Eingangskapazität VOR U401 und muss 9–36 V plus definierte Fahrzeugpulse, Energie/SOA, Gate-Über-/Unterspannung und Einschaltstrom **selbst** sicher beherrschen. Ein **einzelner P-Kanal-FET ist KEIN Verpol-/Rückstromschutz** (Body-Diode beachten). Nur nach vorgeschaltetem nachgewiesenem Reverse-/Surge-Schutz oder geeigneter Back-to-back-Topologie möglich. **Nicht stillschweigend S2 einsetzen, nur um 20–60 µA zu sparen.**

**Entscheidung jetzt:** S1 zuerst auf elektrische Funktions- und Sicherheitsfähigkeit prüfen. S2 ausschließlich bei belegtem Ruhestromproblem und belegtem Nutzen vs. Schutz-, SOA- und BOM-Mehrkosten verfolgen.

## 3. Datenblattgestützte erste Rechnungen

### 3.1 U401 TPS26631: SHDN und Ruhestrom

TI TPS2663 Rev. G, `6.5 Electrical Characteristics`, bei –40 bis +125 °C: `I_Q(OFF) = 21 µA typ., 60 µA max.`; SHDN LOW **unter 0,8 V**, SHDN HIGH **mindestens 2 V**. Für aktives Herunterziehen muss der Treiber **mindestens 10 µA sinken** können. Offene SHDN-Leitung ist nicht sicher abgeschaltet, sondern typischerweise ca. 2,7 V. **SHDN absolut max. +5,5 V**. Eine Schutz-/Startschaltung muss daher auch bei **ACC = 36 V, ACC-Surge, USB-only ohne BAT+**, GPIO-Zustand unbestimmt und offenem MCU-Ausgang sicher bleiben.

Ein theoretischer passiver `R_SHDN = 39 kΩ` gegen GND ergibt bei maximal 10 µA internem Pull-up **0,39 V** am SHDN, unterhalb 0,8 V. **Das ist lediglich eine erste Dimensionierungsprüfung**; tatsächlicher Strom-/Temperaturverlauf, Leckströme, Störfestigkeit sowie Pull-up-/Aktiv-Treiber sind am konkreten Chip zu validieren. **Keine direkte ACC-9–36-V- oder MCU-USB-Leitung auf SHDN legen**; aktiver, geschützter Pegelwandler mit Startfunktion und späterer HOLD-Funktion ist erforderlich.

`MODE = GND` stellt Auto-Retry ein, nicht Latch. U401 ist eine **Industrie-eFuse**, **nicht nachgewiesen AEC-Q100-zertifiziert**. Der externe Q401-Blocking-N-FET und Q402-Fast-Pulldown sind weiterhin Pflicht für diese Reverse-Polarity-Topologie.

### 3.2 Ruhestromoptimierung über den OVP-Teiler (S1)

U401 besitzt einen OVP-Eingang mit **1,176 bis 1,224 V steigender Schaltschwelle**, Eingangs-Leckstrom **–150 bis +150 nA**. Bei `R_TOP = 2,2 MΩ`, `R_BOTTOM = 68 kΩ` ergibt sich nominal:

```text
V_OVP,nom  = 1,2 V × (1 + 2,2 MΩ / 68 kΩ) = 40,02 V
I_div@9V   = 9 V / 2,268 MΩ  = 3,97 µA
I_div@12V  = 12 V / 2,268 MΩ = 5,29 µA
I_div@24V  = 24 V / 2,268 MΩ = 10,58 µA
I_div@36V  = 36 V / 2,268 MΩ = 15,87 µA
```

Gegenüber dem alten **390 kΩ + 12 kΩ**-Teiler (**89,55 µA bei 36 V**) sparen wir etwa **73,68 µA bei 36 V**. Mit 1-%-Widerständen, der spezifizierten OVP-Referenzstreuung und ±150-nA-Eingangsstrom ergibt die algebraische Eckwertrechnung ungefähr **38,14 bis 41,96 V** für die steigende Abschaltschwelle. Diese Bandbreite ist **keine** Automotive-Lastabwurffreigabe: Eingangsstörungen, Leiterplatten-Leckströme, zulässige OVP-Reaktion, Toleranz-/Alterungseinflüsse und das Verhalten bei sehr schnellen Impulsen fehlen noch.

**S1-Ruhestrom-Zwischensumme bei 36 V** nur aus *maximalem* U401-Shutdown-IC-Strom + OVP-Divider-Nennstrom: **60 + 15,87 = 75,87 µA**. Bis zum **100-µA-Gesamtziel** blieben **24,13 µA** für ALLE anderen BAT+-angeschlossenen Stufen (ACC-Messung, Reverse-FET-Leckströme, TVS, Q601, Schutz-/Spannungsteiler, Leiterplatte, Temperatur). Diese Reserve kann bei +85 °C unzureichend sein. **Nicht als bestanden ausgeben.**

### 3.3 P-Kanal-Sicherheitsschalter Q601, nur Bauteilkandidat

ROHM **AG502EPD3HRTTL**, AEC-Q101, **–100 V**, **–28 A**, TO-252/DPAK, `R_DS(on) typ ≈ 74 mΩ` bei `V_GS = –10 V`; nicht ohne Prüfung des konkreten `V_GS(max)`, SOA, Gate-Clamps, Sperrleckstroms, Footprints und Temperatur-Deratings freigegeben. Bei **2 A Dauerstrom** ergäben **I²R ≈ 0,296 W** nur aus der typischen 25-°C-Kennzahl, ohne Temperaturanstieg/PCB. Alternative **ROHM AG501EPD3HRTTL** ebenfalls –100 V und AEC-Q101, `R_DS(on) typ ≈ 25 mΩ`, gleiche Gehäuseklasse; bei 2 A nominal **0,100 W**, aber größere Gate-Ladung. **Reale TripTracer-Last, Stückkosten, Lagerbestand, SOA und die komplette Steuerung sind offen**.

Q601 darf ohne geklärte Rückstromrichtung/Gatespannung nicht unmittelbar in die Netzliste gesetzt werden. Besonders **kein Low-Side-MOSFET im gemeinsamen GND** (USB-/GNSS-/Sensorrückströme und Fehlerpotentiale).

### 3.4 Startunterspannung bleibt eigenständiges Gate

Der TPS26631 verlangt mindestens **4,5 V**, die beschlossene Startannahme erreicht aber kurz **3 V für 15 ms**. **Die eFuse kann diesen 3-V-Einbruch nicht selbst garantieren.** Die Hauptlogik muss für diese Zeit Energie aus einem *nachweisbar richtig angeordneten* Kondensator-/Power-Path-Puffer beziehen, nötigenfalls mit Lastabwurf des Backlights. Rein illustrativ: Bei 5 V / 0,5 A und 15 ms sind **37,5 mJ** erforderlich. Für einen idealen 5-V-Kondensator, der zwischen 5 und 4 V entladen wird, ergäben sich mindestens **8,33 mF**, ohne Wirkungsgrad, ESR, Toleranz und Temperatur. **Nicht automatisch diese Beispielkapazität bestellen** – zuerst echte 3V3/5V-Kernlast und die Wandler-/Buck-UVLO samt Einbruchkurve messen. Kein 3-s-Puffer für Kabelabzug.

## 3.5 Architektur-Vergleichskandidat – ADI LTC4380 (nur Studie, NICHT beschlossen)

**Analog Devices LTC4380** ist ein für Automotive-Anwendungen **AEC-Q100-qualifizierter Surge-Stopper** mit **4–72 V Betriebsbereich**, **8 µA typ. Betrieb** beziehungsweise **6 µA typ. Shutdown**, externem N-MOSFET, einstellbarer Überstromabschaltung, Überspannungs-Clamp-/SOA-Fault-Timer und möglicher Back-to-back-FET-Schaltung für Verpolschutz. In der handlötbareren **10-Pin-MSOP-Familie** erhältlich. Herstellerbeleg: [ADI LTC4380](https://www.analog.com/en/products/ltc4380.html), [Datenblatt](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4380.pdf).

**Technischer Grund für die zusätzliche Prüfung:** Bei 24-V-Fahrzeugen können Load-Dump-Surge-Spitzen sehr viel höher als 60 V werden. Ein mit geeignetem externerem MOSFET dimensionierter LTC4380 kann solche Ereignisse *prinzipiell* behandeln, seine Durchgangsfähigkeit hängt jedoch von der **MOSFET-SOA und der tatsächlichen Surge-Energie** ab. Bei `V_Surge=200 V`, `V_OUT=40 V` und `I_LOAD=2 A` wären während der Klemme **(200−40)·2=320 W** im externen MOSFET zu vernichten: für ein kleines TO-252-Bauteil bei langer Pulsdauer **nicht pauschal zulässig**. Er kann alternativ mit geeigneter TMR-Abschaltung statt dauerhaftem Energieabbau arbeiten; ob das TripTracer-Logging dabei erhalten bleibt, muss geprüft werden. [ADI Hinweis zur LTC4380-SOA bei langen Load-Dumps](https://ez.analog.com/power/f/q-a/165955/ltc4380-actual-clamping-time-limit-mosfet-soa/376834).

**Vorteile vs. TPS26631:** niedrigere Ruhe-/Betriebsaufnahme des Controllers, Automotive-Qualifikation, mehr Flexibilität beim externen Überspannungs-MOSFET. **Nachteile:** Preis (ADI listet ab ca. 3,79 USD bei 1000 Stück für die Familie, kein aktueller Kleinmengen-/JLCPCB-Preis), externe FET-SOA-Dimensionierung ggf. aufwendig und thermisch größer, die integrierte 31-mΩ-eFuse mit definierter PWP-Schaltfunktion entfällt; zusätzlicher unabhängiger Abschaltpfad bleibt bei unserer Zwei-Schalter-Strategie notwendig. **Nicht als elektrisch gleichwertiger Drop-in-Ersatz** betrachten.

**Architekturstatus:** Die explizite PWR-03-eFuse-Bauteilvorgabe bleibt gültig; **LTC4380 wird nicht in die KiCad-Hauptschaltung eingefügt oder bestellt**, solange keine gesonderte Freigabe für eine Bauteil-/Architekturänderung vorliegt. Priorität: zuerst S1 mit TPS26631 sinnvoll dimensionieren; bei ungelöster Surge-/SOA-/Ruhestrom-Problematik diesen Vergleich auf der Basis des vollständigen Fahrzeug-Prüfprofils durchführen.

## 3.6 Erste Lastabschätzung aus Herstellerdaten (noch **kein** gemessener Gesamtstrom)

Das konkrete Riverdi-Modul **RVT35HITNWC00-B** verlangt für seine LED-Hintergrundbeleuchtung **15 V / 100 mA = 1,5 W typisch** (13,5–17 V LED-Betriebsspannung): ein **dedizierter geregelter Konstantstrom-Boost-Treiber** aus 5 V/anderer geeigneter Schiene ist erforderlich; bloßer Anschluss an 5 V ist unzulässig. Beim rechnerisch angenommenen Treiberwirkungsgrad von **85 %** sind allein dafür rund **1,76 W**, also **353 mA aus 5 V** einzuplanen; Wirkungsgrad und Startstrom sind bis zur Treiberwahl **nicht spezifiziert**. [Riverdi Modul-Datenblatt Rev. 1.1, Abschnitt 7](https://download.riverdi.com/RVT35HITNWC00-B/DS_RVT35HITNWC00-B_Rev.1.1.pdf).

Das u-blox **MAX-M10N-00B** benötigt bei nomineller 3-V-Versorgung und Standard-GPS/Galileo/BeiDou-Tracking laut Datenblatt **7 mA am VCC + 3,7 mA am V_IO** (zusammen **10,7 mA typ. bei 1 Hz**, d. h. rund 32 mW bei 3 V), besitzt aber beim Start laut Hersteller **bis 100 mA Inrush**. **Bei den projektierten 5 Hz kann der Mittelwert abweichen**. [u-blox MAX-M10N-00B, Abschn. 4](https://content.u-blox.com/sites/default/files/documents/MAX-M10N-00B_DataSheet_UBXDOC-963802114-13143.pdf).

Espressif verlangt für das **ESP32-S3-MINI-1-N8** eine Versorgung mit der Fähigkeit, **mindestens 500 mA bei 3,3 V** bereitstellen zu können (Leistungsreserve **1,65 W**); **dies ist ausdrücklich keine garantierte dauerhafte CPU-Leistungsaufnahme**. [ESP32-S3-MINI-1, elektr. Bedingungen](https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html).

Eine **nicht-bestellfähige Szenariorechnung** für den Hauptpfad lautet:

| Lastpunkt | Angenommene elektrische Last | Status |
|---|---:|---|
| Riverdi-Backlight inkl. angenommener 85-%-Boost-Wirkung | 1,765 W am Boost-Eingang | Backlight 1,5 W laut Hersteller; 85 % reine Annahme |
| ESP32-S3 Versorgungsauslegung 3,3 V × 0,5 A | 1,650 W | Versorgungsauslegungsreserve, nicht gemessener Dauerwert |
| GNSS, 3,3-V-Schätzung aus 10,7 mA | 0,035 W | Herstellertracking bei 3 V/1 Hz, 5 Hz noch offen |
| Sechs beleuchtete Tastenringe mit hypothetischen 20 mA × 3 V | 0,360 W | **nur hypothetischer Maximalfall**, LED-Treiberspezifikation fehlt |
| microSD 3,3 V × angenommene 100 mA | 0,330 W | **nur Szenario**, kartenabhängige Schreibspitzen offen |
| Zwei 5-V-Geber mit angenommenen je 100 mA | 1,000 W | **nur Szenario**, Kurzschlussgrenzen noch unbekannt |
| Sonstige Verbraucher | 0,100 W | ungemessene Reserve |
| **Summe** | **ca. 5,24 W** | **keine endgültige Worst-Case-Freigabe** |

Bei hypothetisch **80 % Gesamt-Wirkungsgrad ab BAT+** entspräche das etwa **0,73 A bei 9 V**, **0,55 A bei 12 V**, **0,27 A bei 24 V**, **0,18 A bei 36 V**. Hieraus folgt **nicht**, dass wir 2,4 A ILIM benötigen: Stromschwellwert erst nach Messung/Peak-Verteilung einschließlich angeschlossener Radgeber und Worst-Case-Kondensatorladung festlegen. Möglicherweise ist **TPS26630 (nur 1× Strombegrenzung statt der 2×-Pulsvariante TPS26631)** für eine vorteilhaftere Fehlerschutzcharakteristik geeignet, jedoch **nicht** ohne Last- und Lieferfähigkeitsvergleich ersetzen.

**Wichtige Lastabwurf-Folgerung für Kaltstart:** Sobald der Fahrer den Motor startet, kann das zeitweise Abschalten des Backlights die Core-Hold-up-Energie erheblich reduzieren. Bei 15 ms würde die Hintergrundbeleuchtung allein **22,5 mJ am LED-Ausgang** verbrauchen (plus Treiberverluste); diese Last muss nicht gepuffert werden, wenn das Backlight rechtzeitig abgeschaltet ist. Die für 15-ms-Überbrückung entscheidende **CPU/SD/GNSS-Kernlast bleibt zu messen**. Für einen idealen 5-V-Puffer zwischen 5 und 4 V gilt `C = 2·P·t / (5²−4²)`; bei **0,6 W** und **15 ms** z. B. **2,0 mF ideal**, ohne ESR/Toleranzen/Temperatur/Restwirkungsgrad. Die Schaltung muss schon **vor** dem Spannungseinbruch schnell genug auf Lastabwurf umschalten.

## 4. Zustandsautomat und Einschalt-Selbsthaltung

| Zustand | ACC | M8 BAT+ | USB | U401/Q601 | Nachweis |
|---|---|---|---|---|---|
| OFF | LOW | ja | egal | beide AUS; Fahrzeug-GPIO/Timer kein Bootstrap | I_OFF ≤100 µA für 9–36 V und relevante Temperaturen; USB darf Fahrzeugpfad nicht wecken |
| ACC_BOOT | HIGH | ja | egal | **beide EIN auch ohne MCU-Firmware** | Start ohne 3V3_MAIN und ohne bisherigen 5V_AUX; kein Henne-Ei |
| ACC_NORMAL | HIGH | ja | optional | beide EIN | Logging, GNSS, Sensoren, Display normal; M8-Strompriorität |
| ACC_STANDBY | HIGH | ja | optional | beide EIN für definierte Deep-Sleep-Wake-Funktion | keine ungewollte Abschaltung/Entladung; bei ACC AUS trotzdem Dateischluss |
| ACC_SHUTDOWN | LOW | ja | optional | nur zeitbegrenzt via `MCU_HOLD_REQ AND TIMER_WINDOW AND VEH_ARMED` EIN | zuerst Verbraucher außer MCU/FRAM/SD aus, SD flush/unmount, HOLD LOW -> beide AUS |
| USB_ONLY_MSC | LOW | nein | ja | beide AUS | MSC/Flash per USB, interne SD exklusiv, keine BAT+-Rückspeisung |
| ACC_OUT_BAT_LOSS | egal | nein | optional | kontrolliertes OFF soweit möglich, **kein garantierter SD-Flush** | kein vorgetäuschter 3-s-Nachlauf |
| MCU_HUNG_AFTER_ACC_OFF | LOW | ja | egal | Timer beendet HOLD auch bei GPIO HIGH | kein dauerhafter Fahrzeugstrom |
| BROWNOUT / RESTART | instabil | instabil | beliebig | definierte Hysterese, kein GPIO-Power-Glitch-Latch | 3V 15ms/6V mehrere Sekunden (12-V-Profil), 24-V-Profil separat |

**Neue logische Anforderung:** Der Timer `01C_HOLD_TIMER` darf im USB-only-Modus **nicht** aus der USB-3,3-V-Schiene armiert werden. Er benötigt eine *fahrzeugversorgte* Logikschiene, z. B. `3V3_VEH`, und eine saubere, geschützte ACC-Flankenerkennung. Das bestehende **01B_ACC_WAKE hängt an 5V_AUX_COIL** und funktioniert nach Entfall dieses Wandlers **nicht mehr**. Der bereits gezeichnete 01C-TLC555 ist ein **wiederverwendbarer Kandidat, keine Drop-in-Integration**: Das nominale `2,2 MΩ × 10 µF × 1,1 = 24,2 s` hat MLCC-DC-Bias-, Toleranz- und Leakage-Risiken; schon die Start-/Endflankenlogik muss als Gesamtschaltung neu geprüft werden. TLC555-Q1 ist AEC-Q100 und im aktiven 3V3_VEH-Modus nutzbar; **seine circa 180 µA Iq gehören in den EIN-/Shutdown-Verbrauch**, nicht in OFF, wenn `3V3_VEH` dort wirklich spannungsfrei ist.

**Abschalt-Race:** Sobald ACC fällt, muss `HOLD_TIMER_GRANTED` vor Abfall von SHDN/Q601 wirksam sein (oder geeignete definierte Umschaltreserve/RC-Haltezeit vorgesehen werden). Eine bloße Software-Reaktion kann eine zu schnelle eFuse-Öffnung nicht verhindern. Nach FRAM/SD-Flush MUSS die MCU-HOLD-Leitung durch Hardware-Freigabe/Timer beendet werden; bei nicht antwortender MCU zeitbegrenztes OFF.

**Einzelfehler-Entkopplung:** Q601 und U401 dürfen nicht allein an einem gemeinsamen, permanent HIGH möglichen MCU-GPIO hängen. Mindestens ein unabhängiger, hardwareseitig zeitbegrenzter Pfad ist für Q601 erforderlich; U401 muss gesondert auf SHDN-LOW gebracht werden können. Kurzgeschlossener FET, dauerhaft HIGH gehaltenes SHDN, fehlende ACC-Flanke, TIMER stuck HIGH, Reverse-Polarity-/Load-Dump-Schaden und USB-Rückspeisung müssen in einer tatsächlichen Fault-Injection nachgewiesen werden.

## 5. Vorläufige Fehlermöglichkeitsanalyse (FMEA-Gates)

| Fehler / Auslöser | S1 gewünschtes Verhalten | Noch erforderliche Prüfung |
|---|---|---|
| Q601 Drain–Source Kurzschluss | U401 kann die Hauptlast unabhängig abschalten | echte unabhängige SHDN-Logik; Fehlermode verifizieren |
| U401 Ausgang dauerhaft leitend | Q601 kann abschalten | Q601 unabhängig abgesicherte Gate-Ansteuerung; U401-Short simulieren |
| Q601 Gate-Fehler, OFF-Gate-Pull-up offen | kein unkontrollierter Dauerbetrieb | zusätzlicher Gate-Defektmodus, Pull-up-Redundanz/Widerstandsfehler |
| SHDN auf HIGH festgehalten | Q601 muss nach begrenzter Zeit öffnen | eigener Timerpfad, gemeinsame Ursache separieren |
| MCU_HOLD GPIO HIGH durch Firmwarefehler | hardwareseitige Timer-Grenze | RC-Min/Max, POR und Re-Trigger prüfen |
| Fahrzeugstecker mit ACC = 0, BAT+ = 36 V | OFF, <100 µA Gesamtziel | 36V-/+85°C-Leckströme und Eingangs-Transienten |
| BAT+ vorhanden und USB angeschlossen | Fahrzeug versorgt normal; USB liefert nur Daten | Backfeed- und GND-Rückstrommessungen, Source-OR |
| USB-only mit HOLD-Fehler | Kein Fahrzeugpfad an, kein Rückstrom über VIN/SHDN | physikalischer Fahrzeug-ARM-Interlock |
| ACC fällt während Dateioperation | bounded HOLD, FAT32 konsistent nach Flush | High-Speed-Trigger, SD-Worst-Case-Latenz |
| Motorstart bis 3 V | MCU/GNSS/FRAM/SD bleiben im spez. Profil funktionsfähig | Lastmessung, Hold-up, eFuse-UVLO, Buck-Verhalten |
| 24-V-Load-Dump, Verpolung, Masseabfall | keine Überschreitung abs. max.; definierter Fehlerzustand | Fahrzeugprüfprofil, Surge-/TVS-Energie und Leitungs-/M8-Schutz |

**Weitere Systemgrenze:** zwei elektrische MOSFETs verhindern **nicht** einen gemeinsamen Blitz-/Load-Dump-Schaden oder beschädigte gemeinsame Ansteuerung. Deshalb ist „sicherer als Relais“ ohne abgesicherte gemeinsame Fehlerquellen unbewiesen.

## 6. Nächster Schaltplan-Schritt – blockierende technische Gates

1. **G1 – System-Leistungsbudget:** benötigte Leistung/Strom der realen TFT-/LED-, GNSS, ESP32, SD-, 5-V-Geber- und USB-Zustände einschließlich Anlauf bestimmen. Stromlimit und Q601-Thermik daraus, nicht aus 2-A-Relaisvergangenheit ableiten.
2. **G2 – Fahrzeugschutz vor U401:** Norm-/Prüfprofil für 12/24 V, positive/negative Pulse, 36-V-Dauerbetrieb, suppressed/unsuppressed Load Dump. Daraus genau passende TVS, Reverse-FET, Fuses, PCB-GND-/ESD-Pfade dimensionieren. Keine generische SMCJ36A-Freigabe.
3. **G3 – Q401/Q402 und Q601:** richtige Datenblatt-/Pad-Pin-Belegung, SOA, rückwärts leitende Body-Dioden, Gate-Clamp und externe Treiber, Worst-Case-Temperatur und PCB-Copper; MOSFET-Hersteller-/Artikel-/LCSC/JLCPCB-Status nachprüfen.
4. **G4 – Bootstrap/Timer:** vollständige diskrete ACC-Pegelanpassung für 9–36 V, getrennte MCU-HOLD-Arming-/Timer-Logik, getrennte eFuse-SHDN/Q601-Control, Übergang ohne Lücke, USB-Blockierung. `01B` und `01C` dafür neu entwerfen, **nicht** unverändert übernehmen.
5. **G5 – S1-Ruhestrom:** per Rechnung mit maximalen Datenblattwerten, Temperatureinfluss, mit realem TVS/Gate-FET, ADC-Zweigen und danach **Strommessung** bei 9/12/24/36 V und heiß/kalt nachweisen. Bei Überschreitung S2 oder andere Controller erwägen.
6. **G6 – KiCad-Verifikation:** erst dann vollständige Unterseiten mit echten Netzen, Pin-/Pad-/SMD-Footprints/3D, BOM-Preisprüfungen, native KiCad-10-ERC/DRC und danach Labor-/Fahrzeugtests. `main` und die beiden Snapshot-Branches bleiben unverändert.

### Quellen und Messdaten

- [Texas Instruments TPS2663 Rev. G – technische Spezifikation, SHDN, OVP, UVLO, Blocking-FET, ILIM](https://www.ti.com/lit/ds/symlink/tps2663.pdf)
- [Texas Instruments TPS2663 HTML – elektrische Daten](https://www.ti.com/document-viewer/TPS2663/datasheet)
- [Texas Instruments TLC555-Q1 – Automotive LinCMOS Timer](https://www.ti.com/product/TLC555-Q1)
- [ROHM AG502EPD3HRTTL – Automotive –100-V-P-MOSFET](https://www.rohm.de/products/mosfets/automotive/single-pch/ag502epd3hrt-product)
- [ROHM AG501EPD3HRTTL – Automotive –100-V-P-MOSFET](https://www.rohm.com/products/mosfets/automotive/single-pch/ag501epd3hrt-product)
- [Bisherige Eingangsschutzstudie](INPUT_PROTECTION_DESIGN_REVIEW.md)
- [Verbindliche Hardwareanforderungen](HARDWARE_REQUIREMENTS.md)

**Prüfstatus:** Datenblattparameter und einfache Worst-Case-Rechnungen geprüft; keine Simulations-/Labor-/KiCad-10-Prüfung. **Kein fertiger Schaltplan, kein DRC/ERC-Bestehen, kein 12-/24-V-Fahrzeugbetrieb freigegeben.**
