# -*- coding: utf-8 -*-
"""Set TXT Menu.conf Autostart to Futball workspace.

Purpose: after reboot qtmenu starts Futball.py automatically.
Context: must run as ftgui (owns Menu.conf).
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

MENU = "/opt/ft/config/Fischertechnik/TXT_4.0_Menu.conf"
LOAD = "/opt/ft/workspaces/Futball/Futball.py"


def main():
    """Rewrite only fileAutoLoad / fileAutoStart lines.

    @return: None
    """
    with open(MENU, "r") as fh:
        lines = fh.read().splitlines()
    out = []
    seen_load = False
    seen_start = False
    for line in lines:
        if line.startswith("fileAutoLoad="):
            out.append("fileAutoLoad=" + LOAD)
            seen_load = True
        elif line.startswith("fileAutoStart="):
            out.append("fileAutoStart=true")
            seen_start = True
        else:
            out.append(line)
    if not seen_load:
        out.insert(1, "fileAutoLoad=" + LOAD)
    if not seen_start:
        out.insert(2, "fileAutoStart=true")
    text = "\n".join(out) + "\n"
    with open(MENU, "w") as fh:
        fh.write(text)
    # Confirm without dumping secrets.
    ok_load = any(l.startswith("fileAutoLoad=" + LOAD) for l in out)
    ok_start = any(l == "fileAutoStart=true" for l in out)
    print("autostart load=%s start=%s" % (ok_load, ok_start))


if __name__ == "__main__":
    main()
