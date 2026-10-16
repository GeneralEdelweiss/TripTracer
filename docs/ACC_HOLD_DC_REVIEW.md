# Relaislose ACC/HOLD-Freigabe: DC-Entwurfsprüfung

Stand 13.10.2026. **Ergebnis: zwei untersuchte Kandidaten noch nicht geeignet zur Übernahme in den aktiven Strompfad.** Keine Bauteilbestellung, keine neue KiCad-Seite, keine Änderung an bestehenden Schutzfunktionen. Die Variante C bleibt das Entwicklungsziel.

## Untersuchte Schaltung

Ein NMOS Q_KILL hält LM74930_EN standardmäßig auf GND. R_KILL (330k) zieht sein Gate aus der geschützten VS-Versorgung hoch; eine vorläufige 4,7-V-Zenerdiode begrenzt die Gatespannung. ACC zieht dieses Gate über Q_ACC herunter und erlaubt EN. Alternativ können zwei NMOS in Serie das Gate herunterziehen: einer von MCU_HOLD, der zweite ausschließlich von **V5_BUCK_RAW vor dem USB-Power-Path**. Damit lautet die gewünschte Logik ACC ODER (HOLD UND Fahrzeug-5-V-vorhanden). USB-System-5-V dürfen den Qualifikationszweig nicht speisen. Die Schaltung ist noch nicht im KiCad-Root integriert.

ACC-Gate: zwei 220k in Serie, 1M gegen GND und vorläufige 4,7-V-Zenerdiode. HOLD-Gate: 10k/100k; Qualifikations-Gate: 33k/100k aus V5_BUCK_RAW. EN-Pull-up aus VS: zuerst 4,7M, beim zweiten Kandidaten 680k. Kondensatoren EN 10n und KILL_GATE 1n sind im DC-Modell wirkungslos; ihre Einschaltsequenz wurde **nicht simuliert**.

## Tatsächlicher Simulationsumfang

`tools/simulate_acc_hold_candidate.py` nutzt eine installierte ngspice-Bibliothek über deren C-API. 96 DC-Arbeitspunkte: alle acht ACC/HOLD/Fahrzeug-5-V-Kombinationen bei 6/9/30 V, jeweils vier Modellprofile. Der Lauf erzeugte 96 auswertbare DC-Ergebnisse ohne Simulatorfehler. Rohdaten, Log und ein reproduzierbares USB-only-Beispiel liegen in `docs/validation/2026-10-13-acc-hold/`.

**Eigene vereinfachte MOS-Level-1-Modelle; keine Hersteller-MOS-Modelle und kein LM74930-/Buck-Modell.** Modell-VTO/KP sind transparente Annahmen, keine Datenblattkurvenanpassung. Die Zenerdiode hat ein generisches Durchbruchmodell; reale Knie-/Temperaturwerte fehlen. Die 3,3-V-GPIO- und 5-V-Signale sind ideale Spannungsquellen; keine Last-/Startup-Rückkopplung.

TI spezifiziert EN steigend maximal 1,05 V, fallend minimal 0,41 V sowie bis 200 nA EN-Eingangsstrom. Diese Grenzen bilden die DC-Auswertekriterien; das ist kein Modell des vollständigen Controllers. Quelle: [TI LM74930-Q1, elektrische Eigenschaften](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf).

| Profil | Arbeitspunkte | Modell-Logikkriterien verletzt | Konsequenz |
|---|---:|---:|---|
| Q_KILL nominal, EN-Pull-up 4,7M | 24 | 0 | Nur vereinfachte DC-Logik funktioniert |
| Q_KILL mit BSS123-Sperrstrom-Stress, EN-Pull-up 4,7M | 24 | 15 | Sämtliche gewünschte ON-Zustände erreichen EN-HIGH nicht |
| Alternativer Q_KILL, nominal, EN-Pull-up 680k | 24 | 0 | DC-Logik funktioniert im Modell |
| Alternativer Q_KILL mit BSS131-Sperrstrom-Stress, EN-Pull-up 680k | 24 | 0 | Logik im Modell verbessert, Ruhestromziel weiterhin verletzt |

