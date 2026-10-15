# TripPower REV3 – nächster Prüfschritt: 9-V-Kaltstart und 12-V-Bordnetz (15.10.2026)

**Entscheidung:** Keine weiteren experimentellen Umbauten der Eingangsschutzstufe ohne Mess-/Herstellerbeleg. REV3 mit R330=715k und C311=220nF bleibt aktive KiCad-Prototypvariante; Kaltstart, Serien-/Fahrzeugfestigkeit und PCB-Design **nicht freigegeben**. Vorrang: **9 V am VIN_FUSED-Moduleingang**, 12–13,8 V Nennbordnetz, 24–30 V nachgelagert. Bei <9 V darf die Versorgung geordnet ausfallen/restarten; Fahrzeug-Transienten-/Sicherheit müssen separat geprüft werden.

## 1. Neue TI-Erkenntnis – C311=220nF ist nicht garantiert 280ms

**Primärquelle:** [TI TPS3760-Q1 Rev.B](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf), Tabelle 6.5 (RCTR intern **877/1000/1147 kΩ min/typ/max**) und §7.3.4.1, Gl. (1)–(3):

- `tCTR,typ = -ln(0.28) * RCTR,typ * C311,typ + tCTR(open)`;
- `tCTR,min = -ln(0.31) * RCTR,min * C311,min + tCTR(open,min)`;
- `tCTR,max = -ln(0.25) * RCTR,max * C311,max + tCTR(open,max)`.

**Nur Sensitivität unter BAUTEILANNAHMEN:** nominal C311=220nF, beispielhafte Erstwerttoleranz ±10 % und zusätzliche X7R-Temperaturabweichung ±15 % als unabhängige Multiplikation. Offset ohne externen C (typ 40µs) ist gegenüber Hunderten ms unwesentlich und bei der min/max-Rechnung zugunsten eines konservativen Null-Offsets weggelassen.

| angenommener Fall | Formel | Ergebnis |
|---|---|---:|
| Frisch nominal | `-ln(.28) * 1000k * 220nF` | **280,1 ms** |
| Frühestmöglich in angenommenem R-/C-Fenster | `-ln(.31) * 877k * (220nF*.9*.85)` | **172,9 ms** |
| Spätest in angenommenem R-/C-Fenster | `-ln(.25) * 1147k * (220nF*1.1*1.15)` | **442,5 ms** |

**Wichtig:** C311 hat in KiCad aktuell **MPN_PENDING**; wir haben darum noch keinen tatsächlichen Hersteller-Cmin- oder Leckstrom-/Alterungs-/DC-Bias-Nachweis. Diese 172,9–442,5ms sind **kein garantierter Zeitbereich** der realen Platine und dürfen nicht als 9V-Startfreigabe benutzt werden. Bei erneutem Einschalten nach kurzer Unterbrechung kann C311 Restladung tragen: TI weist explizit auf **kürzere Reset-Verzögerung** bei unvollständiger Entladung hin. Erste Freigabeverzögerung ist nicht dieselbe wie Wiederanlauf.

## 2. Was der vorhandene VS-Puffer unter Annahmen schafft

Wenn **VIN_FUSED=9.0V**, die illustrative **OFF-Gesamtlast 34,6µA**, nominal **Ceff(C302+C308)=11µF**, RVS=9,9kΩ und die *obere hypothetische* REV3-Einschaltschwelle 7,510V zusammen gelten, erreicht VS nach **172,9ms** Reset-Freigabezeit näherungsweise **8,42V**, nicht 8,55V (letzterer Wert gilt für etwa 280ms und nominale Schwelle). Damit stehen bis zur **6-V-Untergrenze, bei der TI den CAP-Quellstrom prüft**, 2,42V Differenz zur Verfügung.

Nur als Sensitivität für hypothetische Ceff=8,5µF und CAP-Ladezeit 3,031ms gilt bei **fehlender RVS-Nachladung**: `I_average_ohne_Nachladung ≤ 8,5µF*(8,42−6V)/3,031ms ≈ 6,8mA`. **Weder 8,5µF bei allen Temperaturen noch die realen 3,031ms oder die dynamische VS-Last sind garantiert.** Der Hersteller-CAP-Ausgangsstrom von 1,3/2,7mA darf nicht als VS-Eingangsstrom eingesetzt werden.

TI [LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf) §7.3.1: EN LOW schaltet die Pumpe aus. Das Einschalten erfolgt über CAP-VS-Schwelle typ6,6V, max7,9V, danach wird HGATE freigegeben. Die D302 A→VS-Nachladung **setzt das Einsetzen einer Source-Spannung durch Gate-Freigabe voraus**.

## 3. Entscheidende A/B-Laborprüfung – vor weiteren PCB-Umbauten

