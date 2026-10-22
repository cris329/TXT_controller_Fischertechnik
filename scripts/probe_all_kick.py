# -*- coding: utf-8 -*-
"""Probe S1-S3 and I1-I8 to find working kicker output."""
from __future__ import print_function
import time

import ft
import ftlock


def main():
    """Sweep servos with setLevel and setLevelUs; print inputs.

    @return: None
    """
    ftlock.notify("R")
    txt = ft.fttxt2("auto")
    print("servo.conf:")
    print(open("/opt/ft/config/servo.conf").read())
    for i in range(1, 9):
        try:
            inp = txt.input(i)
            print(
                "I%s conn=%s val=%s"
                % (i, getattr(inp, "conn", None), getattr(inp, "val", None))
            )
        except Exception as exc:
            print("I%s ERR %s" % (i, exc))
    for si in range(1, 4):
        s = txt.servo(si)
        print("=== S%s conn=%s ===" % (si, getattr(s, "conn", None)))
        # Official ROBO Pro positions 250 / 400 via setLevel
        for level in (250, 400, 250, 0, 512, 256):
            try:
                s.setLevel(int(level))
            except Exception as exc:
                print(" setLevel", level, exc)
            time.sleep(0.4)
            print(
                " setLevel %s pwm=%s val=%s"
                % (level, getattr(s, "pwm", None), getattr(s, "val", None))
            )
        # Same via microseconds (servo.conf 610..2360)
        for us in (1465, 1977, 1465, 610, 2360, 1500):
            try:
                s.setLevelUs(int(us))
            except Exception as exc:
                print(" setLevelUs", us, exc)
            time.sleep(0.4)
            print(
                " setLevelUs %s pwm=%s"
                % (us, getattr(s, "pwm", None))
            )
        try:
            s.pwm_set(400)
            time.sleep(0.4)
            print(" pwm_set 400 pwm=%s" % getattr(s, "pwm", None))
            s.pwm_set(250)
            time.sleep(0.4)
            print(" pwm_set 250 pwm=%s" % getattr(s, "pwm", None))
        except Exception as exc:
            print(" pwm_set ERR", exc)
    txt.close()
    print("DONE")


if __name__ == "__main__":
    main()
