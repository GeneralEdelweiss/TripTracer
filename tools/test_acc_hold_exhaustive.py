"""Bounded exhaustive test of the *logical* ACC/HOLD state machine.

Run: python3 tools/test_acc_hold_exhaustive.py
Tests 65,536 four-step traces of qualified ACC, MCU HOLD, vehicle-origin
5V and USB presence, with a 20 ms illustrative deadline. This is not
electrical/analog verification or an approved shutdown interval.
"""
from itertools import product
from test_acc_hold_state_machine import HoldController


def check_exhaustive():
    states = list(product((False, True), repeat=4))
    checked = 0
    for trace in product(states, repeat=4):
        controller = HoldController(max_hold_ms=20)
        off_locked = True
        for i, (acc, hold, vehicle_5v, usb_5v) in enumerate(trace):
            time_ms = i * 10
            enabled = controller.step(time_ms, acc=acc, hold=hold,
                                      vehicle_5v=vehicle_5v, usb_5v=usb_5v)
            if acc:
                off_locked = False
            elif (not hold or not vehicle_5v
                  or controller.deadline_ms is None
                  or time_ms >= controller.deadline_ms):
                off_locked = True

            expected = bool(acc or
                            (not off_locked and hold and vehicle_5v
                             and controller.deadline_ms is not None
                             and time_ms < controller.deadline_ms))
            assert enabled == expected, (trace, i, "unexpected enable")
            assert not (off_locked and enabled), (trace, i, "restarted while locked")
            if not acc:
                assert not (enabled and (not hold or not vehicle_5v)), (trace, i)
        checked += 1
    assert checked == 65536
    print(f"PASS: {checked} four-step logical ACC/HOLD traces")


if __name__ == "__main__":
    check_exhaustive()
