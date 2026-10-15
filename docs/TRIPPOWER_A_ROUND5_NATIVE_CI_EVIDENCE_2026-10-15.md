# TripPower Weg A — Runde 5: native Verifikation und reproduzierbare Gegenprobe (15.10.2026)

**Ziel:** `F_MAIN`-allein gegen herstellerreferenzierte unabhängige AP74502HQ-Hochvolt-Abschaltung, ohne aktive REV5-Änderung.

## Reale GitHub-Actions-Nachweise

- **Vollständiger erster erfolgreicher Round5-KiCad-10-Run**: https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38748812924 , SHA `c948d25f03ff622b471f8414a1879b3e1c1784f1`, Job `116469452560`, **completed / success**.
- GitHub-Joblogs von diesem Run: **`Ran 48 tests in 0.159s`**, viermal **`Found 0 violations`**, Netzlisten-Ergebnis **`native_pin_netlist_guard_match:true`**, **`changed_pin_count:31`**, **`new_populated_positions:12`**. Baseline, D306-Altprototyp, Q307-R342-Altprototyp und neuem AP74502HQ-Prototyp je **ein** nativer KiCad-10-ERC-Durchlauf ohne Violations. Hier sind **kein 200V-Puls-/125°C-/Fertigungs-Gate** eingeschlossen.
- **Folgelauf nach vollständiger Round5-Technikdokumentation:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38749234100 , SHA `a97c48efc33db10f2f291a6db0572e4cd110f9ae`, Job `116470923762`, **completed / success**; sämtliche CI-Stufen erfolgreich.
- Die eigenen frühen Fehlversuche im neuen Guard-Workflow sind ebenfalls dokumentierbar: Fehlende Projekt-Symbolbibliothek und nicht erregter `VIN`-power-input-Pin wurden durch die transportable `TripPower_AP74502.kicad_sym`, die `sym-lib-table`-Registrierung und ein **nicht zu bestückendes** Power-Feed-Flag korrigiert; die erste native Netlist-Differenzprüfung entdeckte anschließend eine **KiCad-interne unconnected-Pseudonetzliste von NC3**, keine echte zusätzliche Verdrahtung. Die Vergleichsfunktion ignoriert ausschließlich solche NC-Pseudonetze und prüft die echten Daten, während physische Fremdverbindungen weiterhin zum Testabbruch führen.

## Erwartete Netzlistendifferenz in Worten

- Q301 D2: `VIN_FUSED` → `VIN_A_GUARD_OUT`.
- Q401 D2=`VIN_FUSED`, S3=`VIN_A_GUARD_OUT`, G1=`AP_HVGATE`. Im OFF-Zustand sperrt Bodydiode die Richtung `VIN_FUSED→VIN_A_GUARD_OUT`.
- U401 Pin1 EN=`AP_VIN_CLAMP`, Pin2 GND, Pin3 NC, Pin4 VCAP=`AP_VCAP`, Pin5 VIN=`AP_VIN_CLAMP`, Pin6 GATE=`AP_HVGATE`, Pin7 OVLO=`AP_OV_SENSE`, Pin8 SRC=`VIN_A_GUARD_OUT`.
- R401–403 mit 56-V-D401 an `AP_VIN_CLAMP`; R404–406 mit R407 an `AP_OV_SENSE`; C401 nach GND/C402 zwischen VCAP und VIN. Zusammen **12 neue bestückte Positionen** (69 AUTO /70 RUN); `#FLG401` ist **kein** Bauteil der Produktionsstückliste.
- Original-/A-Baseline-Teilewerte und 57/58-Bestückzählung unverändert.

## Nicht geschlossene Stop-Gates

- **Der bedeutendste neue Datenblattkonflikt:** Diodes AP74502HQ Table Absolute Ratings: für **VIN>0 gilt SRC ≤ VIN**. Im ideellen 9V-Sensitivitätsfall fällt AP-VIN durch den 9,9k-HV-Zweig tiefer als Q401-SRC. Daher ist auch trotz des erfolgreichen ERC **ein absoluter Datenblattwert gefährdet**. **Keine** Freigabe der Schaltung vor bestätigter Herstellerlösung, D302-/Supervisor-/Startdynamik und echten VIN/SRC-Wellenformen.
- Externe Mersen `A6Y3-1` 3A/500VDC ist kein nachgewiesener Schutz gegen hochohmigen 200V-/350ms-Fehler, F_MAIN für Kabelschutz bleibt notwendig, Halter/I²t/hot offen.
- Diodes AP 1µs-max-Gateabschaltung nur unter Herstellerlast, nicht für Q401-250V/realer Qg+125°C; Q401-Hot-SOA, D401/OV-VS 200V/350ms, Quellimpedanz, F_MAIN DC-I²t, komplette 9V/30V-Funktionsdynamik, PCB-Kriechstrecken und DRC offen.
- **Kein PCB vorhanden**; kein KiCad-PCB-DRC möglich. Erfolg der KiCad-Netzliste bedeutet **nur** Pin-Topologie und ERC-Kohärenz, nicht elektrische/thermische Schutzgarantie.

**Reproduzierbar:** `python3 tools/trippower_a_architecture_decision.py`; `python3 -m unittest discover -s tools -p 'test_trippower_a_*.py' -v`; CI-Datei `.github/workflows/trippower-a-verification.yml` und `tools/check_trippower_a_guard_netlist.py`.

**Architekturvergleich/Entscheid:** `hardware/modules/TripPower_5V2A/WEG_A_ROUND5_FMAIN_VS_AP74502_SYSTEM_DECISION_2026-10-15.md`.

**Status:** Weg B/C nicht angerührt. Fertigung und Fahrzeuge **NICHT** freigegeben.
