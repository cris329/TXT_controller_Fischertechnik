# -*- coding: utf-8 -*-
"""Unit tests for multi-port servo kick."""

from __future__ import print_function

import sys
import types
import time


def _install_ft_stubs():
    """Install fake ft / ftlock for offline tests.

    @return: list of (servo_index, kind, value)
    """
    calls = []

    class FakeServo(object):
        def __init__(self, index):
            self.index = index
            self.pwm = 0

        def setLevelUs(self, us):
            calls.append((self.index, "us", int(us)))

        def setLevel(self, level):
            calls.append((self.index, "level", int(level)))
            self.pwm = int(level)

        def pwm_set(self, level):
            calls.append((self.index, "pwm", int(level)))
            self.pwm = int(level)

    servos = {i: FakeServo(i) for i in range(1, 4)}

    class FakeTxt(object):
        def motor(self, i):
            return types.SimpleNamespace(setSpeed=lambda s: None)

        def servo(self, i):
            return servos[i]

        def close(self):
            return None

    sys.modules["ft"] = types.ModuleType("ft")
    sys.modules["ft"].fttxt2 = lambda mode: FakeTxt()
    sys.modules["ftlock"] = types.ModuleType("ftlock")
    sys.modules["ftlock"].notify = lambda state: None
    return calls


def test_kick_pulses_all_three_servos():
    """Happy: S1 S2 S3 all receive shot level 400."""
    calls = _install_ft_stubs()
    if "robot.hardware" in sys.modules:
        del sys.modules["robot.hardware"]
    from robot.hardware import RobotHardware

    hw = RobotHardware()
    calls[:] = []
    hw.kick()
    time.sleep(0.9)
    for idx in (1, 2, 3):
        levels = [c[2] for c in calls if c[0] == idx and c[1] == "level"]
        assert 400 in levels
        assert 250 in levels


def test_kick_busy_ignored():
    """Edge: overlapping kick does not stack."""
    calls = _install_ft_stubs()
    if "robot.hardware" in sys.modules:
        del sys.modules["robot.hardware"]
    from robot.hardware import RobotHardware

    hw = RobotHardware()
    calls[:] = []
    hw.kick()
    hw.kick()
    time.sleep(0.95)
    shots = [c for c in calls if c[1] == "level" and c[2] == 400]
    # one shot per servo port
    assert len(shots) == 3
