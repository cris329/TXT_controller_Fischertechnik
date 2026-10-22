# -*- coding: utf-8 -*-
"""Probe which servo API actually moves S1."""
from __future__ import print_function
import time

import ft
import ftlock


def try_call(label, fn):
    """Call servo method and report result.

    @param label: str
    @param fn: callable
    @return: None
    """
    try:
        fn()
        print(label, "ok")
    except Exception as exc:
        print(label, "ERR", type(exc).__name__, exc)


def main():
    """Try setLevelUs / pwm_set_us kick motion.

    @return: None
    """
    ftlock.notify("R")
    txt = ft.fttxt2("auto")
    s = txt.servo(1)
    print("before val", getattr(s, "val", None), "pwm", getattr(s, "pwm", None))

    # Microseconds from servo.conf (610..2360)
    for us in (610, 1000, 1500, 2000, 2360):
        try_call("setLevelUs %s" % us, lambda u=us: s.setLevelUs(u))
        time.sleep(0.45)
        print("  val", getattr(s, "val", None), "pwm", getattr(s, "pwm", None))

    print("kick us pulse")
    s.setLevelUs(1200)
    time.sleep(0.2)
    s.setLevelUs(2200)
    time.sleep(0.4)
    s.setLevelUs(1200)
    time.sleep(0.3)

    print("try pwm_set_us")
    try_call("pwm_set_us 1500", lambda: s.pwm_set_us(1500))
    time.sleep(0.3)
    try_call("pwm_set_us 2200", lambda: s.pwm_set_us(2200))
    time.sleep(0.4)
    try_call("pwm_set_us 1200", lambda: s.pwm_set_us(1200))

    print("try setLevel again after extend")
    try_call("extend_range", lambda: s.extend_range())
    for v in (0, 256, 400, 512):
        try_call("setLevel %s" % v, lambda x=v: s.setLevel(x))
        time.sleep(0.35)
        print("  val", getattr(s, "val", None))

    txt.close()
    print("done")


if __name__ == "__main__":
    main()
