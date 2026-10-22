# -*- coding: utf-8 -*-
"""Restart permanent Futball app on TXT over SSH."""

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
