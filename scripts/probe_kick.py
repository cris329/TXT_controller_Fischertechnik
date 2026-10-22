# -*- coding: utf-8 -*-
"""Probe TXT servo S1 kick positions."""
from __future__ import print_function
import time

import ft
import ftlock


def main():
    """Sweep servo levels and print API attrs.

    @return: None
    """
    print(open("/opt/ft/config/servo.conf").read())
    ftlock.notify("R")
    txt = ft.fttxt2("auto")
    s = txt.servo(1)
    print("attrs", [a for a in dir(s) if not a.startswith("_")])
    for v in (0, 100, 250, 300, 400, 450, 512):
        try:
            s.setLevel(int(v))
            print("setLevel", v, "val", getattr(s, "val", None), "conn", getattr(s, "conn", None))
            time.sleep(0.4)
        except Exception as exc:
            print("setLevel", v, "ERR", exc)
    # kick motion like firmware
    s.setLevel(250)
    time.sleep(0.2)
    s.setLevel(400)
    time.sleep(0.35)
    s.setLevel(250)
    print("kick sequence done")
    txt.close()


if __name__ == "__main__":
    main()