**Einmaliger Minimalaufbau:** TI [LM74930Q1EVM](https://www.ti.com/tool/LM74930Q1EVM), oder elektrisch gleichwertiger abgesicherter Aufbau. Das EVM enthält den 10kΩ-VS-Pfad und die A→VS-Diode, zeigt laut [SLUUCW6](https://www.ti.com/lit/pdf/sluucw6) einen 12V-Start, nicht eine 9V-Garantie. **EVM ohne unsere TPS3760-/Q303-Stufe ist keine vollständige REV3-Funktionsprüfung.**

**Stufe A: Controller isolieren und 9V-Bootstrap identifizieren.** VIN am Prüfling 13,8V →12V→9V; Kaltstart mit entladenem VS/CAP; kontrolliertes EN ohne hochspannungsgefährdende Überbrückung; unter wenig oder keiner Ausgangslast. Mindestens Oszilloskop-Kanäle:
- `VIN_FUSED` am Modul, `VS_CLAMP`, `CTRL_EN`;
- Differenz `CAP_PUMP - VS_CLAMP`, `HGATE - SOURCE_A`;
- `SOURCE_A`, `VIN_PROTECTED_UNFUSED`, `5V_OUT`, Eingangsstrom.
- Den **dynamischen VS-Pinstrom**, falls benötigt, über einen Messtaster/Shunt **im isolierten IC-VS-Zweig** erfassen, nicht fälschlich durch einen Shunt vor allen VS-Kondensatoren; D302 sowie C308 bilden Parallel-/Speicherpfade.

**Stufe B: volle REV3-Logik.** Die gleichen 9/12/13,8V Versuche mit C311220nF, R330715k, Q303–Q305, R319 AUTO und RUN_CMD separat, zuerst 5V unbelastet, dann 0,5A, dann 2A; anschließend AUX 1A unter gegebenem, extern abgesichertem Gesamtstrom. WICHTIG: Dass die Ausgangsspannung ohne Last ansteigt, reicht nicht als 2-A-Nachweis.

**Stufe C: Eingangsdynamik und Worst-Case:** 9→12→9V, langsame Spannungsrampe, schnelle Unterbrechung und Wiedereinschalten **inkl. unvollständig entladenem C311**, sowie OFF-Betrieb / RUN-HIGH während VIN=0. Danach Temperaturpunkte −40/25/85/125°C und Gate-/Schaltverlust unter 5V2A + AUX. 202V/350ms Lastabwurf / Q301-SOA, F_MAIN/I²t und Kurzschluss **sind ein eigener späterer qualifizierter Test**, nicht EVM-Bastelversuch.

**Zu prüfende Grenzwerte:**
- `VEN_ON ≥1,05V`, `VEN_OFF ≤0,41V` (TI-Grenzen);
- `VS ≥6V` **während der für den Start entscheidenden CAP-Ladungsphase** als konservativer Engineering-Test für TI spezifizierte CAP-Quellstrombedingungen; außerhalb dieser Phase VS dauerhaft im erlaubten 4–65V-Bereich;
- `CAP−VS` erreicht die tatsächliche HGATE-Freigabeschwelle, `HGATE` schaltet nachvollziehbar und `SOURCE_A` lädt danach VS über D302 nach;
- 5V-Output bei gewählten Lastfällen ohne unerwartete Neustartfolge; zusätzlich Grenzwerte für 5V-Regulation, Ripple und Temperatur vor Endabnahme verbindlich aus Datenblatt/Modulvertrag definieren;
- keine USB/RUN→VS-Rückspeisung, Hot-OFF-Bias <0,41V, VIN_FUSED ≥9V **direkt am Modul unter Last**, keine thermischen Überschreitungen.

**Diagnose/Entscheidung:**
1. `VS` erreicht vor RESET-Freigabe nicht sicher 7,510V → RVS-Vorladelast, C308-Leck/Temperatur oder Supervisor-Freigabeschwelle kritisch; zuerst tatsächlichen Ioff/Ceff bestimmen.
2. `VS` lädt vorab, aber `EN` bleibt <1,05V → REV3 NPN/PNP-Basis-/Temperatur-Problem; **gezielt qualifizierten Enable-Treiber statt weiterer RC-Kunstgriffe**.
3. `EN` wird HIGH, `CAP−VS` steigt nicht bzw. VS kollabiert → LM74930-Startenergie; erst **dann** eine 202V-feste VS-Startstromquelle oder andere COTS-Topologie dimensionieren.
4. `HGATE` und `SOURCE_A` arbeiten, aber 5V fehlt → LMR38020/UVLO/Buck-Inrush/OCP prüfen.
5. Kaltstart gelingt, schneller Neustart nicht → C311-Restladung, RESET-Wiederanlauf und VS-Dynamik gezielt qualifizieren.

## 4. Kosten-/Konstruktions-Entscheid für die nächste Revision

- **Jetzt keine C311- oder RVS-Blindänderung.** Zuerst C311 konkrete AEC-Q200-1206-MPN inkl. garantierter Cmin/Cmax, Temperatur, Alterung und Leck festlegen. Bei einer beispielhaft 330-nF-Kapazität ergäbe derselbe **nicht garantierte** min-CTR-Fall ca. 259ms statt 173ms, aber zusätzliche Verzögerung ersetzt keinen Nachweis für I(VS,t) oder den Wiederanlauf.
- Eine einzige reproduzierbare 9V-/12V-EVM/REV3-Messreihe spart mehr Entwicklungsrisiko als ein weiterer unbewiesener FET-/Supervisor-Umbau. Wenn kein echter REV3-Testaufbau verfügbar ist, entweder ein minimal geroutetes und mit zugänglichen Testpunkten versehenes Prototyp-PCB (keine Serienfreigabe) erstellen oder zunächst den Hersteller um ein gültiges Worst-Case-I(VS,t)-Profil bitten.
- **Blocker weiterhin**: Q303 OFF-IC_E bei +125°C, Q304/Q303 hFE_min im µA-Bereich −40…125°C, 9V VS-Pumpenstart, 202V/350ms, Sicherung/Fault-I²t, 2A Thermik und physischer PCB DRC.

**Rechencheck:** `tools/check_trippower_rev3_12v_startup.py` berechnet die konditionale CTR-Streuung und VS-Sensitivität unter expliziten Annahmen. Native KiCad-10-ERC/Netzliste und Reports über GitHub Actions erneut prüfen.
