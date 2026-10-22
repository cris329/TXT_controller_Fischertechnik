# -*- coding: utf-8 -*-
"""On-device soak: launch Futball and count MQTT frames locally."""
from __future__ import print_function
import json
import os
import subprocess
import time

import paho.mqtt.client as mqtt

REMOTE = "/opt/ft/workspaces/Futball"


def main():
    """Launch app and print frame/heartbeat counts for 45s.

    @return: None
    """
    subprocess.check_call(
        ["/usr/bin/python3", "-u", REMOTE + "/launch_futball.py"]
    )
    time.sleep(3)
    stats = {"frames": 0, "hb": 0, "last": 0}

    def on_connect(c, u, f, rc):
        c.subscribe("futball/#")

    def on_message(c, u, msg):
        if "jpeg" in msg.topic:
            stats["frames"] += 1
            stats["last"] = len(msg.payload)
        elif "heartbeat" in msg.topic:
            stats["hb"] += 1

    client = mqtt.Client("soak-local")
    client.username_pw_set("ft", "fischertechnik")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 3883, 60)
    client.loop_start()
    for i in range(9):
        time.sleep(5)
        ps = subprocess.check_output(["busybox", "ps", "w"], universal_newlines=True)
        alive = [ln for ln in ps.splitlines() if "Futball" in ln and "soak" not in ln]
        print(
            "T+%s frames=%s hb=%s size=%s procs=%s"
            % ((i + 1) * 5, stats["frames"], stats["hb"], stats["last"], len(alive))
        )
        for ln in alive:
            print(" ", ln.strip())
    client.loop_stop()
    client.disconnect()
    print("DONE", json.dumps(stats))
    print("CAMLOG")
    try:
        print(open("/tmp/Futball_cam.log").read()[-800:])
    except Exception as exc:
        print(exc)
    print("APPLOG")
    try:
        print(open("/tmp/Futball.log").read()[-800:])
    except Exception as exc:
        print(exc)


if __name__ == "__main__":
    main()
