# -*- coding: utf-8 -*-
"""Print Futball process and Autostart flags only."""
from __future__ import print_function
import os
import subprocess

MENU = "/opt/ft/config/Fischertechnik/TXT_4.0_Menu.conf"
print("LOG_TAIL:")
if os.path.isfile("/tmp/Futball.log"):
    print(open("/tmp/Futball.log").read()[-1500:])
print("PS:")
try:
    out = subprocess.check_output(["busybox", "ps", "w"], universal_newlines=True)
except Exception:
    out = subprocess.check_output(["ps", "w"], universal_newlines=True)
for line in out.splitlines():
    if "Futball" in line and "grep" not in line and "check_status" not in line:
        print(line)
print("AUTOSTART:")
for line in open(MENU).read().splitlines():
    if line.startswith("fileAuto"):
        print(line)
