# -*- coding: utf-8 -*-
"""Pausa Futball en el TXT para poder entrar a Ajustes Wi-Fi.

Purpose: desactivar Autostart y detener la app en pantalla.
Context: USB 192.168.7.2; luego wait_wifi_and_switch.py.
@author Cristian Deysdayr Jimenez
@created 2026-10-16
"""

from __future__ import print_function

import os
import time

import paramiko

HOST = os.environ.get("TXT_HOST", "192.168.7.2")
PASSWORD = os.environ.get("TXT_PASSWORD", "fischertechnik")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REMOTE = "/opt/ft/workspaces/Futball"


def put_text(sftp, local, remote):
    """Upload Unix text. @param sftp: SFTP @param local: str @param remote: str"""
    data = open(local, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    with sftp.file(remote, "wb") as fh:
        fh.write(data)


def remote(client, cmd, wait=3):
    """Run SSH cmd. @param client: SSH @param cmd: str @param wait: int @return: str"""
    _, out, err = client.exec_command(cmd, timeout=wait + 20)
    time.sleep(wait)
    return (out.read() + err.read()).decode("utf-8", "replace")


def main():
    """Disable Autostart, stop app, kill leftovers. @return: None"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username="ft", password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    for name in ("autostart_disable.py", "stop_app.py"):
        put_text(sftp, os.path.join(ROOT, "scripts", name), REMOTE + "/" + name)
    sftp.close()

    print(remote(client, "sudo -u ftgui /usr/bin/python3 -u %s/autostart_disable.py" % REMOTE, 2))
    print(remote(client, "sudo -u ftgui /usr/bin/python3 -u %s/stop_app.py" % REMOTE, 3))
    print(
        remote(
            client,
            "busybox pkill -f Futball.py 2>/dev/null; "
            "busybox pkill -f Futball_cam.py 2>/dev/null; "
            "busybox ps w | grep -E 'Futball' | grep -v grep || echo Futball_stopped",
            3,
        )
    )
    client.close()
    print("OK: Futball pausado. En la pantalla del TXT abre Ajustes -> Wi-Fi.")
    print("Cuando este conectado, avisa para cambiar el panel a Wi-Fi.")


if __name__ == "__main__":
    main()
