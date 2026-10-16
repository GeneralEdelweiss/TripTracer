"""TripTracer ACC/HOLD executable behavioral contract (NOT an electrical simulation).

Run: python3 tools/test_acc_hold_state_machine.py
The 30 s deadline is a test fixture, not an approved hardware setting.
Inputs acc and vehicle_5v represent *qualified* signals. Real debounce,
latch retention, power-up, negative pulses and battery loss are unproven.
"""
from dataclasses import dataclass


@dataclass
class HoldController:
    max_hold_ms: int = 30000
    acc: bool = False
    deadline_ms: int | None = None
    shutdown_latched: bool = True
    last_ms: int = -1

    def step(self, now_ms: int, *, acc: bool, hold: bool,
             vehicle_5v: bool, usb_5v: bool = False) -> bool:
        """Return requested vehicle main-enable. USB cannot qualify HOLD."""
        if now_ms < self.last_ms or now_ms < 0:
            raise ValueError("time must be monotonic and nonnegative")
        self.last_ms = now_ms
        was_acc = self.acc
        self.acc = acc

        if acc:
            self.deadline_ms = None
            self.shutdown_latched = False
            return True  # ACC must bootstrap independently of vehicle 5V

        if was_acc:
            self.deadline_ms = now_ms + self.max_hold_ms
            # Real hardware must atomically transition ACC direct drive to
            # hold drive; this model does not prove glitch-free transfer.

        window = self.deadline_ms is not None and now_ms < self.deadline_ms
        if not window or not hold or not vehicle_5v:
            self.shutdown_latched = True
        return bool(window and not self.shutdown_latched and hold and vehicle_5v)


def check():
    # Normal shutdown and permanent stuck-HIGH GPIO.
    m = HoldController()
    assert not m.step(0, acc=False, hold=True, vehicle_5v=False, usb_5v=True)
    assert m.step(100, acc=True, hold=False, vehicle_5v=False)
    assert m.step(101, acc=True, hold=True, vehicle_5v=True)
    assert m.step(200, acc=False, hold=True, vehicle_5v=True)
    assert m.step(30199, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(30200, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(90000, acc=False, hold=True, vehicle_5v=True)

    # New qualified ACC high permits exactly a new cycle.
    assert m.step(91000, acc=True, hold=False, vehicle_5v=False)
    assert m.step(91100, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(91101, acc=False, hold=False, vehicle_5v=True)
    # Critical fix: HOLD must not resurrect main power before deadline.
    assert not m.step(91102, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(91103, acc=False, hold=True, vehicle_5v=True, usb_5v=True)

    # Vehicle-derived power loss is terminal for that ACC-off cycle.
    m = HoldController()
    assert m.step(0, acc=True, hold=True, vehicle_5v=True)
    assert m.step(100, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(101, acc=False, hold=True, vehicle_5v=False, usb_5v=True)
    assert not m.step(102, acc=False, hold=True, vehicle_5v=True)
    assert m.step(200, acc=True, hold=False, vehicle_5v=False)

    # ACC falling while vehicle rail is not established cannot bootstrap HOLD.
    m = HoldController()
    assert m.step(0, acc=True, hold=False, vehicle_5v=False)
    assert not m.step(100, acc=False, hold=True, vehicle_5v=False)
    assert not m.step(101, acc=False, hold=True, vehicle_5v=True)

    try:
        m.step(99, acc=False, hold=False, vehicle_5v=False)
        raise AssertionError("time regression accepted")
    except ValueError:
        pass

    print("PASS: timeout, USB isolation, latching shutdown, power loss, restart")


if __name__ == "__main__":
    check()
