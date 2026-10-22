# -*- coding: utf-8 -*-
"""Launch only the camera bridge under ftgui."""
from __future__ import print_function
import os
import subprocess
import sys

REMOTE = "/opt/ft/workspaces/futball"
null = open("/dev/null", "r+")
subprocess.Popen(
    [sys.executable, "-u", REMOTE + "/boot_camera.py"],
    stdin=null,
    stdout=null,
    stderr=null,
    preexec_fn=os.setsid,
    cwd=REMOTE,
)
print("camera launched")
