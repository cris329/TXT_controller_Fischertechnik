# -*- coding: utf-8 -*-
"""Start Futball via txtapi (preferred) or daemon fallback.

Purpose: keep one permanent process after SSH ends.
Context: called from install_permanent / PC watchdog as ftgui.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import os
import signal
import subprocess
import time

REMOTE = "/opt/ft/workspaces/Futball"
LOG = "/tmp/Futball.log"
PIDFILE = "/tmp/Futball.pid"


def _ps_lines():
    """Return process list with full command lines.

    @return: list of str
    """
    for args in (["busybox", "ps", "w"], ["ps", "w"], ["ps"]):
        try:
            out = subprocess.check_output(args, universal_newlines=True)
            return out.splitlines()
        except Exception:
            continue
    return []


def kill_orphans():
    """Kill leftover Futball processes not managed by txtapi.

    @return: int
    """
    killed = 0
    if os.path.isfile(PIDFILE):
        try:
            os.kill(int(open(PIDFILE).read().strip()), signal.SIGKILL)
            killed += 1
        except Exception:
            pass
    markers = ("Futball.py", "Futball_cam.py", "boot.py", "boot_camera.py", "supervisor.sh")
    for line in _ps_lines():
        if not any(m in line for m in markers):
            continue
        if "launch_futball.py" in line or "start_via_api.py" in line:
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            os.kill(int(parts[0]), signal.SIGKILL)
            killed += 1
        except Exception:
            pass
    return killed


def start_api():
    """Ask txtapi to start workspace Futball.

    @return: bool
    """
    try:
        out = subprocess.check_output(
            ["/usr/bin/python3", "-u", REMOTE + "/start_via_api.py"],
            universal_newlines=True,
            stderr=subprocess.STDOUT,
        )
        print(out.strip())
        return "200" in out or "pid" in out.lower()
    except Exception as exc:
        print("api failed: %s" % exc)
        return False


def start_daemon():
    """Double-fork daemon fallback if API unavailable.

    @return: int pid
    """
    try:
        open(LOG, "w").close()
    except Exception:
        pass
    pid = os.fork()
    if pid > 0:
        time.sleep(1)
        return pid
    os.setsid()
    pid2 = os.fork()
    if pid2 > 0:
        os._exit(0)
    os.chdir(REMOTE)
    env = dict(os.environ)
    env["PYTHONPATH"] = REMOTE
    env["HOME"] = "/home/ftgui"
    os.dup2(open("/dev/null", "r").fileno(), 0)
    os.dup2(open(LOG, "a").fileno(), 1)
    os.dup2(open(LOG, "a").fileno(), 2)
    os.execve(
        "/usr/bin/python3",
        ["/usr/bin/python3", "-u", REMOTE + "/Futball.py"],
        env,
    )


def main():
    """Kill leftovers, start via API, verify process alive.

    @return: None
    """
    n = kill_orphans()
    time.sleep(1)
    ok = start_api()
    if not ok:
        pid = start_daemon()
        with open(PIDFILE, "w") as fh:
            fh.write(str(pid) + "\n")
        print("daemon pid=%s" % pid)
    time.sleep(3)
    alive = [ln for ln in _ps_lines() if "Futball.py" in ln]
    print("Futball killed=%s alive=%s" % (n, bool(alive)))
    for ln in alive:
        print(ln.strip())


if __name__ == "__main__":
    main()
