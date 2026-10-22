# -*- coding: utf-8 -*-
import os
import subprocess

cmds = [
    "cat /opt/ft/config/Fischertechnik/TXT_4.0_Menu.conf",
    "find /opt/ft/workspaces -type f | head -60",
    "ls -la /opt/ft/workspaces/examples/",
    "ls /usr/lib/python3.5/site-packages/txtapi/",
    "grep -rni autostart /usr/lib/python3.5/site-packages/txtapi 2>/dev/null | head -40",
    "grep -rni 'main.py' /usr/lib/python3.5/site-packages/txtapi 2>/dev/null | head -40",
    "strings /usr/bin/qtmenu | grep -iE 'autostart|main.py|workspaces' | head -40",
    "ls -la /opt/ft/tmp 2>/dev/null; ls /var/lib 2>/dev/null | head",
    "find /opt/ft -name '*.conf' -o -name '*project*' 2>/dev/null | head -40",
]
for cmd in cmds:
    print("====", cmd)
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print(out.decode("utf-8", "replace")[:2500])
    except Exception as exc:
        print(exc)
