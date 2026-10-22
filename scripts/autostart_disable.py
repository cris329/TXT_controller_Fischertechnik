# -*- coding: utf-8 -*-
"""Disable TXT Autostart so the menu/Wi-Fi settings are usable.

Purpose: pause Futball takeover while configuring Wi-Fi.
Context: must run as ftgui (owns Menu.conf).
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

from __future__ import print_function

MENU = "/opt/ft/config/Fischertechnik/TXT_4.0_Menu.conf"


def main():
    """Set fileAutoStart=false only. @return: None"""
    with open(MENU, "r") as fh:
        lines = fh.read().splitlines()
    out = []
    seen = False
    for line in lines:
        if line.startswith("fileAutoStart="):
            out.append("fileAutoStart=false")
            seen = True
        else:
            out.append(line)
    if not seen:
        out.insert(1, "fileAutoStart=false")
    with open(MENU, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("autostart start=False")


if __name__ == "__main__":
    main()