## Temperatur-/Sperrstromquellen und Grenzen

[onsemi BSS123, Rev. 12](https://www.onsemi.com/download/data-sheet/pdf/bss123-d.pdf) nennt maximal 60 µA Drain-Sperrstrom bei 125 °C und 100 V. Die 4,7M-Pull-up-Quelle liefert bei 6 V nur etwa 1,28 µA: ein solcher Sperrstrom kann EN unten halten. Im entsprechenden Stressfall ACC EIN bei 6 V ergibt sich EN etwa **2,12 mV** statt mehr als 1,05 V. Der eingesetzte Stressstrom bei niedrigem VDS ist konservativ, keine exakte Temperaturkennlinie. BSS123-G ist dort als abgekündigt aufgeführt; eine beliebige Typbezeichnung allein ist keine Beschaffungsentscheidung.

[onsemi BSS138, Rev. 7](https://www.onsemi.com/download/data-sheet/pdf/bss138-d.pdf) nennt 5 µA maximal bei 125 °C/50 V. Dieser Wert wird als separates Stress-Szenario für Q_ACC/Q_HOLD/Q_QUAL verwendet. Deren normale Drainspannungen sind wesentlich niedriger. Er darf nicht als garantierter 150-°C-Wert umetikettiert werden. Die aufgeführten Schwell-/RDS(on)-Angaben ersetzen keinen Nachweis bei minimaler GPIO-HIGH-Spannung und Kälte.

[Infineon BSS131, Rev. 2.6](https://www.infineon.com/assets/row/public/documents/24/49/infineon-bss131-ds-en.pdf) nennt maximal 5 µA bei 150 °C/240 V; [Herstellerproduktseite](https://www.infineon.com/part/BSS131) führt BSS131H6327XTSA1 als aktiv. Im Alternativprofil werden 5 µA für Q_KILL und 680k für EN untersucht. Die anderen MOS-Stresswerte bleiben 125-°C-Szenarien: **kein vollständiger gemeinsamer Temperatureckwert** und keine festgelegte Serien-BOM.

## Ruhestrom: beide Modelle liefern noch keinen Nachweis

Bei 30 V und ACC AUS / HOLD AUS zieht die erste Schaltung bereits etwa **82,90 µA aus VS**, ohne LM74930-Shutdown-Strom, TVS, VS-Zener, weitere Messzweige oder PCB-Leckstrom. Der zweite Kandidat zieht etwa **120,63 µA allein für diese Bias-Schaltung**, überschreitet also schon das gesamte 100-µA-OFF-Ziel. Eine verbesserte EN-Ansteuerung oder eine anders dimensionierte diskrete Selbsthaltung ist erforderlich. Das Ziel wird nicht stillschweigend erhöht.

USB-only-HOLD bei fehlendem V5_BUCK_RAW bleibt in allen untersuchten DC-Profilen AUS. Das bestätigt nur diese idealisierten Arbeitspunkte; reale USB-Rückspeisung, Power-Path-Fehler, Kapazitätskopplung und Qualifikationsschwelle bleiben zu prüfen. Verlust von V5_BUCK_RAW unter Last kann die Selbsthaltung beenden; Betriebsübergänge brauchen eine Transientenprüfung.

Offen: besserer Bias-/Sperrstromkompromiss, tatsächliche Zener-Kniekurven, 6-V-Bootstrap mit VS-Vorwiderstand, BAT-Anstecken/ACC-Flanken, MCU-GPIO-Minimalpegel, USB-Power-Path, sicheres Reset des Controller-Latch-Off, Abschaltdeadline bei festhängendem HOLD, Pulsfestigkeit der ACC-Widerstände und Temperatur. Kosten **NICHT BELASTBAR**: vier diskrete MOSFETs plus passive Teile werden untersucht; exakte MPNs, deutsche Lieferbarkeit, Warenkorb und Montagekosten noch nicht festgelegt. Keine zusätzlichen Controller oder neuen Funktionen beschlossen.
