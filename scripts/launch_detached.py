# -*- coding: utf-8 -*-
"""Start supervisor under ftgui (NOPASSWD sudo target)."""
from __future__ import print_function
import os
import subprocess
import sys

REMOTE = "/opt/ft/workspaces/futball"


def main():
    """Kill old supervisor/bridges and start supervisor.sh detached.

    @return: None
    """
    null = open("/dev/null", "r+")
    # Stop previous supervisor shells and python bridges.
    ps = subprocess.check_output(["ps"], universal_newlines=True)
    for line in ps.splitlines():
        if "supervisor.sh" in line or "boot.py" in line or "boot_camera.py" in line:
            parts = line.split()
            if parts:
                try:
                    os.kill(int(parts[0]), 9)
                except Exception:
                    pass
    time_sleep = __import__("time").sleep
    time_sleep(1)
    subprocess.Popen(
        ["/bin/sh", REMOTE + "/supervisor.sh"],
        stdin=null,
        stdout=null,
        stderr=null,
        preexec_fn=os.setsid,
        cwd=REMOTE,
        env=dict(os.environ, PYTHONPATH=REMOTE),
    )
    print("supervisor launched")


if __name__ == "__main__":
    main()
