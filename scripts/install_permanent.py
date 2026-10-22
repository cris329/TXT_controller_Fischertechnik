# -*- coding: utf-8 -*-
"""Install Futball workspace on TXT with Autostart (once).

Purpose: one-shot link; reboot keeps program + camera alive.
Context: USB RNDIS 192.168.7.2, user ft, run as ftgui.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import os
import time

import paramiko

HOST = os.environ.get("TXT_HOST", "192.168.7.2")
PASSWORD = os.environ.get("TXT_PASSWORD", "fischertechnik")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REMOTE = "/opt/ft/workspaces/Futball"
MENU = "/opt/ft/config/Fischertechnik/TXT_4.0_Menu.conf"


def put_text(sftp, local, remote):
    """Upload text file with Unix newlines.

    @param sftp: SFTP client
    @param local: local path
    @param remote: remote path
    @return: None
    """
    data = open(local, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    with sftp.file(remote, "wb") as fh:
        fh.write(data)


def upload_tree(sftp, local_dir, remote_dir):
    """Upload .py files recursively.

    @param sftp: SFTP client
    @param local_dir: local directory
    @param remote_dir: remote directory
    @return: None
    """
    try:
        sftp.stat(remote_dir)
    except IOError:
        sftp.mkdir(remote_dir)
    for name in os.listdir(local_dir):
        local = os.path.join(local_dir, name)
        remote = remote_dir + "/" + name
        if os.path.isdir(local):
            upload_tree(sftp, local, remote)
        elif name.endswith(".py"):
            put_text(sftp, local, remote)


def remote(client, cmd, wait=4):
    """Run SSH command and return output.

    @param client: SSH client
    @param cmd: shell command
    @param wait: seconds
    @return: str
    """
    _, out, err = client.exec_command(cmd, timeout=wait + 20)
    time.sleep(wait)
    return (out.read() + err.read()).decode("utf-8", "replace")


def main():
    """Deploy Futball workspace, enable Autostart, start app.

    @return: None
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username="ft", password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    try:
        sftp.stat(REMOTE)
    except IOError:
        sftp.mkdir(REMOTE)
    for folder in ("shared", "robot"):
        upload_tree(sftp, os.path.join(ROOT, folder), REMOTE + "/" + folder)
    for name in (
        "Futball.py",
        "Futball_cam.py",
        "autostart_enable.py",
        "launch_futball.py",
        "start_via_api.py",
        "check_status.py",
    ):
        put_text(sftp, os.path.join(ROOT, "scripts", name), REMOTE + "/" + name)
    sftp.close()

    print(remote(client, "chmod -R a+rwX %s/Futball.py %s/robot %s/shared 2>/dev/null || true" % (REMOTE, REMOTE, REMOTE), 2))
    # Enable Autostart keys only (no secrets printed).
    print(
        remote(
            client,
            "sudo -u ftgui /usr/bin/python3 -u %s/autostart_enable.py" % REMOTE,
            3,
        )
    )
    # Kill old bridges and start permanent app detached as ftgui.
    print(
        remote(
            client,
            "sudo -u ftgui /usr/bin/python3 -u %s/launch_futball.py" % REMOTE,
            5,
        )
    )
    time.sleep(3)
    print(remote(client, "busybox ps w | grep -E 'Futball.py|boot.py|boot_camera' | grep -v grep || true", 2))
    print(remote(client, "tail -n 20 /tmp/Futball.log 2>/dev/null || true", 2))
    client.close()
    print("OK: Futball installed + Autostart on", HOST)


if __name__ == "__main__":
    main()
