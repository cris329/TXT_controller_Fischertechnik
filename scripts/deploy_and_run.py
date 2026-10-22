# -*- coding: utf-8 -*-
"""Deploy Futballroboter to TXT 4.0 (permanent Autostart).

Purpose: thin wrapper around install_permanent.
Context: USB RNDIS default IP 192.168.7.2 user ft.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from install_permanent import main as install_main


if __name__ == "__main__":
    install_main()
