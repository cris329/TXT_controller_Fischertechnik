# -*- coding: utf-8 -*-
"""Restart TXT Futball app over SSH when heartbeat is missing.

Purpose: keep Futballroboter alive without manual redeploy.
Context: permanent workspace /opt/ft/workspaces/Futball.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

import os
import threading
import time

import paramiko

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REMOTE = "/opt/ft/workspaces/Futball"
PASSWORD = os.environ.get("TXT_PASSWORD", "fischertechnik")


class BridgeWatchdog(object):
    """SSH redeploy helper with cooldown."""

    def __init__(self, host, robot_mqtt):
        """Bind host and MQTT facade.

        @param host: TXT IP
        @param robot_mqtt: RobotMqtt instance
        """
        self.host = host
        self.robot = robot_mqtt
        self._lock = threading.Lock()
        self._busy = False
        self.last_restart = 0
        self.last_msg = "idle"

    def _put(self, sftp, local, remote):
        """Upload file with LF newlines.

        @param sftp: SFTP client
        @param local: local path
        @param remote: remote path
        @return: None
        """
        data = open(local, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        with sftp.file(remote, "wb") as fh:
            fh.write(data)

    def restart_now(self):
        """Upload Futball app and relaunch as ftgui.

        @return: str result message
        """
        with self._lock:
            if self._busy:
                return "restart already running"
            self._busy = True
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.host, username="ft", password=PASSWORD, timeout=15)
            sftp = client.open_sftp()
            for folder in ("shared", "robot"):
                local_dir = os.path.join(ROOT, folder)
                remote_dir = REMOTE + "/" + folder
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    sftp.mkdir(remote_dir)
                for name in os.listdir(local_dir):
                    if name.endswith(".py"):
                        self._put(sftp, os.path.join(local_dir, name), remote_dir + "/" + name)
            for src, dst in (
                ("scripts/Futball.py", "Futball.py"),
                ("scripts/Futball_cam.py", "Futball_cam.py"),
                ("scripts/launch_futball.py", "launch_futball.py"),
                ("scripts/start_via_api.py", "start_via_api.py"),
                ("scripts/autostart_enable.py", "autostart_enable.py"),
            ):
                self._put(sftp, os.path.join(ROOT, src), REMOTE + "/" + dst)
            sftp.close()
            _, out, err = client.exec_command(
                "chmod -R a+rwX %s; "
                "sudo -u ftgui /usr/bin/python3 -u %s/autostart_enable.py; "
                "sudo -u ftgui /usr/bin/python3 -u %s/launch_futball.py"
                % (REMOTE, REMOTE, REMOTE),
                timeout=30,
            )
            msg = (out.read() + err.read()).decode(errors="replace")
            client.close()
            self.last_restart = time.time()
            self.last_msg = msg.strip() or "ok"
            return self.last_msg
        except Exception as exc:
            self.last_msg = "error: %s" % exc
            return self.last_msg
        finally:
            self._busy = False

    def auto_loop(self):
        """Background: restart if no heartbeat for 20s (after warm-up).

        @return: None
        """
        time.sleep(30)
        while True:
            age = self.robot.heartbeat_age()
            if age is not None and age > 20:
                if time.time() - self.last_restart > 60:
                    self.restart_now()
            time.sleep(5)
