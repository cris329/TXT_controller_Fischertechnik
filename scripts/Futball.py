# -*- coding: utf-8 -*-
"""Official TXT workspace entry: Futballroboter forever.

Purpose: drive + kick over MQTT; spawn resilient camera child.
Context: Autostart via Menu.conf fileAutoLoad/fileAutoStart.
@author Cristian Deysdayr Jimenez
@created 2026-10-13
"""

from __future__ import print_function

import json
import os
import subprocess
import sys
import threading
import time
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

LOG = "/tmp/Futball.log"
CAM = os.path.join(BASE, "Futball_cam.py")


def log(msg):
    """Append log line. @param msg: text @return: None"""
    try:
        with open(LOG, "a") as fh:
            fh.write("%s %s\n" % (int(time.time()), msg))
    except Exception:
        pass


def spawn_cam():
    """Start camera child. @return: Popen"""
    env = dict(os.environ)
    env["PYTHONPATH"] = BASE
    env["HOME"] = "/home/ftgui"
    logf = open("/tmp/Futball_cam.log", "a")
    return subprocess.Popen(
        ["/usr/bin/python3", "-u", CAM],
        cwd=BASE, env=env, stdin=open("/dev/null", "r"),
        stdout=logf, stderr=logf, preexec_fn=os.setsid,
    )


def run_once():
    """Drive MQTT loop and keep camera child alive. @return: None"""
    log("run_once begin")
    import ftlock
    import paho.mqtt.client as mqtt
    from robot.hardware import RobotHardware
    from robot.mqtt_bridge import CommandBridge
    from shared.protocol import DEFAULT_MQTT_PASSWORD, DEFAULT_MQTT_USER, TOPIC_STATUS

    class _NoCam(object):
        """Stub; cam real vive en hijo."""

        def start(self):
            return None

        def stop(self):
            return None

    ftlock.notify("R")
    hardware = RobotHardware()
    log("hardware ok")
    client = mqtt.Client("Futball-%s" % os.getpid())
    client.username_pw_set(DEFAULT_MQTT_USER, DEFAULT_MQTT_PASSWORD)
    bridge = CommandBridge(hardware, _NoCam())
    cam_proc = spawn_cam()
    log("camera child pid=%s" % cam_proc.pid)

    def on_connect(client, userdata, flags, rc):
        log("mqtt rc=%s" % rc)
        for topic in bridge.topics():
            client.subscribe(topic)
        client.publish(TOPIC_STATUS, bridge.status_payload(), retain=True)

    def on_message(client, userdata, msg):
        if msg.topic.endswith("/kick"):
            log("kick cmd")

            def _kick():
                bridge.handle(msg.topic, msg.payload)
                time.sleep(0.35)
                log("kick mid pwm=%s" % getattr(hardware, "last_kick_pwm", None))

            threading.Thread(target=_kick).start()
            return
        bridge.handle(msg.topic, msg.payload)

    try:
        client.max_queued_messages_set(1)
    except Exception:
        pass
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 3883, 60)
    client.loop_start()
    log("Futball running pid=%s" % os.getpid())
    beat = 0
    while True:
        beat += 1
        if cam_proc.poll() is not None:
            log("camera child exit=%s — respawn" % cam_proc.returncode)
            cam_proc = spawn_cam()
        client.publish(
            "futball/heartbeat",
            json.dumps({"role": "app", "t": int(time.time()), "n": beat}),
        )
        if beat % 5 == 0:
            ftlock.notify("R")
            log("heartbeat %s cam_pid=%s" % (beat, cam_proc.pid))
        time.sleep(2)


def main():
    """Restart forever after crash. @return: None"""
    log("main pid=%s" % os.getpid())
    while True:
        try:
            run_once()
        except Exception:
            with open(LOG, "a") as fh:
                fh.write(traceback.format_exc())
            log("restart in 3s")
            time.sleep(3)


if __name__ == "__main__":
    main()
