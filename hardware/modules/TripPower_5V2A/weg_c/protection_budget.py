#!/usr/bin/env python3
"""TripPower-C conservative *screening calculations*; not hardware certification.

Pure stdlib, reproducible: python3 protection_budget.py; python3 -m unittest protection_budget.py
Unit-test assertions catch known mistakes, but NONE of them constitute a load-dump pass.
"""
from dataclasses import dataclass
import math
import unittest

VIN_MIN = 9.0
VIN_MAX = 30.0
V_SURGE = 200.0
T_SURGE = 0.350
V_ZENER_ASSUMED = 60.0   # analytical example only, not a selected TVS guaranteed clamp
R_VIN_FEED = 10200.0
VOUT = 5.0
IOUT = 2.0
I_RAW = 1.0
EFFICIENCY_ASSUMED = 0.90
MOSFET_RDS_MAX_25C = 0.097  # SQM35N30-97, 300V, 97mOhm maximum at VGS=10V
FET_COUNT = 2
FET_TJ_MAX = 175.0
BUCK_TJ_MAX = 150.0
TA_MAX = 125.0
OVLO_RTOP = 1_000_000.0
OVLO_RBOT = 39_000.0
OVLO_REFERENCE_TYP = 1.24
AP_SHUTDOWN_MAX = 1.5e-6   # VIN pin, per AP datasheet
AP_EN_SINK_MAX = 5e-6      # may cause relevant voltage divider offsets


@dataclass(frozen=True)
class Conditions:
    vin: float = VIN_MIN
    efficiency: float = EFFICIENCY_ASSUMED
    raw_current: float = I_RAW


def input_current(c: Conditions):
    if not 0 < c.efficiency <= 1:
        raise ValueError("Efficiency outside 0..1")
    return VOUT * IOUT / (c.vin * c.efficiency) + c.raw_current


def mosfet_loss(c: Conditions, rds_multiplier=1.0):
    current = input_current(c)
    return FET_COUNT * current * current * MOSFET_RDS_MAX_25C * rds_multiplier


def feed_pulse():
    current = (V_SURGE - V_ZENER_ASSUMED) / R_VIN_FEED
    return {
        "current_A": current,
        "resistor_peak_W": (V_SURGE - V_ZENER_ASSUMED)**2 / R_VIN_FEED,
        "resistor_energy_J": (V_SURGE - V_ZENER_ASSUMED)**2 / R_VIN_FEED * T_SURGE,
        "zener_peak_W": V_ZENER_ASSUMED * current,
        "zener_energy_J": V_ZENER_ASSUMED * current * T_SURGE,
    }


def ovlo_levels():
    divider_fraction = OVLO_RBOT / (OVLO_RTOP + OVLO_RBOT)
    return {
        "ovlo_rising_nominal_input_V": OVLO_REFERENCE_TYP / divider_fraction,
        "divider_current_30V_uA": VIN_MAX / (OVLO_RTOP + OVLO_RBOT) * 1e6,
        "ovlo_pin_at_200V": V_SURGE * divider_fraction,
        # Leakage into or out of comparator input has to be substituted from full datasheet.
        "per_1uA_input_leakage_threshold_shift_V": 1e-6 * OVLO_RTOP,
    }


def max_allowed_theta_c_per_w(power_W, ambient=TA_MAX, junction=BUCK_TJ_MAX):
    """Derating upper bound, not a claim that a physical PCB has this theta."""
    return (junction - ambient) / power_W


def buck_loss_at_efficiency(efficiency):
    return VOUT * IOUT * (1 / efficiency - 1)


class ProtectionBudgetUnitTests(unittest.TestCase):
    def test_spec_pulse_is_200_not_202(self):
        self.assertEqual(V_SURGE, 200.0)
        self.assertAlmostEqual(T_SURGE, 0.350)

    def test_9V_plus_raw_does_not_get_missed(self):
        self.assertGreater(input_current(Conditions()), 2.2)
        self.assertLess(input_current(Conditions()), 2.4)

    def test_inrush_not_always_equal_normal_current(self):
        self.assertGreater(mosfet_loss(Conditions(), 1.8), 1.7)

    def test_feed_resistor_pulse_budget(self):
        x = feed_pulse()
        self.assertAlmostEqual(x["resistor_energy_J"], 0.67255, places=4)
        self.assertAlmostEqual(x["zener_energy_J"], 0.288235, places=4)
        self.assertAlmostEqual(x["resistor_peak_W"], 1.9215686, places=4)

    def test_ovlo_nominal_above_30(self):
        self.assertGreater(ovlo_levels()["ovlo_rising_nominal_input_V"], 30.0)
        self.assertLess(ovlo_levels()["ovlo_rising_nominal_input_V"], 36.0)

    def test_high_hot_board_thermal_not_automatically_safe(self):
        p = buck_loss_at_efficiency(0.90)
        self.assertAlmostEqual(p, 10/0.9-10)
        self.assertLess(max_allowed_theta_c_per_w(p), 25.0)

    def test_undocumented_ovlo_leakage_is_material(self):
        self.assertGreaterEqual(ovlo_levels()["per_1uA_input_leakage_threshold_shift_V"], 1.0)


def report():
    c = Conditions()
    x = feed_pulse()
    o = ovlo_levels()
    print("TRIPPOWER WEG C - RECHEN-SCREENING; NO CERTIFICATION")
    print("INPUT 9V, 5V/2A + RAW/1A: %.3f A at eta=90%%" % input_current(c))
    print("Q1+Q2 97mOhm each at 25C: %.3f W; hot x1.8: %.3f W" %
          (mosfet_loss(c), mosfet_loss(c, 1.8)))
    print("200V/350ms, 60V analytical clamp, 10.2k feed: R %.2fW / %.3fJ, clamp %.2fW / %.3fJ" %
          (x["resistor_peak_W"], x["resistor_energy_J"], x["zener_peak_W"], x["zener_energy_J"]))
    print("OVLO 1M/39k (nominal reference): rising %.2fV, 30V I %.2fuA, pin@200V %.2fV" %
          (o["ovlo_rising_nominal_input_V"], o["divider_current_30V_uA"], o["ovlo_pin_at_200V"]))
    print("OVLO 1uA leakage changes threshold by %.2fV; actual datasheet leakage +/- and tolerance required" %
          o["per_1uA_input_leakage_threshold_shift_V"])
    for eta in (0.85, 0.90, 0.93):
        p = buck_loss_at_efficiency(eta)
        print("BUCK 10W eta=%.0f%%: loss=%.3fW; theta_JA must <=%.1f C/W at 125C ambient, max 150C junction" %
              (eta * 100, p, max_allowed_theta_c_per_w(p)))
    print("BLOCKED: component pulse curve, HV FET SOA/thermal, full VIN waveform, TVS, native KiCad checks, ISO lab.")


if __name__ == "__main__":
    report()
