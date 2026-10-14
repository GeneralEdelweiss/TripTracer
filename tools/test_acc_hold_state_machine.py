"""TripTracer ACC/HOLD *behavioral specification*, not an electrical simulation.

Run: python3 tools/test_acc_hold_state_machine.py
No external packages. Does not prove timer, bootstrap, leakage or transient behavior.
"""
from dataclasses import dataclass

@dataclass
class HoldController:
    max_hold_ms: int = 30000  # TEST VALUE ONLY; not a hardware requirement
    acc: bool = False
    deadline_ms: int | None = None
    vehicle_5v: bool = False

    def step(self, now_ms: int, *, acc: bool, hold: bool, vehicle_5v: bool, usb_5v: bool = False) -> bool:
        """Return requested vehicle power-enable; USB is deliberately not a power source."""
        if now_ms < 0:
            raise ValueError("negative simulation timestamp")
        was_acc = self.acc
        self.acc = acc
        self.vehicle_5v = vehicle_5v
        if acc:
            self.deadline_ms = None
            return True  # bootstraps independently of MCU and vehicle-derived 5V
        if was_acc:
            self.deadline_ms = now_ms + self.max_hold_ms
        active_window = self.deadline_ms is not None and now_ms < self.deadline_ms
        return bool(active_window and hold and vehicle_5v)

def check():
    m = HoldController(max_hold_ms=30000)
    assert not m.step(0, acc=False, hold=True, vehicle_5v=False, usb_5v=True), "USB-only enabled vehicle"
    assert m.step(100, acc=True, hold=False, vehicle_5v=False), "ACC boot depends on buck"
    assert m.step(101, acc=True, hold=True, vehicle_5v=True)
    assert m.step(200, acc=False, hold=True, vehicle_5v=True)
    assert m.step(30199, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(30200, acc=False, hold=True, vehicle_5v=True), "stuck HOLD exceeded deadline"
    assert not m.step(90000, acc=False, hold=True, vehicle_5v=True), "HOLD retriggered after deadline"
    assert m.step(91000, acc=True, hold=False, vehicle_5v=False), "genuine ACC rearm failed"
    assert m.step(91100, acc=False, hold=True, vehicle_5v=True)
    assert not m.step(91101, acc=False, hold=False, vehicle_5v=True), "MCU release did not shut down"

    m = HoldController(max_hold_ms=30000)
    assert m.step(0, acc=True, hold=False, vehicle_5v=False)
    assert not m.step(100, acc=False, hold=True, vehicle_5v=False), "HOLD without vehicle rail"
    assert not m.step(101, acc=False, hold=True, vehicle_5v=False, usb_5v=True)
    assert m.step(102, acc=False, hold=True, vehicle_5v=True), "vehicle rail qualification failed"
    assert not m.step(30100, acc=False, hold=True, vehicle_5v=True)
    print("PASS: behavioral ACC/HOLD transitions, stuck-HOLD timeout, USB isolation and re-arm")

if __name__ == "__main__":
    check()
